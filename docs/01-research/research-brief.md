# Research Brief: LLM Market Observatory

**Stage:** 01 Research (Bloom-style). **Date:** 2026-11-10. **Status:** v1, verification pass appended below.
**Raw reports:** `reports/01-hiring-bar.md`, `reports/02-landscape-datasets.md`, `reports/03-method-and-stack.md`, `reports/04-verification.md`.

## Decision question
Should a new-grad AI-engineering/evals candidate targeting **Product Analyst, Data Engineer (analytics), and Product Data Scientist** roles at FAANG and top AI startups build the **LLM Market Observatory** this week, fully AI-assisted? Or pivot to (B) Arena preference lab or (C) synthetic AI-app analytics + A/B? What scope survives?

## Candidate and constraints
- **Candidate:** new grad (UC Davis), background in AI engineering and LLM evals, aiming for product-facing data roles. One project must flex across Product Analyst, DE (analytics), and Product DS.
- **Deadline:** end of this week, Sun 2026-11-15.
- **Build mode:** the entire project is implemented, tested, and documented by AI (Claude Code primarily). The candidate works on it full-time. The binding constraint is Claude usage limits (5-hour session windows plus a weekly cap), not the candidate's hours. Plans state order and gates, never hour estimates.
- **Budget:** $0 tooling. The one exception is the candidate's own Gemini API credits, which are real money: every call must be worth it, verified, and capped.
- **Output:** a public GitHub repo plus a static dashboard. Nothing may expire before recruiters look.

## The idea under test
A daily-refreshing warehouse that answers: **"What does LLM quality cost, how fast is it falling, and does it move developer adoption?"**
- **Analyst slice:** price per Arena-Elo point by tier, open vs closed gap, lag from launch to first price cut. Dashboard plus decision memo.
- **DE slice:** ingestion -> staging -> marts with declared grain, an SCD2 price dimension, incremental facts, tests and contracts, freshness SLA, CI plus daily cron.
- **Product DS slice:** event study or synthetic control. Do model launches and price cuts lift PyPI downloads of provider SDKs?
- **AI-native slice:** an "ask the observatory" agent over a MetricFlow semantic layer, plus an eval suite comparing semantic-layer access with raw text-to-SQL.

## Evidence table
Confidence: H = primary source, read directly. M = mirror, vendor-run survey, or hand tally. L = secondary or opinion.

### Hiring signals

| ID | Claim | Source | Date | Conf |
|---|---|---|---|---|
| E1 | Across 42 postings, all four role flavors share SQL, data modeling and one-definition metrics. Product DS postings: experimentation 11/12, causal 8/12, LLM/AI 8/12 (evals 4/12). | `reports/01-hiring-bar.md` (42 postings, tallied by hand, ±1) | 2025-26 | M |
| E2 | Meta DE Product Analytics asks for SQL/ETL/modeling, owning SLAs, logging frameworks and "cost-benefit tradeoffs". AI appears only as a preferred skill. | https://jobfound.org/job/meta-is-hiring-for-data-engineer-product-analytics-united-states-remote-usa-3-november-2026 | 2026-11-03 | M |
| E3a | Anthropic Recruiting Analytics DE asks for dimensional models with SCDs, dbt and "semantic layers for data agents". | https://job-boards.greenhouse.io/anthropic/jobs/5424111008 | 2026-09-17 | H |
| E3b | Anthropic DS Product asks for experiments and synthetic controls, plus defining core metrics. | https://job-boards.greenhouse.io/anthropic/jobs/5182605008 | 2026-08-24 | H |
| E3c | Snowflake Staff Analyst wants work built "AI-first", a verified query library and SQL-accuracy evals. | https://careers.wing.vc/companies/snowflake/jobs/75596844-staff-analyst-finance-analytics-ai | ~2026-Q1 | M |
| E3d | Google DS Search AI asks for auto-rater evaluations and "LLM-based evaluation and causal inference". | https://jobs.anitab.org/companies/google-2-6e248a84-5b9b-4601-aff7-7c2e9e285b9c/jobs/98500058-data-scientist-product-search-ai-experiences | 2026-10-30 | M |
| E4 | dbt State of AE 2026 (n=363): 72% prioritize AI-assisted coding vs 24% AI testing/observability. 71% fear hallucinated or incorrect data reaching stakeholders. | https://www.getdbt.com/blog/new-dbt-labs-report-finds-ai-driven-acceleration-is-outpacing-trust-and-governance | 2026-04-14 | M (vendor) |
| E5a | 29% of US hiring managers have received AI-generated portfolio projects, and 86% expect verification to get harder. The concern is authenticity, not AI use. | https://resumegenius.com/blog/job-hunting/ai-impact-on-hiring-2026 | 2026-07-14 | L |
| E5b | 62% of engineering leaders prohibit AI in technical interviews. | https://karat.com/engineering-interview-trends-2026/ | 2026-01-07 | M |
| E5c | Anthropic: complete interviews without Claude unless told otherwise. | https://www.anthropic.com/candidate-ai-guidance | 2025-07-10 | H |
| E13 | Practical Data survey (n=1,101): Kimball-style modeling 27.8%, self-managed Airflow 22.9%, 82% use AI daily. | https://joereis.github.io/practical_data_data_eng_survey | 2026-02 | M |
| E14 | Stack Overflow 2025: 84% use or plan to use AI, 46% distrust its accuracy, 66% cite "almost right" answers. | https://survey.stackoverflow.co/2025/ai | 2025 | H |
| E16 | In an agency survey of 41 hiring managers, AI-skill interviews use live sessions (46%), review tasks (27%), work walkthroughs (15%) and AI-allowed take-homes with a debrief (10%). | https://www.hirewithnear.com/insights/how-to-interview-developers-for-ai-skills | 2026-10-16 | L |
| E17 | OpenAI Core Experimentation asks for CUPED, sequential testing, SRM detection and heterogeneous treatment effects. | https://jobs.glynncapital.com/companies/openai/jobs/78766751-data-scientist-core-experimentation | 2025-26 | M |
| E18 | Airbnb Senior Staff DE asks for trusted metrics, on-call for owned datasets and measuring AI unit economics. | https://careers.airbnb.com/positions/8224032 | 2026-11-10 | H |
| E19 | Perplexity AE asks for data contracts, tests, warehouse cost management and an "AI-readable" warehouse. | https://jobs.accel.com/companies/perplexity-2/jobs/68367031-member-of-data-staff-analytics-engineer | 2026-02 | M |

### Portfolio landscape

| ID | Claim | Source | Date | Conf |
|---|---|---|---|---|
| E6 | Oversaturated topics: Titanic (107k GitHub repos), Superstore (38k), Netflix (25k), NYC taxi (12.6k). All 30 DataCamp projects use static snapshots with no tests or modeling layer. | https://www.datacamp.com/blog/data-analytics-projects-all-levels ; https://api.github.com/search/repositories?q=titanic | 2026-02-27 / 2026-11-10 | H (counts) |
| E7 | Praised projects share: one surprising specific number, one-command rebuild, a refreshing artifact, written metric definitions and caveats, a ground-truth check. Weak AI-topic Show HNs were criticized because their metrics didn't mean what they claimed (e.g. "Elo is relative"). | https://toddwschneider.com/posts/analyzing-1-1-billion-nyc-taxi-and-uber-trips-with-a-vengeance/ ; https://duckdb.org/2022/10/12/modern-data-stack-in-a-box ; https://hn.algolia.com/api/v1/items/48130711 ; https://datatalksclub.github.io/podwiki/wiki/analytics-engineering-portfolio-projects/ | various | M (inference) |

### Data sources and licensing

| ID | Claim | Source | Date | Conf |
|---|---|---|---|---|
| E8a | LMArena leaderboard history: CC BY 4.0, 2.72M rows, last published 2026-11-08. | https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset | 2026-11-08 | H |
| E8b | Epoch AI datasets: CC BY, 3,700+ models. | https://epoch.ai/data | 2026-11 | H |
| E8c | PyPI downloads: CC BY 4.0 via BigQuery. ClickPy has daily aggregates. | https://docs.pypi.org/api/bigquery/ ; https://clickpy.clickhouse.com/ | 2026-11-10 | H |
| E8d | HF hub-stats: apache-2.0, updated daily. | https://huggingface.co/datasets/cfahlgren1/hub-stats | 2026-11-10 | M |
| E8e | OpenRouter terms (updated 2026-08-31) ban scraping the site. Republishing API data has no explicit grant. | https://openrouter.ai/terms | 2026-08-31 | H |

### Tooling

| ID | Claim | Source | Date | Conf |
|---|---|---|---|---|
| E9 | dbt v2 went GA 2026-09-16. dbt-core 1.12.x remains Apache 2.0 and supported. MetricFlow is Apache 2.0 from v0.209. | https://www.getdbt.com/blog/dbt-summit-2026-product-announcements ; https://docs.getdbt.com/docs/dbt-licensing ; https://github.com/dbt-labs/metricflow | 2026-09/10 | H |
| E10a | DuckDB 2.0.0 LTS (2026-10-21) writes files that versions below 2.0 cannot read. | https://duckdb.org/2026/10/21/announcing-duckdb-200 | 2026-10-21 | H |
| E10b | Elementary CLI 0.23.3 was malware. Pin 0.23.4 or later. | https://www.stepsecurity.io/blog/elementary-data-compromised-on-pypi-and-ghcr-forged-release-pushed-via-github-actions-script-injection | 2026-04-24 | H |
| E10c | BigQuery sandbox: no DML, 60-day table expiry, 1 TiB of queries a month free. | https://docs.cloud.google.com/bigquery/docs/sandbox | 2026-11-10 | H |
| E11 | dbt benchmark: semantic layer 98.2-100% vs text-to-SQL 84-90% on modeled data. Text-to-SQL fails as "plausible but incorrect". | https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026 | 2026-04-07 | M (vendor) |
| E15 | GitHub Actions standard runners are free on public repos. | https://docs.github.com/en/billing/concepts/product-billing/github-actions | 2026-11-10 | H |

### Method

| ID | Claim | Source | Date | Conf |
|---|---|---|---|---|
| E12 | Bloom's council uses five lenses (Contrarian, First principles, Expansionist, Outsider, Executor), anonymized A-E peer review and a chair verdict. Karpathy's llm-council: parallel answers -> anonymized ranking -> chairman synthesis. | https://bloom-beta.com/features ; https://github.com/karpathy/llm-council | 2026-11-10 | H |

## Competitors and alternatives
Source: `reports/04-verification.md` §10, all accessed 2026-11-10. The gap is **narrower than assumed**.

| Competitor | What it already shows | What it lacks |
|---|---|---|
| Artificial Analysis (https://artificialanalysis.ai/trends) | Cost per index task over time, output price over time at capability thresholds, open vs proprietary | No adoption angle. No downloadable history: legacy data API retired 2026-11-04, free API is a snapshot only at 10 requests/day |
| Epoch AI (https://epoch.ai/publications/the-plunging-price-of-thought) | Headline decline: about 13×/yr at fixed capability (2026-09-22); 9–900×/yr (2025-03-12) | No adoption/demand link ("no user stays permanently on the cost frontier"); updated per paper, not daily |
| sanand0/llmpricing (https://sanand0.github.io/llmpricing/, MIT) | **Closest to our idea:** Arena Elo vs price, Pareto frontier, month slider since 2023 | One representative price per model, no price history, no adoption; mixes slug and display names |
| OpenRouter rankings | Top-50 models per day by tokens since 2025-01-01 | A signal to *use*, not a causal competitor; tokens not comparable across providers |
| simonw/llm-prices | Current prices for 191 models | Only 13 dated price changes; no license file |
| tokencanopy/price (MIT) | 1,057 models × 82 hosts, refreshed every 6 h | History only since 2026-09-02; no quality join |

**What is still open (our wedge):**
1. A governed, reproducible **daily price panel back to 2023**, rebuilt from LiteLLM git history. Nobody publishes this.
2. **Adoption joined to price and quality**, studied causally around price cuts and launches.
3. A **semantic layer plus an evaluated question-answering agent** over those metrics. No competitor has either.

**Implication:** "how fast is quality-adjusted price falling" is not novel (Epoch owns it). It becomes a **ground-truth check**: reproduce Epoch's number (E7 pattern). The centerpiece shifts to **adoption response**.

## Risks
| ID | Risk | Why it matters | Early mitigation idea |
|---|---|---|---|
| R1 | Authenticity / defensibility of a fully AI-built project | E5a-c: interviewers probe without AI | DECISIONS.md, AI_USAGE.md, grilling drill, hand-rewrite of core SQL |
| R2 | Entity resolution: model names differ across sources | Wrong joins break every metric | Curated mapping seed + uniqueness/coverage tests |
| R3 | Competitor overlap on price-vs-quality charts | Weakens the "surprising number" | Differentiate on adoption/causal angle + evaluated agent |
| R4 | Weak causal identification: downloads are noisy (CI), launches cluster | Product DS reviewers will attack it | Pre-register method, placebo tests, honest null results |
| R5 | Licensing / terms | Public repo republishes data | Use CC BY / Apache / MIT sources only, with attribution |
| R6 | Scope vs Claude usage limits | Unfinished project = no signal | Milestones, cut order, STATUS.md handoff |
| R7 | Gemini spend and accuracy | Real money; the user wants zero waste | Offline-first harness, cache, caps, smoke test, ledger |
| R8 | Tool churn (DuckDB 2.0, dbt v2) | Version mismatch breaks the build | Pin versions; verify compatibility first |
| R9 | Misreading Arena Elo (relative, category-dependent) | E7: the main critique of trackers | Use within-snapshot ranks/percentiles, documented caveats |
| R10 | Source cadence unknown (Arena history) | "Daily refresh" could be a lie | Measure actual freshness; SLA set to the real cadence |

## Not verified (as of v1)
See the verification pass below. Also unverified:
- How hiring managers value this specific project type: no primary source exists.
- Stripe and Ramp live postings.
- Meta's official DE prep pages.

## Verification pass (from `reports/04-verification.md`, endpoints called live 2026-11-10)
| ID | Claim | Source | Conf |
|---|---|---|---|
| E20 | LiteLLM `model_prices_and_context_window.json`: MIT (outside `enterprise/`), 5,870 entries, 2,940 commits since 2023-09-06. The first commit was a rename, so use `--follow`. Retired models are deleted from today's file, so history requires git. Commit time = *observed* time, not the provider's effective date. | https://github.com/BerriAI/litellm | H |
| E21 | LMArena leaderboard-dataset: 23 configs, parquet, CC BY 4.0, text history 2023-05-08 to 2026-11-09. Names switched from slugs to display names on 2026-10-20. Rating method changed Jan 2024, May 2025 and Jul 2025, so scores are not comparable across those breaks. The 140k vote set is static (Apr–Jul 2025). | https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset | H |
| E22 | Epoch AI: `epoch.ai/data/*.csv`, daily, CC BY, 3,708 models, 57 columns. | https://epoch.ai/data | H |
| E23 | ClickPy public SQL works live: host `sql-clickhouse.clickhouse.com`, user `play`, table `pypi.pypi_downloads_per_day`, with installer and country filters. pypistats keeps only about 217 days. | `04-verification.md` §4 | H |
| E24 | PyPI is a noisy adoption proxy: dominated by uv and CI, weekends about −40%, about 83% US. `openai` is inflated as a `litellm` dependency. Google migrated from `google-generativeai` to `google-genai`, so the two must be summed. | `04-verification.md` §4 | M |
| E25 | OpenRouter `GET /api/v1/datasets/rankings-daily`: top-50 models/day by tokens since 2025-01-01, **CC BY 4.0** with citation, free API key, 30 requests/min and 500/day. Resolves E8e: scraping the site is banned, but this official dataset API is licensed. | https://openrouter.ai/docs/api/api-reference/datasets/get-rankings-daily.md | H |
| E26 | HF hub-stats is a snapshot only; history would need about 1.7 GB per daily revision. **Drop it as a history source.** | `04-verification.md` §5 | H |
| E27 | Gemini, confirmed: prices, JSON Schema structured output, `count_tokens`, SDK `google-genai` 3.1.0. **Free-tier prompts are used for training.** EEA/UK requires the paid tier. Deprecated model IDs auto-route to other models from 2026-12-01. Free-tier rate limits are not published (AI Studio only). Cheap-tier list prices are rising: Flash-Lite went $0.10/$0.40 → $0.25/$1.50 → $0.30/$2.50. | https://ai.google.dev/gemini-api/docs/pricing | H |
| E28 | `dbt-core` 1.12.6 + `dbt-duckdb` 1.11.1 + `dbt-metricflow` 0.15.0 resolve together with uv. dbt-duckdb tests DuckDB 2.0 only in nightly pre-release CI, so **pin `duckdb<2`**, Python 3.12. | PyPI JSON | H |
| E29 | Evidence Core's current docs describe a server with live connectors; static GitHub Pages deploy is not confirmed. **Observable Framework** builds static sites deployable to Pages and bundles DuckDB-WASM 1.1.1, so ship Parquet files, not `.duckdb`. | `04-verification.md` §8 | M |
| E30 | Entity resolution is hard: no shared ID across sources. Bridges: OpenRouter `/api/v1/models` (469 models, `canonical_slug`, `hugging_face_id`) and Epoch's HF developer id. Open-weight models are covered well, closed models poorly, so a hand-curated crosswalk seed is required. | `04-verification.md` §9 | H |
| E31 | Competitor gap: see the Competitors section above. | `04-verification.md` §10 | H |

### Risk updates after verification
- **R2 confirmed high (E30):** scope the crosswalk to a top-N model set and test coverage explicitly.
- **R3 confirmed (E31):** lead with adoption; Epoch's number becomes the ground-truth check.
- **R9 widened (E21):** method breaks plus the 2026-10-20 rename. Use within-snapshot ranks or split the series.
- **R11 (new):** OpenRouter needs a free API key (an account action by the user). Tokens are not comparable across providers, so use within-provider share or rank.
- **R12 (new, E27):** Gemini free tier trains on prompts (fine for public-data questions, but disclose it). Pin a non-deprecated model ID. Rising cheap-tier prices mean the cost cap must use live prices.

### Still not verified
- BigQuery bytes scanned per package-month.
- `dbt build` / `mf query` runtime on these versions.
- Gemini free-tier rate-limit numbers.
- Evidence Core launch date.
