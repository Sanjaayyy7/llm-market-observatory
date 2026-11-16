"""Deterministic replay of the LiteLLM price file: last commit per UTC day -> one Parquet partition."""
import hashlib
import json
import shutil
import subprocess
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import NamedTuple

import pyarrow as pa
import pyarrow.parquet as pq

from ingest.freshness import append_freshness

REPO_URL = "https://github.com/BerriAI/litellm.git"
PRICE_FILE = "model_prices_and_context_window.json"
SCHEMA = pa.schema([
    ("model_key", pa.string()),
    ("litellm_provider", pa.string()),
    ("mode", pa.string()),
    ("input_cost_per_token", pa.float64()),
    ("output_cost_per_token", pa.float64()),
    ("commit_sha", pa.string()),
    ("commit_ts", pa.timestamp("us", tz="UTC")),
])
ERRORS_SCHEMA = pa.schema([("snapshot_date", pa.date32()), ("commit_sha", pa.string()), ("error", pa.string())])
SCHEMA_HASH = hashlib.sha256(SCHEMA.to_string(show_schema_metadata=False).encode()).hexdigest()
PROVIDER_BY_PREFIX = {
    "gpt": "openai", "o1": "openai", "o3": "openai", "o4": "openai", "text-davinci": "openai",
    "claude": "anthropic",
    "gemini": "vertex_ai-language-models", "chat-bison": "vertex_ai-language-models",
    "text-bison": "vertex_ai-language-models",
}


class Commit(NamedTuple):
    sha: str
    commit_ts: datetime
    path: str


class ReplayResult(NamedTuple):
    days_written: int
    errors: list[tuple[date, str, str]]
    replay_hash: str


def _git(repo, *args, data=None):
    return subprocess.run(["git", "-C", str(repo), *args], input=data, capture_output=True, check=True).stdout


def list_commits(repo: Path) -> list[Commit]:
    log = _git(repo, "log", "HEAD", "--follow", "--format=C|%H|%cI", "--name-status", "--", PRICE_FILE).decode()
    commits, cur = [], None
    for line in log.splitlines():
        if line.startswith("C|"):
            _, sha, ts = line.split("|")
            cur = [sha, datetime.fromisoformat(ts).astimezone(UTC), None]
            commits.append(cur)
        elif line and cur is not None:
            cur[2] = line.split("\t")[-1]  # path at this commit (new name on rename)
    # --follow also reaches a max_tokens.json ancestor with no prices
    return [Commit(*c) for c in commits if c[2] and c[2].endswith(PRICE_FILE)]


def last_per_day(commits: list[Commit]) -> dict[date, Commit]:
    by_day: dict[date, Commit] = {}
    for c in commits:
        day = c.commit_ts.date()
        if day not in by_day or c.commit_ts > by_day[day].commit_ts:
            by_day[day] = c
    return dict(sorted(by_day.items()))


def _cost(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def _str(value):
    return value if isinstance(value, str) else None


def _infer_provider(key):
    return next((p for prefix, p in PROVIDER_BY_PREFIX.items() if key.startswith(prefix)), None)


def normalize(doc: dict) -> list[dict]:
    if not isinstance(doc, dict):
        raise TypeError("price file is not a JSON object")
    return [{
        "model_key": key,
        "litellm_provider": _str(v.get("litellm_provider")) or _infer_provider(key),
        "mode": _str(v.get("mode")),
        "input_cost_per_token": _cost(v.get("input_cost_per_token")),
        "output_cost_per_token": _cost(v.get("output_cost_per_token")),
    } for key, v in doc.items() if key != "sample_spec" and isinstance(v, dict)]


def _write_partition(out: Path, day: date, commit: Commit, rows: list[dict]) -> None:
    rows = sorted(rows, key=lambda r: r["model_key"])
    table = pa.Table.from_pylist([{**r, "commit_sha": commit.sha, "commit_ts": commit.commit_ts} for r in rows], SCHEMA)
    dest = out / f"snapshot_date={day.isoformat()}" / "part.parquet"
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_name("part.parquet.tmp")
    pq.write_table(table, tmp)
    tmp.replace(dest)


def _resolve_blobs(repo, days):
    spec = "".join(f"{c.sha}:{c.path}\n" for c in days.values()).encode()
    lines = _git(repo, "cat-file", "--batch-check=%(objectname)", data=spec).decode().splitlines()
    if len(lines) != len(days) or any(" " in line for line in lines):
        raise RuntimeError("blob resolve failed")
    if subprocess.run(["git", "-C", str(repo), "config", "--get", "remote.origin.promisor"],
                      check=False, capture_output=True, text=True).stdout.strip() == "true":
        # one batched fetch; per-blob lazy fetch is far slower
        _git(repo, "-c", "fetch.negotiationAlgorithm=noop", "fetch", "origin", "--no-tags", "--no-write-fetch-head",
             "--filter=blob:none", "--stdin", data="\n".join(sorted(set(lines))).encode())
    return lines


def _write_errors(out: Path, errors, full: bool) -> None:
    path = out / "_replay_errors.parquet"
    old = pq.read_table(path).to_pylist() if path.exists() and not full else []
    new = [{"snapshot_date": d, "commit_sha": s, "error": e} for d, s, e in errors]
    merged = list({(r["snapshot_date"], r["commit_sha"]): r for r in reversed(old + new)}.values())[::-1]
    if full or new:
        out.mkdir(parents=True, exist_ok=True)
        pq.write_table(pa.Table.from_pylist(merged, ERRORS_SCHEMA), path)


def _replay_hash(out: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(out.glob("snapshot_date=*/part.parquet")):
        h.update(f.read_bytes())
    return h.hexdigest()


def replay(repo: Path, raw_dir: Path, state_path: Path) -> ReplayResult:
    out = raw_dir / "litellm"
    commits = list_commits(repo)
    days = last_per_day(commits)
    by_sha = {c.sha: c for c in commits}
    state_sha = json.loads(state_path.read_text())["last_sha"] if state_path.exists() else None
    start = None  # None = full replay
    if state_sha in by_sha:
        last = by_sha[state_sha].commit_ts.date()
        start = last if days[last].sha != state_sha else last + timedelta(days=1)
    todo = {d: c for d, c in days.items() if start is None or d >= start}
    blobs = _resolve_blobs(repo, todo)
    errors, written = [], []
    for (day, commit), oid in zip(todo.items(), blobs):
        try:
            rows = normalize(json.loads(_git(repo, "cat-file", "blob", oid)))
        except (ValueError, TypeError) as exc:  # JSON/Unicode decode errors are ValueErrors
            errors.append((day, commit.sha, str(exc)[:200]))
            continue
        _write_partition(out, day, commit, rows)
        written.append(day)
    if start is None:
        keep = {f"snapshot_date={d.isoformat()}" for d in written}
        for stale in out.glob("snapshot_date=*"):
            if stale.name not in keep:
                shutil.rmtree(stale)
    _write_errors(out, errors, full=start is None)
    parts = sorted(out.glob("snapshot_date=*/part.parquet"))
    if parts:
        dates = [date.fromisoformat(p.parent.name.split("=")[1]) for p in parts]
        append_freshness(raw_dir, "litellm", sum(pq.ParquetFile(p).metadata.num_rows for p in parts),
                         dates[0], dates[-1], SCHEMA_HASH)
    if days:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        state_path.write_text(json.dumps({"last_sha": list(days.values())[-1].sha}))
    return ReplayResult(len(written), errors, _replay_hash(out))


def main() -> None:
    repo, raw_dir, state = Path("data/cache/litellm.git"), Path("data/raw"), Path("data/cache/replay_state.json")
    if repo.exists():
        _git(repo, "fetch", "--filter=blob:none", "origin", "+main:main")
    else:
        repo.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "--bare", "--filter=blob:none", REPO_URL, str(repo)], check=True)
    res = replay(repo, raw_dir, state)
    parts = sorted((raw_dir / "litellm").glob("snapshot_date=*"))
    errors = pq.read_table(raw_dir / "litellm" / "_replay_errors.parquet").to_pylist()
    days = len(parts) + len(errors)
    print(f"days_written={res.days_written}")
    print(f"first_snapshot_date={parts[0].name.split('=')[1]} last_snapshot_date={parts[-1].name.split('=')[1]}")
    print(f"replay_hash={res.replay_hash}")
    print(f"errors={len(errors)} days={days} errors/days={len(errors) / days:.4f}")
    for e in errors:
        print(f"  replay_error {e['snapshot_date']} {e['commit_sha'][:7]}")


if __name__ == "__main__":
    main()
