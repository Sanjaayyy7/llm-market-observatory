# Drill — G3b staging and the SCD2 price dimension

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `dim_model_price`, and what exactly do `valid_from` and `valid_to` hold? A key is listed on snapshots 1–2, absent on 3, and back on 4–6 at the same price. How many rows does it get, what is the first row's `valid_to`, and which row has `delisted = true`?

   Answer: _pending_

2. **A test it relies on.** `test_mode_fill_and_filter` feeds keys whose mode is null on some days. Which rule fills a null mode, and why is the next non-null mode tried before the previous one? On 2023-09-06 every key has a null mode: what would `dim_model_price` show for those keys if staging dropped null-mode rows instead?

   Answer: _pending_

3. **Failure mode.** ClickPy's `pypi_downloads_per_day` is a SummingMergeTree, so one `(date, project)` can arrive as two rows before ClickHouse merges them. What does `stg_pypi__downloads` do with them, what number would a `max()` or `any_value()` report instead, and which test fails if a second fetch partition gets summed in too?

   Answer: _pending_
