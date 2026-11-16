"""Throwaway spike: Arena top-tier population, name matching, and launch-price survival preview.

Usage: python -I analyze_toptier.py <arena_text_full.parquet> <out_dir>   (reads out_dir/models.csv, cuts.csv)
"""
import re
import sys

import pandas as pd

TOP_PCT = 0.25
WINDOW_DAYS = 60
RENAME_DATE = "2026-10-20"  # Arena switched to display names in place (research E21 / 04-verification)
HORIZON = 365
VARIANT = re.compile(r"(-thinking.*|\s*\(.*\)|-(high|low|medium)$)")


def norm(name):
    return VARIANT.sub("", str(name).lower().strip())


def load_arena(path):
    a = pd.read_parquet(path, columns=["model_name", "license", "rating", "category", "leaderboard_publish_date"])
    a = a[a.category == "overall"].copy()
    a["date"] = pd.to_datetime(a.leaderboard_publish_date)
    a["key"] = a.model_name.map(norm)
    a["n"] = a.groupby("date").model_name.transform("size")
    a["rank"] = a.groupby("date").rating.rank(ascending=False, method="min")
    a["pct"] = a["rank"] / a["n"]
    # variants collapse to best variant within a snapshot (design §6)
    a = a.sort_values("pct").drop_duplicates(["date", "key"])
    a["closed"] = a.license.str.lower().str.contains("propriet", na=False)
    return a


def main(arena_path, out):
    a = load_arena(arena_path)
    models = pd.read_csv(f"{out}/models.csv", parse_dates=["listed", "last"])
    cuts = pd.read_csv(f"{out}/cuts.csv", parse_dates=["date"])
    real = cuts[cuts.real].sort_values("date").drop_duplicates(["group", "name"])[["group", "name", "date", "pct"]]

    pre = a[a.date < RENAME_DATE]
    arena_keys = set(pre.key)
    models["matched"] = models.name.isin(arena_keys)

    # PRD §6: first Arena snapshot within 60 days after LiteLLM listing; pct <= 25%
    m = models[models.matched].merge(pre[["key", "date", "pct", "closed"]], left_on="name", right_on="key")
    m = m[(m.date >= m.listed) & (m.date <= m.listed + pd.Timedelta(days=WINDOW_DAYS))]
    first = m.sort_values("date").drop_duplicates(["group", "name"])
    top = first[first.pct <= TOP_PCT].copy()

    print(f"Arena overall: {a.date.nunique()} snapshots {a.date.min().date()}..{a.date.max().date()}, {a.key.nunique()} names")
    print(f"LiteLLM first-party chat models: {len(models)}; exact name match to pre-rename Arena: {models.matched.sum()}"
          f" ({models.matched.mean():.0%}); versioned matched: {(models.matched & models.versioned).sum()}/{models.versioned.sum()}")
    print(f"Ranked within {WINDOW_DAYS}d of listing: {len(first)}; top-tier (pct<={TOP_PCT:.0%}): {len(top)}"
          f" | versioned: {top.versioned.sum()} | closed: {top.closed.sum()}")

    # top-tier by Arena alone (first 60d of Arena life), to see what the exact-match crosswalk misses
    life = pre.assign(first=pre.groupby("key").date.transform("min"))
    life = life[life.date <= life["first"] + pd.Timedelta(days=WINDOW_DAYS)]
    arena_top = life.groupby("key").agg(best=("pct", "min"), closed=("closed", "first"))
    arena_top = arena_top[arena_top.best <= TOP_PCT]
    hit = arena_top.index.isin(set(models.name))
    print(f"Arena-only top-tier names: {len(arena_top)} (closed {arena_top.closed.sum()}); "
          f"exact-matched to LiteLLM first-party: {hit.sum()} ({hit.mean():.0%}); closed matched: "
          f"{(hit & arena_top.closed).sum()}/{arena_top.closed.sum()} ({(hit & arena_top.closed).sum() / max(arena_top.closed.sum(), 1):.0%})")
    print("  unmatched closed sample:", sorted(arena_top[~hit & arena_top.closed].index)[:25])

    last_pre = pre[pre.date == pre.date.max()]
    top10 = last_pre[last_pre.closed].nsmallest(10, "pct")
    print(f"\nTop 10 closed on last pre-rename snapshot ({last_pre.date.max().date()}):")
    for k in top10.key:
        print(f"  {'MATCH ' if k in set(models.name) else 'miss  '} {k}")
    post = a[a.date == a.date.max()]
    print(f"Post-rename latest ({post.date.max().date()}): exact-matched {post.key.isin(set(models.name)).sum()}/{len(post)}; "
          f"sample names: {list(post.nsmallest(5, 'pct').model_name)}")

    # survival preview over versioned top-tier
    vt = top[top.versioned].merge(real, on=["group", "name"], how="left", suffixes=("", "_cut"))
    vt["days_to_cut"] = (vt.date_cut - vt.listed).dt.days
    end = pd.Timestamp(cuts.date.max()) if len(cuts) else models["last"].max()
    vt["follow"] = (vt["last"].clip(upper=end) - vt.listed).dt.days
    cut365 = (vt.days_to_cut <= HORIZON).sum()
    eligible = ((vt.days_to_cut <= HORIZON) | (vt.follow >= HORIZON)).sum()
    print(f"\nVersioned top-tier n={len(vt)}; ever cut: {vt.date_cut.notna().sum()}; cut within {HORIZON}d: {cut365}"
          f" of {eligible} with full follow-up -> Y={cut365 / max(eligible, 1):.0%}")
    print(vt[["group", "name", "listed", "pct", "date_cut", "pct_cut", "follow"]].sort_values("listed").to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
