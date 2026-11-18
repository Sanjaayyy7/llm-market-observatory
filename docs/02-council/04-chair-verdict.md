# Chair verdict

## Verdict

**go-with-changes.** Build around the LiteLLM price panel, with adoption as a pre-registered secondary result and the eval last; both pivots fail (B's votes are static, E21; C has no ground truth).

## Decision question restated

Which narrowed Observatory can Claude finish by Sun 2026-11-15 under usage limits and shippable at every cut?

## Where the council agrees

All five memos, unless noted:

- The centerpiece is a LiteLLM price panel back to 2023, with SCD2 (E20, E31).
- Crosswalk coverage tests come first (memo-executor, memo-first-principles; E30, R2).
- Epoch is a ground-truth check (E31, R3); no live agent.
- The event study is pre-registered, with placebos and a publishable null (R4).

## Where it diverges

- **Eval.** memo-contrarian cuts it. Ruling: keep it static, offline, and last (R7, unverified `mf query`).
- **Headline.** Adoption (memo-expansionist, memo-executor) or the panel (memo-first-principles, memo-outsider)? Ruling: the panel; it survives cuts and a null on noisy data (E24).
- **Event-study order.** Sixth in memo-first-principles, so the causal slice is cut first (review-contrarian). Ruling: after a minimal dashboard, before the eval.
- **OpenRouter.** memo-first-principles adds it; memo-executor cuts it (R11). Ruling: optional, given a key; being model-level (E25), it eases memo-contrarian's unit mismatch.
- **Unsupported:** "cite and fork" and "an Epoch match answers Elo" (memo-expansionist). "No donor pool" (memo-contrarian) is inference.

## What's missing

- **Price** (review-contrarian): first-party, standard-tier list price at a declared input:output blend. A cut is a same-ID drop above a threshold, excluding corrections. Spot-check levels against tokencanopy (MIT).
- **Power** (review-contrarian, review-outsider, review-executor): pre-registration fixes unit, window, minimum non-clustered events and MDE; below it, descriptive only.
- **Causal limits** (review-first-principles): an observational design does not prove an experimental effect; disclosed, not closed.
- **Memo reader** (review-first-principles): a product lead: buy at launch price, or wait?
- **Usage limits** (review-executor, review-expansionist): main stays shippable; STATUS.md every session; a twice-failed gate triggers the next cut; no new slice after Sat 2026-11-14.
- **Crosswalk owner** (review-executor): Claude drafts (E30); the owner approves each row.
- **Decay** (review-contrarian, review-first-principles): no runtime Gemini; CI fails on stale data; idle-repo cron disabling (review-outsider) is outside the brief: verify.

## Surviving scope

**Headline question:** How long does a newly listed top-tier LLM keep its launch price, and does the first cut move developer adoption?

**Number:** survival-curve median days, first observed listing to first observed cut, uncut models censored: "X days (IQR a–b, n=k, commit lag ±d)". If most are never cut, use the share cut within 365 days. Top-tier = within-snapshot Arena rank (R9).

**Keep** (done = gate passes):

1. Pinned stack and source probes (G0–G1).
2. Crosswalk (G2).
3. SCD2 price dimension and daily fact (G3).
4. Event-date audit (G4).
5. Epoch check (G5).
6. Headline, metric definitions, decision memo, Parquet dashboard (G6–G7).
7. ClickPy event study, Google SDKs summed (E24) (G8–G9).
8. Static fixed-question eval: semantic layer vs text-to-SQL (G10).

**Cut:** price-per-Elo (R9); synthetic control (weak identification, R4; DECISIONS.md explains); the live agent (R7); BigQuery (tables expire, E10c); hub-stats (E26); Elementary (E10b); the "daily" claim (R10).

**Add:** pre-registration (defensible null); level spot-check (Epoch checks only trend); event-date audit (commit time ≠ effective time, E20); DATA.md (attribution, R5); STATUS.md (handoff).

**Cut order:** paid Gemini run → MetricFlow and eval → OpenRouter → event-study inference (keep the descriptive plot and one placebo) → cron (static snapshot). Never cut: crosswalk tests, panel, Epoch check.

**Traceability:** DECISIONS.md: choice, rejected alternative, E-ID. Each README number links to its model and test.

**Gemini guardrails:** keep cache, ledger, smoke test, live-price cap, pinned ID, disclosure (R7, R12, E27). Change: no calls from CI, cron or page; free tier first; user approves a `count_tokens` estimate before the first paid call; hard stop at cap; nothing before G9.

## Gates

- G0: pins resolve (Python 3.12, `duckdb<2`; E28); `dbt build` passes.
- G1: freshness table logs rows and max date per source; SLA = measured cadence.
- G2: crosswalk unique, not-null, coverage ≥ threshold incl. closed models; else panel only.
- G3: replay hash stable across two runs; `--follow` and deletions handled; SCD2: no overlaps, one current row per key.
- G4: an audit table covers a declared sample of cuts.
- G5: Epoch within a pre-committed tolerance; else no headline.
- G6: headline number matches the model output.
- G7: Pages first screen: question, number, chart, data stamp.
- G8: pre-registration commit precedes event-study code.
- G9: results and placebos published regardless.
- G10: `mf query` probe and scorer tests pass; user approves; spend ≤ cap.

## Next actions

**PRD:** headline and number shape; price and cut definitions; N rule and thresholds; Epoch tolerance; pre-registration skeleton; gates; cut order; user actions (OpenRouter key, Gemini approval, Pages).

**design.md:** grain for each model; git-replay SCD2 algorithm; crosswalk schema; freshness table; Parquet export; CI and cron; STATUS.md; eval harness.

## Confidence

**Medium.** It drops if G2 fails on closed models, same-model cuts are rare, G5 misses.
