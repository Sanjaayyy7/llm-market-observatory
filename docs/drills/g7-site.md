# Drill — G7 exports, site and pre-publish checks

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `uncovered.parquet`, and which two tables does `analysis/export.py` join to build it? `crosswalk_uncovered_has_reason` checks two directions. Name both, and say what a weekly refresh does when Arena adds a new top-25% name that has no seed row. Why is the test disabled on the `ci` target?

   Answer: _pending_

2. **A test it relies on.** `test_cut_incidence_equals_one_minus_km_without_competing_events` checks Aalen–Johansen against Kaplan–Meier. Why must the two agree when no row has code 2, and why does the real data give 9.31% against 9.54%? In `methods.json`, which rows get code 0, which code 1 and which code 2? Why does `cut_incidence_365` pass `seed=0` to lifelines?

   Answer: _pending_

3. **Failure mode.** `mart_cut_audit.lag_days` is announced − observed. What did the site print before the fix, for the median and for `claude-3-5-haiku-20241022`, and why was that misleading? Separately, every tokencanopy row for a first-party platform has `source = openrouter`, and 64 of 68 mismatches are exactly 2×. Why does Methods call this a check on that feed rather than evidence about our panel? What would you need to fetch to tell which side is wrong for one model?

   Answer: _pending_
