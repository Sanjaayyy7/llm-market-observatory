"""Throwaway spike: same-key price cuts on first-party LiteLLM keys.

Usage: python3 -I analyze_cuts.py <snapshots.csv> <out_dir>
Writes cuts.csv, models.csv; prints summary.
"""
import re
import sys

import pandas as pd

SDK_GROUP = {  # litellm_provider -> provider SDK group (first-party only)
    "openai": "openai", "text-completion-openai": "openai", "anthropic": "anthropic",
    "gemini": "google", "vertex_ai-language-models": "google", "xai": "xai",
    "mistral": "mistral", "deepseek": "deepseek", "cohere_chat": "cohere", "cohere": "cohere",
    "moonshot": "moonshot", "dashscope": "qwen",
}
GOOGLE_PREF = {"gemini": 0, "vertex_ai-language-models": 1}  # AI Studio key wins for Google
MODES = {"chat", "completion", "responses"}
CUT = 0.10
CLUSTER_DAYS = 28
CORRECTION_DAYS = 30  # cut undone within this window = data fix, not a real cut
LAUNCH_FIX_DAYS = 7   # cut this soon after listing = launch typo fix
VERSIONED = re.compile(r"(\d{4}-\d{2}-\d{2}|\d{8}|-\d{4}$|-\d{3}$|-\d{2}-\d{2}$)")
TEST = [("gpt-4o-2024-08-06", 1), ("claude-3-5-sonnet-20241022", 1), ("gpt-4-0613", 1),
        ("gemini-1.5-pro-002", 1), ("gemini-2.5-pro-preview-05-06", 1), ("gpt-4o", 0),
        ("o3", 0), ("claude-3-5-sonnet-latest", 0), ("gemini-2.5-pro", 0), ("deepseek-chat", 0)]
assert all(bool(VERSIONED.search(k)) == bool(want) for k, want in TEST), "versioned regex self-check"


def infer_provider(key):
    k = key.lower()
    if k.startswith(("gpt", "text-davinci", "davinci", "babbage", "o1", "o3", "o4")):
        return "openai"
    if k.startswith("claude"):
        return "anthropic"
    if k.startswith(("gemini", "chat-bison", "text-bison")):
        return "vertex_ai-language-models"
    return None


def load(path):
    d = pd.read_csv(path, usecols=["snapshot_date", "model_key", "litellm_provider", "mode", "in_cost", "out_cost"])
    d["litellm_provider"] = d.litellm_provider.fillna(d.model_key.map(infer_provider))
    d = d[d.litellm_provider.isin(SDK_GROUP) & (d["mode"].isin(MODES) | d["mode"].isna())].copy()
    d["name"] = d.model_key.str.split("/").str[-1].str.lower()
    d["group"] = d.litellm_provider.map(SDK_GROUP)
    d["pref"] = d.litellm_provider.map(GOOGLE_PREF).fillna(0)
    # one first-party key per (day, group, name): prefer AI Studio for Google, then shortest key
    d = d.assign(klen=d.model_key.str.len()).sort_values(["snapshot_date", "group", "name", "pref", "klen"])
    d = d.drop_duplicates(["snapshot_date", "group", "name"])
    d["blend"] = (3 * pd.to_numeric(d.in_cost, errors="coerce") + pd.to_numeric(d.out_cost, errors="coerce")) / 4 * 1e6
    d = d[d.blend > 0]
    d["date"] = pd.to_datetime(d.snapshot_date)
    d["versioned"] = d.name.str.contains(VERSIONED) & ~d.name.str.contains("latest")
    return d[["date", "group", "name", "versioned", "blend"]]


def find_cuts(d):
    d = d.sort_values(["group", "name", "date"])
    g = d.groupby(["group", "name"])
    d = d.assign(prev=g.blend.shift(), listed=g.date.transform("min"))
    ch = d[d.prev.notna() & (d.blend != d.prev)].copy()
    ch["pct"] = ch.blend / ch.prev - 1
    cuts = ch[ch.pct <= -CUT].copy()

    def reverted(r):
        later = d[(d.group == r.group) & (d.name == r["name"]) & (d.date > r.date)
                  & (d.date <= r.date + pd.Timedelta(days=CORRECTION_DAYS))]
        return bool((later.blend >= r.prev * 0.999).any())

    cuts["reverted"] = cuts.apply(reverted, axis=1)
    cuts["launch_fix"] = (cuts.date - cuts.listed).dt.days <= LAUNCH_FIX_DAYS
    cuts["real"] = ~cuts.reverted & ~cuts.launch_fix
    return cuts


def cluster(first_cuts):
    """Merge first cuts within ±CLUSTER_DAYS per group; count clustered and isolated events."""
    events, isolated = 0, 0
    for _, grp in first_cuts.sort_values("date").groupby("group"):
        dates = list(grp.date)
        runs, run = [], [dates[0]]
        for x in dates[1:]:
            if (x - run[-1]).days <= CLUSTER_DAYS:
                run.append(x)
            else:
                runs.append(run)
                run = [x]
        runs.append(run)
        events += len(runs)
        isolated += sum(len(r) == 1 for r in runs)
    return events, isolated


def main(path, out):
    d = load(path)
    models = d.groupby(["group", "name"]).agg(versioned=("versioned", "first"), listed=("date", "min"),
                                              last=("date", "max"), launch=("blend", "first")).reset_index()
    cuts = find_cuts(d)
    cuts.to_csv(f"{out}/cuts.csv", index=False)
    models.to_csv(f"{out}/models.csv", index=False)
    print("first-party chat models by group (versioned / all):")
    print(models.groupby("group").versioned.agg(["sum", "count"]).sort_values("count", ascending=False).to_string())
    print(f"\ncuts >= {CUT:.0%}: raw={len(cuts)} reverted={cuts.reverted.sum()} launch_fix={cuts.launch_fix.sum()} real={cuts.real.sum()}")
    for label, sub in [("versioned", cuts[cuts.real & cuts.versioned]), ("unversioned", cuts[cuts.real & ~cuts.versioned])]:
        first = sub.sort_values("date").drop_duplicates(["group", "name"])
        ev, iso = cluster(first) if len(first) else (0, 0)
        print(f"\n[{label}] models with >=1 real cut: {len(first)} | clustered events: {ev} | isolated: {iso}")
        print(first[["date", "group", "name", "prev", "blend", "pct"]].round(4).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:3])
