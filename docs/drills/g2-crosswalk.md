# Drill — G2 crosswalk, aliases and Arena rank

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `seed_model_crosswalk`, and what is one row of `fct_arena_rank`? On one leaderboard date, Arena lists "Claude Opus 5.5 (High)" at rank 2 and `claude-opus-5.5-thinking` at rank 5, and both map to the same canonical model. How many `fct_arena_rank` rows does that date get for the model, and which `rank_percentile` does it carry? Why do "Gemini 2.5 Pro (03-25)" and "(05-06)" stay two canonical models?

   Answer: _pending_

2. **A test it relies on.** `crosswalk_manual_evidence` passes on every draft row but fails when a row is approved. What exactly makes an approved `manual` row fail, and why is `match_score` computed on the raw name rather than on `canon()`? Which rows does the test never check, and what approves those instead?

   Answer: _pending_

3. **Failure mode.** `gpt-4o` is an undated key, and `gpt-4o-2024-08-06` exists in the same provider group. What does `is_moving_alias` return for `gpt-4o`? If the flag were missing and OpenAI re-pointed `gpt-4o` to a cheaper snapshot, what would the headline wrongly count? Why does `claude-opus-4` with only `claude-opus-4-1-20250805` not count as a twin?

   Answer: _pending_
