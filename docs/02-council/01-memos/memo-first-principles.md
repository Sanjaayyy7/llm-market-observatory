# Memo

## Position
Starting from what a hiring team must see, the Observatory is the right vehicle, but only if the governed price panel and its metric definitions are the centerpiece and the causal and agent slices shrink to small, defensible claims.

## Three strongest arguments
1. **Every target role wants trusted, defined metrics on a modeled warehouse, and only this option shows it on real data.** All role flavors share SQL, modeling and one-definition metrics (E1); postings name SCDs, contracts, SLAs, semantic layers (E3a, E18, E19). LiteLLM history yields an SCD2 price dimension nobody publishes (E20, E31). Pivot C's synthetic data allows no ground-truth check (E7); pivot B rests on a static vote set (E21).
2. **The proposed centerpiece sits on the weakest data.** Epoch owns the price-decline story (E31, R3), so the plan leans on adoption causality, yet PyPI is CI-dominated and dependency-inflated (E24), and launches cluster (R4).
3. **The candidate's edge is evals, and the market wants it as verification, not chat.** Teams fear incorrect data reaching stakeholders (E4, E14) and ask for SQL-accuracy evals and semantic layers for agents (E3a, E3c). A fixed-question eval of semantic layer vs text-to-SQL (E11) proves that; a chat agent adds spend and risk (R7, R12).

## Key risk
Authenticity (R1): interviews run without AI (E5b, E5c), so a repo the candidate cannot rebuild by hand is negative signal. Also, Product DS postings want experimentation (E1, E17), which no observational design proves.

## What would change my mind
- Crosswalk coverage fails for a top-N model set (E30, R2): narrow to the price panel.
- The Epoch reproduction misses badly: fix the panel.
- Primary evidence that hiring teams prefer experiment write-ups: pivot C.

## Recommendation
**build with changes**

**Keep**
- LiteLLM price panel: SCD2, declared grain, tests, contracts (E20).
- Top-N crosswalk with coverage tests (E30).
- Epoch reproduction as ground-truth gate (E22, E7).
- MetricFlow metrics with written definitions, Elo caveats (R9, E28).
- Static Observable dashboard (E29); SLA at measured cadence (R10).

**Cut**
- Synthetic control; "daily" claim; HF hub-stats (E26); BigQuery (E10c).
- Agent UI; keep only an offline-first, capped eval harness.
- Elo comparisons across method breaks (E21).

**Add**
- Pre-registered event study with placebos; OpenRouter within-provider share beside PyPI (E25, R11); nulls reported.
- DECISIONS.md, AI_USAGE.md, hand-rewritten core SQL (R1).
- Order: crosswalk gate, panel, Epoch check, metrics, dashboard, event study, eval harness.
