"""Drill check: independent SQL re-derivations in docs/drills/sql must equal the warehouse tables.

Spec: docs/05-build-plan/2026-11-15-v1-ship-line.md Task 9 Step 5.
"""
import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
PENDING_LINE = "drill pending: blocks v1.0 tag"
TARGETS = {
    "headline": ("mart_launch_price_survival",
                 "canonical_model_id, listed_at, first_cut_at, days_at_launch_price, censored"),
    "scd2": ("dim_model_price", "model_key, valid_from, valid_to, in_per_mtok, out_per_mtok, delisted"),
}


def _diff_counts(con, sql: str, table: str, cols: str) -> tuple[int, int]:
    # run the file as written (trailing ';' or comments are fine), then compare as a registered relation
    con.register("drill_result", con.sql(sql).df())
    drill, target = "(select * from drill_result)", f"(select {cols} from {table})"
    extra = con.execute(f"select count(*) from ({drill} except all {target})").fetchone()[0]
    missing = con.execute(f"select count(*) from ({target} except all {drill})").fetchone()[0]
    return extra, missing


def main(warehouse: Path = ROOT / "data/warehouse.duckdb", drills: Path = ROOT / "docs/drills",
         strict: bool = False) -> int:
    sql_files = {name: drills / "sql" / f"{name}.sql" for name in TARGETS}
    present = {name: p for name, p in sql_files.items() if p.exists()}
    failed = False
    if present:
        con = duckdb.connect(str(warehouse), read_only=True)
        con.execute("SET TimeZone = 'UTC'")
        for name, path in present.items():
            table, cols = TARGETS[name]
            extra, missing = _diff_counts(con, path.read_text(), table, cols)
            if extra or missing:
                failed = True
                print(f"drill {name}: {extra} rows only in drill SQL, {missing} rows only in {table}")
        con.close()
    if failed:
        return 1
    pending = len(present) < len(TARGETS) or any("_pending_" in p.read_text() for p in drills.glob("*.md"))
    if pending:
        print(PENDING_LINE)
        return 1 if strict else 0
    print("drill ok")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    sys.exit(main(strict=ap.parse_args().strict))
