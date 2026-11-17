"""ClickPy (ClickHouse playground) daily PyPI downloads for the SDK packages in seed_sdk_packages."""
import io
import re
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from ingest.freshness import FetchResult, finish_fetch, run_cli

URL = "https://sql-clickhouse.clickhouse.com/?user=play"
SEED = Path(__file__).resolve().parents[1] / "dbt" / "seeds" / "seed_sdk_packages.csv"
START = date(2023, 8, 1)  # Task 11 needs a -28-day window before the earliest possible cut
TIMEOUT = httpx.Timeout(300.0, connect=30.0)


def build_query(packages: list[str], start: date) -> str:
    if not packages or not all(re.fullmatch(r"[A-Za-z0-9._-]+", p) for p in packages):
        raise ValueError(f"bad package names: {packages}")
    quoted = ", ".join(f"'{p}'" for p in packages)
    return (f"SELECT date, project, count FROM pypi.pypi_downloads_per_day "
            f"WHERE project IN ({quoted}) AND date >= '{start.isoformat()}' "
            f"ORDER BY project, date FORMAT Parquet")


def _download(sql: str) -> bytes:
    resp = httpx.post(URL, content=sql, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.content


def fetch(raw_dir: Path, run_date: date, probe: bool = False) -> FetchResult:
    packages = sorted(pd.read_csv(SEED)["package"])
    table = pq.read_table(io.BytesIO(_download(build_query(packages, START))))
    i = table.schema.get_field_index("date")  # ClickHouse Date arrives as uint16 days
    table = table.set_column(i, "date", table["date"].cast(pa.int32()).cast(pa.date32()))
    dates = table["date"].to_pylist()
    return finish_fetch(raw_dir, "pypi", run_date, table, min(dates), max(dates), probe)


if __name__ == "__main__":
    run_cli(fetch)
