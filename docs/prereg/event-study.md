# Pre-registration — G8 descriptive adoption view

**Written:** 2026-11-17. At this point the only inputs read are event dates (`mart_launch_price_survival`, `mart_cut_audit`), seed hashes, and PyPI coverage metadata: first date, last date and row count per project. **No download values have been read for any date.**
**Binding plan text:** `docs/05-build-plan/2026-11-15-v1-ship-line.md` Task 11, as of commit `787ebcc`. PRD §8 (skeleton). Design §9 item 3 (v1.2: descriptive only).
**Rulings:** `docs/DECISIONS.md` "G4 kill action", "G5 kill action" and "G8 prereg" (2026-11-17).
**Review:** an Opus reviewer (First-principles lens), blinded to download values: 1 BLOCK and 8 WARN, all resolved in this text.
This file is committed once and never edited (`tests/test_prereg.py`). Amendments go in a new file.

**What this is:** a descriptive plot of SDK downloads around price cuts. It is not a test, and it supports no causal or market claim. G5 failed as pre-registered, so cut dates are dates in LiteLLM's price file.

## 1. Frozen inputs

| Input | Definition |
|---|---|
| SDK map | `dbt/seeds/seed_sdk_packages.csv`, sha256 `d4e0df84a3a6ec3a237c68ee07b7cf3fe7f5211c49e5763bcf2d169af6340e13`. Groups, in this fixed order (index i = 0…5): `openai`, `anthropic`, `google` (`google-genai` + `google-generativeai`), `mistral` (`mistralai`), `cohere`, `xai` (`xai-sdk`). Control: `requests` |
| Provider → group | `dbt/seeds/seed_provider_map.csv`, sha256 `48316ffa0ea454d0efbbae0b353105e92ed52b313b66f6a964dbc797c123a26d`. Joined as `select distinct provider, sdk_group … where sdk_group <> ''`, because openai, google and cohere each have 2 rows. Providers with no `sdk_group` (deepseek, moonshot, qwen) are excluded |
| Event seeds | `dbt/seeds/seed_cut_audit.csv` sha256 `b73d5142b52a8cd98c1a9523542c936c8466dbe056c0eaecd113ea6c293a7acb`; `seed_temporary_price.csv` `68ddf35ed983920fbd2349820c2eef9e86794c28d113a28e6176430857d5dba2`; `seed_model_reroute.csv` `f75e27ac9ac9a70705af3fd1667cbb416fc4df967d52019459c87bfce86421fd` |
| Downloads | `stg_pypi__downloads(date, project, downloads)`: ClickPy `pypi_downloads_per_day`, UTC dates, all installers. The fetched table has no installer column (`ingest/fetch_clickpy.py:24`). ClickPy's per-installer tables were not fetched (DECISIONS 2026-11-16, G1 FINDING (c)), so there is no installer filter |

**Group day series:** a group's downloads on date d = the sum over its member packages of their rows on d. A member with no row on d contributes 0: ClickPy's summing table has no row for a zero day, as with `xai-sdk`'s 6 missing days in early 2024. A group's coverage runs from its earliest member's first date to the data's last date. This gives google 2023-08-01 (`google-genai` begins 2024-12-10 as a new package), mistral 2023-12-09, xai 2023-12-08, and 2023-08-01 for the rest.

## 2. Events

- **Series A, "observed"** (primary; matches the G6 measurement): each row of `mart_launch_price_survival` with `not censored`, dated `(first_cut_at at time zone 'UTC')::date` and assigned to its provider's group.
- **Series B, "verified"** (shown beside A): the subset of A whose scored `mart_cut_audit` row has `not is_data_fix`, dated `announced_date` (the provider's own dated statement).
- **Clustering** (both series): within a group, sort cuts by date. The earliest cut not yet assigned opens a cluster, dated by itself. Every later cut of that group dated ≤ 28 days after the opening date joins it. The rule is anchored at the opening date, never chained. Each cluster is one event.
- **Frozen event rows**, read 2026-11-17:

  | model | group | A date (UTC) | B date |
  |---|---|---|---|
  | `mistral-large-2402` | mistral | 2024-05-31 | — |
  | `claude-3-5-haiku-20241022` | anthropic | 2025-02-28 | 2024-12-03 |
  | `o3-2025-04-16` | openai | 2025-06-10 | 2025-06-10 |
  | `gpt-5.6-terra` | openai | 2026-07-31 | 2026-07-30 |
  | `gpt-5.6-luna` | openai | 2026-07-31 | 2026-07-30 |
  | `grok-4.20-0309-reasoning` | xai | 2026-08-12 | — |
  | `grok-4.20-multi-agent-beta-0309` | xai | 2026-08-12 | — |
  | `gpt-5.6-sol` | openai | 2026-08-22 | 2026-08-21 |
  | `mistral-large-4` | mistral | 2026-11-03 | — |

  Series A has 6 events: mistral 2024-05-31 and 2026-11-03; anthropic 2025-02-28; openai 2025-06-10 and 2026-07-31 (terra, luna, and sol at +22 days); xai 2026-08-12. Series B has 3 events: anthropic 2024-12-03; openai 2025-06-10 and 2026-07-30 (sol at +22 days).
  The run reports `matches_prereg`, which is true only if its event rows equal this table. Any later difference, such as a new cut from the weekly refresh, is reported and labelled "after prereg".

## 3. Window and outcome

- `rel_day` = date − event date, from −28 to +28. Pre = −28…−1 and post = 0…+27: 28 days each, exactly 4 of each weekday. So the day-of-week mix is equal by construction, and that is the day-of-week adjustment.
- `norm` = downloads / mean(downloads over pre), per event and group. Over pre, `norm` averages exactly 1.
- **Outcome** = `ratio = mean(post) / mean(pre)` of the group's daily downloads.
- An event whose pre or post window extends outside its group's coverage gets its path plotted over the covered days and **no ratio** (flag `incomplete_window`). At writing, this applies to mistral 2026-11-03, whose post window ends after 2026-11-15. The ratio appears once a weekly refresh covers the window, with no rule change.

## 4. Placebo and control

- **Who draws:** each group with at least one series A event (today openai, anthropic, mistral, xai).
- **Eligible dates:** the dates d whose window [d−28, d+27] lies within the group's coverage, and with |d − e| > 28 days for every e in that group's exclusion set. The exclusion set is all series A and series B event dates of the group, plus G5's provider-verified cuts LiteLLM missed (mistral 2024-09-17).
- **Draw:** for group index i (§1), `numpy.random.default_rng([20261115, i]).choice(eligible_sorted, size=min(100, len(eligible)), replace=False)`. Each pseudo-date gets the same `ratio`.
- For each event, report the share of its group's placebo ratios ≤ the event ratio. This is a descriptive percentile, not a p-value.
- **Control:** the `requests` ratio at every series A event date, beside each event.

## 5. Verdict and what is reported

- Verdict line, verbatim: "Descriptive only: n=k events, below the pre-registered floor of 8." k is the number of series A events at run time. Series B's count is stated beside it.
- If k ≥ 8 at a later refresh, the line reads "Descriptive only: n=k events; inference not built in v1.0." The PRD §8 floor also requires MDE ≤ 20% and the OLS/HAC specification, and v1.0 builds neither (design §9 item 3, v1.2).
- Every event is reported: group, date, member models, ratio (or `incomplete_window`), placebo percentile, and the `requests` ratio. Nulls and decreases are reported the same way as increases.

## 6. Deviations from PRD §8 (design §9 item 3, v1.2: below the floor, descriptive only)

Dropped:
- the log-downloads outcome with day-of-week fixed effects (replaced by the balanced 28-day ratio);
- the comparison with other SDK groups that have no event;
- the MDE.

Added:
- series B;
- the anchored clustering rule;
- the exclusions from the placebo pool.

## 7. Known limitations (disclosed on the page)

- The events are model-level, but the outcome is provider-level SDK downloads (PRD §8).
- Series A dates are LiteLLM dates:
  - 4 of the 9 scored cuts have no dated provider announcement (G4: two unannounced, one without evidence, one real but undated).
  - Anthropic's A date is 87 days after its announcement.
  - LiteLLM missed 2 provider cuts that G5 verified (Gemini 1.5 Pro, 2024-10-01; Mistral Large 2, 2024-09-17), so those cuts have no window.
- Download counts include CI and mirror traffic, with no installer filter.
