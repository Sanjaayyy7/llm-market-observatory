"""Append-only freshness log: one row per fetch run."""
import argparse
import hashlib
from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path
from typing import NamedTuple

import pyarrow as pa
import pyarrow.parquet as pq

SCHEMA = pa.schema([
    ("source", pa.string()),
    ("run_ts", pa.timestamp("us", tz="UTC")),
    ("rows", pa.int64()),
    ("min_date", pa.date32()),
    ("max_date", pa.date32()),
    ("schema_hash", pa.string()),
    ("probe", pa.bool_()),
])


def append_freshness(raw_dir: Path, source: str, rows: int, min_date: date, max_date: date,
                     schema_hash: str, probe: bool = False) -> None:
    path = raw_dir / "_freshness.parquet"
    new = pa.Table.from_pylist([{
        "source": source, "run_ts": datetime.now(UTC), "rows": rows,
        "min_date": min_date, "max_date": max_date, "schema_hash": schema_hash, "probe": probe,
    }], SCHEMA)
    if path.exists():
        new = pa.concat_tables([pq.read_table(path, schema=SCHEMA), new])
    raw_dir.mkdir(parents=True, exist_ok=True)
    pq.write_table(new, path)


class FetchResult(NamedTuple):
    rows: int
    min_date: date
    max_date: date
    schema_hash: str


def schema_hash(schema: pa.Schema) -> str:
    return hashlib.sha256(schema.to_string(show_schema_metadata=False).encode()).hexdigest()


def finish_fetch(raw_dir: Path, source: str, run_date: date, table: pa.Table, min_date: date,
                 max_date: date, probe: bool) -> FetchResult:
    """Write run_date partition (tmp + rename; skipped for a probe) and log one freshness row."""
    result = FetchResult(table.num_rows, min_date, max_date, schema_hash(table.schema))
    if not probe:
        dest = raw_dir / source / f"run_date={run_date.isoformat()}" / "part.parquet"
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_name("part.parquet.tmp")
        pq.write_table(table, tmp)
        tmp.replace(dest)
    append_freshness(raw_dir, source, *result, probe=probe)
    return result


def run_cli(fetch: Callable[..., FetchResult]) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--probe", action="store_true")
    print(fetch(Path("data/raw"), datetime.now(UTC).date(), probe=parser.parse_args().probe))
