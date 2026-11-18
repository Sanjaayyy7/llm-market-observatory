# Drill — G6 Kaplan–Meier dataset measurement

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of the KM input, and where do `duration` and `event` come from in `mart_launch_price_survival`? For the verified-only KM, what happens to a model whose first cut is a data fix: what are its new `duration` and `event`, and why does it use `int_model_exposure.end_ts` rather than `first_cut_at`? Why is `exposure_ctes()` a macro and not a model?

   Answer: _pending_

2. **A test it relies on.** Work `km_small.csv` by hand: why is S(365) = 693/1600, and why is the row censored at day 365 still in the risk set for the event at day 365? `test_km_matches_statsmodels` compares point estimates only. What pins the CI, and what formula does it use? Why read S at the last timeline point ≤ 365 rather than the nearest point?

   Answer: _pending_

3. **Failure mode.** `headline.json` says `scope = "dataset_measurement"` and `validation = "failed"`. Which two pre-registered results force those labels, and why is the observed KM not a lower bound on the market cut share while the verified-only KM is? LiteLLM delisted `gemini-3-pro-preview` 197 days after Google's shutdown. Which way does that lag bias the share, and why did we not censor at the provider's shutdown date?

   Answer: _pending_
