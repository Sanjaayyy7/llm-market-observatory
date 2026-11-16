import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # package=false: make `ingest` importable

OLD = "litellm/model_prices_and_context_window.json"
NEW = "model_prices_and_context_window.json"
GPT4 = {"input_cost_per_token": 3e-05, "output_cost_per_token": 6e-05}


def _git(repo, *args, when=None):
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
           "GIT_COMMITTER_EMAIL": "t@t"}
    if when:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = when
    return subprocess.run(["git", "-c", "commit.gpgsign=false", "-C", str(repo), *args], env=env,
                          check=True, capture_output=True, text=True).stdout.strip()


def commit(repo, when, files, message="c"):
    for rel, text in files.items():
        (repo / rel).parent.mkdir(parents=True, exist_ok=True)
        (repo / rel).write_text(text)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-m", message, when=when)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def add_commit():
    return commit


@pytest.fixture
def price_repo(tmp_path):
    repo = tmp_path / "price_repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "uploadpack.allowFilter", "true")
    _git(repo, "config", "uploadpack.allowAnySHA1InWant", "true")
    doc = {"sample_spec": {"mode": "chat"}, "gpt-4": GPT4}
    commit(repo, "2024-01-01T12:00:00+00:00", {OLD: json.dumps(doc)})
    _git(repo, "mv", OLD, NEW)
    commit(repo, "2024-01-02T10:00:00+00:00", {})
    doc["gpt-4"] = {**GPT4, "input_cost_per_token": 2e-05}
    commit(repo, "2024-01-02T23:30:00-08:00", {NEW: json.dumps(doc)})  # UTC 2024-01-03
    commit(repo, "2024-01-04T12:00:00+00:00", {NEW: "{not json"})
    del doc["gpt-4"]
    doc["claude-2"] = {"input_cost_per_token": 1e-05, "output_cost_per_token": 3e-05}
    commit(repo, "2024-01-05T12:00:00+00:00", {NEW: json.dumps(doc)})
    return repo
