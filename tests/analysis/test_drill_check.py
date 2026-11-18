import sys
from pathlib import Path

import duckdb
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.drill_check import main

PENDING = "drill pending: blocks v1.0 tag"
HEADLINE = "select * from (values ('a', 1), ('b', 2)) t(canonical_model_id, days_at_launch_price)"


@pytest.fixture
def wh(tmp_path):
    path = tmp_path / "w.duckdb"
    con = duckdb.connect(str(path))
    con.execute("create table mart_launch_price_survival(canonical_model_id varchar, listed_at timestamptz,"
                " first_cut_at timestamptz, days_at_launch_price bigint, censored boolean)")
    con.execute("insert into mart_launch_price_survival values"
                " ('a','2024-01-01'::timestamptz,null,1,true), ('b','2024-01-01'::timestamptz,null,2,true)")
    con.execute("create table dim_model_price(model_key varchar, valid_from timestamptz, valid_to timestamptz,"
                " in_per_mtok double, out_per_mtok double, delisted boolean)")
    con.execute("insert into dim_model_price values ('k','2024-01-01'::timestamptz,null,1.0,2.0,false)")
    con.close()
    return path


def drills(tmp_path, headline=None, scd2=None, md="done"):
    d = tmp_path / "drills"
    (d / "sql").mkdir(parents=True)
    (d / "g.md").write_text(md)
    if headline:
        (d / "sql/headline.sql").write_text(headline)
    if scd2:
        (d / "sql/scd2.sql").write_text(scd2)
    return d


FULL_HEADLINE = ("select canonical_model_id, listed_at, first_cut_at, days_at_launch_price, censored "
                 "from mart_launch_price_survival;")
FULL_SCD2 = "select model_key, valid_from, valid_to, in_per_mtok, out_per_mtok, delisted from dim_model_price"


def test_drill_check_lenient_when_pending(wh, tmp_path, capsys):
    d = drills(tmp_path, md="_pending_")
    assert main(wh, d, strict=False) == 0
    assert PENDING in capsys.readouterr().out


def test_drill_check_strict_fails_when_pending(wh, tmp_path):
    assert main(wh, drills(tmp_path, md="_pending_"), strict=True) == 1


def test_drill_check_pending_when_scd2_sql_missing(wh, tmp_path, capsys):
    assert main(wh, drills(tmp_path, headline=FULL_HEADLINE), strict=False) == 0
    assert PENDING in capsys.readouterr().out


def test_drill_check_passes_when_complete_and_equal(wh, tmp_path):
    d = drills(tmp_path, headline=FULL_HEADLINE, scd2=FULL_SCD2)
    assert main(wh, d, strict=True) == 0


@pytest.mark.parametrize("strict", [False, True])
def test_drill_check_detects_row_diff(wh, tmp_path, strict, capsys):
    short = FULL_HEADLINE.rstrip(";") + " where canonical_model_id = 'a'"
    assert main(wh, drills(tmp_path, headline=short), strict=strict) == 1
    assert "headline" in capsys.readouterr().out
