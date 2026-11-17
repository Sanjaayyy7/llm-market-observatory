# Drill — G1 source fetchers

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `data/raw/arena/run_date=D/part.parquet`, which columns together identify it, and what does the `config` column distinguish?

   Answer: _pending_

2. **A test it relies on.** `test_fetch_probe_writes_no_partition` asserts that a probe leaves no `<source>/` directory. Why must a probe never write a partition, and what would a later `make build` read if it did?

   Answer: _pending_

3. **Failure mode.** tokencanopy fills `effective_date` with an old date on every row. Before fix `206a00b`, what would the freshness row have reported as `max_date`, and what would `source_freshness` have concluded about a fetch made today?

   Answer: _pending_
