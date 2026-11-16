# 04 — Verification of open factual questions

All checks ran on **2026-11-10** (local time; about 2026-11-11 05:00 UTC). Unless noted otherwise, every number below comes from an endpoint I actually called that day: a GitHub API or raw file, Hugging Face API or parquet, ClickHouse SQL, PyPI JSON, or a docs page source. Where I could only read about something without calling it, the text says so. "(acc. 2026-11-10)" means accessed on that date.

## Summary verdicts

| # | Question | Verdict | One-line answer |
|---|----------|---------|-----------------|
| 1 | LiteLLM price file, and whether its history can be rebuilt | **CONFIRMED** (with caveats) | The file sits at the repo root, is MIT outside `enterprise/`, holds 5,870 entries and 276 distinct fields, and has **2,940 commits since 2023-09-06**. Retired models are **deleted** from the current file, so history has to come from git. |
| 2 | LMArena `leaderboard-dataset` and `arena-human-preference-140k` | **CONFIRMED** | 23 configs, each with `latest` and `full` splits, as parquet, CC-BY-4.0. Text history runs 2023-05-08 to 2026-11-09 over 256 publish dates. **The model-name format changed on 2026-10-20**, and the method changed 3 times. The 140k set is a static snapshot (Apr–Jul 2025). |
| 3 | Epoch AI models CSV, and whether Epoch already published price-decline work | **CONFIRMED**, and it is a direct competitor | The CSVs are at `epoch.ai/data/*.csv`, CC-BY, updated daily, 3,708 models and 57 columns. Epoch has **already published** "LLM inference prices have fallen rapidly but unequally" (2025-03-12; 9–900×/yr, median 50×) and "The plunging price of thought" (2026-09-22; **13×/yr**). |
| 4 | Free daily PyPI downloads since 2023 | **CONFIRMED** through ClickPy. pypistats and BigQuery are **PARTLY** | I ran live SQL against `sql-clickhouse.clickhouse.com` (user `play`). It returns daily rows per package with installer and country breakdowns. pypistats keeps only about 180–217 days. I could not dry-run BigQuery bytes without credentials. |
| 5 | HF `cfahlgren1/hub-stats` | **CONFIRMED: snapshot only** | Apache-2.0. The parquet files are overwritten every day. History exists only as 4,551 git commits since 2024-07-24, and `models.parquet` is about 1.7 GB per snapshot. |
| 6 | Gemini API: models, prices, free tier, terms, structured output, countTokens, SDK, pinning | **PARTLY** | Model IDs, prices, terms, JSON Schema output, `count_tokens` and the SDK (`google-genai` 3.1.0) are all confirmed. **Free-tier RPM/RPD/TPM figures are not published** (they show only inside AI Studio). Deprecated IDs **auto-route to other models** on 2026-12-01. |
| 7 | dbt-duckdb, DuckDB 2.0, dbt-core 1.12 + MetricFlow, uv | **PARTLY** | All four resolve together with uv. DuckDB 2.0 has only nightly "pre-release coverage" in dbt-duckdb CI, and dbt-duckdb has open 2.0 issues. dbt docs document pip, not uv. |
| 8 | Static dashboard on GitHub Pages | **Evidence Core: FALSE** (as documented). **Observable Framework: CONFIRMED** | Evidence Core self-hosting runs a Docker server (`evidence serve`) against a live direct connector and has no static build command. Observable Framework documents a GitHub Pages deploy and ships DuckDB-Wasm, pinned to DuckDB 1.1.1. I could not verify the "launched 2026-08-26" date. |
| 9 | Entity resolution across LiteLLM, LMArena and Epoch | **CONFIRMED: hard** | No shared key. Mapping is 1:N (LiteLLM has many providers per model) and N:1 (LMArena has many reasoning-effort variants per model). LMArena names changed mid-series, and Epoch dates are announcement dates. For about 150–250 core models this is a manual crosswalk of roughly 2–4 days, with fuzzy suggestions to speed it up. |
| 10 | Competitors | **CONFIRMED: the gap is narrower than assumed** | Artificial Analysis already charts price over time and cost per task over time. Epoch publishes decline rates. sanand0/llmpricing already plots Arena Elo against price month by month. OpenRouter publishes daily token-share data. What remains open is **adoption and causality**, plus a reproducible, governed panel. |

---

## 1. LiteLLM `model_prices_and_context_window.json`

**Verdict: CONFIRMED (with caveats).**

**Facts**

- **Path.** `model_prices_and_context_window.json` sits at the repo root on branch `main`. A raw GET returned HTTP 200 and **4,007,150 bytes** (https://raw.githubusercontent.com/BerriAI/litellm/main/model_prices_and_context_window.json, acc. 2026-11-10).
- **License.** The GitHub API reports `NOASSERTION` ("Other"). The LICENSE file says content outside `enterprise/` is **MIT**, and `enterprise/` has its own license (https://raw.githubusercontent.com/BerriAI/litellm/main/LICENSE; https://api.github.com/repos/BerriAI/litellm, acc. 2026-11-10). The price JSON is outside `enterprise/`, so it is MIT.
- **Entry count.** **5,870** keys, which includes a `sample_spec` documentation entry. Of these, 3,554 have `mode=chat` and 205 have `mode=responses`. Other modes include image_generation (967), video_generation (417) and embedding (157). Keys cover **157 `litellm_provider` values**, led by fal_ai (883), fireworks_ai (356), bedrock (342), replicate (323), azure (322) and openai (223). Source: my parse of the raw file, acc. 2026-11-10.
- **Fields.** There are **276 distinct field names**. The most common:
  - `litellm_provider` (5,771 entries), `mode` (5,761), `source` (4,444; a URL to the provider's price page), `input_cost_per_token` (4,023), `output_cost_per_token` (3,996), `max_input_tokens`, `max_output_tokens`.
  - Capability flags: `supports_function_calling`, `supports_vision`, `supports_reasoning`, `supports_response_schema`, `supports_prompt_caching`.
  - Cache prices: `cache_read_input_token_cost`, `cache_creation_input_token_cost`.
  - Lifecycle fields: `deprecation_date`, `deprecation_source`, `successor_model`.
  - Tier variants: `*_batches`, `*_priority`, `*_flex`, plus context-tier variants such as `input_cost_per_token_above_200k_tokens` and `..._above_272k_tokens`.
  - Prices are **USD per token**. For example, `gpt-4o` has `input_cost_per_token: 2.5e-06` and `output_cost_per_token: 1e-05`.
- **Commit history.**
  - `GET https://api.github.com/repos/BerriAI/litellm/commits?path=model_prices_and_context_window.json&per_page=1` returned a Link header of `rel="last"` → `page=2940`. That means **2,940 commits** touch this path (acc. 2026-11-10).
  - The **oldest** path-filtered commit is `c5151aa573b797ef58cf9d0532162ed14964002f`, dated **2023-09-06T23:31:44Z**, titled "move model_prices to root github". It is a **rename** from `litellm/model_prices_and_context_window.json` (https://api.github.com/repos/BerriAI/litellm/commits/c5151aa573b797ef58cf9d0532162ed14964002f). Older history needs `git log --follow`.
  - The newest commit is `e35eec2…`, dated 2026-11-11T04:51:57Z. The file changes several times a day.
- **Schema drift.** The oldest version, fetched at `c5151aa`, has only **19 entries and 3 fields** (`input_cost_per_token`, `output_cost_per_token`, `max_tokens`). It has no `litellm_provider` and no `mode` (https://raw.githubusercontent.com/BerriAI/litellm/c5151aa573b797ef58cf9d0532162ed14964002f/model_prices_and_context_window.json, acc. 2026-11-10).
- **Rate limits.**
  - The unauthenticated REST API response carried `x-ratelimit-limit: 60` per hour, per IP. Authenticated requests get 5,000 per hour (https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api, acc. 2026-11-10).
  - In May 2025 GitHub tightened unauthenticated limits for raw.githubusercontent.com and anonymous clones, and did not publish the numbers (https://github.blog/changelog/2025-05-08-updated-rate-limits-for-unauthenticated-requests/, acc. 2026-11-10).
- **Is pulling every version by SHA practical?**
  - 2,940 raw GETs at up to about 4 MB each comes to several GB, and is likely to hit the undisclosed anonymous raw limit.
  - The full repo is about **2.93 GB** (GitHub API `size`: 2,927,503 KB), so a full clone is heavy.
  - The practical route is a **blobless partial clone**: `git clone --filter=blob:none --no-checkout`, then `git log --follow --format='%H %cI' -- model_prices_and_context_window.json`, then `git show <sha>:<path>` for **one commit per day**. That is about 1,150 snapshots. Run it with a token in CI, or do it once and cache the result as parquet.

**Gotchas**

- **Retired models are deleted from the current file.** Neither `claude-3-5-sonnet-20241022` (first-party key), `xai/grok-4-0709` nor `mistral/mistral-large-2411` exists in today's file. They survive only as Bedrock, Vertex or gateway keys, if at all. Any "current snapshot" approach therefore biases the panel toward survivors.
- **Commit time is not the price-effective time.** Commits lag provider announcements and sometimes lead them. LiteLLM also cannot represent future-dated prices. For example, Gemini 3.8 Flash doubles on 2027-01-01 (see item 6), but the file stores one value, $0.75/$3.75 per 1M.
- **Aliases drift.** `deepseek/deepseek-reasoner` costs $0.28/$0.42 per 1M, while `deepseek/deepseek-r1` costs $0.55/$2.19. Unversioned aliases such as `o3`, `gpt-4o` and `mistral-large-latest` silently change which model they point to.
- **The same model ID can belong to different providers.** `gemini-2.5-flash` has provider `vertex_ai-language-models`, while `gemini/gemini-2.5-flash` has provider `gemini`.

## 2. LMArena datasets on Hugging Face

**Verdict: CONFIRMED.**

### `lmarena-ai/leaderboard-dataset`

Source: https://huggingface.co/api/datasets/lmarena-ai/leaderboard-dataset and README https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset/raw/main/README.md, acc. 2026-11-10.

- **License and access.** **CC-BY-4.0**, not gated. HF reports `lastModified` 2026-11-11T04:01:46Z. The repo `createdAt` is 2026-04-02 even though the data goes back to 2023, which suggests the repo was recreated.
- **Configs.** There are 23 configs, each with two splits: `latest` and `full`.
  - text: `text`, `text_style_control`, `text_factuality`
  - vision: `vision`, `vision_style_control`
  - search: `search`, `search_style_control`, `search_factuality`
  - document: `document`, `document_style_control`
  - `webdev`
  - media: `text_to_image`, `image_edit`, `text_to_video`, `image_to_video`, `video_edit`
  - agent: `agent`, plus 6 `agent_*` signal subsets.
- **Format and size.** One parquet file per split (`<config>/full-00000-of-00001.parquet`).
  - `text/full`: **1,268,299 rows**; 63.7 MB download, which I measured.
  - `text_style_control/full`: 1,126,709 rows; 57.8 MB.
  - Most other configs are under 6 MB.
- **Schema for the Bradley-Terry arenas.**
  - `model_name` (str), `organization` (str), `license` (str)
  - `rating`, `rating_lower`, `rating_upper`, `variance` (float)
  - `vote_count` and `rank`: **float64 in `text`**, int64 in most other configs
  - `category` (29 categories in text, e.g. overall, english, coding, hard_prompts_english, math)
  - `leaderboard_publish_date` (**string**, `YYYY-MM-DD`)
- **Schema for agent configs.** IPS scores instead: `score`, `score_ci_lower`, `score_ci_upper`, `observation_count`, `session_count`, `rank`, `category`, `leaderboard_publish_date`. The `agent` config also has `cost_per_task_p50` and `output_tokens_per_task_p50`.
- **Date range** (my parse):
  - `text`: **2023-05-08 → 2026-11-09**, 256 publish dates.
  - `text_style_control`: 2024-08-28 → 2026-11-09, 196 dates.
- **Cadence.** Irregular: the median gap is **4 days**, and recent gaps run from 1 to 12 days. The file itself is re-uploaded about daily.
- **Method changes** (from the README):
  - 2024-01-09: rating method moved from Elo to Bradley-Terry.
  - 2025-05-16: **style control became the default, and the scale offset was adjusted**.
  - 2025-07-23: frequency-based re-weighting added.
  - Search data starts 2025-08-07, webdev 2025-11-12 and agent 2026-06-04.
- **Model-name format changed on 2026-10-20.**
  - Up to 2026-10-15, names were API-style slugs such as `claude-3-5-sonnet-20241022` and `gpt-4o-2024-08-06`.
  - From 2026-10-20, names are display names such as `Claude 3.5 Sonnet (20241022)` and `GPT-4o (2024-08-06)`.
  - In `text_style_control` overall, **only 26 of 416 names** are identical on 2026-10-15 and 2026-10-20. The rest were renamed in place.
  - Old snapshots were **not** back-filled. So `text` overall shows 852 distinct names, and most models appear twice.
  - The README still shows a filter example using `gpt-4o-2024-05-13`, which no longer matches current rows.

### `lmarena-ai/arena-human-preference-140k`

Source: https://huggingface.co/api/datasets/lmarena-ai/arena-human-preference-140k, README, and datasets-server `/statistics`, acc. 2026-11-10.

- **License.** `cc-by-4.0` tag. The README says: "User prompts are licensed under CC-BY-4.0, and model outputs are governed by the terms of use set by the respective model providers."
- **Size and format.** **135,634 rows**, one `train` split, 7 parquet shards. About **1.6 GB** download, about 3.0 GB in memory.
- **Columns.** `id`, `model_a`, `model_b`, `winner` (model_a / model_b / tie / both_bad), `evaluation_session_id`, `evaluation_order`, `conversation_a`, `conversation_b`, `full_conversation`, `conv_metadata` (token and markdown counts for style control), `category_tag`, `language`, `is_code`, `timestamp`.
- **Coverage.** Timestamps run from **2025-04-17 to 2025-07-24**, across **53 models** (slug names). The dataset was last modified 2025-08-01, so it is static.

## 3. Epoch AI models data and competing analyses

**Verdict: CONFIRMED.** Epoch is also a **direct competitor** on the price-decline question.

**Downloads**

All returned HTTP 200 on 2026-11-10:

| URL | Size |
|---|---|
| https://epoch.ai/data/all_ai_models.csv | 6.9 MB |
| https://epoch.ai/data/notable_ai_models.csv | 2.3 MB |
| https://epoch.ai/data/large_scale_ai_models.csv | 1.1 MB |
| https://epoch.ai/data/frontier_ai_models.csv | 0.37 MB |
| https://epoch.ai/data/ai_models.zip | 3.4 MB |

The landing page is https://epoch.ai/data/ai-models.

- **License.** CC BY 4.0, "free to use, distribute, and reproduce provided the source and authors are credited".
- **Update frequency.** "available for download in CSV format, updated daily" (https://epoch.ai/data/ai-models-documentation, acc. 2026-11-10). An automated weekly search finds new models, and major models are usually added within 2 weeks of release. The max `Last modified` value in the file is 2026-11-09.

**Contents of `all_ai_models.csv`**

- **3,708 rows and 57 columns.** 2,136 are language-domain models, and 1,443 of those were published from 2023 onward.
- **Key columns:**
  - `Model`, `Organization`, `Publication date` (1950-07-02 → 2026-10-28), `Domain`
  - `Model accessibility`: Open weights (unrestricted / restricted use / non-commercial), API access, Unreleased, Hosted access (no API)
  - `Open model weights?`: Yes 1,395 / No 1,461 / NaN 852
  - `Parameters` (2,366 non-null), `Training compute (FLOP)` (1,424 non-null)
  - `Frontier model`, `Base model`, `Country (of organization)`
  - `Hugging Face developer id` (685 non-null; a useful join key to the HF Hub)
  - `Training compute cost (2023 USD)`, `Confidence`

**Existing Epoch analyses that compete directly**

1. **"LLM inference prices have fallen rapidly but unequally across tasks"**, Data Insight, **2025-03-12**, by Ben Cottier, Ben Snodin, David Owen and Tom Adamczewski (https://epoch.ai/data-insights/llm-inference-price-trends, acc. 2026-11-10).
   - Headline: prices to reach a fixed performance level fell **9× to 900× per year depending on the milestone, median 50×/yr**. With pre-2024 data removed, the median rises to 200×/yr. The price to reach GPT-4 level on GPQA Diamond fell about **40×/yr**.
   - Method: price is a **3:1 input:output blend**. Reasoning models are excluded. Where no first-party API exists, the median across providers is used. Price data comes from **Artificial Analysis** plus Epoch's own data, on 6 benchmarks including the LMSys Arena Elo.
   - Code: https://github.com/epoch-research/llm-benchmark-efficiency.
2. **"The plunging price of thought"**, **2026-09-22, updated 2026-09-23**, by Luke Emberson and David Roodman (https://epoch.ai/publications/the-plunging-price-of-thought, acc. 2026-11-10).
   - Headline: the cost of a given performance level fell **about 47% per quarter, roughly 13× per year, since 2023**. At the state of the art the decline is about 66% per quarter (75×/yr), slowing to 32% per quarter (4.7×/yr) two years later. Example: GPQA-Diamond-level performance went from about $0.30 per question with o3 (Jan 2025) to $0.0004 with GPT-5.6 Luna, a 725-fold drop.
   - Method: costs are taken from benchmark transcripts (CAISI-derived), not list prices, across 5 benchmarks.
   - Data and code: https://github.com/droodman/inference-cost (HTTP 200). The page also cites Gundlach et al. (2026), which found 5–10× per year, and Demirer, Fradkin & Tadelis (2026).
   - Relevant quote for our adoption angle: "Essentially no user stays permanently on the cost frontier". The piece reports **no adoption metrics**.
3. Related: "How many AI agents could we run?" includes a token price table for Aug–Sep 2026 (https://epoch.ai/publications/estimating-the-agent-population). I saw it only in search results and did not open it.

**Gotchas**

- **`Publication date` is the announcement date, not API availability.** `o3` is dated 2024-12-20, but the API model `o3-2025-04-16` shipped in April 2025.
- **Organization labels are inconsistent.** "Gemini 2.5 Flash Image" is under "Google", while "Gemini 2.5 Flash" is under "Google DeepMind".
- **Parameters and compute are mostly blank for closed models.** Claude Opus 4.6 and o3 have neither.

## 4. PyPI daily downloads

**Verdict: CONFIRMED through ClickPy (live query). pypistats is PARTLY usable. BigQuery is PARTLY/UNKNOWN: I could not dry-run it.**

### ClickPy / ClickHouse public endpoint (tested live)

- **Connection.** Host `https://sql-clickhouse.clickhouse.com`, user `play`, no password. POST SQL as the request body: `curl "https://sql-clickhouse.clickhouse.com/?user=play" --data-binary "SELECT ..."`. The server reported ClickHouse 26.11.1.1102 (acc. 2026-11-10).
- **Tables.** Database `pypi`:
  - `pypi_downloads_per_day` (`date`, `project`, `count`; 1.11 billion rows; SharedSummingMergeTree)
  - `pypi_downloads_per_day_by_version_by_installer_by_type` (`project`, `version`, `date`, `installer`, `type`, `count`)
  - `pypi_downloads_per_day_by_version_by_installer_by_type_by_country` (adds `country_code`)
  - `..._by_python`, `..._by_system`, `..._by_file_type`, `pypi_downloads_per_month`
  - The raw `pypi` table holds 3.7 trillion rows.
  - **`pypi_downloads_per_day_by_installer` is empty (0 rows). Use the `..._by_version_by_installer_by_type` table instead.**
  - Coverage: `min(date)` = 2016-01-22, `max(date)` = 2026-11-10.
- **Test query.** Daily `anthropic` downloads for October 2026 returned 31 rows, for example:

  | Date | Downloads | Day |
  |---|---|---|
  | 2026-10-01 | 6,899,191 | |
  | 2026-10-03 | 4,015,454 | Saturday |
  | 2026-10-28 | 8,075,066 | |
  | 2026-10-31 | 4,848,331 | |

  The strong weekday/weekend pattern points to CI and automation traffic.

- **All 7 packages since 2023-01-01** (`sum(count)`; first date, total):

  | Package | First date | Total downloads |
  |---|---|---|
  | openai | 2023-01-01 | 4.64 B |
  | litellm | 2023-07-27 | 3.50 B |
  | google-genai | 2024-12-10 | 3.33 B |
  | anthropic | 2023-02-09 | 1.63 B |
  | cohere | 2023-01-01 | 407 M |
  | mistralai | 2023-12-09 | 325 M |
  | google-generativeai | 2023-05-03 | 266 M |

- **Filtering CI and mirrors.**
  - *By installer.* For anthropic in October 2026: uv 135.7 M, pip 53.0 M, poetry 3.2 M, blank 0.85 M, Bazel 0.69 M. Mirror installers are tiny: `bandersnatch` about 8.3 k and `devpi` about 2 k.
  - *By country.* For anthropic in October 2026, US accounts for 160.4 M of about 194 M (about 83%). DE is 5.3 M and SG 4.2 M. The US share reflects cloud CI.
  - Neither filter gives a true human-vs-CI split. Installer plus country plus weekday/weekend patterns are proxies only.
- **Limits.**
  - `readonly=1`, `max_execution_time=60` seconds, quota of **300 queries per hour**.
  - `max_result_rows=1000` with `result_overflow_mode=break`. Even so, a 2,781-row result came back complete.
  - **Always cross-check row counts**, because `break` mode can truncate without an error.
  - The table is a SummingMergeTree, so **always `GROUP BY date` and `sum(count)`**. `count()` returned 1,420 rows for openai over 1,410 calendar days, which shows unmerged parts.
- **Cross-check against pypistats.** For anthropic on 2026-10-15, ClickPy shows 7,532,172 and pypistats (without mirrors) shows 7,503,716. They differ by 0.4%.

### pypistats.org

Source: https://pypistats.org/api/ docs, plus a live `GET /api/packages/anthropic/overall?mirrors=false`, acc. 2026-11-10.

- The docs say "Time series data is retained only for 180 days". The live call returned **217 days** (2026-04-08 → 2026-11-10). So the series **cannot reach back to 2023**.
- Mirrors are excluded by default, and there is a `mirrors=true/false` switch. There is no installer or country filter on `/overall`.
- Rate limiting is per IP. The response headers showed `x-ratelimit-limit: 60`, and the docs ask users to "cache your results" and not bulk-download.

### BigQuery `bigquery-public-data.pypi.file_downloads`

- **Documentation.** The table is partitioned by day on `timestamp`, and docs recommend a `timestamp` filter. The PyPA guide's `pypinfo requests` example processed **6.87 GiB (about $0.04)**. A Python-versions-over-time query "processes over 500 GB" (https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads/, acc. 2026-11-10).
- **Clustering.** I found **no official statement** that the table is clustered by `project`. Hugo van Kemenade measured a 1-day, top-10-packages query at 46.6 GiB and found bytes grow with the number of days, not packages (https://hugovk.dev/blog/2024/a-surprising-thing-about-pypis-bigquery-data/, 2024-11-24, acc. 2026-11-10).
- **Sandbox.** 1 TiB of query processing per month, 10 GiB lifetime storage, **tables expire after 60 days**, no credit card required (https://docs.cloud.google.com/bigquery/docs/sandbox, acc. 2026-11-10).
- **Feasibility.** A single package-month probably scans single-digit to tens of GiB, so the sandbox covers roughly 20–100 package-months per month. A backfill of 7 packages × 46 months (about 322 package-months) **likely exceeds one month's free quota**. This is an estimate; I could not dry-run it because no `bq`/`gcloud` credentials are available here. The table has `details.installer.name` and `country_code` columns, so the same filters as ClickPy are possible.
- **Verdict.** ClickPy is the primary source. BigQuery is only an audit fallback.

**Gotchas**

- **Dependency inflation.** `litellm` 1.109.0 requires `openai>=2.20.0,<4.0.0` (https://pypi.org/pypi/litellm/json), so every litellm install also counts as an openai download. The openai and litellm series are not independent.
- **SDK migration break.** `google-generativeai` (legacy, last release 0.8.6 on 2025-12-16) was replaced by `google-genai`, which first appears on 2024-12-10. Model "Google adoption" as the **sum of both**, or the result will show a fake jump in 2025.
- **uv's caching behavior affects counts.** uv is about 70% of anthropic installs, so changes in how uv caches can move counts with no change in adoption.

## 5. HF `cfahlgren1/hub-stats`

**Verdict: CONFIRMED — it is a snapshot dataset, not a history dataset.**

Sources: https://huggingface.co/api/datasets/cfahlgren1/hub-stats, datasets-server `/info` and `/first-rows`, and the README, acc. 2026-11-10.

- **License.** apache-2.0. Created 2024-07-24; last modified 2026-11-10T13:40Z.
- **Configs.** `models`, `datasets`, `spaces`, `posts`, `papers` (daily_papers), and `arxiv_papers`. Each is a **single parquet file overwritten on every upload**.
- **`models` schema.** `_id`, `id`, `author`, `cardData`, `inferenceProviderMapping`, `lastModified`, `likes`, `trendingScore`, `config`, `downloads`, `downloadsAllTime`, `tags`, `pipeline_tag`, `library_name`, `siblings`, `createdAt`, `baseModels`, `safetensors`, `transformersInfo`, `gguf`.
- **`models` size.** 3,227,480 rows, about **1.72 GB** download.
- **History.**
  - The rows contain no per-day download history. `downloads` is the Hub's recent-window figure (the "last month" number), and `downloadsAllTime` is cumulative. The live HF API returns the same pair, e.g. `meta-llama/Llama-3.1-8B-Instruct` → `downloads: 4,535,750`, `downloadsAllTime: 193,752,576`.
  - The repo does have **4,551 commits** (per the `x-total-count` header), with daily uploads back to about 2024-07-30. In principle you could rebuild a daily panel by reading `models.parquet` at each revision. That means about 830 snapshots of about 1.7 GB each. It is only practical with remote parquet reads (`hf://…@<sha>`) using column and row-group pruning, and I did not test it.
- **How HF counts downloads.** "Every HTTP request to these files, including GET and HEAD, will be counted", based on query files such as `config.json`. GGUF files are counted per file (https://huggingface.co/docs/hub/models-download-stats, acc. 2026-11-10). Cache-check HEAD requests and CI therefore inflate counts.

## 6. Gemini API (as of 2026-11-10)

**Verdict: PARTLY.** Free-tier RPM/RPD/TPM limits are not published.

**Docs moved.** `ai.google.dev/gemini-api/docs/*` now returns **301 → `aistudio.google.com/docs/*`**. I fetched the raw page source for the pages below, acc. 2026-11-10.

**Current text models** (https://aistudio.google.com/docs/models)

- **Recommended for new projects:** `gemini-3.5-flash-lite` or `gemini-3.8-flash`.
- **Stable:** `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`.
- **New:** `gemini-3.8-flash`.
- **Unlabelled:** `gemini-4-argon`, `gemini-4-carbon`.
- **Preview:** `gemini-3-flash-preview`, `gemini-3.1-pro-preview`.
- **Deprecated:**
  - `gemini-2.5-flash` and `gemini-2.5-pro` are deprecated, "API access to the 2.5 models is limited to existing users".
  - "Effective December 1, 2026, all API requests to `gemini-2.5-flash` will automatically route to `gemini-3.5-flash-lite`", and `gemini-2.5-pro` will route to `gemini-3.8-flash`. Both are billed at the new model's rates.
- **Shut down:** `gemini-2.0-flash` and `gemini-2.0-flash-lite`.

**Prices** (USD per 1M tokens, Standard paid tier; https://aistudio.google.com/docs/pricing). Amounts are as printed in the raw page.

| Model | Free tier | Input | Output (incl. thinking) | Batch in/out | Free tier data "used to improve our products" |
|---|---|---|---|---|---|
| `gemini-3.8-flash` | free of charge | **$0.75 through 2026-12-31, $1.50 from 2027-01-01** | **$3.75 → $7.50 from 2027-01-01** | $0.375 / $1.875 | Yes (free) / No (paid) |
| `gemini-3.6-flash` | free of charge | $0.75 → $1.50 (same schedule) | $3.75 → $7.50 | $0.375 / $1.875 | Yes / No |
| `gemini-3.5-flash-lite` | free of charge | $0.30 (text/image/video/audio) | $2.50 | $0.15 / $1.25 | Yes / No |
| `gemini-3.1-flash-lite` | free of charge | $0.25 (text/image/video), $0.50 audio | $1.50 | $0.125 / $0.75 | Yes / No |
| `gemini-2.5-flash-lite` | free of charge | $0.10 | $0.40 | $0.05 / $0.20 | Yes / No |
| `gemini-3-flash-preview` | free of charge | $0.50 | $3.00 | $0.25 / $1.50 | Yes / No |
| `gemini-3.1-pro-preview` | not available | $2.00 (≤200k) / $4.00 | $12.00 / $18.00 | $1.00 / $6.00 | n/a / No |

**Free-tier limits and terms**

- **Rate limits** (https://aistudio.google.com/docs/rate-limits). The docs explain RPM, TPM and RPD; RPD resets at midnight Pacific; limits apply "per project, not per API key". Tier 1 has a spend cap of $10 per 10 minutes. The docs **no longer publish per-model free-tier RPM/RPD/TPM numbers**: "can be viewed in Google AI Studio". **UNKNOWN until you check your own project in AI Studio.**
- **Data use on the free tier** (https://aistudio.google.com/docs/terms). For Unpaid Services (AI Studio and the unpaid Gemini API quota), "Google uses the content you submit … and any generated responses to provide, improve, and develop Google products … human reviewers may read, annotate, and process your API input and output." The terms also say: "**You may use only Paid Services when making API Clients available to users in the European Economic Area, Switzerland, or the United Kingdom.**"

**Structured output** (https://aistudio.google.com/docs/structured-output)

- JSON Schema is supported; the SDKs accept Pydantic and Zod.
- Current Python call shape: `client.interactions.create(model=…, input=…, response_format={"type":"text","mime_type":"application/json","schema": Model.model_json_schema()})`.
- Only "a subset" of JSON Schema is supported. `minLength`, `maxLength`, `minProperties`, `maxProperties`, `uniqueItems`, `contains`, `minContains` and `maxContains` are **not enforced** by constrained decoding.
- Model pages for 3.5 Flash-Lite, 3.1 Flash-Lite and 2.5 Flash-Lite show "Structured outputs: supported", a 1,048,576-token input limit and a 65,536-token output limit.

**Pre-run cost estimation** (https://aistudio.google.com/docs/tokens)

- `client.models.count_tokens(model="gemini-3.8-flash", contents=prompt)` returns `.total_tokens` for the **input only**.
- Actual usage comes from `interaction.usage`, with `total_input_tokens`, `total_output_tokens`, `total_thought_tokens`, `total_cached_tokens`, `total_tool_use_tokens` and `total_tokens`.

**SDK**

- **`google-genai` 3.1.0**, uploaded 2026-11-10, `requires_python >=3.11` (https://pypi.org/pypi/google-genai/json).
- The legacy `google-generativeai` 0.8.6 (2025-12-16) is not the current SDK.

**Pinning a model version**

- Stable IDs no longer carry a `-00N` suffix. The model page lists "Stable: `gemini-3.5-flash-lite`", with latest update July 2026.
- Pinning means using the exact stable ID and **avoiding `*-latest` aliases** such as `gemini-flash-latest`, which are "hot-swapped with every new release" with 2 weeks' email notice.
- Even a pinned stable ID can be **auto-routed to a different model at deprecation**, as with 2.5 Flash → 3.5 Flash-Lite on 2026-12-01.

## 7. Tool compatibility (PyPI JSON, acc. 2026-11-10)

**Verdict: PARTLY.**

| Package | Latest | Released | Key requires_dist |
|---|---|---|---|
| dbt-duckdb | **1.11.1** | 2026-10-26 | `duckdb>=1.0.0` (no upper bound), `dbt-core>=1.8.0`, `dbt-adapters<2,>=1`. **The `md` (MotherDuck) extra pins `duckdb==1.5.5`.** |
| duckdb | **2.0.0** | 2026-10-21 | `requires_python >=3.11.0`; 2.0.1/2.1.0 dev builds exist |
| dbt-core | **1.12.6** | 2026-10-14 | **`metricflow<1.0,>=0.213.0`** (core now depends on MetricFlow), `dbt-adapters<2.0,>=1.24.5` |
| dbt-metricflow | **0.15.0** | 2026-09-10 | `dbt-core<1.13,>=1.11`, `metricflow==0.213.0`, extra `dbt-duckdb`; python `>=3.10,<3.15` |
| metricflow | 0.213.0 | 2026-09-10 | python `>=3.10,<3.15` |
| uv | 0.13.7 | 2026-11-03 | — |

URLs: https://pypi.org/pypi/{dbt-duckdb,duckdb,dbt-core,dbt-metricflow,metricflow,uv}/json.

- **Resolution test.** `uv pip compile` on `dbt-core==1.12.6`, `dbt-duckdb==1.11.1`, `dbt-metricflow[dbt-duckdb]==0.15.0` and `duckdb==2.0.0` for Python 3.12 resolved **66 packages** with no conflict. Notable versions: metricflow 0.213.0, dbt-adapters 1.24.5, sqlglot 30.31.0. I did **not** run `dbt build` or `mf query` against DuckDB 2.0, so runtime compatibility is unproven.
- **DuckDB 2.0 support in dbt-duckdb.**
  - The 1.11.1 release notes include "Expand DuckDB 2.0 **pre-release coverage in nightly CI**" (#858) (https://api.github.com/repos/duckdb/dbt-duckdb/releases/tags/1.11.1).
  - Open issues #870 and #871 cover "Support DuckDB 2.0 custom extension repositories in profiles.yml" (2026-10-27).
  - So 2.0 is *installable* and covered by nightly CI, but not declared supported. Pin `duckdb>=1.5,<2` until a release note says otherwise, or spike it first.
- **MetricFlow locally.** The dbt docs show `pip install "dbt-metricflow[dbt-<adapter>]"` and `mf query --metrics order_total --group-by metric_time`. They label the section "Applies to dbt v1.12 and later" and say the user owns version compatibility (https://docs.getdbt.com/docs/build/metricflow-commands, acc. 2026-11-10).
  - The docs claim MetricFlow supports Python 3.8–3.12, while the PyPI metadata says >=3.10,<3.15. Docs and metadata disagree.
  - dbt Core 1.12 also adds the **new Semantic Layer YAML spec**: semantic_model nested under each model, `type: simple` metrics in place of measures, `type_params` deprecated. The legacy spec is still accepted (dbt 1.12 upgrade guide and changelog, https://docs.getdbt.com/docs/dbt-versions/core-upgrade/upgrading-to-v1.12, acc. 2026-11-10, via search summary).
- **Is uv recommended?** No. The dbt docs document **pip**. uv works for resolution and is fine to use, but it is not the official install path.
- **Python version.** The intersection of all constraints is **3.11–3.14**: duckdb 2.0 and google-genai 3.1 need >=3.11, and MetricFlow needs <3.15. **Use 3.12**, which also sits inside the range the MetricFlow docs claim.

## 8. Static dashboard on GitHub Pages: Evidence vs Observable Framework

**Verdict: Evidence Core is FALSE as currently documented. Observable Framework is CONFIRMED.**

**Evidence** (https://docs.evidence.dev/llms.txt and the pages below, acc. 2026-11-10)

- **The docs contradict themselves.**
  - The index says: "**Evidence Core** is an MIT-licensed framework … It builds to a static site you can self-host anywhere — Vercel, Netlify, Docker" (https://docs.evidence.dev/index.md).
  - But the self-host page says self-hosting uses the Docker image `evidencedev/serve`, which "runs `evidence serve` … hardened as a production server". Earlier wording on the same page: "Self-hosted projects *must* use a direct connector" (https://docs.evidence.dev/self-host/index.md).
  - The CLI reference lists `init, dev, launch, link, query, …, serve` and has **no `build` or export command** (https://docs.evidence.dev/cli/commands.md).
- **The migration guide confirms the change.** "Legacy Evidence is a static website generator … DuckDB SQL which queries data you package up in a build step". Current Evidence uses "Server-side: ClickHouse, or your warehouse's dialect via a direct connector", with "No build, Queries re-run on page load" (https://docs.evidence.dev/migration-guide.md).
- **No local DuckDB.** The direct connectors are Snowflake, Fabric, SQL Server, ClickHouse, BigQuery, Databricks, Postgres, Cube, Redshift, Athena and MotherDuck, and MotherDuck connects "over Postgres-wire … no local DuckDB engine". Flat-file (parquet) sources are **uploads to Evidence Studio**.
- **Repo and package status.** The repo `evidence-dev/evidence` is MIT and was pushed 2026-11-11. Its README says "self-host the generated static site", which conflicts with the CLI docs.
- **Legacy Evidence** (`@evidence-dev/evidence` 40.1.8 on npm, MIT) can still build static output, but its **last publish was 2026-02-06** and it is now documented only as "legacy".
- **Launch date.** I found **no primary source for "Evidence Core launched 2026-08-26"**. Search turned up only secondary aggregators. UNKNOWN.

**Observable Framework**

Sources: the repo docs at https://raw.githubusercontent.com/observablehq/framework/main/docs/deploying.md and https://raw.githubusercontent.com/observablehq/framework/main/docs/lib/duckdb.md, acc. 2026-11-10. The observablehq.com pages returned HTTP 429.

- "You can host your built Framework app on any static site hosting service". The docs include a ready-made GitHub Actions workflow: `npm run build`, then `actions/upload-pages-artifact` with `path: dist`, then `actions/deploy-pages`. It runs on a daily schedule plus on push, and can cache data-loader output per day.
- **DuckDB-Wasm in the browser.** `DuckDBClient.of({t: FileAttachment("x.parquet")})`, or attach a whole `.duckdb` file. Files produced by data loaders at build time are written into `dist`, so the data is baked into the static site.
- **Gotcha: old DuckDB version.** Framework "currently uses DuckDB-Wasm 1.29.0 … aligns with DuckDB 1.1.1". You can override it with `npm:@duckdb/duckdb-wasm@…`.
- **Gotcha: slow maintenance.** License ISC (not MIT). The latest release is v1.13.4 (2026-03-02) and the last push was 2026-05-15 (https://api.github.com/repos/observablehq/framework, acc. 2026-11-10). It is maintained, but slowly.

## 9. Entity resolution sample

The table compares how the same model is named in each source. Prices are USD per 1M tokens from the current LiteLLM file. LMArena names come from `text` / `text_style_control` overall. Epoch names come from `all_ai_models.csv`. All acc. 2026-11-10.

| Model | LiteLLM key(s) (price in/out) | LMArena ≤2026-10-15 | LMArena ≥2026-10-20 | Epoch `Model` (pub. date) |
|---|---|---|---|---|
| Claude 3.5 Sonnet (Oct 24) | **first-party key gone**; `anthropic.claude-3-5-sonnet-20241022-v2:0` (Bedrock), `vercel_ai_gateway/anthropic/claude-3-5-sonnet-20241022`, `vertex_ai/claude-3-5-sonnet` | `claude-3-5-sonnet-20241022` | `Claude 3.5 Sonnet (20241022)` | `Claude 3.5 Sonnet (October 2024)` (2024-10-22) |
| GPT-4o (Aug 24) | `gpt-4o-2024-08-06` ($2.50/$10) + `gpt-4o` alias + 70+ azure/* keys | `gpt-4o-2024-08-06` | `GPT-4o (2024-08-06)` | `GPT-4o (Aug 2024)` |
| GPT-4o mini | `gpt-4o-mini-2024-07-18` ($0.15/$0.60) | `gpt-4o-mini-2024-07-18` | `GPT-4o mini (2024-07-18)` | `GPT-4o mini` |
| Llama 3.1 405B | no first-party; `together_ai/meta-llama/Llama-3.1-405B-Instruct`, `nebius/meta-llama/Meta-Llama-3.1-405B-Instruct`, `vertex_ai/meta/llama-3.1-405b-instruct-maas`, … (8 hosts) | `llama-3.1-405b-instruct` → split into `-bf16` / `-fp8` from 2024-09-15 | `Llama 3.1 405B Instruct (BF16)` / `(FP8)` | `Llama 3.1-405B` |
| DeepSeek-R1 | `deepseek/deepseek-r1` ($0.55/$2.19) vs alias `deepseek/deepseek-reasoner` ($0.28/$0.42) + ~30 host keys | `deepseek-r1`, `deepseek-r1-0528` | `DeepSeek-R1`, `DeepSeek-R1 (0528)` | `DeepSeek-R1`, `DeepSeek-R1 (May 2025)` |
| Gemini 2.5 Flash | `gemini/gemini-2.5-flash` (gemini) and `gemini-2.5-flash` (vertex) ($0.30/$2.50) | `gemini-2.5-flash` | `Gemini 2.5 Flash` | `Gemini 2.5 Flash` (Google DeepMind) |
| Mistral Large (Nov 24) | only `vertex_ai/mistral-large-2411`; first-party `mistral/mistral-large-latest` is now a newer model | `mistral-large-2411` | `Mistral Large (2411)` | **`Mistral Large 2.1`** |
| Qwen3-235B Instruct 2507 | `deepinfra/Qwen/Qwen3-235B-A22B-Instruct-2507`, `qwen.qwen3-235b-a22b-2507-v1:0` (Bedrock), … | `qwen3-235b-a22b-instruct-2507` | `Qwen3-235B-A22B-Instruct (2507)` | `Qwen3-235B-A22B (Jul 2025)` |
| o3 | `o3-2025-04-16` and `o3` ($2/$8) | `o3-2025-04-16` | `o3 (2025-04-16)` | `o3` (**2024-12-20**, the announcement date) |
| Grok 4 (0709) | **no `xai/grok-4*` base key**; only `azure_ai/grok-4`, `oci/xai.grok-4` | `grok-4-0709` | `Grok 4 (0709)` | `Grok 4` (2025-07-09) |
| Claude Opus 4.6 | `claude-opus-4-6`, `claude-opus-4-6-20260205` ($5/$25), `anthropic.claude-opus-4-6-v1`, … | `Claude Opus 4.6`, `Claude Opus 4.6 (High)` | same | `Claude Opus 4.6` |

**How hard is the mapping?**

- **No shared identifier.** The best automatic bridges are OpenRouter's public `GET /api/v1/models`, which needs no auth and returns 469 models with `canonical_slug` and **`hugging_face_id`**, and Epoch's `Hugging Face developer id`. These cover open-weight models well and closed models poorly.
- **1:N.** LiteLLM has many provider keys per model, with different prices. The project must pick a **canonical price rule**, for example first-party, else the median across hosts, as Epoch does.
- **N:1.** LMArena lists reasoning-effort and precision variants separately ((High), (Max), (xHigh), BF16/FP8, Thinking/Non-Thinking). LiteLLM has one key, and Epoch has one model.
- **Time breaks.** LMArena renamed most models in place on 2026-10-20. Retired LiteLLM keys disappear from the file. Epoch dates are announcement dates.
- **Estimate.** For about 150–250 frontier and popular chat models, a hand-curated `dim_model_crosswalk` seed takes roughly **2–4 focused days**. Use normalised-string plus date-suffix fuzzy matching (rapidfuzz is already a MetricFlow dependency) to propose matches, then review by hand. Add dbt tests for unmapped high-vote models. A full mapping of all 3,500+ chat keys is not worth doing.

## 10. Competitors for "LLM price vs quality over time"

| Competitor | What it shows | History? | Access / license | What remains for us |
|---|---|---|---|---|
| **Artificial Analysis** (https://artificialanalysis.ai/trends) | "Cost per Intelligence Index Task, Over Time", "**Output Price, Over Time**" at capability thresholds, open vs proprietary over time, by-country trends | Yes, on the website | Free API needs a key and attribution, at **10 requests/day**, `/api/v2/language/models/free` snapshot only. **The legacy `/api/v2/data/*` endpoints returned HTTP 410, retired 2026-11-04** (live call). Spec: https://artificialanalysis.ai/api/v2/openapi | No adoption angle and no downloadable history; Pro-gated |
| **Epoch AI** | Rates of decline at fixed capability (9–900×/yr in 2025; 13×/yr in 2026-09) | Yes (research outputs) | CC BY, code on GitHub | No adoption or demand link; updated per paper, not daily |
| **OpenRouter rankings** | Top 50 models per day by tokens, plus an "other" row; app rankings | **Yes, daily since 2025-01-01** | `GET /api/v1/datasets/rankings-daily` with a free API key, 30 requests/min and 500/day, **CC BY 4.0**, citation required (https://openrouter.ai/docs/api/api-reference/datasets/get-rankings-daily.md, acc. 2026-11-10; unauthenticated call → 401) | This is an **adoption signal we should use**, alongside PyPI. It is not a competitor on causality. Tokens are counted with each provider's own tokenizer, so they are not comparable across providers. |
| **Simon Willison llm-prices** (https://www.llm-prices.com) | Current prices for 191 models; `historical-v1.json` | Thin: 204 records over 190 models, **only 13 dated price changes** (from_date ≥ 2025-02-08) | Repo `simonw/llm-prices` has **no license file** | History too sparse for a time series |
| **sanand0/llmpricing** (https://sanand0.github.io/llmpricing/, MIT, updated 2026-11-08) | **Arena Elo vs price, Pareto frontier, month slider since 2023**; this is the closest to our idea | Partial: "Each model has **one representative price, not a historical price series**" (README); `elo.csv` holds one Elo per model, 522 rows | MIT | No true price or Elo history and no adoption. It also mixes slug and display names, so it hits the same LMArena rename. |
| **tokencanopy/price** (https://github.com/tokencanopy/price, MIT) | Price per platform for 1,057 models on 82 platforms, refreshed every 6 hours, "git is the time-series database" | Only since **2026-09-02** (71 snapshots) | MIT | Short history and no quality join. It is a useful dispersion reference: median 2.0× spread across hosts for open models. |
| Small trackers (mohamadkhani/llm-leaders, LLMPodium SDKs, Potowai/improved-system) | Elo × current OpenRouter price | No | Various | Toy-scale |
| LMArena itself | Leaderboard plus the `full` split history | Yes | CC-BY-4.0 | Quality only |

**What the portfolio project can still own**

1. A **governed, reproducible daily price panel back to 2023** rebuilt from LiteLLM git history. Nobody publishes this as a dataset: Epoch and AA show charts, and tokencanopy only goes back to 2026-09.
2. **Adoption joined to price and quality.** Daily PyPI SDK downloads (ClickPy) plus OpenRouter token share, studied with event-study or diff-in-diff around price cuts and new-model launches. Epoch says outright that it does not do this ("no user stays permanently on the cost frontier").
3. A **semantic layer** of MetricFlow metrics (price per Elo point, cost at a fixed quality threshold, adoption elasticity) plus an **evaluated question-answering agent** over those metrics. No competitor offers either.

---

## Gotchas that change the design

1. **Rebuild the price history from git; never use only the current snapshot.** LiteLLM deletes retired models, and the 2023 schema had 19 entries and 3 fields. Ingest one commit per day through a blobless partial clone with a token. Normalise fields across schema versions. Store `observed_at` as the commit time, and document that it is not the provider's effective date. Future-dated prices, such as Gemini 3.8 Flash doubling on 2027-01-01, have to come from another source (llm-prices `historical-v1.json` has that one).
2. **Quality cannot be compared across LMArena's method changes.** Elo → Bradley-Terry (2024-01-09), style control made default with a scale offset (2025-05-16), and re-weighting (2025-07-23). Use **within-snapshot ranks or percentiles**, or segment the series at these dates. Do not use raw rating differences across them. Build a **name crosswalk inside LMArena itself** for the 2026-10-20 rename, which changed about 390 of 416 names.
3. **Epoch has already published the headline finding** (13×/yr; 9–900×/yr). Do not position "how fast is quality-adjusted price falling" as novel. Reproduce Epoch's number as a validation check, then make **adoption response** the centerpiece.
4. **List prices are not monotonically falling at the cheap end.** Gemini Flash-Lite went from $0.10/$0.40 (2.5) to $0.25/$1.50 (3.1) to $0.30/$2.50 (3.5). 3.8 Flash doubles on 2027-01-01. Epoch's own note warns that a compute crunch could raise token prices. Metrics must be **quality-adjusted**, and the dashboard should show both directions.
5. **PyPI is a noisy adoption proxy.** uv/CI dominates, weekends drop by about 40%, and about 83% of installs are from the US. Dependency inflation means openai is pulled in by litellm and others. Google's SDKs migrated from `google-generativeai` to `google-genai`. Use ClickPy, filter to installer ∈ {pip, uv, poetry}, model weekday effects, and sum the two Google SDKs. Add **OpenRouter rankings-daily** (from 2025-01-01, CC BY 4.0) as a second, usage-based adoption measure.
6. **Data-source choices.**
   - ClickPy is the primary download source. pypistats only reaches about 217 days back. A BigQuery backfill likely exceeds one month of the sandbox's 1 TiB, and sandbox tables expire after 60 days.
   - On ClickPy, always `sum(count) … GROUP BY date`. Assert row counts, because `result_overflow_mode=break` can truncate without an error.
   - hub-stats is snapshot-only. To get HF download history, **start snapshotting now** with a daily job; reconstructing from 4,551 commits of about 1.7 GB each is impractical.
7. **The evaluated agent on Gemini:**
   - Pin exact stable IDs.
   - Log the model ID and `usage` that come back on every response, because deprecated IDs **auto-route** to other models, e.g. 2.5 Flash → 3.5 Flash-Lite on 2026-12-01.
   - Pre-estimate cost with `count_tokens`.
   - Expect the JSON Schema length and uniqueness constraints to go unenforced, so validate with Pydantic yourself.
   - Free-tier prompts may be read by human reviewers and used for training. Keep only public data in prompts.
   - A public demo serving EEA, UK or Swiss users must use the paid tier.
   - The docs moved to `aistudio.google.com/docs`, so update any links in the repo.
8. **Pin DuckDB below 2.0 for now** (`duckdb>=1.5,<2`) until dbt-duckdb declares 2.0 support. The MotherDuck extra is still on 1.5.5. Use Python 3.12. dbt-core 1.12 brings MetricFlow 0.213 as a core dependency. Write semantic models in the **new 1.12 YAML spec**.
9. **Use Observable Framework, not Evidence, for a static GitHub Pages site.** Current Evidence Core self-hosting is a server talking to a live warehouse, and the static legacy version is no longer actively released. Framework bundles DuckDB-Wasm aligned to DuckDB 1.1.1, so **ship Parquet files, not `.duckdb` files** written by a newer engine (likely unreadable by the older engine; not tested). Expect slow upstream releases.
10. **Entity resolution is a first-class seed table, not an afterthought.** It needs a hand-curated `dim_model_crosswalk` with these columns: `model_family`, `canonical_model`, `litellm_keys[]`, `arena_names[]` (slug and display), `epoch_model`, `hf_id`, `openrouter_slug`, `api_release_date` and `announce_date`. Seed it from OpenRouter `hugging_face_id` and Epoch `Hugging Face developer id`. Write an explicit rule for Arena variants such as (High), (Max), BF16 and FP8: either collapse them to the best variant or keep them as separate SKUs. Add dbt tests that fail when an Arena model with many votes is left unmapped.
