<!-- Raw research-agent report, captured verbatim 2026-11-10. Source of E-IDs in ../research-brief.md -->

# Findings report: Bloom's council method and the 2026 $0 analytics-engineering stack (researched 2026-11-10)

## Part 1: Bloom's Research → Debate → Ship method

**What Bloom publishes.** Bloom is an early-access beta. Its pages carry no dated changelog, and all of them were accessed 2026-11-10.

- **Research.** The output is "Demand, competition, risk — sourced and written so you can defend it" ([home](https://bloom-beta.com/)). The features page says "Live sources, competitors, and market context roll into one brief you can defend — not a bookmark graveyard." Deep Research is "Powered by Tavily." Intake uses "AI-generated MCQs", then a restate-and-confirm step: "Does this sound right?" ([features](https://bloom-beta.com/features)).
- **Debate.** The pipeline has three fixed stages: Independent perspectives, Peer review, and Chair synthesis.
  - "five advisor lenses each produce a memo in parallel; those memos are anonymized (A–E) for peer review."
  - Each lens ranks the full set, flags blind spots and gives a lean of support, mixed or reject.
  - "a final chair pass reads the attributed memos plus all reviews and emits one structured verdict." The verdict covers where the group agrees, where it diverges, what is missing, and what to do next.
  - **Lens names:** Contrarian, First principles, Expansionist, Outsider, Executor.
  - **Stated rationale:** the design follows "the LLM Council idea… Parallel generation plus blind cross-review dampens sycophancy." The trail is auditable "so 'we ran it through council' refers to a specific process, not a vibe" ([features](https://bloom-beta.com/features)).
- **Ship.** The output is a "Design spec + PRD tied to what you proved — or a deliberate pivot" ([home](https://bloom-beta.com/)).
  - PRD: "Every feature traces back to evidence."
  - Design.md: "Visual direction, component guidelines, and UX patterns generated from your brief" ([features](https://bloom-beta.com/features)).
  - The /research page sets the PRD bar: another builder can scope it without guesswork. It must tie the problem to evidence, show a real user context, make explicit scope cuts, define observable success, and name risks. It also describes an evidence ladder: named hypothesis → observed behavior → comparison with existing tools → costly commitment ([research](https://bloom-beta.com/research)).
- **Pricing.**
  - Free: 1 project, 300k Gemini tokens a month, 8 deep-research runs a month, 2 source files.
  - PRD and Design.md generation are **Pro-only**. Pro costs $29 a month ([pricing](https://bloom-beta.com/pricing)).

**Karpathy's llm-council.** Released around 2025-11-22 ([VentureBeat, 2025-11-26](https://venturebeat.com/ai/a-weekend-vibe-code-hack-by-andrej-karpathy-quietly-sketches-the-missing)).

- **Stage 1.** The raw user query goes, with no role prompt, in parallel via OpenRouter to `openai/gpt-5.1`, `google/gemini-3-pro-preview`, `anthropic/claude-sonnet-4.5` and `x-ai/grok-4` ([config.py](https://github.com/karpathy/llm-council/blob/master/backend/config.py)).
- **Stage 2.** Answers are relabeled "Response A/B/C…". Each model must "evaluate each response individually", then output a strict `FINAL RANKING:` numbered list, which is parsed by regex. Rankings are aggregated as average rank, where lower is better. Self-ranking is **not** excluded ([council.py](https://github.com/karpathy/llm-council/blob/master/backend/council.py)).
- **Stage 3.** The Chairman (Gemini 3 Pro preview) gets the question, the Stage 1 answers *with model names*, and the Stage 2 rankings. It is not given the label-to-model map, and it writes "the council's collective wisdom" (council.py).
- **Rationale.**
  - Karpathy built it for reading books alongside several LLMs and seeing their "cross-opinions". Anonymization exists "so that the LLM can't play favorites."
  - The README says it is "99% vibe coded" and unsupported ([README](https://github.com/karpathy/llm-council)).
  - His observation: "the models are surprisingly willing to select another LLM's response as superior to their own." The council rated GPT-5.1 highest, and Karpathy disagreed with that ranking (VentureBeat).
- **How Bloom differs.** Bloom gets diversity from *role lenses*, not different models. It adds blind spots and a lean to each review, and it ends in a structured verdict instead of a single answer.

### Reusable manual council template (my synthesis of both)

1. **Frame (main agent).** Write one decision question, a scope boundary and any hard constraints. For your project: "Which $0 stack and scope best serve the product in 7 days?"
2. **Research sprint (one subagent).** Produce `research-brief.md` with these sections:
   - Question
   - Evidence table (claim | URL | date | confidence)
   - Competitors and alternatives
   - Risks
   - Open questions
   - Each claim cited, and a list of what was *not* verified
3. **Memos (five subagents in parallel, each sees only the brief).**
   - Lens prompts:
     - Contrarian: why this fails.
     - First principles: rebuild from constraints.
     - Expansionist: bigger upside.
     - Outsider: a non-expert's read.
     - Executor: the day-by-day plan and what to cut.
   - Memo format (at most 400 words): Position · 3 strongest arguments · Key risk · What would change my mind · Recommendation.
4. **Anonymize (main agent).** Shuffle the memos, relabel them A–E, and keep the mapping private.
5. **Peer review (five subagents in parallel, each sees all A–E memos).**
   - Per memo: strengths and weaknesses.
   - Across memos: blind spots none of them addressed.
   - `FINAL RANKING:` 1–5.
   - A lean of support, mixed or reject on the decision.
   - Drop each reviewer's rank of its own memo before averaging, which fixes Karpathy's self-ranking gap.
6. **Chair (one subagent).** Input: the de-anonymized memos, all reviews and the average-rank table. Output: Verdict (go / pivot / no-go) · Where the council agrees · Where it diverges · What's missing · Next actions · Confidence.
7. **Ship.**
   - `PRD.md`: Problem + evidence · User and context · Scope / explicit cuts · Requirements, each with an evidence ID · Success metrics · Risks.
   - `design.md`: Visual direction · Components · UX patterns.
   - Keep the whole trail in `/council/`.

## Part 2: The 2026 analytics-engineering stack (solo, one week, $0)

### Changes since 2025 (deprecated, relicensed or acquired)

**dbt and Fivetran**
- **dbt Labs and Fivetran merged.** The deal was announced 2025-10-13 ([getdbt](https://getdbt.com/blog/dbt-labs-and-fivetran-sign-definitive-agreement-to-merge)) and closed 2026-06-01. The company operates as "Fivetran + dbt Labs", with Fraser as CEO and Handy as President ([Fivetran PR, 2026-06-01](https://www.fivetran.com/press/fivetran-dbt-labs-complete-merger-to-create-the-data-infrastructure-for-trusted-ai-agents)).
- **dbt licensing has shifted.**
  - Fusion launched under ELv2 on 2025-05-28 ([getdbt](https://www.getdbt.com/blog/new-code-new-license-understanding-the-new-license-for-the-dbt-fusion-engine)).
  - **dbt v2 went GA on 2026-09-16** and runs on a single Rust engine. Fusion and Core v2 merge into it ([dbt Summit blog, 2026-09-16](https://www.getdbt.com/blog/dbt-summit-2026-product-announcements)).
  - `pip install dbt` "is proprietary to dbt Labs" under the dbt Product Licensing Agreement but "completely free to use". `dbt-oss` is the Apache 2.0 subset. dbt v1 (formerly Core) remains Apache 2.0 and "fully supported" ([dbt licensing, updated 2026-10-23](https://docs.getdbt.com/docs/dbt-licensing)).
  - The `dbt-core` PyPI namespace "will be deprecated" long-term ([PyPI dbt-core](https://pypi.org/project/dbt-core/), latest 1.12.6 on 2026-10-14).
- **The standalone dbt State app is retired** (Sep 2026). dbt State itself is a paid feature ([release notes](https://docs.getdbt.com/docs/dbt-versions/release-notes)).

**SQLMesh and MetricFlow**
- **SQLMesh:** Fivetran acquired Tobiko Data on 2025-09-03 ([Fivetran blog](https://www.fivetran.com/blog/fivetran-acquires-tobiko-data-to-power-enterprise-grade-transformations)) and donated SQLMesh to the Linux Foundation on 2026-03-25 ([Techzine](https://www.techzine.eu/news/analytics/139955/fivetran-donates-sqlmesh-to-the-linux-foundation/)). It is still active: v0.236.4, Apache 2.0, 2026-10-22 ([PyPI](https://pypi.org/project/sqlmesh/)).
- **MetricFlow moved to Apache 2.0 from v0.209.0**, announced 2025-10-14 ([getdbt](https://www.getdbt.com/blog/dbt-labs-affirms-commitment-to-open-semantic-interchange-by-open-sourcing-metricflow); [GitHub](https://github.com/dbt-labs/metricflow)). The hosted Semantic Layer APIs still need a Starter plan or higher ([docs, 2026-09-10](https://docs.getdbt.com/docs/build/metricflow-commands)).

**Data quality**
- **Soda Core moved to ELv2** (Apache 2.0 before), announced 2026-01-27. It is still free for internal use ([Soda](https://soda.io/blog/soda-core-license-update-moving-to-elastic-license)).
- **Great Expectations split up.**
  - GX Cloud goes to FICO and is "no longer publicly available beginning June 1".
  - Fivetran becomes steward of GX Core ([GX, 2026-05-06](https://www.greatexpectations.io/blog/an-update-from-great-expectations); [Fivetran PR, 2026-05-13](https://www.fivetran.com/press/fivetran-to-become-steward-of-the-great-expectations-open-source-community-and-gx-core-project)).
- **Elementary CLI 0.23.3 was malware.** It was a supply-chain compromise via GitHub Actions on 2026-04-24. Pin version 0.23.4 or later. The dbt package was not affected ([StepSecurity](https://www.stepsecurity.io/blog/elementary-data-compromised-on-pypi-and-ghcr-forged-release-pushed-via-github-actions-script-injection); [CSA, 2026-04-29](https://labs.cloudsecurityalliance.org/research/csa-research-note-pypi-elementarydata-supply-chain-20260429/)).

**App layer**
- **Evidence:** the old open-source framework was replaced by **Evidence Core**, MIT-licensed, on 2026-08-26. A `migrate` command handles most of the move ([Evidence](https://evidence.dev/blog/evidence-core); [docs](https://docs.evidence.dev)).
- **Observable Cloud was deprecated** on 2025-04-15. Framework apps can be hosted on GitHub Pages, Netlify and similar hosts ([Observable](https://observablehq.com/release-notes/2025-04-15-deprecating-observable-cloud)). Framework activity is low: latest release v1.13.4 on "02 Mar", with no year shown ([releases](https://github.com/observablehq/framework/releases)).

**DuckDB**
- **DuckDB 2.0.0 LTS shipped on 2026-10-21.** Versions before 2.0 "cannot read database files created by DuckDB 2.0." Support for 1.4 ends 2026-11-17, and 1.5 is extended to March 2027 ([DuckDB](https://duckdb.org/2026/10/21/announcing-duckdb-200)).
- MotherDuck's docs list nothing newer than 1.5.6 ([lifecycle](https://motherduck.com/docs/troubleshooting/version-lifecycle-schedules/)). **Pin `duckdb<2` if you use MotherDuck.**

### Stack comparison table

Setup times are my estimates for a solo developer who already knows SQL and Python.

| Tool | What it does | Version · license (date) | $0 limits | Setup (est.) |
|---|---|---|---|---|
| dbt v1 / dbt v2 | SQL transforms, tests, docs | dbt-core 1.12.6, Apache ([PyPI](https://pypi.org/project/dbt-core/), 2026-10-14). `dbt` 2.0.11, proprietary but free ([PyPI](https://pypi.org/project/dbt/), 2026-11-03). DuckDB adapter is GA in v2, CLI only ([upgrade doc](https://docs.getdbt.com/docs/dbt-versions/dbt-upgrade/upgrading-to-v2), 2026-10-29) | Free locally | 1–2 h |
| SQLMesh | dbt alternative with plan/apply | 0.236.4, Apache, Linux Foundation (2026-10-22) | Free | 2–4 h |
| DuckDB | Embedded OLAP engine | 2.0.0, MIT ([PyPI](https://pypi.org/project/duckdb/), 2026-10-21) | Free | 0.5 h |
| dbt-duckdb | dbt adapter, supports MotherDuck | 1.11.1, Apache ([PyPI](https://pypi.org/project/dbt-duckdb/), 2026-10-26) | Free | Included above |
| MotherDuck Lite | Hosted DuckDB | n/a | 10 GB, 10 h Pulse compute a month, 3 users ([pricing](https://motherduck.com/product/pricing/), accessed 2026-11-10) | 0.5 h |
| BigQuery sandbox | Google's warehouse | n/a | 10 GiB lifetime storage, 1 TiB of queries a month, 60-day table expiry, **no DML or streaming**, no card needed ([docs](https://docs.cloud.google.com/bigquery/docs/sandbox), accessed 2026-11-10) | 1 h |
| Snowflake trial | Warehouse | n/a | 30 days or $400, whichever comes first, then suspended ([docs](https://docs.snowflake.com/en/user-guide/admin-trial-account)) | 1 h |
| Databricks Free Edition | Lakehouse | n/a | Serverless only, one 2X-Small SQL warehouse, 5 concurrent tasks, no commercial use ([docs](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations), 2026-10-18) | 1–2 h |
| Dagster | Asset orchestration | 1.13.29, Apache ([PyPI](https://pypi.org/project/dagster/), 2026-11-05) | Open source free. Dagster+ Solo $10/mo with 30-day trial ([pricing](https://dagster.io/pricing)) | 3–5 h |
| Airflow 3 | DAG orchestration | 3.4.0, Apache ([PyPI](https://pypi.org/project/apache-airflow/), 2026-11-06) | Free locally | 4–8 h |
| Prefect | Python orchestration | 3.9.2, Apache ([PyPI](https://pypi.org/project/prefect/), 2026-11-06) | Hobby: 2 seats, 5 deployments, 7-day history, 500 serverless minutes ([pricing](https://www.prefect.io/pricing)) | 2–3 h |
| dlt | Python ingestion | 1.32.0, Apache ([PyPI](https://pypi.org/project/dlt/), 2026-10-29) | Library is free. dltHub is paid ([pricing](https://dlthub.com/pricing)) | 1–3 h |
| MetricFlow | Semantic layer engine | Apache 2.0 from v0.209 | `mf` CLI is free locally. APIs need a paid plan (docs, 2026-09-10) | 2–4 h |
| Cube | Semantic layer | Backend Apache, client MIT ([GitHub](https://github.com/cube-js/cube)) | Cloud Free: 5 workbooks, 1,000 requests a day ([pricing](https://cube.dev/pricing)) | 3–5 h |
| Evidence Core | BI as code | MIT, launched 2026-08-26 | Self-host. Docs conflict: static site vs Docker-only ([index](https://docs.evidence.dev) vs [self-host](https://docs.evidence.dev/self-host.md)) | 2–4 h |
| Rill | Local BI on DuckDB | v0.91.1, Apache ([releases](https://github.com/rilldata/rill/releases), "03 Nov") | Developer free locally. Cloud is paid with a $250 credit ([pricing](https://www.rilldata.com/pricing)) | 1 h |
| Lightdash | BI on dbt | Open-source core | Self-host only. Cloud Pro $3,000/mo, 21-day trial ([pricing](https://www.lightdash.com/pricing)) | 3–6 h |
| Streamlit | Python app layer | Apache | Community Cloud: about 2.7 GB memory, sleeps after 12 h idle. Limits dated Feb 2024 ([docs](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app)) | 1–2 h |
| Observable Framework | Static data apps | v1.13.4 | Free hosting on GitHub Pages | 2–4 h |
| dbt data and unit tests | Logic and data quality tests | Unit tests from v1.8 ([docs](https://docs.getdbt.com/docs/build/unit-tests), 2026-09-14) | Free | 1–2 h |
| Elementary | dbt observability | CLI 0.26.1 ([releases](https://github.com/elementary-data/elementary/releases)) | Open source free | 1–2 h |
| Soda Core 4 | Checks and contracts | ELv2, 2026-01 | Free for internal use | 2 h |
| GX Core | Expectations | 1.24.1 ([changelog](https://docs.greatexpectations.io/docs/changelog), 2026-10-22) | Free | 3–5 h |
| ODCS + datacontract-cli | Data contracts | ODCS v3.2.0 (2026-09-08, per [BARC](https://barc.com/de/odcs-3-2-data-contract-standard/)). CLI MIT ([comparison](https://cli.datacontract.com/comparison)) | Free | 1–2 h |
| GitHub Actions | CI | n/a | Standard runners free on public repos. Private repos on the Free plan get $12 of compute a month ([docs](https://docs.github.com/en/billing/concepts/product-billing/github-actions)) | 1–2 h |
| dbt MCP server | Agent access to dbt | Apache ([GitHub](https://github.com/dbt-labs/dbt-mcp)) | Self-hosted works "with or without a dbt platform account". `text_to_sql` and the Semantic Layer APIs need the platform ([docs](https://docs.getdbt.com/docs/dbt-ai/about-mcp), 2026-11-05) | 1 h |

### AI in analytics: evidence

- **dbt's 2026 benchmark** (11 questions × 20 runs, 2026-04-07; [dbt](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026)):
  - On modeled data, the semantic layer reached 98.2–100% against 84–90% for text-to-SQL.
  - On the raw schema, it reached 72.7% against 64.5%.
  - "With text-to-SQL, failure looks like a plausible but incorrect answer. With the Semantic Layer, failure looks like an error message."
  - The benchmark is reproducible from `dbt-labs/dbt-llm-sl-bench`. It is vendor-authored. MotherDuck counters with about 95% on BIRD using the schema alone ([Atlan summary](https://atlan.com/know/snowflake/cortex-analyst-vs-text-to-sql/)).
- **Spider 2.0** (including Spider 2.0-DBT) is the public agent benchmark ([GitHub](https://github.com/xlang-ai/Spider2)).
- **dbt State of Analytics Engineering 2026** (n=363, 2026-04-14; [dbt](https://www.getdbt.com/blog/new-dbt-labs-report-finds-ai-driven-acceleration-is-outpacing-trust-and-governance)):
  - 72% prioritize AI-assisted coding.
  - 71% worry about hallucinated outputs.
  - Only 24% prioritize AI-assisted pipeline management.

### Recommended $0 one-week stack (two alternatives)

**A. Local-first, no accounts, nothing expires**

- **Pipeline:** dlt → DuckDB file → dbt (v1 + dbt-duckdb, or dbt v2 CLI) → MetricFlow `mf`.
- **Quality:** dbt unit and data tests, one ODCS contract checked by datacontract-cli.
- **CI:** GitHub Actions on a public repo.
- **Apps:** Observable Framework on GitHub Pages for dashboards, Streamlit Community Cloud for a "metrics agent" demo.
- **AI:** self-hosted dbt-mcp, plus a small eval set: about 20 questions, scored by exact match against `mf query` results.
- **Day plan:**
  - Days 1–2: ingest and staging.
  - Day 3: marts and tests.
  - Day 4: metrics.
  - Day 5: CI and contracts.
  - Day 6: app layer.
  - Day 7: agent, evals and README.
- Mention the dbt v2 migration in the README.

**B. Cloud-warehouse signal**

- **Pipeline:** dlt → MotherDuck Lite (pin `duckdb<2`) or BigQuery sandbox → dbt.
- **Orchestration:** Airflow 3.4 run locally. Show the DAG in a screenshot and the README.
- **Quality:** Elementary report (≥0.23.4).
- **App and CI:** Streamlit, GitHub Actions.
- **BigQuery caveat (inference):** BigQuery sandbox has no DML, so dbt incremental merges and snapshots likely fail. Use table and view materializations only.
- **Snowflake:** a 30-day trial is fine for screenshots only, since the account is suspended after 30 days.

## Where evidence is thin

- **Bloom:** no published templates for the brief, PRD or design.md sections. No lens prompts and no sample memos or verdicts. The council behavior cannot be tested without beta access.
- **dbt v2 licensing conflict:** press coverage says both editions are Apache 2.0, but the docs say `dbt` is proprietary. The PyPI classifier still says "4 - Beta" despite the GA announcement.
- **Unconfirmed points:**
  - Evidence Core: static hosting vs Docker-only.
  - Databricks: no numeric quota published.
  - Streamlit: limits date from 2024.
  - Release years not shown on the Rill, Observable and Elementary pages.
  - ODCS v3.2 date comes from a secondary source.
  - GitHub's self-hosted runner charge: postponement status after early 2026.
- **Text-to-SQL benchmarks** are vendor-authored on both sides.

---
I did not check LLM API costs for the agent demo, and those are not $0 (use a local model or recorded runs), or the Snowflake and Evidence Studio pricing details. Before you commit to MotherDuck or the BigQuery sandbox, confirm that DuckDB 2.0 works with your tools and test whether dbt incremental models run on the sandbox.