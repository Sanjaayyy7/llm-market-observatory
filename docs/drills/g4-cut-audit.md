# Drill — G4 cut-date audit

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `mart_cut_audit`, and what does `is_scored_event` select? Why is `grok-4-0709`'s 2026-08-30 cut audited but not a scored event, and why is `open-mixtral-8x7b`'s? Spot-check 3 audit rows: open each `source_url` and confirm the quote and the date.

   Answer: _pending_

2. **A test it relies on.** `documented_promo_is_correction` and `drop_undoing_recent_rise_is_correction` were added after the audit failed. What failure does each prevent, and why is the mirror-revert tolerance ±0.1% and not wide enough to catch `mistral-large-4` (1.0325 → 2.065 → 1.05)? What does `cut_audit_covers_scored_events` guard against?

   Answer: _pending_

3. **Failure mode.** The re-audit found 4/9 data fixes. Why is the headline still the observed KM rather than the verified-only one, and what does the verified-only KM bound — from which side, and why? Which provider makes verification structurally harder, and how does that bias a verified-only number?

   Answer: _pending_
