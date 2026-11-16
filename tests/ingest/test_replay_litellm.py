import json
import subprocess
from datetime import UTC, date, datetime
from unittest.mock import ANY

import pyarrow.parquet as pq
import pytest

from ingest import replay_litellm as rl

NEW = "model_prices_and_context_window.json"
D = {i: date(2024, 1, i) for i in range(1, 7)}


def run(repo, tmp_path, name="a"):
    raw = tmp_path / name
    return raw, tmp_path / f"{name}.json", rl.replay(repo, raw, tmp_path / f"{name}.json")


def part(raw, day):
    return raw / "litellm" / f"snapshot_date={day}" / "part.parquet"


def test_follow_crosses_rename(price_repo):
    assert D[1] in rl.last_per_day(rl.list_commits(price_repo))


def test_last_commit_per_utc_day(price_repo):
    days = rl.last_per_day(rl.list_commits(price_repo))
    assert sorted(days) == [D[i] for i in range(1, 6)]
    assert days[D[3]].commit_ts == datetime(2024, 1, 3, 7, 30, tzinfo=UTC)


def test_invalid_json_logged_and_skipped(price_repo, tmp_path):
    raw, _, res = run(price_repo, tmp_path)
    sha = rl.last_per_day(rl.list_commits(price_repo))[D[4]].sha
    assert res.errors == [(D[4], sha, ANY)]
    assert not part(raw, D[4]).exists()
    err = pq.read_table(raw / "litellm" / "_replay_errors.parquet").to_pylist()
    assert err == [{"snapshot_date": D[4], "commit_sha": sha, "error": ANY}]


def test_sample_spec_dropped(price_repo, tmp_path):
    raw, _, _ = run(price_repo, tmp_path)
    assert "sample_spec" not in pq.read_table(part(raw, D[1]))["model_key"].to_pylist()


def test_partition_carries_commit(price_repo, tmp_path):
    raw, _, _ = run(price_repo, tmp_path)
    t = pq.ParquetFile(part(raw, D[3])).read()
    assert t.schema == rl.SCHEMA
    assert t["commit_sha"].to_pylist() == [rl.last_per_day(rl.list_commits(price_repo))[D[3]].sha]
    assert t["commit_ts"].to_pylist() == [datetime(2024, 1, 3, 7, 30, tzinfo=UTC)]
    assert t["input_cost_per_token"].to_pylist() == [2e-05]


def test_null_provider_inferred(price_repo, tmp_path):
    raw, _, _ = run(price_repo, tmp_path)
    gpt4 = pq.read_table(part(raw, D[1])).to_pylist()[0]
    claude = pq.read_table(part(raw, D[5])).to_pylist()[0]
    assert (gpt4["litellm_provider"], claude["litellm_provider"]) == ("openai", "anthropic")
    assert gpt4["mode"] is None


@pytest.mark.parametrize("key,provider", [("o1-mini", "openai"), ("gemini-pro", "vertex_ai-language-models"),
                                          ("mystery", None)])
def test_provider_table(key, provider):
    assert rl.normalize({key: {}})[0]["litellm_provider"] == provider


def test_normalize_coercion():
    doc = {"sample_spec": {}, "junk": 5, "m": {"litellm_provider": "x", "mode": 3, "input_cost_per_token": "1e-5",
                                              "output_cost_per_token": True}}
    assert rl.normalize(doc) == [{"model_key": "m", "litellm_provider": "x", "mode": None,
                                  "input_cost_per_token": 1e-5, "output_cost_per_token": None}]
    assert rl.normalize({"m": {"input_cost_per_token": "abc", "output_cost_per_token": 2}})[0][
        "output_cost_per_token"] == 2.0
    with pytest.raises(TypeError):
        rl.normalize([])


def test_hash_stable_across_runs(price_repo, tmp_path):
    assert run(price_repo, tmp_path, "a")[2].replay_hash == run(price_repo, tmp_path, "b")[2].replay_hash


def test_incremental_replays_only_new_days(price_repo, add_commit, tmp_path):
    raw, state, first = run(price_repo, tmp_path)
    add_commit(price_repo, "2024-01-06T12:00:00+00:00", {NEW: json.dumps({"gpt-4": {}})})
    second = rl.replay(price_repo, raw, state)
    assert second.days_written == 1
    assert second.replay_hash == run(price_repo, tmp_path, "fresh")[2].replay_hash != first.replay_hash
    assert pq.read_table(raw / "_freshness.parquet").num_rows == 2


def test_same_day_new_commit_rewrites_day(price_repo, add_commit, tmp_path):
    raw, state, _ = run(price_repo, tmp_path)
    add_commit(price_repo, "2024-01-05T13:00:00+00:00", {NEW: json.dumps({"gpt-4": {}})})
    assert rl.replay(price_repo, raw, state).days_written == 1


def test_incremental_errors_deduped(price_repo, tmp_path):
    raw, state, _ = run(price_repo, tmp_path)
    state.write_text(json.dumps({"last_sha": rl.last_per_day(rl.list_commits(price_repo))[D[3]].sha}))
    res = rl.replay(price_repo, raw, state)
    assert len(res.errors) == 1
    assert pq.read_table(raw / "litellm" / "_replay_errors.parquet").num_rows == 1


def test_rewritten_history_full_replay(price_repo, add_commit, tmp_path):
    raw, state, _ = run(price_repo, tmp_path)
    assert part(raw, D[1]).exists()
    # drop d1 (and d2) from history: first commit becomes d3's content
    subprocess.run(["git", "-C", price_repo, "checkout", "-q", "--orphan", "new"], check=True)
    subprocess.run(["git", "-C", price_repo, "branch", "-D", "main"], check=True, capture_output=True)
    subprocess.run(["git", "-C", price_repo, "branch", "-m", "main"], check=True)
    add_commit(price_repo, "2024-01-03T12:00:00+00:00", {NEW: json.dumps({"gpt-4": {}})})
    res = rl.replay(price_repo, raw, state)
    assert not part(raw, D[1]).exists()
    assert res.days_written == 1
    assert res.replay_hash == run(price_repo, tmp_path, "fresh")[2].replay_hash


def test_partial_run_recovers(price_repo, tmp_path, monkeypatch):
    raw, state = tmp_path / "a", tmp_path / "a.json"
    real, calls = rl._write_partition, []

    def boom(*args):
        calls.append(1)
        if len(calls) == 2:
            raise OSError("disk full")
        return real(*args)

    monkeypatch.setattr(rl, "_write_partition", boom)
    with pytest.raises(OSError):
        rl.replay(price_repo, raw, state)
    assert not state.exists()
    monkeypatch.setattr(rl, "_write_partition", real)
    assert rl.replay(price_repo, raw, state).replay_hash == run(price_repo, tmp_path, "fresh")[2].replay_hash


def test_blobless_clone_batched_fetch(price_repo, tmp_path):
    clone = tmp_path / "clone.git"
    subprocess.run(["git", "clone", "-q", "--bare", "--filter=blob:none", f"file://{price_repo}", str(clone)],
                   check=True)
    assert run(clone, tmp_path, "c")[2].replay_hash == run(price_repo, tmp_path, "a")[2].replay_hash


def test_freshness_appended_per_run(price_repo, tmp_path):
    raw = tmp_path / "raw"
    rl.replay(price_repo, raw, tmp_path / "s1.json")
    rl.replay(price_repo, raw, tmp_path / "s2.json")
    rows = pq.read_table(raw / "_freshness.parquet").to_pylist()
    assert len(rows) == 2
    assert {r["source"] for r in rows} == {"litellm"}
    assert all(r["run_ts"].tzinfo is not None and r["run_ts"].utcoffset().total_seconds() == 0 for r in rows)
    assert [r["probe"] for r in rows] == [False, False]


def test_error_day_fixed_same_day_clears_error(price_repo, add_commit, tmp_path):
    raw, state, _ = run(price_repo, tmp_path)
    add_commit(price_repo, "2024-01-06T10:00:00+00:00", {NEW: "{not json"})
    assert len(rl.replay(price_repo, raw, state).errors) == 1
    add_commit(price_repo, "2024-01-06T14:00:00+00:00", {NEW: json.dumps({"gpt-4": {}})})
    rl.replay(price_repo, raw, state)
    errs = pq.read_table(raw / "litellm" / "_replay_errors.parquet").to_pylist()
    assert [e["snapshot_date"] for e in errs] == [D[4]]
    assert part(raw, D[6]).exists()


def test_missing_partitions_forces_full_replay(price_repo, tmp_path):
    raw, state, first = run(price_repo, tmp_path)
    subprocess.run(["rm", "-rf", str(raw / "litellm")], check=True)  # state kept, partitions gone
    res = rl.replay(price_repo, raw, state)
    assert res.days_written == first.days_written
    assert res.replay_hash == first.replay_hash


def test_branch_commit_not_used_merge_dated(price_repo, add_commit, tmp_path):
    from tests.ingest.conftest import _git
    claude = {"claude-2": {"input_cost_per_token": 1e-05}}
    add_commit(price_repo, "2024-01-05T13:00:00+00:00", {NEW: json.dumps(claude, indent=1)})
    _git(price_repo, "checkout", "-q", "-b", "feat")
    feat = {"gpt-4": {"input_cost_per_token": 9e-05}, **claude}
    add_commit(price_repo, "2024-01-06T12:00:00+00:00", {NEW: json.dumps(feat, indent=1)})
    _git(price_repo, "checkout", "-q", "main")
    add_commit(price_repo, "2024-01-07T12:00:00+00:00", {NEW: json.dumps({**claude, "zzz": {}}, indent=1)})
    _git(price_repo, "merge", "--no-ff", "-m", "merge", "feat", when="2024-01-08T12:00:00+00:00")
    days = rl.last_per_day(rl.list_commits(price_repo))
    assert date(2024, 1, 6) not in days
    assert days[date(2024, 1, 8)].sha == _git(price_repo, "rev-parse", "HEAD")
    raw, _, _ = run(price_repo, tmp_path)
    rows = {r["model_key"]: r for r in pq.read_table(part(raw, date(2024, 1, 8))).to_pylist()}
    assert rows["gpt-4"]["input_cost_per_token"] == 9e-05
    assert "zzz" in rows
