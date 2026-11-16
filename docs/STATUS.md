# STATUS — LLM Market Observatory

**Updated:** 2026-11-16 · **Now:** C1 plan hardening (next) · **Deadline:** none. Ship continuously, G0–G7 first.
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

## Roadmap

Each row closes only when its checkpoint holds. Gate evidence goes in the body of the gate's last commit (the STATUS update, made on the branch before the fast-forward merge).

| Stage | Plan task | Deliverable | Checkpoint (must hold to close) | Gate / kill | State |
|---|---|---|---|---|---|
| C0 | — | Hire: agents, settings, CLAUDE.md, roadmap | A fresh session runs as cofounder; project edits are not gated; reorg + hire on main | — | done |
| C1 | — | Plan v1.1: close the C1 checklist, apply DECISIONS rows 1–5, mini-council | Every checklist item is closed with a diff. Pins resolve (`uv pip compile` dry run). Source URLs and the supported Node LTS are verified live, with citations. Every council finding is resolved. Plan v1.1 committed | — | **next** |
| G0 | 1 | Scaffold | `uv sync --frozen && make test && cd dbt && uv run dbt build --target ci` → `1 passed`, `PASS=4` | — | todo |
| G3a | 2 | LiteLLM replay | `pytest tests/ingest` passes. Two replay runs give the same `replay_hash`, ~720 days, 2 error days | kill: >2% error days | todo |
| G1 | 3 | Fetchers + probes | `make probe`: one `_freshness` row per source, rows > 0 | Epoch GPQA missing → mini-council replan (owner FYI) | todo |
| G3b | 4 | Staging + SCD2 `dim_model_price` | dbt build passes on ci and dev; `unique(model_key, valid_from)`; hand-worked SCD2 golden rows match; reviewer pass | — | todo |
| G2 | 5 | Crosswalk + Arena rank | Coverage ≥90% in-scope top-tier, ≥80% closed. The evidence test passes (URL + match score on every manual row). Reviewer pass on low-score rows | kill: <30 top-tier → panel-only | todo |
| — | 6 | Price facts + survival mart | `dbt build --target dev` passes; ~9 real first cuts | — | todo |
| G4 | 7 | 20-cut audit (runs alone) | `mart_cut_audit` passes | kill: >25% data fixes → re-audit once | todo |
| G5 → G6 | 8 → 9 | Epoch check, then KM headline | G5: factor inside tolerance. G6: Y ≈ 10% at n ≈ 91; lifelines and statsmodels agree on the golden set; reviewer pass | G5 fails after one diagnosis → "validation pending" + mini-council replan | todo |
| G7 | 10 | Exports, site, docs, Pages | Export test passes. Playwright at 1280 and 375 px passes. gitleaks clean. `security-review` + reviewer pass | **S1: owner approves `gh repo create`, first push and Pages** | todo |
| G8–9 | 11 | Descriptive adoption view | Prereg commit precedes the code; `make all` prints the "Descriptive only" verdict line | kill: <8 events → descriptive | todo |
| — | 12 | Weekly refresh | `gh workflow run refresh.yml` green, with a new stamp commit | **S1: push** | todo |
| R | — | v1.0 release | `make drill-check` strict passes; tag | **A1: owner writes the drills without AI. S1: tag push** | todo |

## C1 checklist

From the build-plan analysis of 2026-11-16. Line numbers refer to the plan, or to `D` = `docs/03-spec/design.md`. Some were off by one (corrected: l.159, l.291), so verify each before editing. Each item closes with a diff plus evidence.

1. `make site` and `make all` are used (l.345, l.346, l.378) but never defined; Task 10's file list omits the Makefile.
2. `make build` = `dbt build --target dev` (l.52) runs from the repo root, so it needs `--project-dir dbt --profiles-dir dbt`. l.78 runs it from `cd dbt` instead.
3. `make drill-check` exits 0 while drills are pending (l.317), but release says it "must pass" (l.395). Add a strict mode for R.
4. Fixture path is inconsistent: `tests/fixtures/<source>/` (l.134) vs `tests/fixtures/raw/` (l.18, l.162). Pick one.
5. Source URLs missing or vague: LiteLLM repo (l.95), tokencanopy (l.155), the Epoch `epoch.ai/data/*.csv` glob (l.153). Verify live and pin exact URLs. Check the research brief and reports first.
6. Task 4 has no tokencanopy staging model (l.168), yet Task 8 consumes tokencanopy raw (l.272).
7. "20 models within 5% of tokencanopy" (l.291) has no stated basis. Derive it from evidence or drop it.
8. The plan uses Node 20 (l.9, l.16), possibly end-of-life (UNVERIFIED). Verify the current supported LTS on nodejs.org and pin it.
9. Task 10's files (l.323) lack `site/package.json` and a lockfile, despite the exact-pin rule (l.16).
10. gitleaks is required in design (D §17 item 11) but missing from `ci.yml` (l.79).
11. The `dbt-core~=1.12.6` + `dbt-duckdb~=1.11.1` pins (l.15) are unverified. Dry-run resolve them before Task 1.
12. D l.325 ("gate failing twice → cut order") conflicts with "hard stop after one diagnosis" (l.24, l.292). Reconcile per DECISIONS row 5.
13. The G2 approval flow (l.222) and the export test's approved-rows check (l.332) must follow DECISIONS row 3. Task 5 gets a test that fails unless every manual crosswalk row has a source URL and a name-match score; low-score rows go to the reviewer.
14. Golden fixtures (owner decision): Task 4 hand-worked SCD2 rows; Task 9 lifelines vs statsmodels KM agreement on a small known dataset.
15. Reroute every plan line that sends a non-safety item to "the user" to the co-founder + mini-council (l.24, l.159, l.292). S1 and A1 items stay with the owner.
16. Ownership: l.26 (drills files) and l.27 ("every builder call adds a DECISIONS row") go to the co-founder. Builders report `CHOICE:` lines; the co-founder writes the rows and the drills questions.

## Owner gates pending
- None right now. Next owner gate: **G7** (`gh repo create`, first push, Pages).
- G2 is delegated to the co-founder (evidence test); the owner gets an FYI.
- Release: the owner writes the drills without AI.

## Resume
Open `claude` in this repo. The co-founder orients from this file and continues with the `Now:` stage. After a `/clear`, type `go` if it doesn't start on its own (whether `initialPrompt` re-fires after `/clear` is UNVERIFIED).
