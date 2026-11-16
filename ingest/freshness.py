"""Append-only freshness log: one row per fetch run."""
from datetime import UTC, date, datetime
from pathlib import Path

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
