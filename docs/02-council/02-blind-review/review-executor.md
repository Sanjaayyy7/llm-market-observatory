# Review

## Per memo

**A**
Strength: Real gate sequence (pinned stack E28, measured freshness, crosswalk before any mart) and an explicit cut order.
Weakness: Over the 400-word cap, so the cut order and keep/add lists earn no credit; no budget for Claude usage windows per gate.

**B**
Strength: Narrowest scope with a defensible core (LiteLLM SCD2 panel, E20).
Weakness: No build order or cut order, and no tooling pins; "Elo was the first critique" overstates the evidence, which names it as one example.

**C**
Strength: Static, precomputed agent eval keeps Gemini spend capped and nothing expiring (R7, R12).
Weakness: Over the cap, so its content gets no credit; it keeps nearly everything and adds a dataset release plus a post. There is no cut order.

**D**
Strength: Ordered gates where a failed gate stops scope, including an event-date audit against provider announcements (E20 commit-time caveat).
Weakness: "No donor pool" for synthetic control is inference, not in the brief; no tooling pins or Gemini cap.

**E**
Strength: Explicit order (crosswalk gate, panel, Epoch check, metrics, dashboard, event study, eval harness) with the agent UI cut and an offline capped harness kept.
Weakness: Keeps MetricFlow ahead of the event study without a gate, and never says who curates the crosswalk or how big N is.

## Blind spots
- Allocating Claude 5-hour windows and the weekly cap across gates; no memo names what is built per window.
- How the crosswalk is built: top-N size, who curates it, and the closed-model fallback (E30).
- Causal spec details: outcome unit (provider-level downloads vs model-level events), clustered launches, effect window, and what counts as a null.
- Replaying 2,940 LiteLLM commits with `--follow` into SCD2 (E20); cost and failure handling.
- Still-unverified items: ClickPy and BigQuery volume, `dbt build` and `mf query` runtime, Gemini free-tier limits.
- Gemini cap amount, model ID pin before the 2026-12-01 routing change (E27), and the user's OpenRouter key (R11).
- Deploy path: Parquet to Pages on a cron, and Arena cadence before any "daily" claim (R10).

## Must-keep changes
1. Crosswalk coverage gate precedes every mart, with a pinned stack (Python 3.12, `duckdb<2`) and measured source freshness as gate zero (A).
2. Explicit cut order: Gemini live runs, then agent and MetricFlow, then synthetic control, with only an offline capped harness retained (A, E).
3. Pre-registered event study with placebos, after the Epoch reproduction and dashboard, allowed to publish a null, with an event-date audit (D, E).

## Final ranking
FINAL RANKING: E > D > A > B > C

## Lean
LEAN: support
Build the panel-first Observatory with E and D's gates and A's cut order, because those gates leave a shippable warehouse and dashboard if limits stall.
