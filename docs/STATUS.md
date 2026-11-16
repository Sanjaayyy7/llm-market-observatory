# STATUS — LLM Market Observatory

**Updated:** 2026-11-16 · **Now:** G0 scaffold (next; P3 Python approved and installed, 3.12.12 arm64) · **Deadline:** none. Ship continuously, G0–G7 first.
**Owner:** the `cofounder` agent (`.claude/agents/cofounder.md`). The human owner is involved only at the owner gates marked **bold** below.
**Grand plan:** `docs/00-charter/2026-11-10-grand-plan.md` · **Decisions:** `docs/DECISIONS.md`

## Done
- [x] Research sprint → `docs/01-research/research-brief.md` (E1–E31, R1–R12)
- [x] Council → `docs/02-council/04-chair-verdict.md` (go-with-changes)
- [x] PRD + design v1.1 (builder check, user decisions)
- [x] Feasibility spike → `docs/04-feasibility-spike/feasibility-spike.md`. Replay works; ~10% of top-tier models cut their price within 365 days; the event study is below its power floor
- [x] Spec v1.2 (PRD §13): relaxed ID rule, KM 365-day headline, descriptive event study, eval deferred, kill criteria (design §18). Design approved by delegation 2026-11-15
- [x] Docs reorganized into chronological phase folders (2026-11-16, `22408f2`)
- [x] C0: co-founder hired. Agents, project settings, CLAUDE.md, this roadmap (2026-11-16)
- [x] C1: plan v1.1. Checklist 1–16 closed, mini-council resolved, 11 DECISIONS rows added (2026-11-16)

## Roadmap

Each row closes only when its checkpoint holds. Gate evidence goes in the body of the gate's last commit (the STATUS update, made on the branch before the fast-forward merge).

| Stage | Plan task | Deliverable | Checkpoint (must hold to close) | Gate / kill | State |
|---|---|---|---|---|---|
| C0 | — | Hire: agents, settings, CLAUDE.md, roadmap | A fresh session runs as cofounder; project edits are not gated; reorg + hire on main | — | done |
| C1 | — | Plan v1.1: close the C1 checklist, apply DECISIONS rows 1–5, mini-council | Every checklist item is closed with a diff. Pins resolve (`uv pip compile` dry run). Source URLs and the supported Node LTS are verified live, with citations. Every council finding is resolved. Plan v1.1 committed | — | done |
| G0 | 1 | Scaffold | `uv sync --frozen && make test && make ci` → `1 passed`, `PASS=4` | P3 done 2026-11-16 (`uv python install 3.12` → 3.12.12 arm64) | **next** |
| G3a | 2 | LiteLLM replay | `pytest tests/ingest` passes. Two fresh full replays give the same `replay_hash`; error days ≤2% (spike: ~720 days, 2 errors) | kill: >2% error days or hash differs | todo |
| G1 | 3 | Fetchers + probes | `make probe`: one `_freshness` row per source, rows > 0 | — (Epoch GPQA source resolved 2026-11-16: pinned insight CSVs, Task 8) | todo |
| G3b | 4 | Staging + SCD2 `dim_model_price` | dbt build passes on ci and dev; `unique(model_key, valid_from)`; hand-worked SCD2 golden rows match; reviewer pass | — | todo |
| G2 | 5 | Crosswalk + Arena rank | Coverage ≥90% in-scope top-tier, ≥80% closed. The evidence test passes (URL + match score on every manual row). Reviewer pass on low-score rows | kill: <30 top-tier → panel-only | todo |
| — | 6 | Price facts + survival mart | `dbt build --target dev` passes; ~9 real first cuts | — | todo |
| G4 | 7 | 20-cut audit (runs alone) | `mart_cut_audit` passes | kill: >25% data fixes → re-audit once | todo |
| G5 → G6 | 8 → 9 | Epoch check, then KM headline | G5: `reproduced_factor` = 42.02 ± 0.01 and `passed` (dated price agreement; DECISIONS "G5 replan"). G6: Y ≈ 10% at n ≈ 91; `fit_km` matches the hand-worked KM golden, and lifelines and statsmodels agree; reviewer pass | G5 fails after one diagnosis → "validation pending" + mini-council replan | todo |
| G7 | 10 | Exports, site, docs, Pages | Export test passes. Playwright at 1280 and 375 px passes. gitleaks clean. `security-review` + reviewer pass | **P3: Node 24 default, gitleaks, Playwright browser (if not cached). S1: owner approves `gh repo create`, first push and Pages** | todo |
| G8–9 | 11 | Descriptive adoption view | Prereg commit precedes the code; `make all` prints the "Descriptive only" verdict line | kill: <8 events → descriptive | todo |
| — | 12 | Weekly refresh | `gh workflow run refresh.yml` green, with a new stamp commit | **S1: push** | todo |
| R | — | v1.0 release | `make drill-check STRICT=1` exits 0; tag | **A1: owner writes the drills without AI. S1: tag push** | todo |

## C1 checklist

Closed 2026-11-16 in plan v1.1 (`30d6f0b`, plus council fixes in `89be1be`). Each item maps to its diff and evidence in those commits and in the DECISIONS rows dated 2026-11-16. The item list is preserved in git history at `0527633:docs/STATUS.md`.

## Owner gates pending
- G0 P3 is done: the owner approved it, and `uv python install 3.12` installed 3.12.12 arm64. uv also linked `~/.local/bin/python3.12`, which now comes before the broken x86 `/usr/local/bin/python3.12` on PATH.
- Later: **G7** P3 (Node 24 default, gitleaks, maybe a Playwright browser) plus S1 (`gh repo create`, first push, Pages).
- G2 is delegated to the co-founder (evidence test); the owner gets an FYI.
- Release: the owner writes the drills without AI.

## Resume
Open `claude` in this repo. The co-founder orients from this file and continues with the `Now:` stage. After a `/clear`, type `go` if it doesn't start on its own (whether `initialPrompt` re-fires after `/clear` is UNVERIFIED).
