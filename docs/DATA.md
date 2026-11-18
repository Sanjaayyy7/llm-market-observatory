# Data sources and licenses

Every source this project reads, what we take from it, its license as stated by the source, and
how the input is pinned. Licenses were checked on 2026-11-18 against the URLs given.

| Source | What we use | License or terms (quoted from the source) | Pinning |
|---|---|---|---|
| **LiteLLM** — [`BerriAI/litellm`](https://github.com/BerriAI/litellm), file `model_prices_and_context_window.json` | Daily replay of the price file's git history from 2023-09-06: per-key input/output price, provider and mode | MIT for content outside `litellm/enterprise/`: "Content outside of the above mentioned directories or restrictions above is available under the MIT license" ([LICENSE](https://github.com/BerriAI/litellm/blob/main/LICENSE)). The price file is outside that directory | Each site build names the LiteLLM commit it read (data stamp). The replay hash is deterministic (plan Task 2) |
| **LMArena** — Hugging Face dataset [`lmarena-ai/leaderboard-dataset`](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset) | `text` / `overall` leaderboard snapshots: model name, rating, rank, organization | CC BY 4.0 (dataset card `license: cc-by-4.0`) | Partitioned by fetch date under `data/raw/arena/` |
| **Epoch AI** — AI models dataset ([`all_ai_models.csv`](https://epoch.ai/data/all_ai_models.csv)) | Model metadata for the crosswalk | "Epoch AI's data is free to use, distribute, and reproduce provided the source and authors are credited under the Creative Commons Attribution license" ([epoch.ai/data](https://epoch.ai/data)) | Partitioned by fetch date under `data/raw/epoch/` |
| **Epoch AI** — data insight ["LLM inference prices have fallen rapidly but unequally across tasks"](https://epoch.ai/data-insights/llm-inference-price-trends) and its code [`epoch-research/llm-benchmark-efficiency`](https://github.com/epoch-research/llm-benchmark-efficiency) | The GPQA-Diamond price observations behind the 42×/year GPT-4-level trend. Used only to check our panel (validation), never as our series | "Epoch's work is free to use, distribute, and reproduce provided the source and authors are credited under the Creative Commons BY license." Their price data "comes from both Artificial Analysis and our own database of API prices" (insight page) | Two CSVs committed verbatim as seeds from commit `34b923314338360d1b1bbed6ec30d9299e54fdae`; their sha256 is in `docs/prereg/epoch-check.md` |
| **Artificial Analysis** | Indirectly: part of the Epoch price data above | Credited here because Epoch's insight credits it as a price source | Via the Epoch seeds |
| **tokencanopy** — [`tokencanopy/price`](https://github.com/tokencanopy/price), `data/current/prices.csv` | A level spot-check of our latest prices | MIT ([LICENSE](https://github.com/tokencanopy/price/blob/main/LICENSE)) | Partitioned by fetch date. Its rows for first-party platforms come from its OpenRouter feed (`source = openrouter`), so the spot-check tests that feed, not provider pages (Methods → Data quality) |
| **PyPI downloads via ClickPy** — public `play` user on `sql-clickhouse.clickhouse.com` | Daily download counts of provider SDK packages (descriptive adoption view) | ClickPy's code is Apache-2.0 ([LICENSE](https://github.com/ClickHouse/clickpy/blob/main/LICENSE)). The counts come from PyPI's public download logs (ClickPy README). The README states no separate license for the hosted counts; we publish only daily aggregates per package | Partitioned by fetch date under `data/raw/pypi/` |
| **Provider pages** (pricing, changelogs, deprecations, news) | Evidence for crosswalk rows, the cut audit, reroutes and the uncovered-name reasons | Quoted facts with their URL, row by row, in `dbt/seeds/*.csv` (`evidence_url`, `source_url`, `announce_url` columns) | URL plus fetch date in the seed or in `docs/DECISIONS.md` |

## Citation for the Epoch insight

Ben Cottier et al. (2025), "LLM inference prices have fallen rapidly but unequally across tasks".
Published online at epoch.ai. Retrieved from
'https://epoch.ai/data-insights/llm-inference-price-trends' [online resource].

## What the site publishes

Parquet and JSON files under `site/src/data/`, written by `analysis/export.py` (`make export`):
model prices, price changes, the survival mart, the cut audit, coverage and the uncovered-name
reasons, freshness, the event-study panel, and the analysis outputs (`headline.json`,
`epoch_check.json`, `event_study.json`, `methods.json`, `stamp.json`). The DuckDB warehouse is never
published. Export refuses to run while any hand-matched crosswalk row or model row lacks an
approver (`test_export_refuses_unapproved_crosswalk`).

## What we do not use

No paid API, no scraped pages beyond the cited provider pages, and no LLM calls anywhere in the
data pipeline, CI or the site.
