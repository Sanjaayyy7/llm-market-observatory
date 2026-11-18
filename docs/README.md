# Docs index — LLM Market Observatory

Everything written so far, in the order it happened. Start with [STATUS.md](STATUS.md) for where things stand now.

[HANDOFF.md](HANDOFF.md) is the shared Codex/Claude checkpoint: assistant attribution, commits, checks, unresolved findings, and the exact next action. Both assistants use the same specification and branch.
Codex reads `AGENTS.md` (root) and the repo skills in `.agents/skills/` (`ponytail`, `cofounder-gate`). Claude Code reads `CLAUDE.md` and `.claude/agents/`. `.githooks/commit-msg` enforces the `Agent:` commit trailer for both.

## How this folder is organized

- **Numbered folders (`00-` … `05-`)** are project phases, in the order they happened. Each one holds that phase's record. The spec (03) and the plan (05) can still get versioned revisions; each doc keeps its own change log.
- **Unnumbered files at this level** are living documents that stay current: [STATUS.md](STATUS.md), [HANDOFF.md](HANDOFF.md), [DECISIONS.md](DECISIONS.md), [DATA.md](DATA.md) and [prereg/](prereg/). Their paths are fixed by the build plan and its tests, so they don't go in a numbered folder.
- Raw assistant session logs stay local and gitignored, because they contain machine paths and working notes.

## Timeline

| # | Date | Phase | Outcome | Folder | Commits |
|---|---|---|---|---|---|
| 00 | 2026-11-10 | Charter | Goal, milestones M0–M6, Gemini spend guardrails | [00-charter/](00-charter/) | written before the repo existed; copied in 2026-11-16 |
| 01 | 2026-11-10 | Research | 4 research reports condensed into one brief with evidence IDs E4–E31 and risks R2–R12 | [01-research/](01-research/) | `8c9bbe5` |
| 02 | 2026-11-10 | Council | 5 lens memos, blind peer review and rank aggregation. Chair verdict: **go-with-changes**, gates G0–G10 | [02-council/](02-council/) | `8c9bbe5` `e2c73a3` `22ccc1e` |
| 03 | 2026-11-11 → 11-15 | Spec | PRD + design v1, then v1.1 (builder check and user decisions), then v1.2 (after the spike) | [03-spec/](03-spec/) | `4b9b9c5` `f3ab78b` `b3de42c` |
| 04 | 2026-11-15 | Feasibility spike | LiteLLM replay works. About 10% of top-tier models cut their list price within 365 days. The event study is below its power floor | [04-feasibility-spike/](04-feasibility-spike/) | `b3de42c` |
| 05 | 2026-11-15 | Build plan | 12 TDD tasks, gates G0 → G9 plus the weekly refresh | [05-build-plan/](05-build-plan/) | `37d6b38` |
| 06 | 2026-11-16 → 11-18 | Build | Gates G0–G9 and the weekly refresh closed; the site is live at <https://sanjaayyy7.github.io/llm-market-observatory/>. Code lives at the repo root (`ingest/`, `dbt/`, `analysis/`, `site/`) | — | [STATUS.md](STATUS.md) |

The spike (04) ran after spec v1.1 and fed spec v1.2, which is why 03 spans two dates.

## File map

```text
docs/
├── README.md                          this index
├── STATUS.md                          living: done, next, blockers, resume prompt
├── HANDOFF.md                         living: shared checkpoint between coding assistants
├── DECISIONS.md                       living: every open choice and deviation, with evidence
├── DATA.md                            living: sources, licenses, pinning
├── prereg/                            pre-registrations, each committed before its outcome was read
│   ├── epoch-check.md                 validation against Epoch AI (G5)
│   └── event-study.md                 descriptive SDK-adoption event study (G8)
├── 00-charter/
│   └── 2026-11-10-grand-plan.md       original plan: validate → spec → build
├── 01-research/
│   ├── research-brief.md              the brief the council read (E4–E31, R2–R12)
│   └── reports/                       raw research-agent reports behind the brief
│       ├── 02-landscape-datasets.md   project landscape and candidate datasets
│       ├── 03-method-and-stack.md     Bloom council method and the $0 analytics stack
│       └── 04-verification.md         live endpoint checks of open factual questions
├── 02-council/                        read in number order: that's the process order
│   ├── 00-protocol.md                 rules: lenses, models, memo format, blind review
│   ├── 01-memos/                      stage 1: one memo per lens
│   │   └── memo-{contrarian,executor,expansionist,first-principles,outsider}.md
│   ├── 02-blind-review/               stage 2
│   │   ├── anonymized-memos.md        the memos relabeled A–E, as reviewers saw them
│   │   ├── map.json                   label → lens key (kept from reviewers)
│   │   └── review-{…same 5 lenses}.md each lens's blind review and ranking
│   ├── 03-ranks.md                    average ranks, with self-ranks dropped
│   └── 04-chair-verdict.md            stage 3: verdict, cuts, gates G0–G10
├── 03-spec/
│   ├── PRD.md                         what and why; every requirement cites an E-ID
│   └── design.md                      architecture, grain, metrics, kill criteria (§18)
├── 04-feasibility-spike/
│   ├── feasibility-spike.md           method, results, verdicts, caveats
│   ├── scripts/                       the code that produced the numbers, kept as run
│   │   ├── replay.py                  last LiteLLM commit per UTC day → snapshots CSV
│   │   ├── analyze_cuts.py            same-key price cuts → cuts.csv, models.csv
│   │   ├── analyze_toptier.py         Arena top tier, name matching, survival preview
│   │   └── analyze_relaxed.py         recount under the relaxed ID rule
│   └── outputs/
│       ├── cuts.csv                   87 price drops, flagged real / reverted / launch fix
│       └── models.csv                 527 model keys: first and last listed, launch price
├── 05-build-plan/
│   └── 2026-11-15-v1-ship-line.md     12 tasks, global constraints, hard stops
```

## Reading paths

- **Use or cite the data:** [root README](../README.md) → [DATA.md](DATA.md) → the site's Methods page
- **Catch up fast:** [STATUS.md](STATUS.md) → [PRD](03-spec/PRD.md) → [build plan](05-build-plan/2026-11-15-v1-ship-line.md)
- **Audit why it's built this way:** [charter](00-charter/2026-11-10-grand-plan.md) → [brief](01-research/research-brief.md) → [chair verdict](02-council/04-chair-verdict.md) → [design](03-spec/design.md) → [spike](04-feasibility-spike/feasibility-spike.md)
- **Check a number:** find its E-ID in the brief, then the matching section in `01-research/reports/`.

## Old paths

These files moved on 2026-11-16 (`docs/validation/…` and `docs/plans/…` became the numbered folders). The charter is a verbatim copy, so it still uses the old paths. `git log --follow <file>` traces any file's history across the move.
