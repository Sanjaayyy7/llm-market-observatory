# Drill — Task 6 price facts and the survival mart

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `fct_price_change`, of `mart_top_tier_screen` and of `mart_launch_price_survival`? `grok-4.20-0309-reasoning` has four first-party LiteLLM keys that all move from one price to another on the same day. How many `fct_price_change` rows does that day get, and why? Why does `mart_top_tier_screen` keep a row with a null `listed_at` for `gemma-3-27b-it`, and why can that model never reach the survival mart?

   Answer: _pending_

2. **A test it relies on.** `reroute_cut_is_censored_not_scored` gives model A (listed 2026-05-19, rerouted to B with no date) a −50% change on 2026-11-24 and gives B a −50% change on 2026-08-18. Which date censors A, and why that date rather than 2026-11-24 or the run date? B's new price equals a newer sibling's price exactly. Why is B still scored as a cut, and which rejected S8 option would have scored it wrongly?

   Answer: _pending_

3. **Failure mode.** `claude-sonnet-5` went 3/15 → 2/10 three days after listing, and `mistral-large-4` went 0.68/2.09 → 1.36/4.18 → 0.70/2.10 in four weeks. Which of the two is a correction under the 7-day / 14-day rules, and which is scored as a real cut? If LiteLLM wrote the 3.8-flash price onto `gemini-2.5-pro` on 2026-11-24, what would `first_cut_at` be, and what would it have been under option A without the "first seen in docs" refinement?

   Answer: _pending_
