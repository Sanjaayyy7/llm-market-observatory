import json
import sys
from pathlib import Path

import duckdb
import numpy as np
import pytest
from lifelines import KaplanMeierFitter

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.export import ROOT, SOURCES, cut_incidence_365, export_site

EXPORT_FILES = ("headline.json", "epoch_check.json", "event_study.json", "km_curve.parquet", "placebo.parquet")
PASSTHROUGH = (
    "mart_launch_price_survival", "fct_model_price_daily", "fct_price_change", "mart_cut_audit",
    "dim_model", "mart_top_tier_screen", "int_crosswalk_coverage", "mart_event_study_panel",
)


def build_wh(path, *, approved_bad=False, drop_source=None):
    c = duckdb.connect(str(path))
    c.execute("create table seed_model_crosswalk(source varchar, source_key varchar, canonical_model_id varchar,"
              " match_method varchar, approved_by varchar)")
    ok = "'me'" if not approved_bad else "''"
    c.execute(f"insert into seed_model_crosswalk values ('litellm','k-ok','m1','manual','me'),"
              f"('litellm','k-bad','m2','manual',{ok}),('arena','k-exact','m1','exact','')")
    c.execute("create table seed_models(canonical_model_id varchar, approved_by varchar)")
    c.execute(f"insert into seed_models values ('m1','me'),('m-bad',{ok})")
    c.execute("create table seed_model_reroute(canonical_model_id varchar, reroute_date date,"
              " target_model_id varchar, evidence_url varchar)")
    c.execute("insert into seed_model_reroute values ('m1','2024-01-10','m3','https://example.org/u')")
    c.execute("create table stg_litellm__snapshots(snapshot_date date, commit_sha varchar,"
              " commit_ts timestamptz, model_key varchar)")
    c.execute("insert into stg_litellm__snapshots values ('2024-01-01','aaaaaaa111','2024-01-01 00:00:00+00','k-ok'),"
              "('2024-01-20','bbbbbbb222','2024-01-20 00:00:00+00','other'),"
              "('2024-02-01','ccccccc333','2024-02-01 00:00:00+00','other')")
    c.execute("create table source_freshness(source varchar, max_date date)")
    for s in SOURCES:
        if s != drop_source:
            c.execute(f"insert into source_freshness values ('{s}','2024-02-01')")
    c.execute("create table mart_launch_price_survival(canonical_model_id varchar, days_at_launch_price bigint,"
              " censored boolean)")
    c.execute("insert into mart_launch_price_survival values ('m1',100,false),('m2',200,true),('m3',50,true)")
    c.execute("create table int_model_exposure(canonical_model_id varchar, end_ts timestamptz)")
    c.execute("insert into int_model_exposure values ('m1','2024-01-05 00:00:00+00'),"
              "('m2','2024-02-01 00:00:00+00'),('m3','2024-01-05 00:00:00+00')")
    c.execute("create table mart_top_tier_screen(canonical_model_id varchar, is_unranked boolean)")
    c.execute("insert into mart_top_tier_screen values ('m1',true),('m2',false)")
    c.execute("create table seed_crosswalk_uncovered(model_name varchar, reason_code varchar, evidence_url varchar)")
    c.execute("create table int_crosswalk_coverage(model_name varchar, provider varchar, closed boolean,"
              " covered boolean)")
    c.execute("create table seed_epoch_mismatch_audit(model_name varchar, obs_date date, verdict varchar,"
              " source_url varchar)")
    c.execute("create table stg_tokencanopy__prices(platform varchar)")
    c.execute("insert into stg_tokencanopy__prices values ('OpenAI')")
    for t in PASSTHROUGH:
        if t not in ("mart_launch_price_survival", "mart_top_tier_screen", "int_crosswalk_coverage"):
            c.execute(f"create table {t}(x integer)")
    c.close()


def build_exports(d):
    d.mkdir()
    for f in EXPORT_FILES:
        (d / f).write_text("{}")
    (d / "headline.json").write_text(json.dumps({"share_cut_365": 0.1}))
    return d


def build_raw(d):
    (d / "litellm").mkdir(parents=True)
    duckdb.sql(f"copy (select date '2024-01-01' as snapshot_date where false) to '{d}/litellm/_replay_errors.parquet'"
               " (format parquet)")
    tc = d / "tokencanopy/run_date=2024-02-01"
    tc.mkdir(parents=True)
    duckdb.sql(f"copy (select 'OpenAI' as platform, 'openrouter' as source union all select 'Azure', 'azure')"
               f" to '{tc}/part.parquet' (format parquet)")
    return d


def run(tmp_path, **kw):
    tmp_path.mkdir(parents=True, exist_ok=True)
    wh = tmp_path / "wh.duckdb"
    build_wh(wh, **kw)
    out = tmp_path / "out"
    st = export_site(wh, out, exports=build_exports(tmp_path / "ex"), raw=build_raw(tmp_path / "raw"))
    return st, out


def test_export_refuses_unapproved_crosswalk(tmp_path):
    wh = tmp_path / "wh.duckdb"
    build_wh(wh, approved_bad=True)
    out = tmp_path / "out"
    with pytest.raises(ValueError) as e:
        export_site(wh, out, exports=build_exports(tmp_path / "ex"), raw=build_raw(tmp_path / "raw"))
    msg = str(e.value)
    assert "seed_model_crosswalk:litellm:k-bad" in msg
    assert "seed_models:m-bad" in msg
    assert "k-exact" not in msg
    assert not out.exists() or not list(out.iterdir())


def test_stamp_has_all_sources(tmp_path):
    st, out = run(tmp_path)
    j = json.loads((out / "stamp.json").read_text())
    assert set(st.max_dates) == set(SOURCES) == set(j["max_dates"])
    assert st.litellm_sha7 == "ccccccc" == j["litellm_sha7"]
    assert st.run_ts.tzinfo is not None
    assert (out / "methods.json").exists() and (out / "reroute_lag.parquet").exists()
    lag = duckdb.sql(f"select lag_days from '{out}/reroute_lag.parquet'").fetchone()[0]
    assert lag == 10  # last_listed 01-01, next snapshot 01-20, reroute 01-10
    m = json.loads((out / "methods.json").read_text())
    assert m["outcome_counts"] == {"cut": 1, "still_listed": 1, "ended": 1}
    assert m["tokencanopy_sources"] == ["openrouter"]
    assert m["replay_days"] == 3 and m["replay_error_days"] == 0 and m["unranked_count"] == 1
    wh = tmp_path / "wh2.duckdb"
    build_wh(wh, drop_source="pypi")
    with pytest.raises(ValueError, match="pypi"):
        export_site(wh, tmp_path / "out2", exports=tmp_path / "ex", raw=tmp_path / "raw")


def test_no_duckdb_file_in_site_data(tmp_path):
    _, out = run(tmp_path)
    assert not list(out.glob("*.duckdb*"))
    repo = ROOT / "site/src/data"
    if repo.exists():
        assert not list(repo.glob("*.duckdb*"))


def test_cut_incidence_equals_one_minus_km_without_competing_events():
    d = np.array([30, 90, 90, 200, 300, 400, 500, 700, 800])
    c = np.array([1, 1, 0, 1, 0, 1, 0, 1, 0])
    km = KaplanMeierFitter().fit(d, c)
    assert cut_incidence_365(d, c) == pytest.approx(1 - km.survival_function_.loc[:365].iloc[-1, 0], abs=1e-9)


def test_export_bytes_do_not_depend_on_warehouse_row_order(tmp_path):
    # A rebuilt warehouse can return the same rows in another order; the committed Parquet must not churn.
    _, out_a = run(tmp_path / "a")
    wh = tmp_path / "b.duckdb"
    build_wh(wh)
    c = duckdb.connect(str(wh))
    c.execute("create or replace table mart_launch_price_survival as "
              "select * from mart_launch_price_survival order by canonical_model_id desc")
    c.close()
    out_b = tmp_path / "out_b"
    export_site(wh, out_b, exports=build_exports(tmp_path / "ex_b"), raw=build_raw(tmp_path / "raw_b"))
    assert (out_a / "survival.parquet").read_bytes() == (out_b / "survival.parquet").read_bytes()


def test_export_refuses_non_https_url(tmp_path):
    # Seeds feed <a href>; a javascript: or http: URL must never reach the published data.
    wh = tmp_path / "wh.duckdb"
    build_wh(wh)
    c = duckdb.connect(str(wh))
    c.execute("update seed_model_reroute set evidence_url = 'javascript:alert(1)'")
    c.close()
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="reroute_lag.evidence_url"):
        export_site(wh, out, exports=build_exports(tmp_path / "ex"), raw=build_raw(tmp_path / "raw"))
    assert not out.exists() or not list(out.iterdir())
