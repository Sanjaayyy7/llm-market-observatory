"""Throwaway spike: re-count top-tier events under a relaxed ID rule + normalized Arena matching.

Rule: keep versioned keys and stable undated keys; drop '-latest' and any undated key with a dated twin
(dedupe to the twin). Usage: python -I analyze_relaxed.py <arena_text_full.parquet> <out_dir>
"""
import re
import sys

import pandas as pd

from analyze_cuts import cluster
from analyze_toptier import TOP_PCT, WINDOW_DAYS, load_arena

SEP = re.compile(r"[ .]")


def canon(s):
    return SEP.sub("-", s)


def main(arena_path, out):
    models = pd.read_csv(f"{out}/models.csv", parse_dates=["listed", "last"])
    cuts = pd.read_csv(f"{out}/cuts.csv", parse_dates=["date"])
    dated = models[models.versioned]
    twin = models.apply(lambda r: (not r.versioned) and dated[(dated.group == r.group)
                        & dated.name.str.startswith(r["name"] + "-")].shape[0] > 0, axis=1)
    keep = models[~models.name.str.contains("latest") & ~twin].copy()
    keep["ck"] = keep.name.map(canon)

    a = load_arena(arena_path)
    a["ck"] = a.key.map(canon)
    m = keep.merge(a[["ck", "date", "pct"]], on="ck")
    m = m[(m.date >= m.listed) & (m.date <= m.listed + pd.Timedelta(days=WINDOW_DAYS))]
    first = m.sort_values("date").drop_duplicates(["group", "name"])
    top = first[first.pct <= TOP_PCT]

    real = cuts[cuts.real].sort_values("date").drop_duplicates(["group", "name"])
    ev = real.merge(top[["group", "name"]], on=["group", "name"])
    n_ev, n_iso = cluster(ev) if len(ev) else (0, 0)
    print(f"relaxed population: {len(keep)} (dropped twins {int(twin.sum())}); top-tier: {len(top)}"
          f" (versioned {int(top.versioned.sum())}, stable-undated {int((~top.versioned).sum())})")
    print(f"top-tier models with a real first cut: {len(ev)} | clustered events: {n_ev} | isolated: {n_iso} (floor 8)")
    print(ev[["date", "group", "name", "prev", "blend", "pct"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
