.PHONY: test build ci fetch probe analyze drill-check export site all

test:
	uv run pytest -q

build:
	cd dbt && uv run dbt build --target dev

fetch:
	uv run python -m ingest.replay_litellm
	uv run python -m ingest.fetch_arena
	uv run python -m ingest.fetch_epoch
	uv run python -m ingest.fetch_clickpy
	uv run python -m ingest.fetch_tokencanopy

probe:
	uv run python -m ingest.fetch_arena --probe
	uv run python -m ingest.fetch_epoch --probe
	uv run python -m ingest.fetch_clickpy --probe
	uv run python -m ingest.fetch_tokencanopy --probe

ci:
	uv run ruff check . && uv run pytest -q && cd dbt && uv run dbt build --target ci
