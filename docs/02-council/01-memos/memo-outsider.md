# Memo

## Position

Build it, narrowed to one real data asset and one honest causal question, because the four-slice pitch is a checklist of components and breadth dilutes the one real data asset.

## Three strongest arguments

1. **The price panel is what lands.** A daily price history back to 2023, rebuilt from LiteLLM git history, is something nobody publishes (E20, E31). It makes SCD2 necessary, not decorative, and "commit time is observed time, not effective date" is the caveat worth stating up front.
2. **The headline metric invites the obvious attack.** "Price per Arena-Elo point" treats a relative, method-broken score as a ratio scale (E21, R9). "Elo is relative" was the first critique of similar trackers. Use within-snapshot rank tiers, and reproduce Epoch's ~13×/yr as the ground-truth check (E31).
3. **Breadth is a liability.** SCD2, contracts, MetricFlow, an agent, evals and synthetic control each need their own caveats and documentation. The shared core is SQL, modeling and one-definition metrics: go deep there.

## Key risk

Unexplained caveats. A reader who cannot tell the grain of the price fact, why SCD2 rows have gaps, why `openai` downloads are inflated, or why clustered launches confound the study (E24, R4) will distrust the numbers. Also: four half-finished slices give no usable result (R6).

## What would change my mind

- The event study survives placebos with a clear effect: lead with adoption.
- Closed-model crosswalk coverage fails its test (E30, R2): ship the price panel alone.

## Recommendation

**build with changes**

**Keep:** LiteLLM price panel with SCD2 and declared grain; crosswalk coverage tests; daily CI cron showing measured freshness (R10); Epoch reproduction; one decision memo; static Observable dashboard on Parquet (E29).

**Cut:** price-per-Elo-point; the live chat agent (Gemini spend, expiry; R7, R12); synthetic control (keep a placebo-tested event study); the tool list atop the README.

**Add:** README's first three lines: the question, one number with an interval, one chart with a "last refreshed" stamp. A caveats section. DECISIONS.md with defensible tradeoffs. Pre-registration so a null result still ships. Agent evals only as a static table, after the panel and event study ship.
