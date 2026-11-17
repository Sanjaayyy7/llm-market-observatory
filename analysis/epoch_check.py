"""G5 Epoch ground-truth check: do our first-party list prices agree with Epoch's dated prices?

Spec: docs/05-build-plan/2026-11-15-v1-ship-line.md Task 8; rules frozen in docs/prereg/epoch-check.md.
"""
import json
import math
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

import duckdb
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # package=false: make `ingest` importable
from ingest.draft_crosswalk import canon, norm

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs/prereg/epoch-check.md"
HISTORY_START = date(2023, 9, 6)
EQUAL_TOL = 0.005
COVERAGE = 0.8
COMPARED = ("agrees", "agrees_late", "changed_then_agrees", "mismatch")
AUDITED = ("mismatch", "changed_then_agrees")
GATED_VERDICTS = ("epoch_non_list_price", "real_change")
EPOCH_PUBLISHED = {"epoch_published_factor": 42.0189988368494, "epoch_ci90": [4.398, 401.44], "epoch_n": 6}
ROW_COLS = ["model_name", "obs_date", "api_id", "canonical_model_id", "series", "is_headline", "epoch_price",
            "our_price_at_start", "first_date_ours_equal", "lag_days", "status", "verdict"]
SERIES_COLS = ["snapshot_date", "price", "series"]


def _d(x) -> date:
    return pd.Timestamp(x).date()


def _bare(model_key: str, litellm_provider: str) -> str:
    return model_key.lower().removeprefix(litellm_provider.lower() + "/")  # G2 rule, ingest/draft_crosswalk.py


def frozen_headline(path: Path = PREREG) -> set:
    """The frozen headline api_ids, parsed from the prereg."""
    m = re.search(r"Frozen headline rows \(\d+\):\*\*.*?\n\s*`([^`]+)`", path.read_text())
    return {x.strip() for x in m.group(1).split(",")}


# ---- Epoch's frontier ----

def epoch_frontier(cands: pd.DataFrame, threshold: float):
    upper = min(threshold + 100, 100)
    points, best = [], math.inf
    for r in cands.sort_values("obs_date", kind="stable").itertuples(index=False):
        if threshold <= r.gpqa_score < upper and r.usd_per_mtok < best:
            if points and points[-1].obs_date == r.obs_date:
                points.pop()
            points.append(r)
            best = r.usd_per_mtok
    if len(points) < 4:
        return None
    return pd.DataFrame(points).reset_index(drop=True)


def annualized_factor(points: pd.DataFrame) -> float:
    x = np.array([_d(v).toordinal() for v in points["obs_date"]], dtype=float)
    slope = np.polyfit(x, np.log10(points["usd_per_mtok"].astype(float)), 1)[0]
    return float(10 ** (-slope * 365))


# ---- our price series ----

_BLEND = "round((3 * v.in_per_mtok + v.out_per_mtok) / 4, 6)"


def our_series(con, api_id: str, provider: str) -> pd.DataFrame:
    """fct series when api_id is in fct, else the key series. attrs['key_conflicts'] lists days keys disagree."""
    con.execute("SET TimeZone = 'UTC'")
    fct = con.execute("select date as snapshot_date, blended_per_mtok as price, 'fct' as series "
                      "from fct_model_price_daily where canonical_model_id = ? order by 1", [api_id]).df()
    out = fct if len(fct) else pd.DataFrame(columns=SERIES_COLS)
    out.attrs["key_conflicts"] = []
    if len(fct):
        return out
    keys = con.execute("select distinct s.model_key, s.litellm_provider from stg_litellm__snapshots s "
                       "join seed_provider_map p on p.litellm_provider = s.litellm_provider and p.is_first_party "
                       "where p.provider = ?", [provider]).df()
    keys["bare"] = [_bare(k, lp) for k, lp in zip(keys["model_key"], keys["litellm_provider"])]
    keys = keys[keys["bare"].map(norm) == norm(api_id)]
    if keys.empty:
        return out
    con.register("g5_keys", keys[["model_key"]])
    try:
        per_key = con.execute(f"""
            select d.snapshot_date, v.model_key, {_BLEND} as price
            from dim_model_price v join g5_keys k using (model_key)
            join (select distinct snapshot_date from stg_litellm__snapshots) d
              on v.valid_from::date <= d.snapshot_date and (v.valid_to is null or v.valid_to::date > d.snapshot_date)
            where {_BLEND} > 0""").df()
    finally:
        con.unregister("g5_keys")
    if per_key.empty:
        return out
    g = per_key.groupby("snapshot_date")["price"].agg(["min", "max"]).reset_index().sort_values("snapshot_date")
    res = pd.DataFrame({"snapshot_date": g["snapshot_date"], "price": g["min"], "series": "key"}).reset_index(drop=True)
    res.attrs["key_conflicts"] = [str(_d(x)) for x in g.loc[(g["max"] - g["min"]) > 1e-6, "snapshot_date"]]
    return res


# ---- price agreement ----

def _equal(ours, epoch) -> bool:
    return ours is not None and round(abs(ours - epoch), 6) <= EQUAL_TOL


def _compare(series: pd.DataFrame, obs: date, epoch: float, snapshot_dates) -> dict:
    # price(d) = series price on the latest global snapshot <= d; None if the series has no row on that snapshot
    by_day = {_d(x): float(p) for x, p in zip(series["snapshot_date"], series["price"])}
    cal = sorted(_d(x) for x in snapshot_dates)
    start = max(obs, HISTORY_START)
    days = [start] + [x for x in cal if x > start]
    at = []
    for day in days:
        prior = [x for x in cal if x <= day]
        at.append(by_day.get(prior[-1]) if prior else None)
    out = {"our_price_at_start": at[0], "first_date_ours_equal": None, "lag_days": None}
    if _equal(at[0], epoch):
        return {**out, "status": "agrees", "first_date_ours_equal": start}
    first = next((i for i, p in enumerate(at) if _equal(p, epoch)), None)
    if first is None:
        return {**out, "status": "mismatch"}
    out["first_date_ours_equal"] = days[first]
    if any(p is not None for p in at[:first]):
        return {**out, "status": "changed_then_agrees"}
    return {**out, "status": "agrees_late", "lag_days": (days[first] - start).days}


def _verdict(audit_row, provider: str, domains) -> str:
    if audit_row is None or audit_row["approved_by"] != "cofounder" or audit_row["verdict"] not in GATED_VERDICTS:
        return "panel_error"
    url = urlparse(str(audit_row["source_url"]))
    host = (url.hostname or "").lower()
    if url.scheme != "https" or not host or domains is None:
        return "panel_error"
    for dom in domains.loc[domains["provider"] == provider, "doc_domain"].str.lower():
        if host == dom or host.endswith("." + dom):
            return audit_row["verdict"]
        if host == "web.archive.org" and dom in (url.path + "?" + (url.query or "")).lower():
            return audit_row["verdict"]
    return "panel_error"


def price_agreement(cands, status, xwalk, series_by_row, audit, headline_ids, *, provider_domains=None, snapshot_dates):
    """One row per (model_name, obs_date) of the status seed. provider_domains gates audit source_urls.
    snapshot_dates is the sorted global LiteLLM snapshot calendar (required: no fallback to series dates)."""
    price = {(r.model_name, _d(r.obs_date)): r.usd_per_mtok for r in cands.itertuples(index=False)}
    canon_of = dict(zip(xwalk["source_key"], xwalk["canonical_model_id"]))
    audits = {(r["model_name"], _d(r["obs_date"])): r for _, r in audit.iterrows()}
    rows = []
    for s in status.to_dict("records"):
        key = (s["model_name"], _d(s["obs_date"]))
        api = s.get("api_id") if isinstance(s.get("api_id"), str) and s.get("api_id") else None
        row = dict.fromkeys(ROW_COLS)
        row.update(model_name=key[0], obs_date=key[1], api_id=api, epoch_price=price.get(key),
                   canonical_model_id=canon_of.get(f"{key[0]}|{key[1]}"), is_headline=api in headline_ids)
        series = series_by_row.get(key)
        if s["scope"] == "out_of_scope":
            row.update(status="out_of_scope", is_headline=False)
        elif series is None or len(series) == 0:
            row.update(status="not_in_panel")
        else:
            row.update(series=series["series"].iloc[0], **_compare(series, key[1], row["epoch_price"], snapshot_dates))
        if row["status"] in AUDITED:
            row["verdict"] = _verdict(audits.get(key), s["provider"], provider_domains)
        rows.append(row)
    return pd.DataFrame(rows, columns=ROW_COLS)


# ---- gate ----

def counts(rows: pd.DataFrame, status_seed: pd.DataFrame) -> dict:
    st = rows["status"]
    pe = rows["verdict"] == "panel_error"
    hl = rows["is_headline"].astype(bool)
    return {"n_candidates": len(rows), "n_in_scope": int((status_seed["scope"] == "in_scope").sum()),
            "n_compared": int(st.isin(COMPARED).sum()), "n_agree": int((st == "agrees").sum()),
            "n_agree_late": int((st == "agrees_late").sum()),
            "n_changed_then_agrees": int((st == "changed_then_agrees").sum()),
            "n_mismatch": int((st == "mismatch").sum()), "n_not_in_panel": int((st == "not_in_panel").sum()),
            "n_key_series": int((rows["series"] == "key").sum()), "n_panel_error": int(pe.sum()),
            "n_panel_error_headline": int((pe & hl).sum()), "n_headline": int(hl.sum()),
            "n_headline_compared": int((hl & st.isin(COMPARED)).sum())}


def evaluate(rows, status_seed, provider_map, frozen_headline) -> bool:
    keys = list(zip(status_seed["model_name"], status_seed["obs_date"].map(_d)))
    rkeys = list(zip(rows["model_name"], rows["obs_date"].map(_d)))
    if len(set(keys)) != len(keys) or sorted(rkeys) != sorted(keys) or rows["status"].isna().any():
        return False  # (1) exactly one status per pair
    first_party = set(provider_map.loc[provider_map["is_first_party"].astype(bool), "provider"])
    status_of = dict(zip(rkeys, rows["status"]))
    for k, scope, prov in zip(keys, status_seed["scope"], status_seed["provider"]):
        if scope == "in_scope" and (prov not in first_party or status_of[k] == "out_of_scope"):
            return False
        if scope == "out_of_scope" and status_of[k] != "out_of_scope":
            return False
    c = counts(rows, status_seed)
    if c["n_compared"] == 0 or c["n_compared"] < math.ceil(COVERAGE * c["n_in_scope"]):
        return False  # (2)
    if c["n_panel_error_headline"] != 0:
        return False  # (3)+(4): unaudited rows are panel errors; only headline ones gate
    hl = rows[rows["is_headline"].astype(bool)]
    return set(hl["api_id"]) == set(frozen_headline) and bool((hl["series"] == "fct").all())  # (5)


# ---- reports ----

def listing_lag(mart: pd.DataFrame, epoch_models: pd.DataFrame, xwalk: pd.DataFrame) -> pd.DataFrame:
    x = xwalk[xwalk["source"] == "epoch"][["source_key", "canonical_model_id"]]
    m = x.merge(epoch_models, left_on="source_key", right_on="model").merge(mart, on="canonical_model_id")
    m = m[m["publication_date"].notna()].copy()
    m["listed_at"] = pd.to_datetime(m["listed_at"], utc=True).dt.date
    m["epoch_publication_date"] = m["publication_date"].map(_d)
    m["lag_days"] = [(a - b).days for a, b in zip(m["listed_at"], m["epoch_publication_date"])]
    return m[["canonical_model_id", "listed_at", "epoch_publication_date", "lag_days"]].reset_index(drop=True)


def level_spot_check(ours: pd.DataFrame, tokencanopy: pd.DataFrame) -> pd.DataFrame:
    """Key-level level check; ours.model_key is the bare key. attrs['n_theirs_zero'] counts dropped rows."""
    tc = tokencanopy
    if "run_date" in tc.columns:
        tc = tc[tc["run_date"] == tc["run_date"].max()]
    m = ours.assign(_c=ours["model_key"].map(canon)).merge(
        tc.assign(_c=tc["model_slug"].map(canon)), on=["_c", "provider"], suffixes=("_o", "_t"))
    parts, n_zero = [], 0
    for metric in ("in_per_mtok", "out_per_mtok"):
        p = pd.DataFrame({"model_key": m["model_key"], "metric": metric, "ours": m[f"{metric}_o"].round(6),
                          "theirs": m[f"{metric}_t"].round(6)}).drop_duplicates()
        n_zero += int((p["theirs"] == 0).sum())
        p = p[p["theirs"] != 0]
        parts.append(p.assign(pct_diff=(p["ours"] - p["theirs"]) / p["theirs"]))
    res = pd.concat(parts, ignore_index=True)[["model_key", "metric", "ours", "theirs", "pct_diff"]]
    res.attrs["n_theirs_zero"] = n_zero
    return res


# ---- run ----

def _clean(v):
    if v is None or v is pd.NA or (isinstance(v, float) and math.isnan(v)):
        return None
    return v.isoformat() if isinstance(v, date) else v


def _records(df: pd.DataFrame) -> list:
    rows = [{k: _clean(v) for k, v in r.items()} for r in df.astype(object).to_dict("records")]
    return [{**r, "lag_days": int(r["lag_days"])} if r.get("lag_days") is not None else r for r in rows]


def main(db: Path = ROOT / "data/warehouse.duckdb", out: Path = ROOT / "exports/epoch_check.json") -> dict:
    con = duckdb.connect(str(db), read_only=True)
    con.execute("SET TimeZone = 'UTC'")

    def q(sql):
        return con.execute(sql).df()

    cands = q("select * from stg_epoch__gpqa_candidates")
    status = q("select * from seed_epoch_candidate_status")
    audit = q("select * from seed_epoch_mismatch_audit")
    pmap = q("select * from seed_provider_map")
    calendar = list(q("select distinct snapshot_date from stg_litellm__snapshots order by 1")["snapshot_date"])
    headline_ids = set(q("select canonical_model_id from mart_launch_price_survival")["canonical_model_id"])
    sbr, conflicts = {}, []
    for s in status[status["scope"] == "in_scope"].to_dict("records"):
        k = (s["model_name"], _d(s["obs_date"]))
        sbr[k] = our_series(con, s["api_id"], s["provider"])
        conflicts += [{"model_name": k[0], "obs_date": str(k[1]), "api_id": s["api_id"], "date": day}
                      for day in sbr[k].attrs["key_conflicts"]]
    rows = price_agreement(cands, status, q("select * from seed_model_crosswalk where source = 'epoch_insight'"),
                           sbr, audit, headline_ids, provider_domains=q("select * from seed_provider_domains"),
                           snapshot_dates=calendar)
    frontier = epoch_frontier(cands, 33.0)

    ours = q("""select distinct d.model_key, p.provider, d.in_per_mtok, d.out_per_mtok, s.litellm_provider
                from dim_model_price d
                join (select distinct model_key, litellm_provider from stg_litellm__snapshots) s using (model_key)
                join seed_provider_map p on p.litellm_provider = s.litellm_provider
                where d.is_current and not d.delisted""")
    ours["model_key"] = [_bare(k, lp) for k, lp in zip(ours["model_key"], ours["litellm_provider"])]
    sc = level_spot_check(ours, q("select * from stg_tokencanopy__prices"))
    lag = listing_lag(q("select canonical_model_id, listed_at from mart_launch_price_survival"),
                      q("select * from stg_epoch__models"), q("select * from seed_model_crosswalk"))
    con.close()
    result = {**EPOCH_PUBLISHED,
              "reproduced_factor": None if frontier is None else annualized_factor(frontier),
              **counts(rows, status), "passed": evaluate(rows, status, pmap, frozen_headline()),
              "rows": _records(rows), "audited": _records(rows[rows["status"].isin(AUDITED)]),
              "late_lags": _records(rows[rows["status"] == "agrees_late"][["model_name", "obs_date", "api_id", "lag_days"]]),
              "key_conflicts": conflicts, "listing_lag": _records(lag),
              "spot_check": {"status": "ok" if len(sc) else "empty", "n_matched": int(sc["model_key"].nunique()),
                             "n_mismatch": int((sc["pct_diff"].abs() > 0).sum()),
                             "n_theirs_zero": sc.attrs["n_theirs_zero"], "rows": _records(sc)}}
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: v for k, v in r.items() if not isinstance(v, (list, dict))}, indent=2))
