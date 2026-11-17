"""Draft the model crosswalk (G2): LiteLLM keys, Arena names and Epoch names -> canonical model ids.

Writes dbt/seeds/seed_models.csv and seed_model_crosswalk.csv. Never overwrites a seed a human has
approved (any evidence_url / approved_by filled)."""
import difflib
import re
from datetime import timedelta
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "warehouse.duckdb"
SEEDS = ROOT / "dbt" / "seeds"
RAW_ARENA = ROOT / "data" / "raw" / "arena" / "*" / "part.parquet"

MANUAL_ALIASES = {"deepseek-chat", "deepseek-reasoner"}
ORG_TO_PROVIDER = {"alibaba": "qwen"}  # Arena organization -> seed_provider_map provider
TOP_PERCENTILE = 0.25
LAUNCH_WINDOW = timedelta(days=60)
DATED_TWIN_REST = re.compile(r"\d{4}-\d{2}-\d{2}|\d{8}|\d{4}|\d{2}-\d{2}|\d{3}")
XWALK_COLS = ["source", "source_key", "canonical_model_id", "match_method", "is_moving_alias",
              "match_score", "evidence_url", "approved_by"]
MODEL_COLS = ["canonical_model_id", "provider", "family", "display_name", "open_weights",
              "announce_date", "announce_url", "approved_by"]


def canon(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"\s*\((\d{2}-\d{2}|\d{4}-\d{2}-\d{2})\)", r"-\1", s)
    s = re.sub(r"\s*\([^)]*\)", "", s)
    s = re.sub(r"[ .]", "-", s)
    s = re.sub(r"(-no)?-thinking.*", "", s)
    s = re.sub(r"-(minimal|low|medium|high|xhigh)(-\d+k)?$", "", s)
    return s.strip("-")


def norm(bare: str) -> str:
    return re.sub(r"[ .]", "-", bare.lower())


def match_score(source_key: str, canonical_model_id: str) -> float:
    return round(difflib.SequenceMatcher(None, source_key.lower(), canonical_model_id).ratio(), 3)


def dated_twins(name: str, group_keys: set[str]) -> list[str]:
    return sorted(k for k in group_keys
                  if k.startswith(name + "-") and DATED_TWIN_REST.fullmatch(k[len(name) + 1:]))


def is_moving_alias(name: str, group_keys: set[str]) -> bool:
    return name in MANUAL_ALIASES or name.endswith("-latest") or bool(dated_twins(name, group_keys))


def _name_facts(arena: pd.DataFrame) -> pd.DataFrame:
    def closed_any(s):
        s = s.dropna()
        return bool(s.any()) if len(s) else None

    g = arena.groupby("model_name")
    facts = pd.DataFrame({
        "org": g["organization"].agg(lambda s: next((x for x in s if isinstance(x, str) and x), None)),
        "min_pct": g["rank_percentile"].min(),
        "closed": g["closed"].agg(closed_any),
    })
    facts["provider"] = facts["org"].map(lambda o: ORG_TO_PROVIDER.get(o, o))
    return facts


def build(arena, litellm, epoch, provider_map) -> dict:
    """Pure core. Returns models, crosswalk, notes (UNMATCHED/COLLISION lines) and stats."""
    notes = []
    arena = arena.assign(publish_date=pd.to_datetime(arena["publish_date"]))
    first_party = provider_map[provider_map["is_first_party"].astype(bool)]
    prov_of = dict(zip(first_party["litellm_provider"], first_party["provider"]))
    keys = litellm[litellm["litellm_provider"].isin(prov_of)].copy()
    keys["provider"] = keys["litellm_provider"].map(prov_of)
    keys["bare"] = [k.lower().removeprefix(lp.lower() + "/")
                    for k, lp in zip(keys["model_key"], keys["litellm_provider"])]
    keys["norm"] = keys["bare"].map(norm)

    canon_of, bare_to_canon, group_keys = {}, {}, {}
    for (prov, n), grp in keys.groupby(["provider", "norm"]):
        bares = sorted(set(grp["bare"]))
        canon_of[(prov, n)] = bares[0]
        for b in bares:
            bare_to_canon[(prov, b)] = bares[0]
        if len(bares) > 1:
            notes.append(f"COLLISION {prov}: {bares} -> {bares[0]}")
    for prov, grp in keys.groupby("provider"):
        group_keys[prov] = set(grp["bare"])

    def match(name, prov):
        low = name.lower()
        if (prov, low) in bare_to_canon:
            c = bare_to_canon[(prov, low)]
            return c, "exact" if c == low else "manual"
        c = canon_of.get((prov, canon(name)))
        return (c, "manual") if c else (None, None)

    facts = _name_facts(arena)
    facts = facts[facts["provider"].isin(set(first_party["provider"]))].copy()
    facts["in_scope"] = facts["min_pct"] <= TOP_PERCENTILE
    matches = {n: (r["provider"], *match(n, r["provider"])) for n, r in facts.iterrows()}
    in_scope = {(matches[n][0], matches[n][1]) for n in facts.index[facts["in_scope"]] if matches[n][1]}
    for n in sorted(facts.index[facts["in_scope"]]):
        if not matches[n][1]:
            notes.append(f"UNMATCHED {matches[n][0]}: {n}")
    # AMBIGUOUS cannot occur: same-norm keys are collapsed to one canonical above.

    # R7b: an alias-by-date canonical with exactly one dated twin re-points arena/epoch rows to it.
    multi = []

    def repoint(name, prov, c, how):
        if c in MANUAL_ALIASES or c.endswith("-latest"):
            return c, how
        twins = dated_twins(c, group_keys[prov])
        if len(twins) == 1:
            return twins[0], "manual"
        if twins:
            multi.append(f"MULTI_TWIN {prov}: {name} -> {c} twins={twins}")
        return c, how

    twin_of = {(p, c): dated_twins(c, group_keys[p]) for p, c in in_scope}
    in_scope = in_scope | {(p, t[0]) for (p, c), t in twin_of.items()
                           if len(t) == 1 and c not in MANUAL_ALIASES and not c.endswith("-latest")}
    prov_by_canon = {c: p for p, c in in_scope}

    rows = []
    for n, (prov, c, how) in matches.items():
        if c and (prov, c) in in_scope:
            rows.append(("arena", n, *repoint(n, prov, c, how)))
    for r in keys.itertuples():
        c = canon_of[(r.provider, r.norm)]
        if (r.provider, c) in in_scope:
            rows.append(("litellm", r.model_key, c, "exact" if r.bare == c else "manual"))
    by_norm = {norm(c): c for _, c in in_scope}
    for m in sorted(set(epoch["model"].dropna())):
        c = by_norm.get(canon(m))
        if c:
            rows.append(("epoch", m, *repoint(m, prov_by_canon[c], c, "exact" if m.lower() == c else "manual")))
    notes = [n for pre in ("COLLISION", "MULTI_TWIN", "UNMATCHED") for n in notes + multi if n.startswith(pre)]

    xwalk = pd.DataFrame(rows, columns=["source", "source_key", "canonical_model_id", "match_method"])
    xwalk["is_moving_alias"] = [is_moving_alias(c, group_keys[prov_by_canon[c]])
                                for c in xwalk["canonical_model_id"]]
    xwalk["match_score"] = [match_score(k, c) for k, c in zip(xwalk["source_key"], xwalk["canonical_model_id"])]
    xwalk["evidence_url"] = None
    xwalk["approved_by"] = None
    xwalk = xwalk.sort_values(["source", "source_key"]).reset_index(drop=True)[XWALK_COLS]

    models = _models(arena, facts, xwalk, prov_by_canon)
    return {"models": models, "xwalk": xwalk, "notes": notes,
            "stats": _stats(arena, facts, xwalk, keys, canon_of, group_keys, prov_by_canon, matches)}


def _models(arena, facts, xwalk, prov_by_canon):
    arena_x = xwalk[xwalk["source"] == "arena"]
    last_date = arena.groupby("model_name")["publish_date"].max()
    out = []
    for c in sorted(prov_by_canon):
        names = list(arena_x.loc[arena_x["canonical_model_id"] == c, "source_key"])
        best = min(names, key=lambda n: (-last_date[n].toordinal(), n)) if names else c  # latest, then name order
        closed = [facts.at[n, "closed"] for n in names if facts.at[n, "closed"] is not None]
        out.append((c, prov_by_canon[c], None, best, (not any(closed)) if closed else None, None, None, None))
    return pd.DataFrame(out, columns=MODEL_COLS).sort_values("canonical_model_id").reset_index(drop=True)


def _stats(arena, facts, xwalk, keys, canon_of, group_keys, prov_by_canon, matches):
    scope = facts[facts["in_scope"]]
    closed = scope[scope["closed"] == True]
    method = xwalk[xwalk["source"] == "arena"].set_index("source_key")["match_method"]
    covered = [n for n in scope.index if n in method.index]
    closed_covered = [n for n in closed.index if n in method.index]
    return {
        "n_scope": len(scope), "n_covered": len(covered),
        "n_closed": len(closed), "n_closed_covered": len(closed_covered),
        "closed_exact": sum(method.get(n) == "exact" for n in closed.index),
        "top_tier": _top_tier(arena, xwalk, keys, prov_by_canon),
    }


def _top_tier(arena, xwalk, keys, prov_by_canon) -> int:
    """PRD §6: non-alias model whose first Arena snapshot within 60 days of listing is in the top 25%."""
    arena_x = xwalk[xwalk["source"] == "arena"]
    best = (arena.merge(arena_x, left_on="model_name", right_on="source_key")
            .groupby(["canonical_model_id", "publish_date"])["rank_percentile"].min().reset_index())
    count = 0
    for c, prov in prov_by_canon.items():
        if xwalk.loc[xwalk["canonical_model_id"] == c, "is_moving_alias"].iloc[0]:
            continue
        listed = keys[(keys["provider"] == prov) & (keys["norm"] == norm(c))]["first_ts"].min().date()
        listed = pd.Timestamp(listed)
        snaps = best[(best["canonical_model_id"] == c) & (best["publish_date"] >= listed)
                     & (best["publish_date"] <= listed + LAUNCH_WINDOW)].sort_values("publish_date")
        count += bool(len(snaps) and snaps["rank_percentile"].iloc[0] <= TOP_PERCENTILE)
    return count


def draft(arena, litellm, epoch, provider_map) -> tuple[pd.DataFrame, pd.DataFrame]:
    built = build(arena, litellm, epoch, provider_map)
    return built["models"], built["xwalk"]


def _guard(seeds_dir: Path) -> None:
    for name in ("seed_models.csv", "seed_model_crosswalk.csv"):
        path = seeds_dir / name
        if not path.exists():
            continue
        df = pd.read_csv(path, dtype=str).fillna("")
        for col in ("evidence_url", "approved_by"):
            if col in df and (df[col].str.strip() != "").any():
                raise ValueError(f"{path} has a filled {col}: refusing to overwrite hand-approved seed")


def _flag(v):
    return "" if pd.isna(v) else str(bool(v)).lower()


def write_seeds(seeds_dir: Path, models: pd.DataFrame, xwalk: pd.DataFrame) -> None:
    _guard(seeds_dir)
    models = models.assign(open_weights=models["open_weights"].map(_flag))
    xwalk = xwalk.assign(is_moving_alias=xwalk["is_moving_alias"].map(_flag))
    models.sort_values("canonical_model_id").to_csv(seeds_dir / "seed_models.csv", index=False)
    xwalk.sort_values(["source", "source_key"]).to_csv(seeds_dir / "seed_model_crosswalk.csv", index=False)


def _load(con):
    org = f"""select model_name, lower(max(nullif(organization, ''))) as organization
              from read_parquet('{RAW_ARENA}', hive_partitioning = true)
              where config = 'text' and category = 'overall'
                and run_date = (select max(run_date) from read_parquet('{RAW_ARENA}', hive_partitioning = true))
              group by 1"""
    arena = con.sql(f"""select s.model_name, o.organization, s.publish_date, s.rank_percentile, s.closed
                        from stg_arena__leaderboard s left join ({org}) o using (model_name)
                        where s.config = 'text' and s.category = 'overall'""").df()
    litellm = con.sql("""select model_key, litellm_provider, min(commit_ts) as first_ts
                         from stg_litellm__snapshots group by 1, 2""").df()
    epoch = con.sql("select distinct model from stg_epoch__models").df()
    return arena, litellm, epoch, con.sql("select * from seed_provider_map").df()


def _pct(n, d):
    return f"{n}/{d} = {n / d:.1%}" if d else f"{n}/{d}"


def main() -> None:
    _guard(SEEDS)  # fail before any work if a seed is hand-approved
    con = duckdb.connect(str(DB), read_only=True)
    built = build(*_load(con))
    models, xwalk, s = built["models"], built["xwalk"], built["stats"]
    write_seeds(SEEDS, models, xwalk)
    print("rows per (source, match_method):")
    print(xwalk.groupby(["source", "match_method"]).size().to_string())
    print(f"models: {len(models)}")
    print(f"is_moving_alias rows: {int(xwalk['is_moving_alias'].sum())} "
          f"(canonical models: {xwalk.loc[xwalk['is_moving_alias'], 'canonical_model_id'].nunique()})")
    print(f"in-scope Arena names: {s['n_scope']}, closed: {s['n_closed']}")
    print(f"coverage overall: {_pct(s['n_covered'], s['n_scope'])}")
    print(f"coverage closed: {_pct(s['n_closed_covered'], s['n_closed'])}")
    print(f"closed exact-match share: {_pct(s['closed_exact'], s['n_closed'])}")
    print(f"top-tier models: {s['top_tier']}")
    print("\n".join(built["notes"]))


if __name__ == "__main__":
    main()
