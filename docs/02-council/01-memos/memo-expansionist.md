# Memo

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
