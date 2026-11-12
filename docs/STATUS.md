# STATUS — LLM Market Observatory

**Updated:** 2026-11-11 · **Milestone:** M0 Validate, awaiting design approval · **Deadline:** Sun 2026-11-15
**Grand plan:** `~/.claude/plans/https-www-datacamp-com-blog-data-analyti-jazzy-peach.md`

## Done
- [x] Research sprint: `docs/validation/research/01-04*.md` (raw, cited) → `docs/validation/research-brief.md` (E1–E31, R1–R12)
- [x] Council: 5 memos → anonymized A–E → 5 blind reviews → `ranks.md` (5/5 support) → `chair-verdict.md` (go-with-changes)
- [x] `docs/PRD.md` + `docs/design.md` v1.1 (builder check resolved, user decisions applied)

## In progress
- [ ] User approval of `docs/design.md` (HARD GATE)

## Next
1. superpowers:writing-plans → `docs/plans/` build plan (gates G0–G10, TDD tasks)
2. Build in gate order G0 → G10; drills batched before the v1.0 tag

## Key decisions so far
- Lead idea: Observatory. Pivots B (Arena preference lab), C (synthetic app + A/B).
- Verification shifted the centerpiece to **adoption response**. Epoch's ~13×/yr price decline becomes a ground-truth check, not the headline (E22, E31).
- Pins: Python 3.12, `duckdb<2`, dbt-core 1.12.x + dbt-duckdb 1.11.x + dbt-metricflow 0.15.x (E28). Dashboard: Observable Framework + Parquet on GitHub Pages (E29).

## Blockers / needs user
- Approve design.md (now).
- G2: approve canonical model list + manual matches.
- G7: repo + Pages approved in principle; Claude confirms before first push.
- G10: Gemini key from a **no-billing** project (free tier only, $0).
- Release: drills.

## Resume prompt
"Resume LLM Market Observatory from docs/STATUS.md; continue the 'Next' list in order."
