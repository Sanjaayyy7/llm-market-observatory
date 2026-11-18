# Memo

## Position
Starting from what users of the data need, the Observatory is the right vehicle, but only if the governed price panel and its metric definitions are the centerpiece and the causal and agent slices shrink to small, defensible claims.

## Three strongest arguments
1. **Users need trusted, defined metrics on a modeled warehouse, and only this option provides them on real data.** LiteLLM history yields an SCD2 price dimension nobody publishes (E20, E31). Pivot C's synthetic data allows no ground-truth check; pivot B rests on a static vote set (E21).
2. **The proposed centerpiece sits on the weakest data.** Epoch owns the price-decline story (E31, R3), so the plan leans on adoption causality, yet PyPI is CI-dominated and dependency-inflated (E24), and launches cluster (R4).
3. **The edge is evals, and users want them as verification, not chat.** Teams fear incorrect data reaching stakeholders (E4, E14). A fixed-question eval of semantic layer vs text-to-SQL (E11) proves that; a chat agent adds spend and risk (R7, R12).

## Key risk
No observational design proves an experimental effect, so the event study must be framed as descriptive.

## What would change my mind
- Crosswalk coverage fails for a top-N model set (E30, R2): narrow to the price panel.
- The Epoch reproduction misses badly: fix the panel.

## Recommendation
**build with changes**

**Keep**
- LiteLLM price panel: SCD2, declared grain, tests, contracts (E20).
- Top-N crosswalk with coverage tests (E30).
- Epoch reproduction as ground-truth gate (E22).
- MetricFlow metrics with written definitions, Elo caveats (R9, E28).
- Static Observable dashboard (E29); SLA at measured cadence (R10).

**Cut**
- Synthetic control; "daily" claim; HF hub-stats (E26); BigQuery (E10c).
- Agent UI; keep only an offline-first, capped eval harness.
- Elo comparisons across method breaks (E21).

**Add**
- Pre-registered event study with placebos; OpenRouter within-provider share beside PyPI (E25, R11); nulls reported.
- DECISIONS.md.
- Order: crosswalk gate, panel, Epoch check, metrics, dashboard, event study, eval harness.
