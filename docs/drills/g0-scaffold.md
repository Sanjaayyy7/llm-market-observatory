# Drill — G0 scaffold

Owner answers without AI (release gate A1). `make drill-check STRICT=1` fails while any answer is pending.

1. **Grain.** What is one row of `dbt/seeds/seed_provider_map.csv`, which dbt test in `_seeds.yml` enforces that grain, and why does `vertex_ai-language-models` stay in the seed with `is_first_party = false` instead of being left out?

   Answer: _pending_

2. **A test it relies on.** `tests/test_pins.py` fits a `KaplanMeierFitter` instead of only importing lifelines. Which wrong lock would an import-only test miss, and which pin in `pyproject.toml` prevents it?

   Answer: _pending_

3. **Failure mode.** If the `.PHONY` line is removed from the `Makefile`, what does `make site` print once a `site/` directory exists, what exit code does it return, and why is that dangerous in CI?

   Answer: _pending_
