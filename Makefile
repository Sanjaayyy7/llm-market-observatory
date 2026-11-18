.PHONY: test build ci fetch probe analyze export site all

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

analyze:
	uv run python -m analysis.epoch_check && uv run python -m analysis.survival && uv run python -m analysis.event_study

export:
	uv run python -m analysis.export

site:
	cd site && npm ci && npm run build

all: fetch build analyze export site
