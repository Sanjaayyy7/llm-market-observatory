"""tokencanopy/price current prices (MIT). Every first-party row has an empty effective_date, so run_date is the key."""
import io
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pyarrow as pa

from ingest.freshness import FetchResult, finish_fetch, run_cli

URL = "https://raw.githubusercontent.com/tokencanopy/price/main/data/current/prices.csv"
KEEP = ["source", "platform", "model_key", "variant", "metric", "usd_per_1m", "effective_date"]
TIMEOUT = httpx.Timeout(120.0, connect=30.0)


def _download() -> bytes:
    resp = httpx.get(URL, timeout=TIMEOUT, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def parse_tokencanopy(df: pd.DataFrame, run_date: date) -> pd.DataFrame:
    missing = [c for c in KEEP if c not in df.columns]
    if missing:
        raise ValueError(f"tokencanopy input missing columns: {missing}")
    out = df[KEEP].copy()
    out.insert(0, "run_date", run_date)
    out["usd_per_1m"] = pd.to_numeric(out["usd_per_1m"], errors="coerce")
    dates = pd.to_datetime(out["effective_date"], errors="coerce").dt.date
    out["effective_date"] = dates.astype(object).where(dates.notna(), None)
    return out.sort_values(["source", "platform", "model_key", "variant", "metric"], kind="stable").reset_index(drop=True)


def fetch(raw_dir: Path, run_date: date, probe: bool = False) -> FetchResult:
    df = parse_tokencanopy(pd.read_csv(io.BytesIO(_download())), run_date)
    table = pa.Table.from_pandas(df, preserve_index=False)
    # current-prices snapshot: run_date is the date key (effective_date is often empty)
    return finish_fetch(raw_dir, "tokencanopy", run_date, table, run_date, run_date, probe)


if __name__ == "__main__":
    run_cli(fetch)
