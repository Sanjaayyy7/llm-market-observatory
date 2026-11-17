# Pre-registration — G5 Epoch ground-truth check

**Written:** 2026-11-17, before any G5 analysis ran and before anyone looked at our prices for these candidates. Only key names and canonical IDs were read.
**Binding plan text:** `docs/05-build-plan/2026-11-15-v1-ship-line.md` Task 8, as of commit `c525b10`.
**Rulings:** `docs/DECISIONS.md` rows "G5 replan" (2026-11-16), "G5 comparison base" and "G5 council items not adopted" (2026-11-17).
**Review:** mini-council (Contrarian, Executor, First-principles; 3 Opus lenses) and an Opus evidence reviewer, 2026-11-17. Every finding was resolved in `c525b10`.
This file is committed once and never edited (`tests/test_prereg.py::test_prereg_never_modified`). Amendments go in a new file.

**What a pass supports:** for the headline rows Epoch observed, the headline input (`fct_model_price_daily`) shows the first-party list price level at launch and lists the model on time. It does not validate cut dates; G4 does that.

## 1. Frozen inputs

| File | Source | sha256 |
|---|---|---|
| `dbt/seeds/seed_epoch_insight_frontier.csv` | byte copy of `results/default/lowest_price_models_above_previous_frontier/lowest_price_models_data.csv` | `041d608b6d74dd584321ffc1fcfd3cca16332dbf4af7ec312947770804bb917f` |
| `dbt/seeds/seed_epoch_insight_other.csv` | byte copy of `…/other_models_data.csv` | `f16411740fb7a36c3a708ad28ee8e376acdd36730c6097613ef7e2afac4cad38` |
| `dbt/seeds/seed_epoch_candidate_status.csv` | written by the co-founder (Step 0) | `26569fadd07d2e104dbdfba2518da42fd5f0152d218793c4f0d19d92599ee9de` |

Upstream: `epoch-research/llm-benchmark-efficiency` at commit `34b923314338360d1b1bbed6ec30d9299e54fdae`.
Published result: `lowest_price_models_results.csv` line 7: GPQA Diamond, threshold GPT-4-0314, n = 6, factor `42.0189988368494`, 90% CI `[4.398155473320801, 401.44016598804956]`.
`tests/test_prereg.py::test_seed_sha256_matches_prereg` checks all three hashes.

## 2. Candidates, status table, headline rows

There are 36 candidates (`bench = 'GPQA Diamond'`, `threshold_model = 'GPT-4-0314'`, from both seeds), keyed `(model_name, obs_date)`. The status table is frozen: 30 `in_scope`, 6 `out_of_scope`.

- **Out of scope:**
  - `Llama-3-Instruct-70B`, `Llama-3.1-Instruct-405B` and `Llama-3.1-Instruct-70B` (meta), `Jamba 1.5-Large` (ai21) and `Phi 4` (microsoft): the provider is outside the first-party panel.
  - `Gemma-2-27B`: the Gemini API pricing page lists no Gemma 2 price.
- **`api_id` rule:** a first-party API ID that a provider-domain page names as a whole token, for the model Epoch observed. When the provider documents both an undated alias and a dated ID, the registry's ID is used if it has one and it is not a moving alias; otherwise the dated ID is used.
  - Judgment rows, each with a `note`: `Claude 2` → `claude-2.0`, `Gemini 1.0 Pro` → `gemini-pro`, `Command R+|2024-08-13` → `command-r-plus-04-2024`, `DeepSeek-V3` → `deepseek-chat`.
- **Frozen headline rows (19):** in-scope rows whose `api_id` is a `mart_launch_price_survival` canonical, read 2026-11-17 from IDs only. Each must be compared on `series = 'fct'`:
  `claude-3-5-haiku-20241022, claude-3-5-sonnet-20240620, claude-3-5-sonnet-20241022, claude-3-haiku-20240307, claude-3-opus-20240229, claude-3-sonnet-20240229, command-r-plus-08-2024, gemini-1.5-flash-001, gemini-1.5-flash-002, gemini-1.5-pro-001, gemini-1.5-pro-002, gemini-2.0-flash-001, gpt-4-0125-preview, gpt-4o-2024-05-13, gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18, mistral-large-2402, mistral-large-2407, mistral-large-2411`.
- **Predicted from key names only** (no prices read):
  - `fct` series: 23 rows (the 19 above plus `gemini-pro`, `gpt-4-0314`, `gpt-4-1106-preview`, `open-mixtral-8x22b`).
  - `key` series: 4 rows (`claude-2.1`, `open-mistral-nemo-2407`, `gpt-4o-2024-11-20`, `deepseek-chat`).
  - `not_in_panel`: 3 rows (`claude-2.0`, `command-r-plus-04-2024`, `mistral-small-2501`). That leaves 27 rows compared, against the 24 needed.
- **Excluded reasoning models**, from the notebook's `reasoning_model_names`: `DeepSeek-R1, o1, o1-mini, o1-preview, o3-mini`. None of them is among the 36.

## 3. Rules

- **Series:**
  - `fct` when `api_id` is a canonical in `fct_model_price_daily`.
  - Otherwise `key`: the first-party LiteLLM keys of the row's provider with `norm(bare) = norm(api_id)`, where `bare = lower(model_key).removeprefix(lower(litellm_provider) + '/')`. Moving aliases are included. Prices follow fct's rule: `round((3·in + out)/4, 6) > 0`, validity by `valid_from::date ≤ d < valid_to::date`, and the min over keys.
- **Price on calendar day d:** the series value on the latest `snapshot_date ≤ d`. All dates are in UTC.
- **Equality:** `round(abs(ours − epoch), 6) ≤ 0.005` USD per 1M tokens.
- **Status:**
  - `start = max(obs_date, 2023-09-06)`, and the window runs from `start` through the last snapshot.
  - `agrees`: equal on `start`.
  - `agrees_late`: first equal later, with no price of ours before that day. Its lag is reported as "Epoch date to our first match".
  - `changed_then_agrees`: first equal later, after a different price of ours. It needs an audit row.
  - `mismatch`: not equal on any day of the window.
  - `out_of_scope`: taken from the frozen table.
  - `not_in_panel`: no priced day at all. It is computed.
- **Reproduction:** Epoch's frontier rule on Epoch's 36 rows gives exactly `GPT-4-0314, GPT-4 Turbo, Mistral-Large-2024-02, Claude-3-Haiku, Gemini-1.5-Flash-2024-05, Phi 4` and a factor of `42.02 ± 0.01`. The factor is attributed to Epoch, not to us.

## 4. Pass rule (all must hold)

1. Each of the 36 pairs has exactly one status. Every `in_scope` provider is first-party in `seed_provider_map`, and every `out_of_scope` row has status `out_of_scope`.
2. `n_compared ≥ ⌈0.8 · 30⌉ = 24`, where compared = `agrees + agrees_late + changed_then_agrees + mismatch`.
3. Every `mismatch` and `changed_then_agrees` row has an audit row approved by the co-founder after an Opus reviewer pass. An `epoch_non_list_price` or `real_change` verdict needs a `source_url` on the provider's `doc_domain` (or a `web.archive.org` capture of it). An unaudited row counts as `panel_error`.
4. `n_panel_error_headline == 0`.
5. The headline rows at run time equal the frozen 19 above, and all of them use `series = 'fct'`.

**If it fails:** `passed: false` after one audit pass leads to a mini-council and an owner FYI. The site shows "validation pending" until it is resolved.
