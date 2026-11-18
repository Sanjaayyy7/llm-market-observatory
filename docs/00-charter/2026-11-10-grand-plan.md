# Grand Plan: LLM Market Observatory (validate -> spec -> build)

## Context
ONE public data product, built entirely with AI (Claude Code primarily), for analysts tracking LLM API list prices, developers choosing providers, and researchers, spanning:
- Analyst work: price vs quality, decision memo
- Analytics data engineering: governed marts, tests, freshness
- Causal analysis of adoption

Validation must mirror Bloom (bloom-beta.com): **Research -> Debate (council) -> Ship (PRD + design.md)**, evidence-first, auditable trail. Deadline: end of this week (Sun 2026-11-15).

## User decisions
- Lead idea: **LLM Market Observatory**. Pivot options for council: (B) Arena preference lab, (C) synthetic AI-app analytics + A/B.
- LLM API: user's **Gemini API credits** (real money). Must be worth it, working, accurate, error-free.
- Effort: all-in, all day, Claude Code only. **No hour/time estimates anywhere.** Binding constraint = Claude usage limits (5-hr session + weekly).

## My calls (flagged so user can override)
- $0 tooling apart from Gemini; nothing that expires after publication. Local-first + one public GitHub repo at `~/projects/llm-market-observatory/`.
- Council memos split across opus / sonnet / fable subagents for model diversity (Bloom uses lenses; Karpathy uses models; we get both).
- Skipped a separate Plan-agent pass: the council *is* the adversarial review, and it saves usage.
- PRD = what/why with evidence; `design.md` = architecture, data model, metric definitions, plus dashboard visual/UX direction (Bloom's design.md scope).

## Lead idea (draft, council will attack it)
Daily-refreshing warehouse answering: **"What does model quality cost, how fast is it falling, and does it move developer adoption?"**
- **Analyst:** price per Arena-Elo point by tier, open vs closed gap, launch -> price-cut lag. Dashboard + decision memo with caveats (Elo is relative).
- **DE:** ingestion -> staging -> marts with declared grain, SCD2 price dimension, incremental facts, dbt tests/unit tests/contracts, freshness SLA, CI + daily cron, one-command rebuild.
- **Causal:** event study / synthetic control. Do launches and price cuts lift PyPI downloads of provider SDKs (anthropic, openai, google-genai, mistralai)? Caveat: CI-download noise.
- **AI-native (user's edge):** "ask the observatory" agent over the MetricFlow semantic layer, plus an eval suite (gold answers from `mf query`). Compares semantic-layer vs raw text-to-SQL accuracy and builds a failure taxonomy.
- **Sources** (verify in M0): LMArena leaderboard history (CC BY), Epoch AI models (CC BY), PyPI downloads (CC BY 4.0; ClickPy or BigQuery sandbox, no billing), HF hub-stats (apache-2.0), price history candidate LiteLLM price JSON + git history (MIT, VERIFY). Avoid OpenRouter as primary (terms).
- **Stack** (design.md locks it): Python + uv, DuckDB pinned 1.5.x (2.0 compat with dbt-duckdb unverified), dbt-core 1.12 + dbt-duckdb, MetricFlow local, GitHub Actions (CI + cron), static dashboard on GitHub Pages (Evidence Core vs Observable Framework, decided by spike), Gemini for the agent.

## Evidence base (research done 2026-11-10; becomes E-IDs in the brief)
- **E4** dbt State of AE 2026: 72% prioritize AI coding vs 24% AI testing; 71% fear hallucinated numbers.
- **E6** Overdone topics: Titanic, Netflix, Superstore, Airbnb, Spotify, NYC taxi. DataCamp's list is all static snapshots.
- **E8** Licensing per source (see Sources above).
- **E9** dbt v2 GA 2026-09-16; dbt-core 1.12.6 Apache; MetricFlow Apache.
- **E10** Traps: DuckDB 2.0 file compat, Elementary 0.23.3 malware (pin >=0.23.4), BigQuery sandbox no DML.
- **E11** dbt benchmark: semantic layer 98-100% vs text-to-SQL 84-90% (vendor-authored).
- **E12** Bloom lenses and template.

## Milestones (ordered; no time estimates; each ends with commit + `docs/STATUS.md` handoff)

### M0 Validate (Bloom replica)
1. **Research brief** `docs/validation/research-brief.md`.
   - Evidence table (E-ID | claim | URL | date | confidence), competitors (OSS Insight, Arena Elo trackers, Artificial Analysis-style sites), risks, not-verified list.
   - First verify the open items: LiteLLM license/history, ClickPy access, Arena history schema/cadence, Epoch CSV, Gemini current models/pricing/free tier (ai.google.dev).
2. **Council** `docs/validation/council/`.
   - Decision question: "Build the Observatory as scoped this week with full AI assistance, or pivot to B/C? What scope survives?"
   - 5 lens memos in parallel, <=400 words each: Contrarian, First principles, Expansionist, Outsider (non-expert reader), Executor. Format: position, 3 args, key risk, what changes my mind, recommendation.
   - Shuffle and relabel A-E; keep the map private in `map.json`.
   - 5 blind reviews: per-memo strengths/weaknesses, blind spots, `FINAL RANKING`, support/mixed/reject. Self-rank dropped before averaging.
   - Chair verdict: go/pivot/no-go, agreement, divergence, missing, next actions, confidence.
3. **Ship.**
   - `docs/PRD.md`: problem + evidence, users (analysts, developers choosing providers, researchers), explicit cuts, requirements each citing an E-ID, success metrics, risks.
   - `docs/design.md`: architecture, data model + grain, metric definitions, eval design, Gemini guardrails, dashboard visual/UX direction, what's left to the builder.
   - Builder-check subagent reads it, then one round of "theirs" questions goes to the user.
4. **HARD GATE:** user approves `design.md`. Then superpowers:writing-plans -> `docs/plans/` build plan with TDD tasks.

### Build (executed from the writing-plans output)
- **M1** Repo scaffold, source fetchers, raw -> staging, `make build` from a clean clone.
- **M2** Marts (SCD2 price dim, facts), dbt tests + unit tests + contracts, GitHub Actions CI.
- **M3** MetricFlow metrics, descriptive analyses, causal analysis (event study first; synthetic control if the council keeps it).
- **M4** Static dashboard on GitHub Pages + daily refresh cron.
- **M5** Agent + eval suite (Gemini, guarded; see below).
- **M6** Docs kit: `README.md` (one surprising number up top), `DECISIONS.md`, decision memo.

**Cut order if usage limits bite** (council may reorder): synthetic control -> HF source -> dashboard polish -> daily cron (keep manual refresh). The core slice M1-M3 + M5 evals + M6 is never cut.

## Gemini guardrails (real money)
- **Honest bar:** the harness, tests and spend controls will be error-free and verified. The *LLM's answers* will not be 100% accurate; measuring that accuracy is what the eval suite does and what we report.
- **Free tier first;** credits only if free-tier limits block the run. Re-verify models, prices and limits on ai.google.dev at M5. Pin the exact model version, temperature 0.
- **Offline first:** the harness and graders are built and tested against a fake LLM / recorded fixtures, so all tests pass with zero API calls.
- **Before any batch:** a dry-run cost estimate (tokens x price), then a 1-question smoke test checking parse + grade. User gives explicit go before the first paid call.
- **Content-hash response cache:** never pay twice for the same call.
- **Limits:** hard cap on calls/tokens per run; fail fast on the first unexpected error; at most 2 retries with backoff, on 429 only.
- **Spend ledger:** `evals/ledger.csv` records model, tokens and estimated cost per call.
- **Key handling:** API key only in env / `.env` (gitignored), never logged or committed; secret scan before every push.

## Usage-limit resilience
- `docs/STATUS.md` is updated at every milestone: done, next, blockers, and a resume prompt, so any fresh session continues without re-research.
- Small milestones, a commit after each. Subagents only where Bloom requires them (council) or for parallel independent build tasks.
- Research is done once and cited from the brief, never redone.

## Verification
- M0: every PRD requirement maps to an E-ID; the council folder holds 5 memos, `map.json`, 5 reviews and the chair verdict; builder-check is resolved.
- Build:
  - `git clone` -> `make build` succeeds on a clean machine.
  - `dbt build` shows all tests passing; CI is green on a PR.
  - Freshness check passes after a cron run; the dashboard loads from the Pages URL.
- Evals:
  - Offline test suite passes with zero API calls.
  - Smoke test passes before the batch.
  - Ledger total stays at or under the agreed cap.
  - Results table reports accuracy with failure examples.
- **Outward actions need explicit user OK at the time:** creating or pushing the public GitHub repo (GitHub MCP is down; use the `gh` CLI), and the first paid Gemini call.
