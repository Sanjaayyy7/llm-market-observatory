"""G8 descriptive adoption view: SDK downloads around price cuts (docs/prereg/event-study.md).

Descriptive only. No test, no causal claim. Events and clustering live in dbt (mart_event_study_panel).
"""
import json
import math
import subprocess
from datetime import date, datetime
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261115
N_PLACEBO = 100
WINDOW = 28
FLOOR = 8
CONTROL = "control"
GROUP_ORDER = ("openai", "anthropic", "google", "mistral", "cohere", "xai")
# Provider-verified cuts LiteLLM missed (DECISIONS 2026-11-17 "G5 kill re-verified"); excluded from placebo pools.
G5_VERIFIED_MISSED = {"mistral": ["2024-09-17"], "google": ["2024-10-01"]}
# prereg §2 frozen event rows: (canonical_model_id, sdk_group, a_date, b_date | None)
FROZEN_EVENTS = (
    ("mistral-large-2402", "mistral", "2024-05-31", None),
    ("claude-3-5-haiku-20241022", "anthropic", "2025-02-28", "2024-12-03"),
    ("o3-2025-04-16", "openai", "2025-06-10", "2025-06-10"),
    ("gpt-5.6-terra", "openai", "2026-07-31", "2026-07-30"),
    ("gpt-5.6-luna", "openai", "2026-07-31", "2026-07-30"),
    ("grok-4.20-0309-reasoning", "xai", "2026-08-12", None),
    ("grok-4.20-multi-agent-beta-0309", "xai", "2026-08-12", None),
    ("gpt-5.6-sol", "openai", "2026-08-22", "2026-08-21"),
    ("mistral-large-4", "mistral", "2026-11-03", None),
)

_CUTS_SQL = """
with g as (select distinct provider, sdk_group from seed_provider_map where sdk_group <> '')
select s.canonical_model_id, g.sdk_group,
       (s.first_cut_at at time zone 'UTC')::date as a_date,
       case when c.is_scored_event and not c.is_data_fix then c.announced_date end as b_date
from mart_launch_price_survival s
join g on g.provider = s.provider
left join mart_cut_audit c using (canonical_model_id)
where not s.censored
"""

_DOWNLOADS_SQL = """
select f.sdk_group, f.date, f.downloads,
       exists (select 1 from excl e where e.sdk_group = f.sdk_group
               and abs(date_diff('day', e.d, f.date)) <= 28) as excluded
from fct_sdk_downloads_daily f
"""


def verdict_line(k_a: int) -> str:
    if k_a < FLOOR:
        return f"Descriptive only: n={k_a} events, below the pre-registered floor of {FLOOR}."
    return f"Descriptive only: n={k_a} events; inference not built in v1.0."


def matches_prereg(rows) -> bool:
    got = {(m, g, str(a), None if b is None else str(b)) for m, g, a, b in rows}
    return got == set(FROZEN_EVENTS)


def _ratio(pre: pd.Series, post: pd.Series):
    if len(pre) != WINDOW or len(post) != WINDOW or pre.mean() <= 0:
        return None
    return float(post.mean() / pre.mean())


def event_windows(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (event_id, group), p in panel.groupby(["event_id", "sdk_group"], sort=True):
        pre = p.loc[(p["rel_day"] >= -WINDOW) & (p["rel_day"] < 0), "downloads"]
        post = p.loc[(p["rel_day"] >= 0) & (p["rel_day"] < WINDOW), "downloads"]
        ratio = _ratio(pre, post)
        rows.append({"series": p["series"].iloc[0], "event_id": event_id, "event_date": p["event_date"].iloc[0],
                     "sdk_group": group, "n_pre": len(pre), "n_post": len(post), "ratio": ratio,
                     "incomplete_window": ratio is None})
    out = pd.DataFrame(rows, columns=["series", "event_id", "event_date", "sdk_group", "n_pre", "n_post",
                                      "ratio", "incomplete_window"])
    out["ratio"] = out["ratio"].astype(object)
    return out


def placebo_ratios(downloads: pd.DataFrame, n: int = N_PLACEBO, seed: int = SEED) -> pd.DataFrame:
    df = downloads.assign(date=pd.to_datetime(downloads["date"]))
    rows = []
    for i, group in enumerate(GROUP_ORDER):
        g = df[df["sdk_group"] == group].sort_values("date")
        if g.empty:
            continue
        series = g.set_index("date")["downloads"]
        step = pd.Timedelta(1, "D")
        has_window = [
            all(d + k * step in series.index for k in range(-WINDOW, WINDOW)) for d in g["date"]
        ]
        eligible = sorted(g.loc[~g["excluded"].to_numpy() & np.array(has_window), "date"])
        if not eligible:
            continue
        rng = np.random.default_rng([seed, i])
        picks = rng.choice(np.array(eligible, dtype="datetime64[ns]"), size=min(n, len(eligible)), replace=False)
        for d in pd.to_datetime(picks):
            pre = series.loc[d - WINDOW * step: d - step]
            post = series.loc[d: d + (WINDOW - 1) * step]
            rows.append({"sdk_group": group, "pseudo_date": d, "ratio": _ratio(pre, post)})
    out = pd.DataFrame(rows, columns=["sdk_group", "pseudo_date", "ratio"])
    out["ratio"] = out["ratio"].astype(object)
    return out


def placebo_share(ratio, pool: pd.Series) -> float | None:
    """Share of placebo ratios <= the event ratio; None when there is no ratio (NaN or None) or no pool."""
    if ratio is None or pd.isna(ratio) or pool.empty:
        return None
    return float((pool <= ratio).mean())


def _clean(o):
    if isinstance(o, dict):
        return {str(k): _clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_clean(v) for v in o]
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (float, np.floating)):
        return None if math.isnan(o) or math.isinf(o) else float(o)
    if isinstance(o, (date, datetime, pd.Timestamp)):
        return str(o)[:10]
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def to_strict_json(obj) -> str:
    return json.dumps(_clean(obj), indent=2, allow_nan=False)


def _prereg_commit() -> str | None:
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", "docs/prereg/event-study.md"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    return out[-1] if out else None


def _members(cuts: pd.DataFrame, windows: pd.DataFrame) -> dict:
    """Assign each cut to its group's latest event anchored on or before the cut date."""
    members: dict[str, list[str]] = {}
    for series, col in (("A", "a_date"), ("B", "b_date")):
        ev = windows[(windows["series"] == series) & (windows["sdk_group"] != CONTROL)]
        for _, c in cuts.dropna(subset=[col]).iterrows():
            anchors = ev[(ev["sdk_group"] == c["sdk_group"]) & (pd.to_datetime(ev["event_date"]) <= pd.Timestamp(c[col]))]
            if not anchors.empty:
                eid = anchors.sort_values("event_date")["event_id"].iloc[-1]
                members.setdefault(eid, []).append(c["canonical_model_id"])
    return {k: sorted(v) for k, v in members.items()}


def main(db: Path = ROOT / "data/warehouse.duckdb", out: Path = ROOT / "exports") -> dict:
    con = duckdb.connect(str(db), read_only=True)
    con.execute("SET TimeZone = 'UTC'")
    panel = con.execute("select * from mart_event_study_panel").df()
    cut_rows = con.execute(_CUTS_SQL).fetchall()
    cuts = pd.DataFrame(cut_rows, columns=["canonical_model_id", "sdk_group", "a_date", "b_date"])
    windows = event_windows(panel)
    own = windows[windows["sdk_group"] != CONTROL]
    excl = [(g, str(d)[:10]) for g, d in zip(own["sdk_group"], own["event_date"], strict=True)]
    excl += [(g, d) for g, ds in G5_VERIFIED_MISSED.items() for d in ds]
    con.register("excl_raw", pd.DataFrame(excl, columns=["sdk_group", "d"]))
    con.execute("create temp table excl as select sdk_group, d::date as d from excl_raw")
    drawers = set(own.loc[own["series"] == "A", "sdk_group"])
    base = con.execute(_DOWNLOADS_SQL).df()
    con.close()

    placebo = placebo_ratios(base[base["sdk_group"].isin(drawers)])
    members = _members(cuts, windows)
    control = windows[windows["sdk_group"] == CONTROL].set_index("event_id")["ratio"].to_dict()
    events = []
    for r in own.itertuples():
        pool = placebo.loc[placebo["sdk_group"] == r.sdk_group, "ratio"].dropna().astype(float)
        share = placebo_share(r.ratio, pool)
        events.append({"series": r.series, "event_id": r.event_id, "event_date": r.event_date,
                       "sdk_group": r.sdk_group, "members": members.get(r.event_id, []), "ratio": r.ratio,
                       "incomplete_window": r.incomplete_window, "placebo_share_le": share,
                       **({"control_ratio": control.get(r.event_id)} if r.series == "A" else {})})
    k_a = sum(e["series"] == "A" for e in events)
    result = {"k_a": k_a, "k_b": len(events) - k_a, "verdict": verdict_line(k_a),
              "matches_prereg": matches_prereg(cut_rows),
              "prereg_commit": _prereg_commit(), "events": events}
    out.mkdir(parents=True, exist_ok=True)
    (out / "event_study.json").write_text(to_strict_json(result))
    placebo.to_parquet(out / "placebo.parquet", index=False)
    return result


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if k != "events"}, indent=2))
