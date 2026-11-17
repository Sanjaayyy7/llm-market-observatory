# Drill — G5 Epoch ground-truth check

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `price_agreement`, and why is it keyed by `(model_name, obs_date)` and not by model? For a headline row, which table is "our price" read from, and for which rows is the `key` series used instead, and why? On the calendar day between two snapshots, what price do we use, and what happens on a day after a model is delisted?

   Answer: _pending_

2. **A test it relies on.** What does `test_changed_then_agrees_needs_audit` guard against, and why would `agrees_late` alone have let a headline data fix pass? Why does the equality rule round the difference to 6 decimals before comparing with 0.005 (try 0.525 against 0.53)? What does `test_prereg_never_modified` prevent, and why does that matter more than any single threshold?

   Answer: _pending_

3. **Failure mode.** G5 failed with 4 headline panel errors. For `gemini-1.5-pro-001` and `mistral-large-2407`, what did the provider announce, what did LiteLLM record, and what does the survival mart say about each model? Why did the council refuse to fix those rows and re-run G5, and why is the observed KM not a lower bound while the verified-only KM is? What does "4/19, 95% CI 6–46%" mean, and why is it a floor on the miss rate rather than an estimate of it?

   Answer: _pending_
