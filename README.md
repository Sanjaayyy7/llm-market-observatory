# LLM Market Observatory

**Do top-tier LLMs ever cut their launch price?**

**v1.0 answer: no market estimate.** Validation against Epoch AI failed as pre-registered (2026-11-17):
LiteLLM's public price file missed provider cuts we could verify. On the 19 headline models Epoch AI
observed, 4 rows are panel errors. 3 of them come from 2 provider cuts LiteLLM never recorded
(Gemini 1.5 Pro, 2024-10-01, on both versions; Mistral Large 2, 2024-09-17), and 1 row's price change has
no provider source. The kill criterion's own action applies, so this project publishes no market number
([design §18](docs/03-spec/design.md), [DECISIONS "G5 kill action"](docs/DECISIONS.md)).
Code: [`analysis/epoch_check.py`](analysis/epoch_check.py), with verdicts in
[`dbt/seeds/seed_epoch_mismatch_audit.csv`](dbt/seeds/seed_epoch_mismatch_audit.csv). The pre-registration
is [`docs/prereg/epoch-check.md`](docs/prereg/epoch-check.md).

What it does publish is a governed, tested history of first-party list prices, rebuilt day by day from
LiteLLM's git history since 2023-09-06. It also publishes a labeled measurement of the cuts recorded in
that file, with its limits stated.

## The numbers, each linked to its model and test

Values as of LiteLLM commit `ea987e7` (data through 2026-11-16). The site's data stamp always names the
commit it was built from.

| Number | Value | Model / code | Test |
|---|---|---|---|
| Dataset measurement: share of 105 top-tier models with a list-price cut recorded in LiteLLM's file within 365 days of listing (Kaplan–Meier) | 9.5% (95% CI 5.1–17.6%), 9 cuts | [`mart_launch_price_survival`](dbt/models/marts/mart_launch_price_survival.sql), [`analysis/survival.py`](analysis/survival.py) | [`test_fit_km_matches_golden`, `test_km_matches_statsmodels`](tests/analysis/test_survival.py) |
| Verified-only lower bound (a cut no provider page confirms counts as no change) | 5.1% (95% CI 2.2–11.9%), 5 cuts | [`analysis/survival.py`](analysis/survival.py) | [`test_verified_data_fix_becomes_censored_at_end_ts`](tests/analysis/test_survival.py) |
| Recorded first cuts that are data fixes, not verified provider cuts | 4 of 9 | [`mart_cut_audit`](dbt/models/marts/mart_cut_audit.sql), [`seed_cut_audit.csv`](dbt/seeds/seed_cut_audit.csv) | [`cut_audit_covers_scored_events`](dbt/tests/cut_audit_covers_scored_events.sql), [`cut_audit_evidence`](dbt/tests/cut_audit_evidence.sql) |
| Cut incidence at 365 days with retirement as a competing risk (Aalen–Johansen), against 1 − KM | 9.31% vs 9.54% | [`analysis/export.py`](analysis/export.py) (`cut_incidence_365`) | [`test_cut_incidence_equals_one_minus_km_without_competing_events`](tests/analysis/test_export.py) |
| Epoch AI's GPT-4-level GPQA-Diamond price trend, reproduced from their pinned data | 42.02×/year (published 42.02×) | [`analysis/epoch_check.py`](analysis/epoch_check.py) | [`test_reproduces_epoch_published_factor`](tests/analysis/test_epoch_check.py) |
| Crosswalk coverage, all in-scope Arena names (pre-set bar 90%: **FAILED**) | 223/303 = 73.6% | [`int_crosswalk_coverage`](dbt/models/intermediate/int_crosswalk_coverage.sql) | [`crosswalk_coverage_overall`](dbt/tests/crosswalk_coverage_overall.sql) (warn, disclosed) |
| Crosswalk coverage, closed models (kill bar 80%) | 184/211 = 87.2% | same | [`crosswalk_coverage_closed`](dbt/tests/crosswalk_coverage_closed.sql) |
| Every uncovered name has a reason code and evidence URL | 80 of 80 | [`seed_crosswalk_uncovered.csv`](dbt/seeds/seed_crosswalk_uncovered.csv) | [`crosswalk_uncovered_has_reason`](dbt/tests/crosswalk_uncovered_has_reason.sql) |
| SDK adoption around first cuts (event study) | 6 events, below the pre-registered floor of 8: descriptive only | [`analysis/event_study.py`](analysis/event_study.py), [`docs/prereg/event-study.md`](docs/prereg/event-study.md) | [`test_verdict_line_below_and_at_floor`](tests/analysis/test_event_study.py) |

Definitions (price, cut, correction, top-tier, listing) are in the [PRD §6](docs/03-spec/PRD.md) and on the
site's Methods page. Sources and licenses: [docs/DATA.md](docs/DATA.md).

## Role map (one artifact per role)

| Role | Artifact |
|---|---|
| Analytics data engineering | Deterministic git replay of LiteLLM's price file into raw Parquet ([`ingest/`](ingest/)), staging and an SCD2 price dimension ([`dim_model_price`](dbt/models/marts/dim_model_price.sql)) with a hand-worked golden test, freshness table, CI on committed fixtures ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) |
| Product analytics | The static site (Home, Price explorer, Methods) with metric definitions, coverage disclosure and a data stamp ([`site/`](site/)); the decision record ([`docs/DECISIONS.md`](docs/DECISIONS.md)) |
| Product data science | Survival analysis with an audit-based lower bound and a competing-risk check ([`analysis/survival.py`](analysis/survival.py)); a pre-registered external validation that failed and was reported as failed ([`analysis/epoch_check.py`](analysis/epoch_check.py)); a pre-registered event study with placebos ([`analysis/event_study.py`](analysis/event_study.py)) |
| AI / evals | Deferred (G10). Not in v1.0 |

## Rebuild

```bash
git clone <this repository's URL> llm-market-observatory && cd llm-market-observatory
make all   # fetch → build → analyze → export → site
```

Prerequisites: [uv](https://docs.astral.sh/uv/) (it installs the pinned Python 3.12), Node 24 (`.nvmrc`), and
network access to the sources in [docs/DATA.md](docs/DATA.md). `make fetch` replays the full LiteLLM git
history. `make ci` needs no network: it runs ruff, pytest and `dbt build --target ci` on committed fixtures.

## Docs

[docs/STATUS.md](docs/STATUS.md) has the current stage. [docs/README.md](docs/README.md) maps every document,
from research and council memos to the spec and the build plan.
