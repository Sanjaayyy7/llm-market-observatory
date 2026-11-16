"""Throwaway spike: replay LiteLLM price file, last commit per UTC day -> one CSV.

Usage: python3 -I replay.py <bare_repo> <log.txt> <out.csv>
"""
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone

PRICE_FILE = "model_prices_and_context_window.json"


def parse_log(log_path):
    """Return {utc_date: (sha, ts, path)} keeping the last commit per day."""
    commits, cur = [], None
    for line in open(log_path, encoding="utf-8"):
        line = line.rstrip("\n")
        if line.startswith("C|"):
            _, sha, ts = line.split("|")
            cur = {"sha": sha, "ts": datetime.fromisoformat(ts).astimezone(timezone.utc)}
            commits.append(cur)
        elif line and cur is not None:
            cur["path"] = line.split("\t")[-1]  # path at this commit (new name on rename)
    by_day = {}
    for c in commits:
        if not c.get("path", "").endswith(PRICE_FILE):
            continue  # pre-history max_tokens.json ancestor: no prices
        day = c["ts"].date().isoformat()
        if day not in by_day or c["ts"] > by_day[day][1]:
            by_day[day] = (c["sha"], c["ts"], c["path"])
    return dict(sorted(by_day.items()))


def git(repo, *args, data=None):
    return subprocess.run(["git", "-C", repo, *args], input=data, capture_output=True, check=True).stdout


def resolve_blobs(repo, days):
    spec = "".join(f"{sha}:{path}\n" for sha, _, path in days.values()).encode()
    out = git(repo, "cat-file", "--batch-check=%(objectname) %(objecttype)", data=spec).decode().splitlines()
    assert len(out) == len(days), "blob resolve count mismatch"
    return [line.split()[0] for line in out]


def read_blob(repo, oid):
    return git(repo, "cat-file", "blob", oid)


def main(repo, log_path, out_csv):
    days = parse_log(log_path)
    blobs = resolve_blobs(repo, days)
    # one batched fetch of every missing blob (server can delta them against each other)
    subprocess.run(
        ["git", "-C", repo, "-c", "fetch.negotiationAlgorithm=noop", "fetch", "origin", "--no-tags",
         "--no-write-fetch-head", "--recurse-submodules=no", "--filter=blob:none", "--stdin"],
        input="\n".join(sorted(set(blobs))).encode(), check=True)
    errors, rows = [], 0
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["snapshot_date", "sha", "model_key", "litellm_provider", "mode", "in_cost", "out_cost"])
        for (day, (sha, _, _)), oid in zip(days.items(), blobs):
            try:
                doc = json.loads(read_blob(repo, oid))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                errors.append((day, sha, str(exc)[:80]))
                continue
            for key, v in doc.items():
                if key == "sample_spec" or not isinstance(v, dict):
                    continue
                w.writerow([day, sha[:7], key, v.get("litellm_provider"), v.get("mode"),
                            v.get("input_cost_per_token"), v.get("output_cost_per_token")])
                rows += 1
    print(f"days={len(days)} first={next(iter(days))} last={next(reversed(days))} rows={rows} errors={len(errors)}")
    for e in errors:
        print("  replay_error", *e)


if __name__ == "__main__":
    main(*sys.argv[1:4])
