from datetime import date
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq
import pyarrow as pa
import pytest

from ingest.freshness import schema_hash
from ingest import fetch_arena, fetch_clickpy, fetch_epoch, fetch_tokencanopy

SAMPLES = Path(__file__).resolve().parents[1] / "fixtures" / "samples"
RUN = date(2026, 11, 16)


def test_parse_arena_keeps_text_configs():
    raw = pd.read_parquet(SAMPLES / "arena" / "text.parquet")
    out = pd.concat([fetch_arena.parse_arena(raw, c) for c in fetch_arena.CONFIGS])
    assert set(out["config"]) == {"text", "text_style_control"}
    assert list(out.columns) == ["config", "model_name", "organization", "license", "rating",
                                 "vote_count", "category", "publish_date"]
    assert out["publish_date"].iloc[0] == date(2026, 11, 11)
    with pytest.raises(ValueError, match="vote_count"):
        fetch_arena.parse_arena(raw.drop(columns="vote_count"), "text")


def test_parse_arena_schema_hash_stable():
    raw = pd.read_parquet(SAMPLES / "arena" / "text.parquet")
    hashes = {schema_hash(pa.Table.from_pandas(fetch_arena.parse_arena(raw, "text"), preserve_index=False).schema) for _ in range(2)}
    assert len(hashes) == 1


def test_clickpy_query_filters_packages_and_date():
    sql = fetch_clickpy.build_query(["openai", "google-genai"], date(2023, 8, 1))
    assert "pypi.pypi_downloads_per_day" in sql
    assert "'openai'" in sql and "'google-genai'" in sql
    assert "2023-08-01" in sql and sql.rstrip().endswith("FORMAT Parquet")
    with pytest.raises(ValueError):
        fetch_clickpy.build_query(["x'; drop"], date(2023, 8, 1))


def test_parse_epoch_models_dates():
    raw = pd.read_csv(SAMPLES / "epoch" / "all_ai_models.csv")
    raw.loc[0, "Publication date"] = "not a date"
    out = fetch_epoch.parse_epoch_models(raw)
    assert out["publication_date"].iloc[0] is None
    assert out["publication_date"].iloc[1:].notna().all()
    assert all(isinstance(d, date) for d in out["publication_date"].iloc[1:])
    with pytest.raises(ValueError, match="Organization"):
        fetch_epoch.parse_epoch_models(raw.drop(columns="Organization"))


def test_parse_tokencanopy_columns():
    raw = pd.read_csv(SAMPLES / "tokencanopy" / "prices.csv")
    assert len(raw.columns) == 12
    out = fetch_tokencanopy.parse_tokencanopy(raw, RUN)
    assert list(out.columns) == ["run_date", "source", "platform", "model_key", "variant", "metric",
                                 "usd_per_1m", "effective_date"]
    assert (out["run_date"] == RUN).all()
    with pytest.raises(ValueError, match="metric"):
        fetch_tokencanopy.parse_tokencanopy(raw.drop(columns="metric"), RUN)


def test_fetch_idempotent_overwrites_run_partition(tmp_path, monkeypatch):
    csv = (SAMPLES / "tokencanopy" / "prices.csv").read_bytes()
    monkeypatch.setattr(fetch_tokencanopy, "_download", lambda: csv)
    part = tmp_path / "tokencanopy" / "run_date=2026-11-16" / "part.parquet"
    first = fetch_tokencanopy.fetch(tmp_path, RUN)
    again = fetch_tokencanopy.fetch(tmp_path, RUN)
    assert first == again and pq.read_table(part).num_rows == first.rows
    assert len(list(part.parent.iterdir())) == 1  # no stray tmp file
    fresh = pq.read_table(tmp_path / "_freshness.parquet").to_pylist()
    assert [r["probe"] for r in fresh] == [False, False]


def test_fetch_probe_writes_no_partition(tmp_path, monkeypatch):
    csv = (SAMPLES / "tokencanopy" / "prices.csv").read_bytes()
    monkeypatch.setattr(fetch_tokencanopy, "_download", lambda: csv)
    res = fetch_tokencanopy.fetch(tmp_path, RUN, probe=True)
    assert res.rows > 0 and not (tmp_path / "tokencanopy").exists()
    assert [r["probe"] for r in pq.read_table(tmp_path / "_freshness.parquet").to_pylist()] == [True]
