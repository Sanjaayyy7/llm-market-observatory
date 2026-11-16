# Anonymized council memos (A–E)
Order shuffled; identities withheld. Word cap was 400; do not credit content beyond the cap.

---

# Memo A  (527 words)

## Position

Build it, but as a sequence of gated slices in which the agent and Gemini work come last and are the first things cut, so a usage-limit stall still leaves a shippable warehouse, dashboard and causal result.

## Three strongest arguments

1. **The tooling is pinnable and the data is free and licensed, so the first gates are cheap.** Python 3.12, `duckdb<2`, dbt-core 1.12.6, dbt-duckdb 1.11.1 and dbt-metricflow 0.15.0 resolve together (E28). DuckDB 2.0 files are unreadable by older versions and dbt-duckdb tests 2.0 only in nightly CI (E10a, R8). The sources are open: LiteLLM (MIT, E20), LMArena (CC BY, E21), Epoch (CC BY, E22), ClickPy (E23). The OpenRouter dataset API is licensed (E25), but it needs the user's key (R11). Gate 1 is a clean `dbt build` on seeds under the pinned versions. Gate 2 is row counts plus a measured freshness for each source (R10), and the SLA is set to that measured cadence.
2. **Entity resolution is the step most likely to break the build, so it comes before any mart.** No shared ID exists across sources and closed models are covered poorly (E30, R2). Gate 3 is a hand-curated top-N crosswalk seed with uniqueness and coverage tests. The LMArena slug-to-display-name switch on 2026-10-20 and the rating-method breaks are handled here, with within-snapshot ranks (E21, R9).
3. **The centerpiece must survive the cut order.** Epoch already owns the price-decline number, so reproducing it is a ground-truth gate (E31, R3, E7). The adoption event study is the differentiator and matches the Anthropic and OpenAI postings (E3b, E17). It needs a pre-registered spec, placebo tests, a sum of `google-generativeai` and `google-genai`, and an honest null (E24, R4).

Sequence after gate 3:
- SCD2 price dimension and incremental facts (E3a), with the one-command rebuild (E7).
- Epoch reproduction.
- Event study.
- Static Parquet dashboard on Observable Framework (E29), with CI and cron (E15).
- DECISIONS.md and AI_USAGE.md (R1).

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
- DECISIONS.md and AI_USAGE.md.

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

Build it, narrowed to one real data asset and one honest causal question, because the four-slice pitch reads as a keyword checklist an AI-built repo cannot defend under probing.

## Three strongest arguments

1. **The price panel is what lands.** A daily price history back to 2023, rebuilt from LiteLLM git history, is something nobody publishes (E20, E31). It makes SCD2 necessary, not decorative, and "commit time is observed time, not effective date" is the caveat worth hearing explained (E7, E18).
2. **The headline metric invites the obvious attack.** "Price per Arena-Elo point" treats a relative, method-broken score as a ratio scale (E21, R9). "Elo is relative" was the first critique of similar trackers (E7). Use within-snapshot rank tiers, and reproduce Epoch's ~13×/yr as the ground-truth check (E31).
3. **Breadth is a liability.** SCD2, contracts, MetricFlow, an agent, evals and synthetic control mirror job-post keywords (E3a, E3c, E19). Reviewers already see AI-built portfolios, worry about authenticity (E5a), and interview without AI (E5b, E5c, E16). Every component is a question to answer cold. The shared core is SQL, modeling and one-definition metrics (E1): go deep there.

## Key risk

The walkthrough. Asked the grain of the price fact, why SCD2 rows have gaps, why `openai` downloads are inflated, or why clustered launches confound the study (E24, R4), the candidate cannot answer. A polished repo with a weak defense scores below no repo (R1). Also: four half-finished slices give no signal (R6).

## What would change my mind

- The event study survives placebos with a clear effect: lead with adoption.
- Closed-model crosswalk coverage fails its test (E30, R2): ship the price panel alone.
- No AI-free walkthrough of the core marts at the first gate: shrink further.

## Recommendation

**build with changes**

**Keep:** LiteLLM price panel with SCD2 and declared grain; crosswalk coverage tests; daily CI cron showing measured freshness (R10); Epoch reproduction; one decision memo; static Observable dashboard on Parquet (E29).

**Cut:** price-per-Elo-point; the live chat agent (Gemini spend, expiry; R7, R12); synthetic control (keep a placebo-tested event study); the tool list atop the README.

**Add:** README's first three lines: the question, one number with an interval, one chart with a "last refreshed" stamp. A caveats section. DECISIONS.md with defensible tradeoffs. Honest AI_USAGE.md. Pre-registration so a null result still ships. Agent evals only as a static table, after the panel and event study ship.

---

# Memo C  (483 words)

## Position

Build it, but aim past a private portfolio piece: publish the 2023-onward daily price panel as a citable open dataset and make the adoption-response finding the headline that gets shared.

## Three strongest arguments

1. **The panel is the only asset nobody else publishes.** Artificial Analysis retired its history API, Epoch updates per paper, and llmpricing and llm-prices keep no real price history (E31). A reproducible daily panel rebuilt from LiteLLM git history (E20) under MIT, joined to CC BY Arena (E21), Epoch (E22) and OpenRouter rankings (E25), is a dataset people cite and fork. A Parquet release with a dataset card and attribution (R5) gives the repo a life beyond a hiring screen.
2. **Reproducing Epoch's ~13x/yr number before extending it earns credibility with a skeptical audience.** E7 says praised projects pair one surprising number with a ground-truth check. Matching Epoch (E31) takes the "Elo is relative" critique off the table (R9). The shareable headline is then the new result: whether price cuts and launches move SDK downloads (E24, E23). A well-controlled null or a small effect with placebo tests (R4) is still a post worth forwarding, because it is honest and nobody else has it.
3. **The evaluated agent is the one slice that matches multiple live postings.** The semantic layer plus the eval suite against raw text-to-SQL (E11) maps to E3a, E3c, E19 and E3d. Most new-grad portfolios cannot show this. Ship it as a static, pre-computed eval report with failure cases, not a live endpoint. That stays inside the $0 and Gemini-cap limits (R7, R12) and nothing expires.

## Key risk

Reaching for a public dataset and a causal claim on top of a thin, noisy proxy (E24). If the adoption effect is unidentified and the crosswalk is leaky (R2, E30), the project looks overreaching. Authenticity is the second risk: the author must be able to defend every number live (R1, E5).

## What would change my mind

- The top-N crosswalk fails coverage tests on closed models (E30), so the panel is untrustworthy.
- The Arena rating-method breaks (E21) leave too little comparable history to support any adoption story.
- Event-study placebos show launches are confounded beyond repair, leaving no adoption result to headline.

## Recommendation

**build with changes**

**Keep**
- Price panel, entity crosswalk with coverage tests, Epoch ground-truth check, adoption event study, semantic layer and agent eval, pinned stack (E28), static Parquet dashboard (E29).
- DECISIONS.md and AI_USAGE.md (R1).

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

As scoped, this ships a wide, AI-built repo whose headline is either Epoch's number or a confounded null, and the candidate cannot defend it without AI.

## Three strongest arguments

1. **The new centerpiece has no identification.** After R3/E31 the story is adoption, where data is weakest: PyPI is uv/CI-dominated, about 83% US, `openai` inflated by `litellm`, Google's SDK split in two (E24). Event dates are LiteLLM commit times, not effective dates (E20), and launches cluster (R4). Downloads are provider-level, cuts model-level, and every provider is treated: synthetic control has no donor pool. Expect a null or an artifact that E3b/E17-style reviewers will attack.
2. **Breadth reads as AI-generated, and interviews remove the AI.** Four Claude-written slices fit the profile managers already distrust (E5a). E5b, E5c and E16 put the candidate in live, no-AI sessions where every slice is a probe surface (R1). Analyst and DE postings treat AI as preferred, not core (E2), so the agent slice signals the wrong role.
3. **The measurements are softer than the claims.** Arena scores break three times plus a rename (E21), so "price per Elo point" over time is the "Elo is relative" failure E7 cites (R9). Closed models need a hand-curated crosswalk (E30, R2). The agent eval re-runs a vendor benchmark (E11) on paid, rising-price Gemini calls (E27, R7). Each compounds R6.

## Key risk

A polished, shallow repo becomes negative signal: the first interviewer asking "why is this causal?" or "rewrite this mart without AI" ends the conversation.

## What would change my mind

- A pre-registered PyPI placebo that does not fire, over enough verified, non-clustered price-cut dates.
- Crosswalk coverage tests passing for top-N closed models.
- The candidate passing a no-AI grilling on core SQL and the identification choice.
- Primary evidence that managers reward this project type.

## Recommendation

**build with changes**

- **Keep:** the DE slice (marts, SCD2 price dimension from LiteLLM git history, tests, contracts, CI) (E1, E3a, E19); one analyst number on within-snapshot ranks; Epoch reproduction as ground truth; DECISIONS.md, AI_USAGE.md, hand-rewritten core SQL.
- **Cut:** the agent and semantic-layer eval; synthetic control; Elo comparisons across method breaks; the "daily" claim until cadence is measured (R10).
- **Add, as ordered gates:** crosswalk coverage test; event-date audit against provider announcements; pre-registered descriptive event study allowed to publish a null; no-AI defense drill. A failed gate stops scope; ship what passed.

---

# Memo E  (397 words)

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
