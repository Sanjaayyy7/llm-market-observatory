"""G7 export: Parquet and JSON for the static site, behind an approval gate (Task 10 steps 1-2)."""
import json
import shutil
from datetime import UTC, date, datetime
from pathlib import Path
from typing import NamedTuple

import duckdb
import numpy as np
from lifelines import AalenJohansenFitter

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ("litellm", "arena", "epoch", "pypi", "tokencanopy")
HORIZON_DAYS = 365
SHA_LEN = 7
COPIED = ("headline.json", "epoch_check.json", "event_study.json", "km_curve.parquet", "placebo.parquet")
PARQUETS = {
    "survival": "mart_launch_price_survival", "price_daily": "fct_model_price_daily",
    "price_changes": "fct_price_change", "cut_audit": "mart_cut_audit", "models": "dim_model",
    "top_tier_screen": "mart_top_tier_screen", "coverage": "int_crosswalk_coverage",
    "event_panel": "mart_event_study_panel", "freshness": "source_freshness",
    "epoch_audit": "seed_epoch_mismatch_audit",
}
UNCOVERED_SQL = """
select c.model_name, c.provider, c.closed, s.reason_code, s.evidence_url
from int_crosswalk_coverage c left join seed_crosswalk_uncovered s using (model_name)
where not c.covered order by c.model_name
"""
TOKENCANOPY_SOURCES_SQL = """
select distinct source from read_parquet(?, hive_partitioning = true)
where run_date = (select max(run_date) from read_parquet(?, hive_partitioning = true))
  and platform in (select distinct platform from stg_tokencanopy__prices)
order by source
"""
UNAPPROVED_SQL = """
select 'seed_model_crosswalk:' || source || ':' || source_key from seed_model_crosswalk
 where match_method = 'manual' and coalesce(trim(approved_by), '') = ''
union all
select 'seed_models:' || canonical_model_id from seed_models where coalesce(trim(approved_by), '') = ''
"""
REROUTE_SQL = """
with last as (
  select r.canonical_model_id, r.reroute_date, r.target_model_id, r.evidence_url,
         (select max(s.snapshot_date) from stg_litellm__snapshots s
           where s.model_key in (select source_key from seed_model_crosswalk x
                                  where x.source = 'litellm' and x.canonical_model_id = r.canonical_model_id)
         ) as last_listed
  from seed_model_reroute r
), d as (
  select *, (select min(snapshot_date) from stg_litellm__snapshots where snapshot_date > last.last_listed)
            as litellm_delisted from last)
select canonical_model_id, reroute_date, target_model_id, evidence_url, last_listed, litellm_delisted,
       date_diff('day', reroute_date, litellm_delisted) as lag_days
from d where litellm_delisted is not null and reroute_date is not null
"""
OUTCOME_SQL = """
select s.days_at_launch_price as d,
       case when not s.censored then 1
            when e.end_ts = (select max(end_ts) from int_model_exposure) then 0 else 2 end as code
from mart_launch_price_survival s join int_model_exposure e using (canonical_model_id)
"""


class Stamp(NamedTuple):
    max_dates: dict[str, date]
    litellm_sha7: str
    run_ts: datetime


def cut_incidence_365(durations, codes) -> float:
    """Aalen-Johansen cumulative incidence of event 1 at the last timeline point <= 365."""
    ajf = AalenJohansenFitter(seed=0).fit(np.asarray(durations), np.asarray(codes), event_of_interest=1)
    cif = ajf.cumulative_density_.iloc[:, 0]
    before = cif[cif.index <= HORIZON_DAYS]
    return float(before.iloc[-1]) if len(before) else 0.0


def _stamp(c) -> Stamp:
    got = dict(c.execute("select source, max(max_date) from source_freshness group by source").fetchall())
    missing = sorted(set(SOURCES) - set(got))
    if missing:
        raise ValueError(f"source_freshness missing sources: {missing}")
    sha = c.execute("select commit_sha from stg_litellm__snapshots order by commit_ts desc, snapshot_date desc"
                    " limit 1").fetchone()[0]
    return Stamp({s: got[s] for s in SOURCES}, sha[:SHA_LEN], datetime.now(UTC))


def _methods(c, exports: Path, raw: Path) -> dict:
    tc = str(raw / "tokencanopy/*/part.parquet")
    errs = raw / "litellm/_replay_errors.parquet"
    if not errs.exists():
        raise FileNotFoundError(f"{errs} (run make fetch)")
    d, code = zip(*c.execute(OUTCOME_SQL).fetchall(), strict=True)
    one = lambda q, *a: c.execute(q, list(a)).fetchone()[0]
    return {
        "aj_cut_365": cut_incidence_365(d, code),
        "km_cut_365": json.loads((exports / "headline.json").read_text())["share_cut_365"],
        "outcome_counts": {"cut": code.count(1), "still_listed": code.count(0), "ended": code.count(2)},
        "unranked_count": one("select count(*) from mart_top_tier_screen where is_unranked"),
        "replay_days": one("select count(distinct snapshot_date) from stg_litellm__snapshots"),
        "tokencanopy_sources": [r[0] for r in c.execute(TOKENCANOPY_SOURCES_SQL, [tc, tc]).fetchall()],
        "replay_error_days": one("select count(distinct snapshot_date) from read_parquet(?)", str(errs)),
    }


def _non_https_urls(c, queries: dict[str, str]) -> list[str]:
    """Columns named *url* whose non-null values do not start with https://, as 'file.column: n'."""
    bad = []
    for name, q in queries.items():
        cols = [d[0] for d in c.execute(f"select * from ({q}) limit 0").description if "url" in d[0].lower()]
        for col in cols:
            n = c.execute(f'select count(*) from ({q}) where "{col}" is not null '
                          f"and \"{col}\" not like 'https://%'").fetchone()[0]
            if n:
                bad.append(f"{name}.{col}: {n}")
    return bad


def export_site(warehouse: Path, out: Path, *, exports: Path = ROOT / "exports",
                raw: Path = ROOT / "data/raw") -> Stamp:
    c = duckdb.connect(str(warehouse), read_only=True)
    try:
        c.execute("SET TimeZone = 'UTC'")
        bad = [r[0] for r in c.execute(UNAPPROVED_SQL).fetchall()]
        if bad:
            raise ValueError(f"unapproved rows block export: {bad}")
        stamp = _stamp(c)
        gone = [f for f in COPIED if not (exports / f).exists()]
        if gone:
            raise FileNotFoundError(f"{gone} missing in {exports} (run make analyze)")
        methods = _methods(c, exports, raw)
        # order by all: a rebuilt warehouse may scan rows in another order; committed Parquet must not churn
        queries = {**{name: f"select * from {rel}" for name, rel in PARQUETS.items()},
                   "reroute_lag": REROUTE_SQL, "uncovered": UNCOVERED_SQL}
        unsafe = _non_https_urls(c, queries)
        if unsafe:  # the pages render these as links; only https may reach an href
            raise ValueError(f"non-https URLs block export: {unsafe}")
        out.mkdir(parents=True, exist_ok=True)
        for f in COPIED:
            shutil.copy2(exports / f, out / f)
        for name, q in queries.items():
            target = str(out / f"{name}.parquet").replace("'", "''")
            c.execute(f"copy (select * from ({q}) order by all) to '{target}' (format parquet)")
        (out / "methods.json").write_text(json.dumps(methods, indent=2))
        # stamp last: a failure above never leaves a new stamp beside stale data (the old stamp may then understate)
        (out / "stamp.json").write_text(json.dumps({
            "max_dates": {s: d.isoformat() for s, d in stamp.max_dates.items()},
            "litellm_sha7": stamp.litellm_sha7, "run_ts": stamp.run_ts.isoformat()}, indent=2))
        return stamp
    finally:
        c.close()


def main() -> None:
    stamp = export_site(ROOT / "data/warehouse.duckdb", ROOT / "site/src/data")
    print(stamp)


if __name__ == "__main__":
    main()
