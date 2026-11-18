# Anonymized council memos (A–E)
Order shuffled; identities withheld. Word cap was 400; do not credit content beyond the cap.

---

# Memo A  (527 words)

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

---

# Memo B  (397 words)

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

---

# Memo C  (483 words)

## Position

Build it, but aim past a private repo: publish the 2023-onward daily price panel as a citable open dataset and make the adoption-response finding the headline that gets shared.

## Three strongest arguments

1. **The panel is the only asset nobody else publishes.** Artificial Analysis retired its history API, Epoch updates per paper, and llmpricing and llm-prices keep no real price history (E31). A reproducible daily panel rebuilt from LiteLLM git history (E20) under MIT, joined to CC BY Arena (E21), Epoch (E22) and OpenRouter rankings (E25), is a dataset people cite and fork. A Parquet release with a dataset card and attribution (R5) gives the repo a life of its own.
2. **Reproducing Epoch's ~13x/yr number before extending it earns credibility with a skeptical audience.** Matching Epoch (E31) takes the "Elo is relative" critique off the table (R9). The shareable headline is then the new result: whether price cuts and launches move SDK downloads (E24, E23). A well-controlled null or a small effect with placebo tests (R4) is still a post worth forwarding, because it is honest and nobody else has it.
3. **The evaluated agent is the one slice no competitor offers.** The semantic layer plus the eval suite against raw text-to-SQL (E11) has no equivalent among competitors (E31). Ship it as a static, pre-computed eval report with failure cases, not a live endpoint. That stays inside the $0 and Gemini-cap limits (R7, R12) and nothing expires.

## Key risk

Reaching for a public dataset and a causal claim on top of a thin, noisy proxy (E24). If the adoption effect is unidentified and the crosswalk is leaky (R2, E30), the project looks overreaching.

## What would change my mind

- The top-N crosswalk fails coverage tests on closed models (E30), so the panel is untrustworthy.
- The Arena rating-method breaks (E21) leave too little comparable history to support any adoption story.
- Event-study placebos show launches are confounded beyond repair, leaving no adoption result to headline.

## Recommendation

**build with changes**

**Keep**
- Price panel, entity crosswalk with coverage tests, Epoch ground-truth check, adoption event study, semantic layer and agent eval, pinned stack (E28), static Parquet dashboard (E29).
- DECISIONS.md.

**Cut**
- HF hub-stats history (E26).
- A live agent endpoint.
- Broad model coverage beyond the top-N set.
- Heavy SCD2 ornamentation beyond the price dimension.

**Add**
- A versioned Parquet and dataset-card release with CC BY attribution and a changelog.
- One-page findings post leading with the adoption result, its caveats, and the null if that is what holds.
- A one-command rebuild plus a freshness badge set to the measured cadence (R10).

---

# Memo D  (398 words)

## Position

As scoped, this ships a wide, AI-built repo whose headline is either Epoch's number or a confounded null,.

## Strongest arguments

1. **The new centerpiece has no identification.** After R3/E31 the story is adoption, where data is weakest: PyPI is uv/CI-dominated, about 83% US, `openai` inflated by `litellm`, Google's SDK split in two (E24). Event dates are LiteLLM commit times, not effective dates (E20), and launches cluster (R4). Downloads are provider-level, cuts model-level, and every provider is treated: synthetic control has no donor pool. Expect a null or an artifact that reviewers will attack.
2. **The measurements are softer than the claims.** Arena scores break three times plus a rename (E21), so "price per Elo point" over time is the "Elo is relative" failure (R9). Closed models need a hand-curated crosswalk (E30, R2). The agent eval re-runs a vendor benchmark (E11) on paid, rising-price Gemini calls (E27, R7). Each compounds R6.

## Key risk

A polished, shallow repo loses trust at the first question such as "why is this causal?".

## What would change my mind

- A pre-registered PyPI placebo that does not fire, over enough verified, non-clustered price-cut dates.
- Crosswalk coverage tests passing for top-N closed models.

## Recommendation

**build with changes**

- **Keep:** the DE slice (marts, SCD2 price dimension from LiteLLM git history, tests, contracts, CI); one analyst number on within-snapshot ranks; Epoch reproduction as ground truth; DECISIONS.md.
- **Cut:** the agent and semantic-layer eval; synthetic control; Elo comparisons across method breaks; the "daily" claim until cadence is measured (R10).
- **Add, as ordered gates:** crosswalk coverage test; event-date audit against provider announcements; pre-registered descriptive event study allowed to publish a null. A failed gate stops scope; ship what passed.

---

# Memo E  (397 words)

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
