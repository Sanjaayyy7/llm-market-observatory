import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import duckdb
import pandas as pd
import pytest
from lifelines import KaplanMeierFitter
from statsmodels.duration.survfunc import SurvfuncRight

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.survival import fit_km, main, sensitivity, verified_frame

GOLDEN = Path(__file__).resolve().parents[1] / "fixtures/golden"


def frame(durations, events):
    return pd.DataFrame({"duration": durations, "event": events})


def ts(s):
    return datetime.fromisoformat(s).replace(tzinfo=UTC)


def test_share_365_simple():
    r = fit_km(frame([100] + [400] * 9, [1] + [0] * 9))
    assert r.share_cut_365 == pytest.approx(0.1)
    assert r.median_days is None


def test_median_when_defined():
    r = fit_km(frame(range(10, 101, 10), [1] * 10))
    assert r.median_days == 50
    assert r.method == "km"


def test_few_events_uses_exact_ci():
    r = fit_km(frame([100] + [400] * 9, [1] + [0] * 9))
    assert r.method == "exact"
    assert (r.ci_low, r.ci_high) == pytest.approx((0.0025285, 0.4450161), abs=1e-6)  # Clopper-Pearson 1/10


def test_exact_counts_only_events_within_365():
    r = fit_km(frame([100, 500, 400], [1, 1, 0]))
    assert r.events == 2
    assert r.share_cut_365 == pytest.approx(1 / 3)


def test_censoring_respected():
    cut = fit_km(frame([50, 60, 70, 80], [1, 1, 1, 1]))
    cens = fit_km(frame([50, 60, 70, 80], [1, 1, 1, 0]))
    assert cut.share_cut_365 == 1.0
    assert cens.share_cut_365 < 1.0
    assert cens.events == 3


def test_fit_km_matches_golden():
    r = fit_km(pd.read_csv(GOLDEN / "km_small.csv"))
    exp = json.loads((GOLDEN / "km_small_expected.json").read_text())
    for k in ("share_cut_365", "ci_low", "ci_high"):
        assert getattr(r, k) == pytest.approx(exp[k], abs=1e-6)
    assert r.ci_low <= r.share_cut_365 <= r.ci_high
    assert r.method == "km"


def test_km_matches_statsmodels():
    df = pd.read_csv(GOLDEN / "km_small.csv")
    kmf = KaplanMeierFitter().fit(df["duration"], df["event"])
    sf = SurvfuncRight(df["duration"], df["event"])
    ours = kmf.survival_function_.iloc[:, 0]
    for t, p in zip(sf.surv_times, sf.surv_prob):
        assert ours.loc[t] == pytest.approx(p, abs=1e-9)


# ---- warehouse-shaped fixtures ----

def exposure(rows):
    return pd.DataFrame(rows, columns=["canonical_model_id", "listed_at", "is_top_tier", "end_ts"])


def changes(rows):
    return pd.DataFrame(rows, columns=["canonical_model_id", "change_ts", "pct", "is_correction"])


def cell(df, population, threshold):
    return df[(df["population"] == population) & (df["threshold"] == threshold)].iloc[0]


def sens_exposure():
    return exposure([(f"m{i}", ts("2024-01-01"), True, ts("2025-01-01")) for i in range(4)]
                    + [("x", ts("2024-01-01"), False, ts("2025-01-01"))])


def test_sensitivity_threshold_is_inclusive_and_graded():
    ch = changes([("m0", ts("2024-02-01"), -0.07, False), ("m1", ts("2024-02-01"), -0.10, False),
                  ("m2", ts("2024-02-01"), -0.25, False)])
    s = sensitivity(sens_exposure(), ch)
    assert [cell(s, "top_tier", t)["events"] for t in (0.05, 0.10, 0.20)] == [3, 2, 1]
    assert cell(s, "top_tier", 0.05)["n"] == 4
    assert cell(s, "all", 0.05)["n"] == 5


def test_sensitivity_ignores_corrections_and_changes_at_or_after_end():
    ch = changes([("m0", ts("2024-02-01"), -0.5, True), ("m1", ts("2025-01-01"), -0.5, False),
                  ("m2", ts("2025-03-01"), -0.5, False)])
    s = sensitivity(sens_exposure(), ch)
    assert (s["events"] == 0).all()


def test_sensitivity_uses_earliest_qualifying_change():
    ch = changes([("m0", ts("2024-06-01"), -0.5, False), ("m0", ts("2024-02-01"), -0.5, False)])
    s = sensitivity(sens_exposure(), ch)
    assert cell(s, "top_tier", 0.10)["events"] == 1


def build_db(path, audit_rows, mart_rows=None):
    con = duckdb.connect(str(path))
    con.execute("create table int_model_exposure(canonical_model_id varchar, listed_at timestamptz,"
                " is_top_tier boolean, end_ts timestamptz)")
    ex = [("a", "2024-01-01", True, "2025-01-01"), ("b", "2024-01-01", True, "2025-01-01"),
          ("c", "2024-01-01", True, "2025-01-01"), ("d", "2024-01-01", True, "2025-01-01"),
          ("e", "2024-01-01", False, "2025-01-01")]
    for r in ex:
        con.execute("insert into int_model_exposure values (?, ?::timestamptz, ?, ?::timestamptz)", list(r))
    con.execute("create table mart_launch_price_survival(canonical_model_id varchar, provider varchar,"
                " listed_at timestamptz, first_cut_at timestamptz, days_at_launch_price bigint,"
                " censored boolean, cut_depth_pct double)")
    mart = mart_rows or [("a", "2024-02-01", 31, False), ("b", "2024-03-01", 60, False),
                         ("c", None, 366, True), ("d", None, 366, True)]
    for m, cut, days, cens in mart:
        con.execute("insert into mart_launch_price_survival values (?, 'p', '2024-01-01'::timestamptz,"
                    " ?::timestamptz, ?, ?, -0.2)", [m, cut, days, cens])
    con.execute("create table fct_price_change(canonical_model_id varchar, change_ts timestamptz,"
                " prev_blended double, blended double, pct double, is_cut boolean, is_correction boolean)")
    con.execute("insert into fct_price_change values ('a','2024-02-01'::timestamptz,1,0.8,-0.2,true,false),"
                " ('b','2024-03-01'::timestamptz,1,0.8,-0.2,true,false)")
    con.execute("create table mart_cut_audit(canonical_model_id varchar, lag_days bigint, is_data_fix boolean,"
                " is_scored_event boolean)")
    for r in audit_rows:
        con.execute("insert into mart_cut_audit values (?, ?, ?, ?)", list(r))
    con.close()


def test_verified_data_fix_becomes_censored_at_end_ts(tmp_path):
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True), ("b", None, True, True)])
    con = duckdb.connect(str(tmp_path / "w.duckdb"), read_only=True)
    v = verified_frame(con).set_index("canonical_model_id")
    assert (v.loc["a", "duration"], bool(v.loc["a", "event"])) == (31, True)
    assert (v.loc["b", "duration"], bool(v.loc["b", "event"])) == (366, False)
    assert (v.loc["c", "duration"], bool(v.loc["c", "event"])) == (366, False)


def test_verified_event_without_audit_row_raises(tmp_path):
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True)])
    con = duckdb.connect(str(tmp_path / "w.duckdb"), read_only=True)
    with pytest.raises(ValueError, match="b"):
        verified_frame(con)


def test_main_writes_headline_and_curve(tmp_path):
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True), ("b", None, True, True)])
    out = tmp_path / "exports"
    main(db=tmp_path / "w.duckdb", out=out)
    h = json.loads((out / "headline.json").read_text())
    assert h["scope"] == "dataset_measurement" and h["validation"] == "failed"
    assert (h["n"], h["events"], h["n_audited"], h["n_data_fix"]) == (4, 2, 2, 1)
    assert h["audit_data_fix_rate"] == 0.5
    assert h["commit_lag_median_days"] == 3
    assert h["verified_only"]["events"] == 1
    assert len(h["sensitivity"]) == 6
    curve = pd.read_parquet(out / "km_curve.parquet")
    assert set(curve["series"]) == {"observed", "verified_only"}
    assert list(curve.columns) == ["series", "days", "survival", "ci_lower", "ci_upper"]


def test_main_self_check_fails_when_mart_disagrees(tmp_path):
    # mart says only 'a' is cut, but fct_price_change also cuts 'b' by 20%
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True)],
             mart_rows=[("a", "2024-02-01", 31, False), ("b", None, 366, True),
                        ("c", None, 366, True), ("d", None, 366, True)])
    with pytest.raises(AssertionError):
        main(db=tmp_path / "w.duckdb", out=tmp_path / "exports")


# ---- G6 review round 1 (reviewer WARNs 1, 3, 4, 5) ----

def test_km_reads_last_point_at_or_before_365_not_nearest():
    # timeline points 300 and 370: 370 is nearer to 365, but S must be read at 300
    r = fit_km(frame([100, 200, 300, 370] + [500] * 6, [1, 1, 1, 1] + [0] * 6))
    assert r.method == "km"
    assert r.share_cut_365 == pytest.approx(0.30)


def test_exact_path_boundary_is_three_events():
    assert fit_km(frame([10, 20, 30, 400], [1, 1, 1, 0])).method == "km"
    assert fit_km(frame([10, 20, 400, 400], [1, 1, 0, 0])).method == "exact"


def test_sensitivity_columns_are_r4_only():
    s = sensitivity(sens_exposure(), changes([("m0", ts("2024-02-01"), -0.5, False)]))
    assert list(s.columns) == ["population", "threshold", "n", "events", "share_cut_365", "ci_low", "ci_high",
                               "method"]


def _no_nan(token):
    raise ValueError(f"invalid JSON constant {token}")


def test_headline_json_is_strict_json_when_medians_differ(tmp_path):
    # top-tier cells: no median; 'all' cells: e is cut early -> any per-cell median would mix None and a float
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True), ("b", None, True, True)])
    main(db=tmp_path / "w.duckdb", out=tmp_path / "exports")
    json.loads((tmp_path / "exports/headline.json").read_text(), parse_constant=_no_nan)


def test_non_scored_audit_rows_are_ignored(tmp_path):
    build_db(tmp_path / "w.duckdb", [("a", 3, False, True), ("b", None, True, True), ("z", 9, True, False)])
    h = main(db=tmp_path / "w.duckdb", out=tmp_path / "exports")
    assert (h["n_audited"], h["n_data_fix"], h["audit_data_fix_rate"]) == (2, 1, 0.5)
    assert h["verified_only"]["events"] == 1
