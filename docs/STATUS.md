# STATUS — LLM Market Observatory

**Updated:** 2026-11-10 · **Milestone:** M0 Validate (Bloom replica) · **Deadline:** Sun 2026-11-15
**Grand plan:** `~/.claude/plans/https-www-datacamp-com-blog-data-analyti-jazzy-peach.md`

## Done
- [x] Research sprint: `docs/validation/research/01-04*.md` (raw, cited) → `docs/validation/research-brief.md` (E1–E31, R1–R12)
- [x] Council protocol: `docs/validation/council/00-protocol.md`

## In progress
- [ ] Council stage 1: 5 lens memos (`council/memo-*.md`)

## Next
1. Anonymize A–E (`map.json`) → 5 blind reviews → ranks (self-rank dropped) → chair verdict
2. `docs/PRD.md` + `docs/design.md` aligned to verdict → builder-check → user approval (HARD GATE)
3. superpowers:writing-plans → `docs/plans/` → build M1–M6

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
