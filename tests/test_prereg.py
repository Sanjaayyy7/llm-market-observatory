import hashlib
import re
import subprocess
from pathlib import Path

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
