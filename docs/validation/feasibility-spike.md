# Feasibility spike (2026-11-15)

Throwaway, read-only check run before design approval. No product code. Scripts lived in the session scratchpad and are not kept; this file records the numbers.

## What was run

- **LiteLLM:** blobless clone of `BerriAI/litellm` at HEAD `d034fb6` (2026-11-15). `git log --follow` on `model_prices_and_context_window.json`, last commit per UTC day, `git show` per day, parse JSON (design §5 steps 1–5).
- **Arena:** `lmarena-ai/leaderboard-dataset`, config `text`, split `full`, category `overall` (257 snapshots, 2023-05-08 → 2026-11-11). Rank recomputed by rating within each snapshot.
- **Scope:** first-party chat/completion/responses keys for OpenAI, Anthropic, Google (AI Studio preferred over Vertex), xAI, Mistral, DeepSeek, Cohere, Moonshot, Qwen. Blended price = (3 × input + output) / 4.
- **Cut:** blended drop ≥10% vs the previous snapshot of the same key. Excluded: cuts undone within 30 days (data fixes) and cuts within 7 days of listing (launch typo fixes).
- **Top-tier:** PRD §6. Percentile ≤25% on the first Arena snapshot within 60 days after LiteLLM listing.
- **Events:** first real cut per top-tier model, clustered at ±28 days per SDK group (PRD §8). The power floor is ≥8 isolated events.
- **PyPI download data was not touched.** The pre-registration stays blind to outcomes.

## Results

| Check | Result |
|---|---|
| Replay | 720 daily snapshots, 2023-09-06 → 2026-11-15, 1.23M rows. 2 invalid-JSON days (2024-08-01 `a52ffb9`, 2025-03-25 `0af9a5e`) logged and skipped. |
| Earliest usable price data | 2023-09-06 (19 keys, no `litellm_provider` field). Earlier history is a `max_tokens.json` ancestor. "Since 2023" really means since Sep 2023. |
| First-party chat models (all time) | 527, of which 193 have versioned IDs |
| Real cuts ≥10%, any first-party key | 64 (from 87 raw: 15 reverted, 9 launch fixes) |
| **Versioned rule (v1.1):** top-tier models | 41 (exact name match only) |
| ↳ ever cut / cut within 365 days | 5 / 4 of 39 with full follow-up → **Y ≈ 10%** |
| ↳ clustered events / isolated | 4 / **3** (floor 8) |
| Versioned models with any real cut (no top-tier filter, upper bound) | 12 → 6 clustered / **4 isolated** |
| **Relaxed rule:** top-tier models | 91 (41 versioned + 50 stable undated) |
| ↳ models with a real first cut | 9 → 7 clustered / **6 isolated** (floor 8) |
| Name match, closed Arena top-tier → LiteLLM, exact | 85/185 (46%) |
| Name match, top 10 closed on 2026-10-15, exact / normalized (space and dot → hyphen) | 0/10 / **7/10** |
| Big-4 chat models listed since 2025-11 with versioned IDs | **25/139 (18%)**. Anthropic 3/20, Google 2/21, OpenAI 14/53, xAI 6/45 |

## Verdict per component

1. **Replay pipeline: feasible.** The design §5 method works as written. Batched blob fetch took about 5 minutes. Keep `_replay_errors`; it fired twice.
2. **Kaplan–Meier headline: the median is undefined, so the PRD §3 fallback fires.** About 90% of top-tier models never cut their launch price. The fallback headline ("Y% cut within 365 days", Y ≈ 10%) is the result. The real story is that **list prices are sticky and declines come from new SKUs, not cuts**.
3. **Event study: below the power floor under every rule tried** (3, 4 and 6 isolated events vs 8). PRD A4 already sends it to descriptive-only. The candidate cuts include o3 −80% (2025-06-10) and Claude 3.5 Haiku −20%.
4. **Crosswalk: workable, with manual effort.** Exact matching gets 46% of closed models and normalization recovers most recent ones. The ≥80% closed-coverage gate (M1) needs a manual pass of about 100 closed names. Unmatched names include Meta "muse" models and Amazon Nova experimental builds.
5. **The versioned-only rule (v1.1 decision 14) drops the 2026 frontier.** GPT-5.x and Gemini 3.x ship as stable undated IDs and are not moving aliases. Under the rule, the headline population is biased toward 2024–25 models.

## Caveats

- The cut list is not audited. Commit subjects are bundled ("LiteLLM Minor Fixes & Improvements"), so the observed date is not the announcement date (G4 audit needed). Suspected data artifacts: the 2024-10-10 Vertex 1.5 preview drops of about 98% (likely unit fixes), and the 2026-08 xAI bulk move to an identical 1.5625 blended price.
- Top-tier counts only include models matched by name. Unmatched top-tier models are missing from the denominator.
- The first-party provider list was picked by hand for the spike, not by `seed_provider_map`.

## Decisions this raises for design v1.2

1. **ID rule:** keep versioned-only, or move to the relaxed rule (stable undated IDs count; drop `-latest` and undated keys that have a dated twin)?
2. **Event study:** keep it as descriptive case studies (per A4), or redefine events as successor launches at a lower price? The second has more events but is a new pre-registration.
3. **Headline:** promote "launch prices are sticky" (Y ≈ 10%) to the primary framing.
4. **Kill criteria** (to write into design.md): replay error days >2% → stop. Top-tier n <30 after crosswalk → panel-only scope. Isolated events <8 → descriptive only (already true).
