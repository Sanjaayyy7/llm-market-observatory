# Drill — G3a LiteLLM replay

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `data/raw/litellm/snapshot_date=D/part.parquet`, and which commit's file state does the partition for day D hold? Why does the replay walk only `main`'s first-parent line instead of every commit that touched the price file?

   Answer: _pending_

2. **A test it relies on.** `test_partial_run_recovers` makes the writer fail on the second day. What does it prove about `replay_state.json`, and what would G3b see if the state were written before every partition succeeded?

   Answer: _pending_

3. **Failure mode.** Upstream force-pushes `main`, so the sha in `replay_state.json` is no longer in history and one previously written day no longer exists. What does the replay do, how is the stale day's partition removed, and how does `replay_hash` show the result equals a fresh run?

   Answer: _pending_
