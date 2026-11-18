# Memo

## Position

Build it, but as a sequence of gated slices in which the agent and Gemini work come last and are the first things cut, so a usage-limit stall still leaves a shippable warehouse, dashboard and causal result.

## Three strongest arguments

1. **The tooling is pinnable and the data is free and licensed, so the first gates are cheap.** Python 3.12, `duckdb<2`, dbt-core 1.12.6, dbt-duckdb 1.11.1 and dbt-metricflow 0.15.0 resolve together (E28). DuckDB 2.0 files are unreadable by older versions and dbt-duckdb tests 2.0 only in nightly CI (E10a, R8). The sources are open: LiteLLM (MIT, E20), LMArena (CC BY, E21), Epoch (CC BY, E22), ClickPy (E23). The OpenRouter dataset API is licensed (E25), but it needs the user's key (R11). Gate 1 is a clean `dbt build` on seeds under the pinned versions. Gate 2 is row counts plus a measured freshness for each source (R10), and the SLA is set to that measured cadence.
2. **Entity resolution is the step most likely to break the build, so it comes before any mart.** No shared ID exists across sources and closed models are covered poorly (E30, R2). Gate 3 is a hand-curated top-N crosswalk seed with uniqueness and coverage tests. The LMArena slug-to-display-name switch on 2026-10-20 and the rating-method breaks are handled here, with within-snapshot ranks (E21, R9).
3. **The centerpiece must survive the cut order.** Epoch already owns the price-decline number, so reproducing it is a ground-truth gate (E31, R3). The adoption event study is the differentiator. It needs a pre-registered spec, placebo tests, a sum of `google-generativeai` and `google-genai`, and an honest null (E24, R4).

Sequence after gate 3:
- SCD2 price dimension and incremental facts, with the one-command rebuild.
- Epoch reproduction.
- Event study.
- Static Parquet dashboard on Observable Framework (E29), with CI and cron (E15).
- DECISIONS.md.

The agent and its eval come only after all of these pass.

## Key risk

A noisy PyPI outcome (E24) combined with crosswalk gaps produces a null or a muddle, and usage limits (R6) get burned on rework. Mitigation: freeze the crosswalk and spec before running the model, and keep a STATUS.md handoff.

## What would change my mind

- Gate 2 shows LMArena or LiteLLM history is too sparse or too stale to support a daily panel (R10, E20). That points to pivot C.
- The crosswalk covers too few closed models to give a meaningful panel (E30).

## Recommendation

**build with changes**

**Keep:**
- The DE slice with an SCD2 price dimension.
- The event study with placebo tests.
- The Epoch reproduction check.
- The Parquet dashboard.
- DECISIONS.md.

**Cut, in order:**
1. Gemini live eval runs. Keep only an offline harness with a cache, a cap set from live prices, and a ledger (E27, R7).
2. The "ask the observatory" agent and MetricFlow.
3. Synthetic control, leaving the event study alone.
4. The OpenRouter ingest (R11).
5. Elementary. If kept, pin 0.23.4 or later (E10b).

**Add:**
- A crosswalk coverage test.
- A source-freshness measurement.
- A pre-registered causal spec.
