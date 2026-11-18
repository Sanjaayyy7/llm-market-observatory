import hashlib
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PREREG = ROOT / "docs/prereg"


def test_prereg_never_modified():
    files = sorted(PREREG.glob("*.md"))
    assert files
    for f in files:
        log = subprocess.run(["git", "log", "--follow", "--format=%H", "--", str(f)],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        assert len(log) == 1, f"{f.name} touched by {len(log)} commits"


def test_seed_sha256_matches_prereg():
    text = (PREREG / "epoch-check.md").read_text()
    pairs = re.findall(r"`(dbt/seeds/[\w.]+\.csv)`.*?`([0-9a-f]{64})`", text)
    assert len(pairs) == 3
    for path, sha in pairs:
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == sha, path


def _git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=check)


def test_prereg_precedes_event_code():
    code = "analysis/event_study.py"
    prereg = "docs/prereg/event-study.md"
    prereg_commits = _git("log", "--diff-filter=A", "--format=%H", "--", prereg).stdout.split()
    if not prereg_commits:
        pytest.skip("event-study prereg not committed yet")
    code_commits = _git("log", "--format=%H", "--", code).stdout.split()
    if not code_commits:
        pytest.skip("event-study code not committed yet")
    first_code = code_commits[-1]
    assert first_code != prereg_commits[-1]
    assert _git("merge-base", "--is-ancestor", prereg_commits[-1], first_code, check=False).returncode == 0
