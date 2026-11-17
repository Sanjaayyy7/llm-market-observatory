"""LMArena leaderboard: text and text_style_control configs -> one run_date partition."""
import io
from datetime import date
from pathlib import Path

import httpx
import pandas as pd
import pyarrow as pa

from ingest.freshness import FetchResult, finish_fetch, run_cli

URL = "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/resolve/main/{config}/full-00000-of-00001.parquet"
CONFIGS = ("text", "text_style_control")
KEEP = ["model_name", "organization", "license", "rating", "vote_count", "category"]
OUT_COLUMNS = ["config", *KEEP, "publish_date"]
TIMEOUT = httpx.Timeout(600.0, connect=30.0)


def _download(config: str) -> bytes:
    resp = httpx.get(URL.format(config=config), timeout=TIMEOUT, follow_redirects=True)
    resp.raise_for_status()
    return resp.content


def parse_arena(df: pd.DataFrame, config: str) -> pd.DataFrame:
    if config not in CONFIGS:
        raise ValueError(f"unknown arena config: {config}")
    missing = [c for c in [*KEEP, "leaderboard_publish_date"] if c not in df.columns]
    if missing:
        raise ValueError(f"arena input missing columns: {missing}")
    out = df[KEEP].copy()
    out.insert(0, "config", config)
    out["publish_date"] = pd.to_datetime(df["leaderboard_publish_date"], errors="coerce").dt.date
    return out.sort_values(["publish_date", "category", "model_name"]).reset_index(drop=True)[OUT_COLUMNS]


def fetch(raw_dir: Path, run_date: date, probe: bool = False) -> FetchResult:
    df = pd.concat([parse_arena(pd.read_parquet(io.BytesIO(_download(c))), c) for c in CONFIGS], ignore_index=True)
    table = pa.Table.from_pandas(df, preserve_index=False)
    return finish_fetch(raw_dir, "arena", run_date, table, df["publish_date"].min(), df["publish_date"].max(), probe)


if __name__ == "__main__":
    run_cli(fetch)
