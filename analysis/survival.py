"""G6 headline: Kaplan-Meier share of top-tier models that cut list price within 365 days.

Published as a dataset measurement (docs/05-build-plan/2026-11-15-v1-ship-line.md Task 9).
"""
import json
import math
from pathlib import Path
from typing import Literal, NamedTuple

import duckdb
import pandas as pd
from lifelines import KaplanMeierFitter
from statsmodels.stats.proportion import proportion_confint

ROOT = Path(__file__).resolve().parents[1]
HORIZON_DAYS = 365
ALPHA = 0.05
EXACT_BELOW_EVENTS = 3
THRESHOLDS = (0.05, 0.10, 0.20)
HEADLINE_CELL = ("top_tier", 0.10)
SELF_CHECK_TOL = 1e-12


class KMResult(NamedTuple):
    n: int
    events: int
    share_cut_365: float
    ci_low: float
    ci_high: float
    median_days: float | None
    method: Literal["km", "exact"]


def _fit(df: pd.DataFrame) -> tuple[KMResult, KaplanMeierFitter]:
    dur = df["duration"].astype(float)
    ev = df["event"].astype(int)
    kmf = KaplanMeierFitter(alpha=ALPHA).fit(dur, ev)
    n, events = len(df), int(ev.sum())
    median = kmf.median_survival_time_
    median_days = None if math.isinf(median) else float(median)
    if events < EXACT_BELOW_EVENTS:
        k = int(((ev == 1) & (dur <= HORIZON_DAYS)).sum())
        low, high = proportion_confint(k, n, alpha=ALPHA, method="beta")
        return KMResult(n, events, k / n, float(low), float(high), median_days, "exact"), kmf
    sf, ci = kmf.survival_function_.iloc[:, 0], kmf.confidence_interval_
    before = sf.index[sf.index <= HORIZON_DAYS]
    if len(before) == 0:  # no timeline point yet: nobody has been observed to cut
        share, low, high = 0.0, 0.0, 0.0
    else:
        t = before[-1]  # last point <= 365, never the nearest
        share, low, high = 1 - sf.loc[t], 1 - ci.loc[t].iloc[1], 1 - ci.loc[t].iloc[0]
    return KMResult(n, events, float(share), float(low), float(high), median_days, "km"), kmf


def fit_km(df: pd.DataFrame) -> KMResult:
    return _fit(df)[0]


_SENS_SQL = """
select e.canonical_model_id,
       date_diff('day', e.listed_at::date, coalesce(min(c.change_ts), e.end_ts)::date) as duration,
       min(c.change_ts) is not null as event
from exposure e
left join changes c
  on c.canonical_model_id = e.canonical_model_id
 and round(c.pct, 9) <= -?
 and not c.is_correction
 and c.change_ts < e.end_ts
where e.is_top_tier or not ?
group by e.canonical_model_id, e.listed_at, e.end_ts
"""


def sensitivity(exposure: pd.DataFrame, changes: pd.DataFrame) -> pd.DataFrame:
    con = duckdb.connect()
    con.execute("SET TimeZone = 'UTC'")
    con.register("exposure", exposure)
    con.register("changes", changes)
    rows = []
    for population, top_only in (("top_tier", True), ("all", False)):
        for threshold in THRESHOLDS:
            df = con.execute(_SENS_SQL, [threshold, top_only]).df()
            fit = fit_km(df)._asdict()
            fit.pop("median_days")  # R4 columns only; a None/float mix would serialize as NaN
            rows.append({"population": population, "threshold": threshold, **fit})
    con.close()
    return pd.DataFrame(rows)


_VERIFIED_SQL = """
select m.canonical_model_id, not m.censored as mart_event,
       (a.canonical_model_id is not null) as audited, coalesce(a.is_data_fix, false) as is_data_fix,
       m.days_at_launch_price,
       date_diff('day', e.listed_at::date, e.end_ts::date) as exposure_days
from mart_launch_price_survival m
join int_model_exposure e using (canonical_model_id)
left join (select * from mart_cut_audit where is_scored_event) a using (canonical_model_id)
"""


def verified_frame(con) -> pd.DataFrame:
    """Mart rows where an event counts only if the audit row is not a data fix (fix -> censored at end_ts)."""
    con.execute("SET TimeZone = 'UTC'")
    v = con.execute(_VERIFIED_SQL).df()
    missing = v[v["mart_event"] & ~v["audited"]]["canonical_model_id"].tolist()
    if missing:
        raise ValueError(f"cut events without a scored audit row: {missing}")
    fix = v["mart_event"] & v["is_data_fix"]
    return pd.DataFrame({
        "canonical_model_id": v["canonical_model_id"],
        "duration": v["days_at_launch_price"].where(~fix, v["exposure_days"]),
        "event": v["mart_event"] & ~fix,
    })


def _curve(series: str, kmf: KaplanMeierFitter) -> pd.DataFrame:
    sf, ci = kmf.survival_function_, kmf.confidence_interval_
    return pd.DataFrame({"series": series, "days": sf.index.astype(float), "survival": sf.iloc[:, 0].to_numpy(),
                         "ci_lower": ci.iloc[:, 0].to_numpy(), "ci_upper": ci.iloc[:, 1].to_numpy()})


def _audit_stats(con) -> dict:
    n_audited, n_fix = con.execute(
        "select count(*), count(*) filter (where is_data_fix) from mart_cut_audit where is_scored_event").fetchone()
    lag = con.execute("select median(lag_days) from mart_cut_audit where not is_data_fix and lag_days is not null"
                      ).fetchone()[0]
    return {"commit_lag_median_days": None if lag is None else float(lag), "n_audited": n_audited,
            "n_data_fix": n_fix, "audit_data_fix_rate": n_fix / n_audited if n_audited else None}


def main(db: Path = ROOT / "data/warehouse.duckdb", out: Path = ROOT / "exports") -> dict:
    con = duckdb.connect(str(db), read_only=True)
    con.execute("SET TimeZone = 'UTC'")
    mart = con.execute("select days_at_launch_price as duration, not censored as event "
                       "from mart_launch_price_survival").df()
    headline, kmf = _fit(mart)
    verified, kmf_v = _fit(verified_frame(con))
    sens = sensitivity(con.execute("select * from int_model_exposure").df(),
                       con.execute("select canonical_model_id, change_ts, pct, is_correction "
                                   "from fct_price_change").df())
    audit = _audit_stats(con)
    con.close()

    cell = sens[(sens["population"] == HEADLINE_CELL[0]) & (sens["threshold"] == HEADLINE_CELL[1])].iloc[0]
    if (cell["n"], cell["events"]) != (headline.n, headline.events) or \
            abs(cell["share_cut_365"] - headline.share_cut_365) > SELF_CHECK_TOL:
        raise AssertionError(f"mart KM {headline} != sensitivity {HEADLINE_CELL} {cell.to_dict()}")

    result = {**headline._asdict(), **audit, "scope": "dataset_measurement", "validation": "failed",
              "verified_only": verified._asdict(), "sensitivity": sens.to_dict("records")}
    out.mkdir(parents=True, exist_ok=True)
    (out / "headline.json").write_text(json.dumps(result, indent=2))
    pd.concat([_curve("observed", kmf), _curve("verified_only", kmf_v)], ignore_index=True
              ).to_parquet(out / "km_curve.parquet", index=False)
    return result


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if not isinstance(v, (list, dict))}, indent=2))
