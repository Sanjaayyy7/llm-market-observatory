.PHONY: test build ci fetch probe analyze drill-check export site all

test:
	uv run pytest -q

build:
	cd dbt && uv run dbt build --target dev

ci:
	uv run ruff check . && uv run pytest -q && cd dbt && uv run dbt build --target ci
