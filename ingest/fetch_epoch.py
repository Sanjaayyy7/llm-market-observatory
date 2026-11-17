"""Epoch AI model catalogue (all_ai_models.csv). The CSV has no API/model-id column."""
import io
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pyarrow as pa

from ingest.freshness import FetchResult, finish_fetch, run_cli

URL = "https://epoch.ai/data/all_ai_models.csv"
RENAME = {"Model": "model", "Organization": "organization", "Publication date": "publication_date",
          "Model accessibility": "model_accessibility", "Open model weights?": "open_model_weights"}
TIMEOUT = httpx.Timeout(120.0, connect=30.0)


def _download() -> bytes:
    resp = httpx.get(URL, timeout=TIMEOUT, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def parse_epoch_models(df: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in RENAME if c not in df.columns]
    if missing:
        raise ValueError(f"epoch input missing columns: {missing}")
    out = df[list(RENAME)].rename(columns=RENAME)
    dates = pd.to_datetime(out["publication_date"], errors="coerce").dt.date
    out["publication_date"] = dates.astype(object).where(dates.notna(), None)
    return out.sort_values(["publication_date", "model"], na_position="first").reset_index(drop=True)


def fetch(raw_dir: Path, run_date: date, probe: bool = False) -> FetchResult:
    df = parse_epoch_models(pd.read_csv(io.BytesIO(_download())))
    table = pa.Table.from_pandas(df, preserve_index=False)
    return finish_fetch(raw_dir, "epoch", run_date, table, df["publication_date"].min(), df["publication_date"].max(), probe)


if __name__ == "__main__":
    run_cli(fetch)
