.PHONY: help test build ci fetch probe analyze export site site-test all
.DEFAULT_GOAL := help

help: ## List the available targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-10s %s\n", $$1, $$2}'

test: ## Run the Python test suite
	uv run pytest -q

build: ## Build the dbt warehouse (dev target)
	cd dbt && uv run dbt build --target dev

fetch: ## Fetch all raw sources
	uv run python -m ingest.replay_litellm
	uv run python -m ingest.fetch_arena
	uv run python -m ingest.fetch_epoch
	uv run python -m ingest.fetch_clickpy
	uv run python -m ingest.fetch_tokencanopy

probe: ## Probe the upstream sources without writing
	uv run python -m ingest.fetch_arena --probe
	uv run python -m ingest.fetch_epoch --probe
	uv run python -m ingest.fetch_clickpy --probe
	uv run python -m ingest.fetch_tokencanopy --probe

ci: ## Lint, test and build against the committed fixtures
	uv run ruff check . && uv run pytest -q && cd dbt && uv run dbt build --target ci

analyze: ## Run the analyses
	uv run python -m analysis.epoch_check && uv run python -m analysis.survival && uv run python -m analysis.event_study

export: ## Export the analysis outputs
	uv run python -m analysis.export

site: ## Build the static site
	cd site && npm ci && npm run build

site-test: ## Run the Playwright smoke and accessibility suite
	cd site && npx playwright test

all: fetch build analyze export site ## Run the full pipeline
