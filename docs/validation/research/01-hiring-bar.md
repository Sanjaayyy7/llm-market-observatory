<!-- Raw research-agent report, captured verbatim 2026-11-10. Source of E-IDs in ../research-brief.md -->

# Analytics data roles at FAANG and AI/data startups: hiring expectations and portfolio signals (as of 2026-11-10)

**Method.** I read 42 postings in full (responsibilities and qualifications). "Primary" means I read the posting on the company's own Greenhouse board or through amazon.jobs' search API. "Mirror" means a VC-portfolio or job-aggregator copy of the official posting. I used mirrors for Meta, Google, Apple, Microsoft, Netflix, OpenAI, Snowflake, Perplexity, Databricks and Notion because their career sites either need JavaScript or block automated fetches. Many of the mirrored postings are now closed, but all were posted in 2025–2026.

| Company | Postings read | Roles | Source |
|---|---|---|---|
| Amazon | 14 | 10 Business Intelligence Engineer (BIE), 4 Data Engineer (DE) | primary |
| Meta | 5 | 4 DE Product Analytics, 1 Data Scientist (DS) Product Analytics | mirror |
| Anthropic | 4 | DE Product; DS Product; DS Growth; Recruiting Analytics DE | primary |
| Google, Apple, Netflix, OpenAI, Snowflake, Perplexity | 2 each | see below | mirror |
| Airbnb | 2 | Senior DS; Senior Staff DE | primary |
| Microsoft, Databricks, Notion | 1 each | DS | mirror |
| Figma, Scale AI | 1 each | Director DS; Senior Data Analyst | primary |
| Stripe, Ramp | 0 | search snippets only | — |

By role: Analytics Engineer (AE) 8, Analyst/BIE 12, analytics-focused DE 10, Product DS 12. Amazon is 14 of the 42, so the Analyst/BIE counts lean toward Amazon's stack.

---

## 1. Skills by role
Counts are the number of postings that name an item as either required or preferred.

### (1) Analytics Engineer (n=8)
- **Counts:** AI/LLM tooling 8/8, SQL 7/8, Python 7/8, metric definition 7/8, tests or quality checks 5/8, dbt 4/8, an explicitly named semantic layer 4/8, Snowflake/BigQuery/Databricks named 4/8, dimensional modeling 3/8, experimentation 2/8, Spark 1/8, Airflow 1/8.
- **Anthropic Recruiting Analytics DE:** wants dimensional models with slowly changing dimensions, dbt with BigQuery, and "semantic layers for data agents" ([Greenhouse, upd. 2026-09-17](https://job-boards.greenhouse.io/anthropic/jobs/5424111008)).
- **Netflix AE 5, Ads:** works on the Ads Metric Catalog, "the semantic layer that defines every core Ads metric once." Asks for LookML or DataJunction and Airflow or Maestro ([mirror, removed 2026-04-24](https://builtin.com/job/analytics-engineer-5-ads-reporting-metric-standards/8884265)).
- **Apple AE:** minimum qualifications include dimensional design, Spark/Presto/Trino, and comfort with AI-assisted development tools ([mirror, 2026-05-28](https://jobs.anitab.org/companies/apple/jobs/80876382-analytics-engineer-apple-services-engineering)).
- **Perplexity AE:** asks for dbt patterns, data contracts, tests, warehouse cost management, and making the warehouse "AI-readable" ([mirror, 2026-02](https://jobs.accel.com/companies/perplexity-2/jobs/68367031-member-of-data-staff-analytics-engineer)).
- **OpenAI AE GTM:** names no dbt. Wants people who can "use AI tools to move faster without creating brittle systems" ([mirror, 2026-08-27](https://jobs.thrivecap.com/companies/openai/jobs/91350390-analytics-engineer-gtm)).
- **Pattern:** startups name dbt, while FAANG AE postings describe internal stacks. The constant across both is modeling plus metric governance.

### (2) Data/Product Analyst and BIE (n=12)
- **Counts:** SQL 12/12, a BI tool 11/12, data modeling or ETL about 10/12, Python about 10/12, GenAI 5/12, dbt 2/12, experimentation 1/12.
- **Amazon BIE template:** Redshift, data modeling/warehousing/ETL, and QuickSight or Tableau. GenAI shows up as a preferred skill: "determining when and how to apply GenAI tools and evaluating their outputs" ([amazon.jobs, 2026-11-10](https://www.amazon.jobs/en/jobs/10600727/business-intelligence-engineer-prime-video-partner-experience-supply-chain-analytics)). One posting makes it a basic qualification: "building AI-based tools for non-technical executives" ([amazon.jobs, 2026-10-29](https://www.amazon.jobs/en/jobs/10592915/senior-business-intelligence-engineer-north-america-supply-chain-execution-strategy)).
- **Scale AI Senior Data Analyst:** "Own data quality," set "centralized metric definitions," use dbt ([Greenhouse, upd. 2026-11-05](https://job-boards.greenhouse.io/scaleai/jobs/4729899005)).
- **Snowflake Staff Analyst:** "Every deliverable … built AI-first." Requires daily use of an LLM coding assistant as your main development tool, and evaluating how accurately it generates SQL ([mirror, ~early 2026](https://careers.wing.vc/companies/snowflake/jobs/75596844-staff-analyst-finance-analytics-ai)).

### (3) Data Engineer, analytics-focused (n=10)
- **Counts:** SQL 10/10, data modeling 10/10, ETL 10/10, data quality 10/10, SLAs 7/10, AI 7/10, dashboards 5/10, cost tradeoffs 4/10, Python named about 6/10 (the rest say "a programming language"), Airflow 2/10, Spark 2/10, dbt 1/10.
- **Meta DE Product Analytics:** minimum is 4+ or 7+ years of "SQL, ETL, data modeling, and at least one programming language." Duties include logging frameworks, owning SLAs, privacy-based security models, and "design and operational cost-benefit tradeoffs." AI appears only under preferred: "integrate AI tools to optimize/redesign workflows and drive measurable impact" and "prompt/context engineering, agent orchestration" ([mirror, 2026-11-03](https://jobfound.org/job/meta-is-hiring-for-data-engineer-product-analytics-united-states-remote-usa-3-november-2026); [mirror, 2026-10-30](https://zapply.jobs/jobs/cfbd4ec5-a6c9-41b6-b51f-33b2ba6c2a9b/)).
- **Meta interview loop (secondary, candidate reports):** one product case moves through product sense, data modeling, SQL and Python, and Kimball-style prep is common ([tryexponent, undated](https://www.tryexponent.com/guides/meta-data-engineer-interview)). I could not retrieve Meta's official prep pages.
- **Anthropic DE Product:** builds dbt pipelines that turn raw logs into canonical datasets, with Airflow, GitHub, Hex and SLAs. Wants AI-driven productivity "without sacrificing the quality" ([Greenhouse, upd. 2026-10-19](https://job-boards.greenhouse.io/anthropic/jobs/5448481008)).
- **Airbnb Senior Staff DE:** dimensional models, trusted metrics, Minerva, on-call for owned datasets, and measuring AI unit economics ([Greenhouse, upd. 2026-11-10](https://careers.airbnb.com/positions/8224032)).

### (4) Product Data Scientist (n=12)
- **Counts:** Python 11/12, experimentation/A-B testing 11/12, metric frameworks about 11/12, SQL 10/12, causal inference 8/12, LLM/AI 8/12 (LLM evals specifically 4/12), Spark 3/12, dbt 0/12.
- **Anthropic DS Product:** experiments and synthetic controls, plus defining core metrics ([Greenhouse, upd. 2026-08-24](https://job-boards.greenhouse.io/anthropic/jobs/5182605008)).
- **Anthropic DS Growth (preferred):** "using coding agents in your own analytical workflow" ([Greenhouse, upd. 2026-11-10](https://job-boards.greenhouse.io/anthropic/jobs/5161402008)).
- **OpenAI Core Experimentation:** CUPED, sequential testing, sample-ratio-mismatch (SRM) detection, and heterogeneous treatment effects ([mirror, 6+ months old](https://jobs.glynncapital.com/companies/openai/jobs/78766751-data-scientist-core-experimentation)).
- **Google DS, Search AI:** metrics for conversational AI (task completion, trust, satisfaction), "auto-rater evaluations," and "LLM-based evaluation and causal inference" ([mirror, 2026-10-30](https://jobs.anitab.org/companies/google-2-6e248a84-5b9b-4601-aff7-7c2e9e285b9c/jobs/98500058-data-scientist-product-search-ai-experiences)).

### Survey context
- **Practical Data 2026 State of Data Engineering (n=1,101):** Kimball-style dimensional 27.8%, mixed approaches 36.8%, semantic models 5.4%. Self-managed Airflow 22.9%, Dagster 6.2%. 82% use AI daily or more ([Joe Reis, 2026-02](https://joereis.github.io/practical_data_data_eng_survey)).
- **March pulse survey (n=194):** Claude is the most-used AI tool at 49%. 49% expect data modeling and semantic layers to matter most by 2027 ([Substack, 2026-03-28](https://joereis.substack.com/p/ai-is-here-but-the-hard-parts-havent)).
- **Stack Overflow 2025:** 84% use or plan to use AI, 46% distrust its accuracy, and 66% cite answers that are "almost right, but not quite" ([survey, 2025](https://survey.stackoverflow.co/2025/ai)).

---

## 2. What "production-grade" means in these postings
- **Tests and CI:** dbt "testing frameworks, CI/CD" ([Snowflake mirror, removed 2026-06-03](https://builtin.com/job/senior-data-analytics-engineer/9076392)). Tests, data contracts and review processes ([Perplexity, 2026-02](https://jobs.accel.com/companies/perplexity-2/jobs/68367031-member-of-data-staff-analytics-engineer)). Work that is "clear, tested, and maintainable" ([OpenAI, 2026-08-27](https://jobs.thrivecap.com/companies/openai/jobs/91350390-analytics-engineer-gtm)). "testing, code review, and deployment" ([Databricks DS, 2026-05-28](https://jobs.thrivecap.com/companies/databricks/jobs/80737981-senior-data-scientist)).
- **Docs, lineage and access:** "documentation, lineage tracking, quality monitoring," plus row- and column-level controls ([Anthropic, 2026-09-17](https://job-boards.greenhouse.io/anthropic/jobs/5424111008)). "Reusable, well-documented" models, plus lineage and anonymization ([Apple, 2026-05-28](https://jobs.anitab.org/companies/apple/jobs/80876382-analytics-engineer-apple-services-engineering)).
- **SLAs and ownership:** all 4 Meta DE postings ask you to define SLAs ([2026-11-03](https://jobfound.org/job/meta-is-hiring-for-data-engineer-product-analytics-united-states-remote-usa-3-november-2026)). Amazon asks you to "Own ongoing data quality, monitoring, and SLAs" ([amazon.jobs, 2026-09-29](https://www.amazon.jobs/en/jobs/10564106/data-engineer-studios-analytics)).
- **Each metric defined once:** Netflix's Ads Metric Catalog ([2026-04](https://builtin.com/job/analytics-engineer-5-ads-reporting-metric-standards/8884265)). Airbnb wants competing requirements reconciled into "one shared definition" ([2026-11-10](https://careers.airbnb.com/positions/8224032)). Microsoft lists "metric governance" ([2026-08-28](https://jobs.anitab.org/companies/microsoft-2/jobs/91524935-senior-data-scientist-for-copilot-evals)).
- **Cost:** Meta's cost-benefit tradeoffs (above). Perplexity's warehouse cost management (above). In the dbt survey, 57% saw higher warehouse/compute spend but only 36% got bigger team budgets ([dbt 2026, 2026-04-10](https://www.getdbt.com/resources/state-of-analytics-engineering-2026)).
- **The gap a candidate can fill:** in dbt's survey (n=363), 72% prioritize AI-assisted coding but only 24% prioritize AI-assisted testing and observability. 71% worry about hallucinated or incorrect data reaching stakeholders, and trust as a priority rose from 66% to 83% ([dbt press release, 2026-04-14](https://www.getdbt.com/blog/new-dbt-labs-report-finds-ai-driven-acceleration-is-outpacing-trust-and-governance)).

---

## 3. Portfolio projects: what impresses and what are red flags
This section relies on secondary sources and my own inference.
- **What impresses (my inference from posting duties):** a project that copies real job work. Raw logs become canonical datasets ([Anthropic, 2026-10-19](https://job-boards.greenhouse.io/anthropic/jobs/5448481008)), then governed metrics, then an experiment readout and a decision.
- **Secondary advice:** name the consumer and a realistic data source, show modeled tables, scheduled runs, and how you handled a failure ([DataTalks.Club wiki, undated](https://datatalks.club/podwiki/wiki/data-engineering-portfolio-projects/)).
- **Red flags and overdone projects:**
  - Titanic or CSV-to-database ETL demos "actively disqualify" ([datadriven.io, 2026](https://datadriven.io/blog/data-engineer-portfolio-2026-projects-that-get-interviews)).
  - A "text box that forwards input to an API."
  - Kaggle-only portfolios.
  - No written rationale for decisions ([learnist, 2026](https://www.learnist.org/signs-ai-portfolio-project-wont-impress-hiring-managers/)).
  - Impact claims without saying what was measured ([fueler, undated](https://fueler.io/blog/how-to-tell-if-a-portfolio-was-made-with-ai)).

---

## 4. How hiring teams view portfolios built heavily with AI coding tools
- **Official policies:**
  - Anthropic says to complete take-homes and live interviews "without Claude unless we indicate otherwise," and for applications to write your own first draft and then refine it with Claude ([Anthropic, 2025-07-10](https://www.anthropic.com/candidate-ai-guidance)).
  - Meta tested AI-assisted coding interviews (secondary reporting) ([Business Today, 2025-07-31](https://www.businesstoday.in/amp/technology/news/story/meta-to-test-job-applicants-with-ai-assisted-coding-interviews-amid-ai-expansion-plans-487200-2025-07-31)).
  - Karat's survey of 400 engineering leaders: 62% prohibit AI in technical interviews, 38% of US employers allow it, and take-home signal "degrades the fastest" ([Karat, 2026-01-07](https://karat.com/engineering-interview-trends-2026/)).
- **How postings frame AI:** as speed under quality control. Anthropic says "without sacrificing the quality," OpenAI says "without creating brittle systems," and Snowflake says "you are the quality gate" (all cited above).
- **Hiring managers (secondary, from one agency's survey of 41):**
  - Formats: 46% use a live session, 27% a review task (often with a planted bug), 15% a walkthrough of past work, and 10% a take-home where AI is allowed but the debrief is about what you kept, rejected and tested.
  - One quote: "I treat AI-written code like a pull request from a stranger" ([Hire With Near, 2026-10-16](https://www.hirewithnear.com/insights/how-to-interview-developers-for-ai-skills)).
- **Prevalence:** 29% of US hiring managers have received AI-generated portfolio projects, and 86% expect it to get harder to verify whether work reflects real skill. The authors note the worry is authenticity, not AI use itself ([Resume Genius, 2026-07-14](https://resumegenius.com/blog/job-hunting/ai-impact-on-hiring-2026)).
- **What makes AI use acceptable or a plus:**
  - You can defend every decision.
  - You disclose how you used AI.
  - You show verification: tests, evals, reconciliations.
  - You can redo the core SQL by hand, since AI-free screens remain common (Karat, above).

---

## 5. Concrete "AI-native analytics" signals in postings
- **Semantic layer for agents:** "semantic layers for data agents" (Anthropic, above). "AI-readable" warehouse through docs, metadata and lineage (Perplexity, above).
- **Text-to-SQL with evals:**
  - Snowflake wants a verified query library, SQL-accuracy evals, and prompts that route correctly "95% of the time" ([~early 2026](https://careers.wing.vc/companies/snowflake/jobs/75596844-staff-analyst-finance-analytics-ai)).
  - Perplexity wants agents that are "not just SQL copilots," with retrieval and evaluation loops, and AI-assisted A/B analysis that drafts ship/no-ship calls ([2026-07-24](https://jobs.accel.com/companies/perplexity-2/jobs/87461018-member-of-data-staff-ai-builder)).
  - Apple wants natural-language interfaces over data (above).
- **LLM evals and AI product metrics:**
  - Microsoft: offline-to-online agreement and grader reliability (above).
  - Google: auto-rater evaluations (above).
  - Apple: LLM evaluation pipelines for "factual accuracy, latency, and user satisfaction" ([2026-09-12](https://jobs.anitab.org/companies/apple/jobs/92983202-data-scientist-us-decision-intelligence)).
  - Figma: "evals, quality, and experimentation for LLM-powered assistants and agents" ([upd. 2026-10-27](https://boards.greenhouse.io/figma/jobs/6130865004)).
  - Airbnb: AI unit economics and adoption of developer AI tools (above).
- **MCP:** none of the 42 postings names it. dbt Labs ships a dbt MCP server with `query_metrics` and `text_to_sql` tools; the remote version reached general availability in October 2025 ([dbt blog, 2025-10](https://www.getdbt.com/blog/dbt-agents-remote-dbt-mcp-server-trusted-ai-for-analytics)). Treat MCP as a way to build the agent, not as a keyword recruiters screen for.

---

## Where evidence is thin
- **Mirrors:** all FAANG postings except Amazon came from mirrors, and most are now closed. Wording may differ from the live posts.
- **Stripe and Ramp:** I read no full 2026 posting from either. The Ramp snippets I found (Fivetran, Snowflake, dbt, Looker, Hightouch) look like 2024–25 postings ([WTTJ, undated](https://app.welcometothejungle.com/jobs/CgLr4zrP)).
- **Amazon skew:** Amazon is 14 of 42 postings, which inflates Redshift and QuickSight in the analyst counts.
- **Meta interview prep:** Meta's official DE prep pages were unreachable, so the loop details are candidate-reported.
- **Views on AI-built portfolios:** I found no primary source for data roles specifically. The evidence is vendor or agency surveys plus SEO-style blogs.
- **dbt 2026 report:** the public summary gives no adoption figures for tools or semantic layers, and the sample (363) is vendor-run.
- **MCP:** no posting mentions it.

---

## Top 5 implications for a one-week solo portfolio project
1. **Build one end-to-end slice that hits the shared core of all four roles.** Use a realistic product-event dataset (a synthetic AI-assistant app works). Go from raw logs to dbt staging and marts with declared grain, one slowly changing dimension, metrics in a semantic layer, an A/B readout with an SRM check and guardrails, and a one-page decision memo.
2. **Make "production-grade" visible.** Include dbt tests (with a custom grain test), model contracts, a GitHub Actions CI job running `dbt build` on DuckDB, a declared freshness SLA, generated docs and lineage, and a short cost note on incremental models. This answers the 72%-vs-24% gap in the dbt survey.
3. **Add a small AI-native layer, with an eval.** Put a text-to-SQL or agent interface over the semantic layer (for example the dbt MCP server). Score it on 30–50 questions with gold answers, comparing semantic-layer access against raw-schema access. Use AI-product metrics such as task completion, retries and thumbs-down, which match the Google and Microsoft postings.
4. **Ship `DECISIONS.md` and `AI_USAGE.md`.** Record what AI wrote, what you rejected, and how you verified it. Practice rebuilding the core SQL and model without AI, because Anthropic, Karat-surveyed employers and Meta's standard rounds still test that.
5. **Tailor the narrative, not the stack.**
   - DE: lead with SLAs, logging and modeling.
   - AE: lead with metric governance.
   - Analyst: lead with the memo and dashboard.
   - Product DS: lead with the experiment and causal readout.
   
   Keep it to a one-command reproducible run.

---

Not checked: Stripe and Ramp live boards, Meta's official prep pages, and Microsoft or Google careers pages directly. My counts are hand-tallied from extractions, not keyword scripts, so treat them as plus or minus 1. Biggest risk: mirrored posting text may differ from the live official posts.