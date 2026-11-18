# design.md — LLM Market Observatory

**Status:** v1.2, approved by delegation (user, 2026-11-15: "take over from here") · **Date:** 2026-11-15 · **Deadline:** original 2026-11-15 passed; the user sets the new date
**Reads with:** `PRD.md` (what/why, requirement IDs), `docs/02-council/04-chair-verdict.md` (scope, gates).
*(my call)* marks defaults Claude chose; everything else comes from the user, the council, or the evidence (E/R IDs in `docs/01-research/research-brief.md`).

**What changed in v1.2** (from `docs/04-feasibility-spike/feasibility-spike.md`)
- Canonical ID rule relaxed: stable undated IDs count; moving aliases excluded by rule (§6).
- Headline is the KM 365-day cut share; the median is secondary (PRD §3).
- Event study descriptive only; the G10 eval is deferred past v1.0 (PRD §11).
- Kill criteria added (§18).

**What changed in v1.1**
- **Builder-check resolutions (my calls):**
  - The Epoch check target is now the 2025 list-price paper (§9.2).
  - One canonical model = one versioned API ID; moving aliases are excluded (§6).
  - Event = each top-tier model's first cut, clustered per SDK group (PRD §8).
  - Eval arm B queries the same marts as arm A (§13).
- **User decisions:**
  - The user approves the model list plus judgment matches.
  - No OpenRouter key, so the rankings source is dropped.
  - Gemini free tier only.
  - Public repo, Pages and weekly refresh approved.

## 0. Intent in one paragraph
This is a public data product for analysts tracking LLM API list prices, developers choosing providers, and researchers.
The project rebuilds a **governed history of LLM API list prices since 2023** from LiteLLM's git history. It answers **how long top-tier models keep their launch price**, then tests honestly, under pre-registration, **whether the first cut moves developer adoption**.
Everything is built by AI, verified by tests, and stated with its limits.

## 1. Architecture

```
SOURCES (licensed)                 INGEST (Python, idempotent)        WAREHOUSE (DuckDB + dbt)              OUTPUTS
LiteLLM git history (MIT) ──────▶ replay_litellm.py ─┐              staging  → intermediate → marts   ┌▶ analysis/*.py (KM, Epoch, event study)
LMArena HF parquet (CC BY) ─────▶ fetch_arena.py ────┤ data/raw/*.parquet   (tests, contracts,       ├▶ exports/*.parquet ─▶ site/ (Observable
Epoch AI CSV (CC BY) ───────────▶ fetch_epoch.py ────┤ (gitignored)          freshness, grain)        │                        Framework) ─▶ GitHub Pages
ClickPy SQL/HTTP (CC BY 4.0) ───▶ fetch_clickpy.py ──┘                                                 └▶ evals/ (static, offline-tested; Gemini free tier, once)
tokencanopy/price (MIT) ────────▶ fetch_tokencanopy.py (level spot-check only)
```

**Rules**
- Every fetcher writes Parquet to `data/raw/<source>/` and appends one row to `data/raw/_freshness.parquet`.
- Fetchers are idempotent: re-running a run date overwrites that run's partition.
- dbt never calls the network. All network I/O lives in fetchers.
- One command, `make all`, runs: fetch → `dbt build` → analysis → export → site build.

## 2. Repo layout (*my call*)

```
llm-market-observatory/
  Makefile                 # all, fetch, build, analyze, export, site, test, ci
  pyproject.toml uv.lock   # Python 3.12, pinned
  ingest/                  # fetchers + replay (stdlib + duckdb + httpx)
  dbt/                     # dbt project (profiles: dev, ci)
    seeds/                 # crosswalk, models, provider map, cut audit, fixtures (ci)
    models/{staging,intermediate,marts}/
    semantic_models/       # MetricFlow (G10 only)
  analysis/                # survival.py, epoch_check.py, event_study.py (+ tests)
  evals/                   # questions.yaml, harness.py, scorer.py, cache/, ledger.csv
  site/                    # Observable Framework app (src/*.md, data/*.parquet)
  tests/                   # pytest: ingest, analysis, evals
  docs/                    # STATUS, DECISIONS, DATA, prereg/; phase history 00-charter/ … 05-build-plan/ (see docs/README.md)
  .github/workflows/       # ci.yml, refresh.yml, pages.yml
```

## 3. Stack and pins (E28, E29, E10)

| Layer | Choice | Pin / note |
|---|---|---|
| Runtime | Python 3.12, `uv` | `uv.lock` committed |
| Engine | DuckDB | `duckdb>=1.5,<2` (DuckDB 2.0 file-compat risk, E10a/E28) |
| Transform | dbt-core + dbt-duckdb | `dbt-core~=1.12.6`, `dbt-duckdb~=1.11.1` |
| Semantic layer | dbt-metricflow (G10 only) | `dbt-metricflow~=0.15.0`; G10 probe proves `mf query` works first |
| Analysis | pandas, statsmodels, lifelines | lifelines for Kaplan–Meier (well tested; no hand-rolled survival math) |
| Site | Observable Framework (Node 20 LTS) | Static build; ships Parquet, never `.duckdb` (bundled DuckDB-WASM 1.1.1, E29) |
| CI | GitHub Actions, public repo | Free standard runners (E15) |
| Lint/test | ruff, pytest | — |

**No dlt, Airflow, Dagster or Elementary** *(my call, in DECISIONS.md)*. There are 5 small sources, and cron in Actions covers scheduling. That gives fewer moving parts to defend. Elementary is cut outright (E10b).

## 4. Sources and ingestion

| Source | Fetcher | Method | Lands as | License / attribution |
|---|---|---|---|---|
| LiteLLM price file | `replay_litellm.py` | Blobless clone + git replay (§5) | `raw/litellm/snapshot_date=*/part.parquet` | MIT; credit BerriAI/litellm |
| LMArena leaderboard | `fetch_arena.py` | HF parquet via `huggingface_hub` / `hf://` (text configs only) | `raw/arena/` | CC BY 4.0; cite lmarena-ai |
| Epoch AI | `fetch_epoch.py` | HTTPS CSV from `epoch.ai/data/*.csv` (models + benchmark files if present) | `raw/epoch/` | CC BY; cite Epoch AI |
| ClickPy | `fetch_clickpy.py` | HTTPS SQL to `sql-clickhouse.clickhouse.com` (user `play`), table `pypi.pypi_downloads_per_day` (installer-level table if present) | `raw/pypi/` | PyPI data CC BY 4.0 |
| tokencanopy | `fetch_tokencanopy.py` | Latest snapshot from repo (MIT) | `raw/tokencanopy/` | MIT; spot-check only |

**G1 source probes** (`make probe`): each fetcher runs in probe mode and records row count, min/max date and schema hash to `_freshness`. The probe must also confirm three things the design depends on:
1. The Arena config names and columns, including the post-2026-10-20 display names.
2. Whether Epoch publishes benchmark scores usable for §9.2. If not, G5 escalates to the user.
3. The ClickPy table and the installer/country columns.

It also verifies that GitHub disables scheduled workflows on idle public repos (chair: verify). If so, the refresh workflow commits a heartbeat (§11).

**Freshness SLA** = the measured cadence per source from G1, never claimed "daily" (R10). Expected: LiteLLM several commits a day, Arena irregular, Epoch daily, ClickPy daily.

## 5. Git-replay SCD2 algorithm (the DE centerpiece)

**Replay** (`replay_litellm.py`, deterministic):
1. Clone with `git clone --filter=blob:none --no-checkout https://github.com/BerriAI/litellm` into `data/cache/litellm.git`. Later runs use `git fetch`.
2. Run `git log --follow --format='%H|%cI' --name-status -- model_prices_and_context_window.json` to list commits with the file's path *at each commit*. `--follow` crosses the 2023-09-06 rename (E20).
3. Keep the **last commit per UTC day** → `(snapshot_date, sha, commit_ts, path)`.
4. For each day, run `git show <sha>:<path>` and parse the JSON.
   - Invalid JSON → log the sha to `_replay_errors` and skip that day. Never guess.
   - Drop the `sample_spec` key.
5. Normalize across schema versions → `model_key, litellm_provider, mode, input_cost_per_token, output_cost_per_token`. Missing fields → null. Unknown extra fields are ignored. The mapping lives in a code table, unit-tested on historical samples.
6. Write one Parquet partition per `snapshot_date`. A model *absent* from a snapshot is how deletions are detected downstream.
7. **Incremental:** `data/cache/replay_state.json` stores the last processed sha. A run replays only newer days.
8. **Determinism:** write sorted rows; `replay_hash` = sha256 over the sorted partition files. **G3 requires two clean runs to produce the same hash.**

**SCD2 in dbt** (`dim_model_price`, gaps-and-islands SQL):
1. `stg_litellm__snapshots`: one row per `(snapshot_date, model_key)`, filtered to `mode in ('chat','completion','responses')`. A null `mode` takes the key's next non-null mode; a key never given a mode is kept. *(v1.2, spike: the v1.1 filter dropped the whole 2023-09-06 snapshot, where all 19 keys have null mode, and `responses`-only models such as `gpt-5.4` and `gpt-5.2-pro`.)* *(v1.2.1, G3b mini-council: the filter is per row. A null mode fills from the next non-null mode, else the previous one. A key reclassified out of scope leaves the set there; 41 keys on 2026-11-16, all realtime, image or TTS. Judging scope by a key's latest mode was rejected: it erased `gemini/gemini-1.5-flash` and its real 2024-09-10 cut after a 2026-03 relabel to `embedding`.)*
2. `int_price_versions`:
   - Compute `price_sig = (input, output)`.
   - Flag a change when `price_sig` differs from the previous snapshot for the same key, or the key reappears after an absence.
   - `version_id` = running sum of change flags.
3. `dim_model_price`: one row per `(model_key, valid_from)`:
   - `valid_from` = first `commit_ts` of the version.
   - `valid_to` = next version's `valid_from`, or the first snapshot where the key is absent (`delisted = true`), or null if current. `delisted` means the key left the in-scope set: removed upstream, or reclassified out of scope. A later version means it returned (122 such returns, median gap 2 days).
   - `is_current` = `valid_to is null`.
4. Tests:
   - unique `(model_key, valid_from)`;
   - no overlapping intervals per key (custom test);
   - exactly one `is_current` row per non-delisted key;
   - `valid_from < valid_to`;
   - dbt unit tests on a hand-built 6-snapshot fixture covering change, revert, deletion, reappearance and rename.

## 6. Crosswalk (G2, R2, E30)

**Seeds**
- `seed_models.csv`: one row per `canonical_model_id`. Columns: `provider, family, display_name, open_weights, announce_date, announce_url, approved_by`.
- `seed_model_crosswalk.csv`: one row per `(source, source_key)`. Columns: `canonical_model_id, match_method ∈ {exact, hf_id, manual}, approved_by`. `source ∈ {litellm, arena, epoch}`.
- `seed_provider_map.csv`: `litellm_provider → provider, is_first_party, sdk_group`.

**Workflow**
1. Claude drafts the rows. It seeds from:
   - OpenRouter's public `/api/v1/models` (`hugging_face_id`, `canonical_slug`). No key is needed; it is used as a matching aid at draft time only, never fetched in the pipeline and never republished.
   - Epoch's HF developer id.
   - Manual matches for closed models.
2. **Approval (user decision v1.1):**
   - The owner approves every row of `seed_models` (the canonical list) and every `match_method = manual` row, by setting `approved_by`.
   - `exact` and `hf_id` rows are approved by tests: string or ID equality, plus the coverage tests.
3. Dev builds may run on draft rows.
4. The export step (and therefore Pages and the README numbers) refuses to run while any required row is unapproved.

**Scope:** every model that is ever top-tier (PRD §6) in the Arena text history since 2023-05, plus each one's first-party LiteLLM keys.

**What one canonical model is** (builder-check resolution, my call):
- **One canonical model = one pinned API model** *(v1.2)*: a dated or versioned ID (`gpt-4o-2024-08-06`, `claude-3-5-sonnet-20241022`) **or** a stable undated ID with no dated twin (`gpt-5.4`, `gemini-3-pro-preview`).
- **Moving aliases are flagged and excluded from the headline population.** A key is a moving alias if (a) it contains `latest`; (b) it is undated and a key in the same group equals it plus a date suffix (`gpt-4o` → `gpt-4o-2024-08-06`, `o3` → `o3-2025-04-16`; dedupe to the dated twin); or (c) the provider documents it as repointing (`deepseek-chat`, `deepseek-reasoner`; listed by hand). Flag them with `is_moving_alias = true` in `seed_model_crosswalk`. They appear only in a sensitivity analysis.
  - An alias repointing to a cheaper snapshot is **never** counted as a cut.
  - So the crosswalk needs no validity dates.
- **Several first-party keys for one canonical model** (e.g. `gemini/gemini-2.5-flash` vs `gemini-2.5-flash`): use the key whose `litellm_provider` is the provider's own first-party value (`seed_provider_map.is_first_party`).
  - If two first-party keys disagree on the same day, a warn-level test fires. The earlier-listed key wins, and the conflict count goes on the Methods page.
- **Arena variants** of the same API model ("thinking", "(high)") map to one canonical model. Its rank is the best variant's rank within the snapshot. Variants that are separate API IDs stay separate.

**Tests**
- unique `(source, source_key)`;
- not-null `canonical_model_id`;
- `relationships` to `seed_models`;
- coverage ≥90% of in-scope top-tier models, and ≥80% of closed ones.

If coverage fails: panel-only scope. The headline is restricted to the mapped set and the coverage is shown in the README.

*v1.2.2 (G2 council, 2026-11-17):* only closed coverage <80% (or <30 top-tier) is the §18 kill, which means no headline. When overall coverage is below 90%, a warn-level test fires, and the shortfall is disclosed on README and Methods. The canonical ID is the bare first-party API ID, and `canon()` applies to Arena and Epoch names only (DECISIONS 2026-11-17).

## 7. Data model (grain declared, each enforced by a uniqueness test)

| Model | Grain (one row per) | Notes |
|---|---|---|
| `stg_litellm__snapshots` | snapshot_date × model_key | from replay |
| `stg_arena__leaderboard` | snapshot_date × arena_model × category | text configs; rank recomputed within snapshot |
| `stg_epoch__models` / `stg_epoch__benchmarks` | epoch model / model × benchmark | |
| `stg_pypi__downloads` | date × package (× installer if available) | |
| `dim_model` | canonical_model_id | from seeds |
| `dim_model_price` | model_key × valid_from | SCD2 (§5) |
| `fct_model_price_daily` | canonical_model_id × date | first-party, standard tier, blended 3:1; date spine from listing to delist/today |
| `fct_price_change` | canonical_model_id × change_ts | pct change, `is_cut` (≥10%), `is_correction` |
| `fct_arena_rank` | canonical_model_id × snapshot_date | rank, rank_percentile, method_era (splits at Jan-2024, May-2025, Jul-2025; E21) |
| `mart_launch_price_survival` | top-tier canonical_model_id | listed_at, first_cut_at, days_at_launch_price, censored |
| `mart_cut_audit` | audited cut | observed_ts, announced_date, lag_days, source_url (seed `seed_cut_audit.csv`) |
| `fct_sdk_downloads_daily` | sdk_group × date | Google SDKs summed (E24) |
| `mart_event_study_panel` | event_id × sdk_group × rel_day | built only after prereg commit (G8) |
| `source_freshness` | source × run_ts | rows, max_date, sla_days, is_stale |

**Event-date audit (G4):**
- Sample: 20 cuts stratified by provider *(my call)*. For each, Claude finds the provider's announcement (changelog or pricing page) and records its URL. The owner spot-checks.
- Output: the commit-lag distribution `±d` in the headline.

## 8. Metric definitions (one definition each; README + site "Methods" page)

| Metric | Definition |
|---|---|
| `blended_price_per_mtok` | `(3·input + 1·output)/4 × 1e6`, first-party standard tier |
| `days_at_launch_price` | first_cut_at − listed_at (days); censored at today or at the final delisting (the model's last version is `delisted` and no later version exists; a temporary absence does not censor, v1.2.1) |
| `km_median_days_at_launch_price` | Kaplan–Meier median over top-tier models, with IQR and n |
| `share_cut_within_365d` | KM-estimated 1 − S(365) (the fallback headline) |
| `cut_depth_pct` | price drop at the first cut |
| `commit_lag_days` | announced − observed, over the audited sample |
| `sdk_downloads_7d` | trailing 7-day sum of downloads, per SDK group |

MetricFlow semantic models mirror these for G10 only. If G10 is cut, the definitions still live in dbt docs and the Methods page.

## 9. Analyses (`analysis/`, each with pytest on fixtures)

1. **Survival (G6):**
   - lifelines `KaplanMeierFitter` on `mart_launch_price_survival`, producing the median, IQR and n.
   - Sensitivity checks reported, not headlined: all models vs top-tier; cut thresholds of 5% and 20%.
2. **Epoch check (G5)**. *Superseded 2026-11-16 by DECISIONS "G5 replan" (plan Task 8): we reproduce Epoch's 42×/yr from their own data and check our prices against theirs observation by observation. The trend band below is kept for history.* *Builder-check resolution, my call:* replicate the method that matches ours.
   - **Not** "The plunging price of thought" (13×/yr). That paper uses transcript costs, not list prices.
   - The target is Epoch's **2025 Data Insight** "LLM inference prices have fallen rapidly but unequally across tasks" (2025-03-12). Its method matches ours: 3:1 blend, list prices, first-party, reasoning models excluded.
   - **Pre-committed spec** (`docs/prereg/epoch-check.md`, committed before the code). Read the exact threshold value and date window from Epoch's repo `epoch-research/llm-benchmark-efficiency` at G1 and freeze them in the prereg:
     - **Milestone:** GPT-4-level on GPQA Diamond.
     - **Target:** ~40×/yr.
     - **Window:** Epoch's own.
     - **Tolerance:** ×/÷2 (20–80×/yr).
   - **Method:** for each date, take the cheapest blended price among non-reasoning models scoring ≥ the threshold, using Epoch's benchmark scores joined through the crosswalk. Fit log price vs time and annualize the slope.
   - The independent part is our price source (LiteLLM git history); Epoch's prices come from Artificial Analysis.
   - **If G5 fails:** one diagnosis pass. If it still fails, escalate to the user before G7. Until resolved, the Home page shows "validation pending", not the number.
   - If Epoch's benchmark scores or thresholds can't be obtained at G1, **stop and ask the user**. Do not substitute Arena rank; that would no longer be a replication.
   - **Level spot-check:** our current blended price vs tokencanopy's first-party price for 20 models, within 5%.
3. **Event study (G8–G9):**
   - The pre-registration (`docs/prereg/event-study.md`, from PRD §8) is committed **before** `event_study.py` exists. CI enforces this with a check that the prereg commit predates the first commit touching `analysis/event_study.py`.
   - Spec: OLS with event-window dummies, SDK-group and day-of-week fixed effects, HAC standard errors. Placebos: 100 random pseudo-dates per group, plus the control package.
   - All results are published, including nulls. Below the power floor: descriptive plot plus one placebo only.
   - **v1.2: the floor is not met (spike: 3–6 isolated events).** The shipped analysis is descriptive: per-event download paths −28…+28 normalized to the pre-window mean, plus the placebo distribution. The OLS/HAC spec above is not run.

## 10. Freshness and quality
- `source_freshness` is computed every run.
- `dbt source freshness`-style checks plus a singular test fail the build when any source is past its SLA.
- CI on `main` therefore goes red when data is stale (chair: decay).
- Replay errors and schema drift are counted and surfaced on the Methods page.

## 11. CI/CD
- **`ci.yml`** (PR + push): `uv sync --frozen` → ruff → pytest → `dbt build --target ci` against the committed **fixture seeds** (small sampled raw data) → site build → prereg-order check → secret scan (gitleaks action) *(my call)*. **No network to data sources and no Gemini in CI.**
- **`refresh.yml`** (weekly cron, Mon 06:00 UTC, plus `workflow_dispatch`) *(my call)*:
  - `actions/cache` restores the git clone and raw Parquet → incremental fetch → `dbt build --target dev` → analysis → export → commits `site/data/*.parquet` and the freshness stamp → triggers Pages.
  - Fails loudly if freshness fails. No Gemini.
- **`pages.yml`:** builds Observable Framework and deploys to GitHub Pages.
- **Keep-alive:** if G1 confirms idle-repo cron disabling, the refresh commit itself is the activity.

## 12. Dashboard: visual direction, components, UX (Bloom design.md scope)
**Direction:** editorial data journalism (FT / Economist tone).
- One idea per screen; annotation over decoration.
- Neutral greys with **one accent color**, used for the highlighted series only.
- Light and dark themes via CSS variables.
- System font stack for UI, tabular numerals for figures.
- No 3D, no gauges, no gradients.

**Pages** (Observable Framework, static):
1. **Home (first screen, G7):**
   - The question as the title.
   - The headline number in large type with its CI/IQR and n.
   - A Kaplan–Meier step chart with a censoring tick-mark legend.
   - A data stamp: "Data as of <max dates> · LiteLLM commit <sha7> · rebuilt <run_ts>".
   - One-line caveat with a link to Methods.
2. **Price explorer:**
   - Per-model step chart of blended price (SCD2 intervals), with cut markers.
   - Provider filter; table of cuts with depth and audit lag.
3. **Adoption:**
   - *(v1.2, descriptive)* One line per event: downloads −28…+28 normalized to the pre-window mean, with the first cut marked.
   - Placebo distribution histogram with the observed post/pre ratio marked.
   - Bold verdict line: "Descriptive only: n=k events, below the pre-registered floor of 8."
   - Link to the pre-registration commit.
4. **Methods & data:**
   - Metric definitions (§8), grain table (§7) and freshness table.
   - Coverage %, the Epoch check result, sources and licenses (DATA.md).
5. **Eval** (only if G10 ships): per-arm accuracy with CI, failure taxonomy table, spend total.

**Components:** `HeadlineStat` (number, interval, n, stamp), `StepChart`, `EventLines` *(v1.2; replaces CoefPlot)*, `PlaceboHist`, `DataStamp`, `CaveatNote`. All built with Observable Plot.

**UX patterns**
- Every number is clickable through to its definition on the Methods page.
- Every chart has a one-sentence takeaway above it and its source below.
- Mobile works at 375 px (single column).
- Charts carry `aria-label` summaries; colors pass WCAG AA; nothing is conveyed by color alone (censoring uses a tick mark).

## 13. Eval harness and Gemini guardrails (G10; last, first to cut)
**Questions:**
- `evals/questions.yaml` holds 30 fixed questions *(my call)* about the marts, e.g. "median days at launch price for Anthropic top-tier models".
- Each question has a gold answer from hand-verified SQL, stored with that SQL.
- Answer types: number with tolerance, date, or entity list.

**Arms:**
- **A (semantic layer):** Gemini returns a JSON MetricFlow query spec (metrics, group_by, where), validated against a JSON Schema. The harness runs it via `mf query`.
- **B (text-to-SQL):** Gemini returns SQL over the **same marts the semantic models sit on**. This way the eval isolates the query method and doesn't also test the data modeling (builder-check resolution, my call). It runs on a **read-only** DuckDB connection with a statement allow-list (SELECT only) and a timeout.

**Scorer:** pure functions, unit-tested on fixtures for correct, wrong, malformed, timeout and empty results. The **failure taxonomy** (wrong metric, wrong filter, wrong grain, hallucinated column, malformed output) is auto-tagged where possible and hand-reviewed.

**Guardrails** (real money; R7, R12, E27):
1. **Order:** nothing runs before G9. Never from CI, cron or the site.
2. **Offline first:** the full harness runs against `FakeLLM` and recorded fixtures. All tests pass with zero API calls.
3. **Model, free tier only ($0, user decision v1.1):** the key must come from a Google project **with no billing enabled**, because with billing on, calls are charged. The user confirms this when providing the key. Pin the exact non-deprecated model ID, verified on ai.google.dev at G10, because deprecated IDs auto-route from 2026-12-01. Temperature 0, structured output.
4. **Pre-run check:**
   - `count_tokens` over all prompts, plus the request count, compared with the free-tier limits the user's AI Studio shows. Those limits are not published (E27).
   - The user confirms the run fits before the batch.
   - A billing/quota error mid-run stops the run, leaves the cache intact, and the run resumes later from the cache.
5. **Smoke test:** 1 question × 2 arms. Parse and grade must succeed before the batch.
6. **Cache:** responses keyed by sha256(model_id, prompt, params), so nothing is paid twice.
7. **Limits:**
   - A hard cap on calls per run, plus an estimated-$ cap of **$0**: any non-free-tier pricing signal stops the run.
   - Fail fast on any unexpected error.
   - A 429 gets at most 2 retries with backoff. After that, stop and resume later from the cache.
8. **Ledger:** `evals/ledger.csv` with ts, model_id, arm, question_id, in/out tokens, est_cost_usd, cache_hit.
9. **Key:** `GEMINI_API_KEY` in env / `.env` (gitignored). It is never logged, and gitleaks runs in CI.
10. **Disclosure:** free-tier prompts may be used for training (E27). The questions are about public data, and this is stated in DATA.md.

**Honest bar:** the harness is verified correct. LLM accuracy is *measured*, not promised.

## 14. Documentation artifacts
- **DECISIONS.md:** `choice | rejected alternative | why | E-ID`. Seeded with the council's cuts and every *(my call)* in this doc.
- **DATA.md:** sources, licenses, attribution text, what is republished (only derived marts and Parquet exports).

## 15. Working protocol under usage limits
- `docs/STATUS.md` is updated at the end of every session: done, next, blockers, resume prompt.
- `main` is always shippable. Each slice goes on a branch and merges when its gate passes.
- A gate failing twice triggers the next item in the PRD §11 cut order.
- *(v1.2)* The original Sat 2026-11-14 slice cutoff passed. Ship line: G0–G7 plus descriptive G8–G9 (PRD §11). The user sets the new date.
- **User touchpoints, in build order:**
  1. G2: approve the crosswalk.
  2. G7: OK to create the repo and enable Pages, already approved in principle; Claude confirms before the first push.
  3. G10: the no-billing Gemini key and the pre-run check *(deferred with G10, v1.2)*.
  4. Release: the owner approves pushing the `v1.0` tag.
- The order of work is the gate order G0 → G9 (G10 deferred, v1.2).

## 16. Left to the builder
- Library choices inside fetchers, and exact SQL formatting.
- Fixture sizes.
- Chart styling details within §12.
- Statsmodels spec details consistent with the pre-registration.
- File naming inside folders.
- Whether a fetcher uses httpx or stdlib.

## 17. My calls for the user to check
1. 3:1 blend.
2. 10% cut threshold and the correction rules.
3. Top-tier = Arena rank percentile ≤25% within 60 days of listing.
4. Coverage thresholds of 90% and 80%.
5. Epoch tolerance ×/÷2.
6. Event-study window and power floor.
7. 20-cut audit sample.
8. 30 eval questions.
9. Weekly cron.
10. No orchestrator.
11. gitleaks in CI.
12. Repo layout.
13. *(v1.1)* Epoch target: 2025 paper, GPT-4-level GPQA Diamond, about 40×/yr ×/÷2.
14. *(v1.1, superseded by 17)* Versioned IDs only; aliases go to sensitivity analysis.
15. *(v1.1)* Events are per-model first cuts, clustered at ±28 days.
16. *(v1.1)* Eval arm B queries the marts.
17. *(v1.2)* Stable undated IDs count; moving aliases by rule (§6).
18. *(v1.2)* Headline = KM 1 − S(365); median secondary.
19. *(v1.2)* Event study descriptive only; eval deferred.
20. *(v1.2)* Kill criteria in §18.

## 18. Kill criteria (v1.2, written before any product data is analysed)
| Gate | Trigger | Action |
|---|---|---|
| G3 | >2% of replay days fail to parse, or the replay hash differs across two runs | Stop; fix the replay before building any model |
| G2 | <30 top-tier canonical models after the crosswalk, or closed coverage <80% | Panel-only scope: no headline number; the dashboard shows the panel |
| G4 | >25% of audited cuts are data fixes, not real price changes | Tighten the correction rules and re-audit once; if it fails again, the headline reports observed changes with the audit rate |
| G5 | ~~Epoch check outside ×/÷2~~ *Superseded 2026-11-16 (DECISIONS "G5 replan"): dated price agreement on Epoch's 36 GPQA-Diamond candidates fails its pre-registered pass rule after one audit pass* | No headline (unchanged) |
| G6 | <3 observed cuts among top-tier models | Report Y with an exact CI and say "too few cuts for a curve"; drop the KM chart |
| G8 | <8 isolated events | Descriptive only (already true per the spike: 3–6) |
