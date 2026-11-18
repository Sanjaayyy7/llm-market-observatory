import math
import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.epoch_check import (
    annualized_factor,
    epoch_frontier,
    evaluate,
    frozen_headline,
    level_spot_check,
    listing_lag,
    our_series,
    price_agreement,
)

ROOT = Path(__file__).resolve().parents[2]
D0 = date(2024, 1, 1)
DOMAINS = pd.DataFrame({"provider": ["openai"], "doc_domain": ["openai.com"]})
PMAP = pd.DataFrame({"litellm_provider": ["openai"], "provider": ["openai"], "is_first_party": [True]})


def d(n, base=D0):
    return base + timedelta(days=n)


def _cands(rows):
    return pd.DataFrame(rows, columns=["model_name", "obs_date", "usd_per_mtok", "gpqa_score"])


# ---- frontier ----

def _real_cands():
    parts = [pd.read_csv(ROOT / f"dbt/seeds/seed_epoch_insight_{n}.csv") for n in ("frontier", "other")]
    df = pd.concat(parts)
    df = df[(df["bench"] == "GPQA Diamond") & (df["threshold_model"] == "GPT-4-0314")]
    return pd.DataFrame({"model_name": df["Model Name"], "obs_date": pd.to_datetime(df["Release Date"]).dt.date,
                         "usd_per_mtok": df["USD per 1M Tokens"], "gpqa_score": df["benchmark_score"]})


def test_reproduces_epoch_published_factor():
    cands = _real_cands()
    assert len(cands) == 36
    pts = epoch_frontier(cands, 33.0)
    assert list(pts["model_name"]) == ["GPT-4-0314", "GPT-4 Turbo", "Mistral-Large-2024-02", "Claude-3-Haiku",
                                       "Gemini-1.5-Flash-2024-05", "Phi 4"]
    assert annualized_factor(pts) == pytest.approx(42.02, abs=0.01)


def test_frontier_same_date_keeps_cheaper():
    c = _cands([("a", d(0), 10.0, 50), ("b", d(10), 8.0, 50), ("c", d(10), 5.0, 50),
                ("d", d(20), 4.0, 50), ("e", d(30), 3.0, 50)])
    pts = epoch_frontier(c, 33.0)
    assert list(pts["model_name"]) == ["a", "c", "d", "e"]


def test_frontier_needs_4_points():
    c = _cands([("a", d(0), 10.0, 50), ("b", d(10), 8.0, 50), ("c", d(20), 5.0, 50)])
    assert epoch_frontier(c, 33.0) is None


# ---- equality and status ----

def _series(rows, kind="fct"):
    return pd.DataFrame({"snapshot_date": [r[0] for r in rows], "price": [r[1] for r in rows], "series": kind})


def _run(epoch_price, series_rows, obs=D0, kind="fct", headline=True, audit=None, api="m1", provider="openai",
         calendar=None):
    cands = _cands([("M", obs, epoch_price, 50)])
    status = pd.DataFrame([{"model_name": "M", "obs_date": obs, "provider": provider, "scope": "in_scope",
                            "api_id": api, "evidence_url": "https://openai.com/x", "note": None}])
    xw = pd.DataFrame(columns=["source_key", "canonical_model_id"])
    sbr = {("M", obs): _series(series_rows, kind)}
    a = audit if audit is not None else pd.DataFrame(
        columns=["model_name", "obs_date", "verdict", "source_url", "approved_by"])
    cal = calendar if calendar is not None else sorted({r[0] for r in series_rows})
    return price_agreement(cands, status, xw, sbr, a, {api} if headline else set(), provider_domains=DOMAINS,
                           snapshot_dates=cal)


@pytest.mark.parametrize("ours,epoch,equal", [
    (0.13125, 0.13, True), (4.375, 4.38, True), (0.525, 0.53, True), (0.175, 0.18, True),
    (0.54, 0.5, False), (4.5, 4.38, False)])
def test_equality_tolerance(ours, epoch, equal):
    r = _run(epoch, [(date(2024, 1, 1), ours), (date(2024, 1, 5), ours)]).iloc[0]
    assert (r["status"] == "agrees") is equal
    assert r["status"] in ("agrees", "mismatch")


def test_agrees_late_reports_lag():
    r = _run(5.0, [(d(40), 5.0), (d(50), 5.0)]).iloc[0]
    assert r["status"] == "agrees_late" and r["lag_days"] == 40
    assert r["first_date_ours_equal"] == d(40)


def _changed(audit=None):
    return _run(3.0, [(D0, 15.0), (d(14), 3.0)], audit=audit)


def test_changed_then_agrees_needs_audit():
    r = _changed().iloc[0]
    assert r["status"] == "changed_then_agrees" and r["verdict"] == "panel_error"
    assert not evaluate(_changed(), _status_of(_changed()), PMAP, {"m1"})
    audit = pd.DataFrame([{"model_name": "M", "obs_date": D0, "verdict": "real_change",
                           "source_url": "https://openai.com/pricing", "approved_by": "cofounder"}])
    rows = _changed(audit)
    assert rows.iloc[0]["verdict"] == "real_change"
    assert evaluate(rows, _status_of(rows), PMAP, {"m1"})


def _status_of(rows):
    return pd.DataFrame({"model_name": rows["model_name"], "obs_date": rows["obs_date"], "provider": "openai",
                         "scope": ["out_of_scope" if s == "out_of_scope" else "in_scope" for s in rows["status"]]})


def test_obs_date_between_snapshots():
    r = _run(5.0, [(d(-3), 5.0), (d(5), 9.0)], obs=d(0)).iloc[0]
    assert r["status"] == "agrees" and r["our_price_at_start"] == 5.0


def test_equal_only_before_start_is_mismatch():
    r = _run(5.0, [(date(2023, 9, 1), 5.0), (date(2023, 9, 3), 9.0)], obs=date(2023, 9, 6)).iloc[0]
    assert r["status"] == "mismatch"


def test_delisting_gap_is_no_price():
    cal = [d(i) for i in range(6)]  # D1..D6 global calendar
    series = [(d(0), 10.0), (d(1), 10.0), (d(2), 10.0), (d(5), 5.0)]  # delisted on D4-D5, relisted at 5 on D6
    r = _run(10.0, series, obs=d(4), calendar=cal).iloc[0]
    assert r["our_price_at_start"] is None or pd.isna(r["our_price_at_start"])
    assert r["status"] == "mismatch"


def test_pre_history_uses_first_day():
    r = _run(5.0, [(date(2023, 9, 6), 5.0), (date(2023, 9, 20), 5.0)], obs=date(2023, 3, 14)).iloc[0]
    assert r["status"] == "agrees"


def _many(n_total, n_compared):
    rows, srows = [], []
    for i in range(n_total):
        rows.append((f"M{i}", D0, 5.0, 50))
        srows.append({"model_name": f"M{i}", "obs_date": D0, "provider": "openai", "scope": "in_scope",
                      "api_id": f"m{i}", "evidence_url": "", "note": None})
    sbr = {(f"M{i}", D0): _series([(D0, 5.0)] if i < n_compared else [], "fct") for i in range(n_total)}
    sbr = {k: (v if len(v) else pd.DataFrame(columns=["snapshot_date", "price", "series"])) for k, v in sbr.items()}
    status = pd.DataFrame(srows)
    rows = price_agreement(_cands(rows), status, pd.DataFrame(columns=["source_key", "canonical_model_id"]), sbr,
                           pd.DataFrame(columns=["model_name", "obs_date", "verdict", "source_url", "approved_by"]),
                           set(), provider_domains=DOMAINS, snapshot_dates=[D0])
    return rows, status


def test_coverage_boundary():
    rows, status = _many(30, 23)
    assert not evaluate(rows, status, PMAP, set())
    rows, status = _many(30, 24)
    assert evaluate(rows, status, PMAP, set())


def test_zero_compared_fails():
    rows, status = _many(5, 0)
    assert set(rows["status"]) == {"not_in_panel"}
    assert not evaluate(rows, status, PMAP, set())


def test_unaudited_nonheadline_mismatch_passes():
    rows = _run(9.0, [(D0, 5.0)], headline=False)
    assert rows.iloc[0]["status"] == "mismatch" and rows.iloc[0]["verdict"] == "panel_error"
    assert evaluate(rows, _status_of(rows), PMAP, set())


def test_unaudited_mismatch_fails():
    rows = _run(9.0, [(D0, 5.0)])
    assert not evaluate(rows, _status_of(rows), PMAP, {"m1"})


def test_non_doc_domain_verdict_fails():
    audit = pd.DataFrame([{"model_name": "M", "obs_date": D0, "verdict": "epoch_non_list_price",
                           "source_url": "https://openrouter.ai/x", "approved_by": "cofounder"}])
    rows = _run(9.0, [(D0, 5.0)], audit=audit)
    assert rows.iloc[0]["verdict"] == "panel_error"
    assert not evaluate(rows, _status_of(rows), PMAP, {"m1"})
    good = audit.assign(source_url="https://web.archive.org/web/2024/https://openai.com/pricing")
    rows = _run(9.0, [(D0, 5.0)], audit=good)
    assert rows.iloc[0]["verdict"] == "epoch_non_list_price"
    assert evaluate(rows, _status_of(rows), PMAP, {"m1"})


def test_status_drift_fails():
    rows = _run(5.0, [(D0, 5.0)])
    status = _status_of(rows).assign(provider="vertex")
    assert not evaluate(rows, status, PMAP, {"m1"})


def test_headline_drift_fails():
    rows = _run(5.0, [(D0, 5.0)])
    st = _status_of(rows)
    assert evaluate(rows, st, PMAP, {"m1"})
    assert not evaluate(rows, st, PMAP, {"m1", "other"})  # frozen row missing at run time
    assert not evaluate(rows, st, PMAP, set())  # run-time headline row not in the frozen list
    keyrows = _run(5.0, [(D0, 5.0)], kind="key")
    assert not evaluate(keyrows, _status_of(keyrows), PMAP, {"m1"})


def test_same_name_rows_kept_apart():
    cands = _cands([("Command R+", d(0), 6.0, 50), ("Command R+", d(30), 4.375, 50)])
    status = pd.DataFrame([
        {"model_name": "Command R+", "obs_date": d(0), "provider": "openai", "scope": "in_scope", "api_id": "a1"},
        {"model_name": "Command R+", "obs_date": d(30), "provider": "openai", "scope": "in_scope", "api_id": "a2"}])
    xw = pd.DataFrame({"source_key": [f"Command R+|{d(30)}"], "canonical_model_id": ["a2"]})
    sbr = {("Command R+", d(0)): _series([(d(0), 6.0)]), ("Command R+", d(30)): _series([(d(0), 4.375)])}
    rows = price_agreement(cands, status, xw, sbr,
                           pd.DataFrame(columns=["model_name", "obs_date", "verdict", "source_url", "approved_by"]),
                           set(), provider_domains=DOMAINS, snapshot_dates=[d(0), d(30)])
    assert list(rows["api_id"]) == ["a1", "a2"]
    assert list(rows["canonical_model_id"].fillna("none")) == ["none", "a2"]


# ---- our_series ----

def _con(tz="America/New_York"):
    con = duckdb.connect(":memory:")
    con.execute(f"SET TimeZone = '{tz}'")
    con.execute("create table seed_provider_map(litellm_provider varchar, provider varchar, is_first_party boolean, sdk_group varchar)")
    con.execute("insert into seed_provider_map values ('mistral','mistral',true,'m'),('vertex_ai-language-models','google_vertex',false,'g'),('gemini','google',true,'g')")
    con.execute("create table stg_litellm__snapshots(snapshot_date date, model_key varchar, litellm_provider varchar)")
    con.execute("create table dim_model_price(model_key varchar, valid_from timestamptz, valid_to timestamptz, in_per_mtok double, out_per_mtok double)")
    con.execute("create table fct_model_price_daily(canonical_model_id varchar, date date, blended_per_mtok double)")
    return con


def _snaps(con, days, key, prov):
    for dd in days:
        con.execute("insert into stg_litellm__snapshots values (?,?,?)", [dd, key, prov])


def test_key_series_strips_provider_prefix():
    con = _con()
    days = [date(2024, 5, 12), date(2024, 5, 13)]
    _snaps(con, days, "mistral/mistral-large-2402", "mistral")
    _snaps(con, days, "gemini-1.5-flash-001", "vertex_ai-language-models")
    con.execute("insert into dim_model_price values ('mistral/mistral-large-2402','2024-05-01 00:00:00+00:00',null,4,4),"
                "('gemini-1.5-flash-001','2024-05-01 00:00:00+00:00',null,1,1)")
    s = our_series(con, "mistral-large-2402", "mistral")
    assert list(s["series"].unique()) == ["key"] and list(s["price"]) == [4.0, 4.0]
    assert our_series(con, "gemini-1.5-flash-001", "google").empty


def test_alias_key_is_compared():
    con = _con()
    _snaps(con, [date(2024, 5, 13)], "mistral/open-mistral-nemo", "mistral")
    con.execute("insert into dim_model_price values ('mistral/open-mistral-nemo','2024-05-01 00:00:00+00:00',null,0.2,0.2)")
    s = our_series(con, "open-mistral-nemo", "mistral")
    assert len(s) == 1 and s.iloc[0]["series"] == "key"


def test_fct_series_preferred():
    con = _con()
    con.execute("insert into fct_model_price_daily values ('mistral-large-2402','2024-05-13',6.0)")
    _snaps(con, [date(2024, 5, 12), date(2024, 5, 13)], "mistral/mistral-large-2402", "mistral")
    con.execute("insert into dim_model_price values ('mistral/mistral-large-2402','2024-05-01 00:00:00+00:00',null,4,4)")
    s = our_series(con, "mistral-large-2402", "mistral")
    assert list(s["series"].unique()) == ["fct"] and list(s["price"]) == [6.0]


def test_utc_day_boundary():
    con = _con("America/New_York")
    _snaps(con, [date(2024, 5, 13)], "mistral/mistral-large-2402", "mistral")
    con.execute("insert into dim_model_price values ('mistral/mistral-large-2402','2024-05-13 03:00:00+00:00',null,4,4)")
    s = our_series(con, "mistral-large-2402", "mistral")
    assert [pd.Timestamp(x).date() for x in s["snapshot_date"]] == [date(2024, 5, 13)]


# ---- spot check ----

def _ours(rows):
    return pd.DataFrame(rows, columns=["model_key", "provider", "in_per_mtok", "out_per_mtok"])


def _theirs(rows):
    return pd.DataFrame(rows, columns=["model_slug", "provider", "in_per_mtok", "out_per_mtok"])


def test_spot_check_lists_every_mismatch():
    ours = _ours([("gpt-x", "openai", 2.5, 10.0), ("only-ours", "openai", 1.0, 1.0)])
    theirs = _theirs([("gpt-x", "openai", 3.0, 10.0), ("only-theirs", "openai", 1.0, 1.0)])
    r = level_spot_check(ours, theirs)
    assert set(r["model_key"]) == {"gpt-x"}
    row = r[r["metric"] == "in_per_mtok"].iloc[0]
    assert row["pct_diff"] == pytest.approx(-1 / 6)
    assert r[r["metric"] == "out_per_mtok"].iloc[0]["pct_diff"] == 0


def test_spot_check_drops_zero_theirs():
    r = level_spot_check(_ours([("m", "p", 1.0, 1.0)]), _theirs([("m", "p", 0.0, 2.0)]))
    assert list(r["metric"]) == ["out_per_mtok"] and r.attrs["n_theirs_zero"] == 1


def test_spot_check_empty_status():
    r = level_spot_check(_ours([("a", "p", 1.0, 1.0)]), _theirs([("b", "p", 1.0, 1.0)]))
    assert r.empty and math.isclose(r.attrs["n_theirs_zero"], 0)


def test_frozen_headline_from_prereg():
    assert len(frozen_headline()) == 19


def test_listing_lag_uses_epoch_rows_utc_dates_and_skips_undated():
    # c maps "Model A" from LiteLLM, not Epoch; d has no Epoch date; a lists at 04:30 UTC on Jan 4.
    xwalk = pd.DataFrame({"source": ["epoch", "epoch", "litellm", "epoch"],
                          "source_key": ["Model A", "Model B", "Model A", "Model D"],
                          "canonical_model_id": ["a", "b", "c", "d"]})
    epoch_models = pd.DataFrame({"model": ["Model A", "Model B", "Model D"],
                                 "publication_date": [date(2024, 1, 1), date(2024, 3, 10), None]})
    mart = pd.DataFrame({"canonical_model_id": ["a", "b", "c", "d"],
                         "listed_at": ["2024-01-03T23:30:00-05:00", "2024-03-01T00:00:00+00:00",
                                       "2024-01-02T00:00:00+00:00", "2024-01-02T00:00:00+00:00"]})
    assert listing_lag(mart, epoch_models, xwalk).to_dict("records") == [
        {"canonical_model_id": "a", "listed_at": date(2024, 1, 4),
         "epoch_publication_date": date(2024, 1, 1), "lag_days": 3},
        {"canonical_model_id": "b", "listed_at": date(2024, 3, 1),
         "epoch_publication_date": date(2024, 3, 10), "lag_days": -9},
    ]
