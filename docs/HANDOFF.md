# Shared assistant handoff

## Current ownership (2026-11-18)

- **Current writer: Codex**, acting as co-founder. Claude Code handed over after publishing G7 (owner S1, 2026-11-18).
- Checkout: `/Users/sanjaym/Projects/llm-market-observatory`. `codex/g12-refresh` is based on `codex/g9-adoption` and contains both slices.
- **Claude Code checkpoint:** `d403154`. The owner approved pushing `c011cd0` and `d403154` only. That push failed because the terminal could not resolve `github.com`. Everything after `d403154` belongs to Codex.
  Review range on return: `git log --format='%h %(trailers:key=Agent,valueonly) %s' <checkpoint>..HEAD`.
- Never run Codex and Claude Code writers on this checkout or `data/warehouse.duckdb` at the same time.

## Who did what so far

- **Codex, before this handoff:** one commit, `b41285b` (`docs: establish shared Codex and Claude handoff`, `Agent: Codex`). It touched only docs and process: `AGENTS.md`, one line of `CLAUDE.md`, `docs/HANDOFF.md`, `docs/README.md` and `docs/STATUS.md`. Its earlier audit made no tracked changes.
- **Claude Code:** every other commit (about 110). Only 10 carry the `Agent: Claude Code` trailer; the rest predate enforcement and are Claude Code by elimination, since the owner commits nothing.
- **From now on** attribution is enforced: `.githooks/commit-msg` (`core.hooksPath` is set in this checkout) rejects commits without `Agent:`, and Codex commits also need `Model: <model id>`. Authors use the noreply email `151817974+Sanjaayyy7@users.noreply.github.com` (owner ruling 1a, 2026-11-18; earlier commits keep the old address, history is not rewritten).

## Project state

- Published: repo `Sanjaayyy7/llm-market-observatory` (public). Pages: `https://sanjaayyy7.github.io/llm-market-observatory/`. Check the first CI and Pages runs: `gh run list --limit 5`.
- Gates done: C0, C1, G0, G3a, G1, G3b, G2, Task 6, G4 (fallback), G5 (**kill tripped: no market estimate in v1.0**), G6 (KM as a dataset measurement, Methods only), G7 (site, exports, docs, security review, Opus review). G8–9 Steps 1–3 (prereg `67fcfb6`, 6 events, descriptive).
- Baselines at the checkpoint: `make ci` → ruff clean, 125 passed, dbt ci `PASS=197`. `make build` → `PASS=202 WARN=1` (the disclosed `crosswalk_coverage_overall`). Playwright 33 passed. `gitleaks git .` exit 0.

## Next actions for Codex, in order

1. **G8–9 closeout:** rerun `make all` where the approved sources are reachable, then `grep -c "Descriptive only: n=" site/dist/adoption.html` → `1`. Recheck the date-basis counts and audit any new top-tier first cuts before publishing. Fast-forward local `main` once the gate holds. A push beyond `d403154` requires S1 approval.
2. **Task 12, weekly refresh:** workflow committed locally. After S1 approval and push, run `gh workflow run refresh.yml` and require a successful refresh with a new `site/src/data/stamp.json` commit and a successful Pages run. If the dev audit flags a new top-tier first cut, check the provider deprecations before updating the audit or reroute seed and rerunning.
3. **Release R:** `make drill-check STRICT=1` must exit 0. The owner answers the drills **without AI** (A1). The tag push is S1.

## Codex change record

- **G7 live check.** `gh run list --limit 5` and run details returned `success` for CI `44314513004` and Pages `44314512900` at `bc69e71`. Pages returned `HTTP/2 200`. Both repo skill files were found and loaded. Codex `/skills` remains unverified because the local TUI and app server failed with `Operation not permitted`.
- **Task 11 Steps 4–5.** `6daee7d`, `8b3b351` and this checkpoint cover the Adoption page, Plot components, navigation and smoke checks, missed-cut metadata in the event export, and `docs/drills/g8-g9-adoption.md`. From cached inputs, `make build analyze export site` passed with dbt `PASS=202 WARN=1`, six primary and three announcement-date events, and `matches_prereg=true`. Expected verdict grep `1`, actual `1`. Playwright `45 passed` at 1280/375 px and in dark mode via an in-memory route to the built files. Negative control: removing the first-cut rule failed with expected `1`, actual `0`. Restored: pass. `make ci`: ruff clean, 125 passed, dbt `PASS=197`. Scoped independent review cleared the disclosure and link findings. The placebo browser test checks that changing groups changes the chart domain. It does not compare every bin to the Parquet.
- **Open.** `make all` stopped before the build at LiteLLM Git fetch, exit `128` (DNS), so G8–9 is still open. `make drill-check` exited `0`; `make drill-check STRICT=1` exited `2` with pending answers, as expected for A1.
- **Task 12.** This checkpoint adds `.github/workflows/refresh.yml`; it follows Adoption checkpoint `ff2b3a1`. The local YAML and Bash checks passed. A mocked publisher committed only the changed stamp and dispatched Pages once. With no changes it made no commit. Simulated build and push failures both blocked dispatch, and restoring success dispatched once. Review tightened branch concurrency and disabled persisted checkout credentials. Hosted execution, cache restore, branch protection and whether bot commits keep the schedule active remain unverified. GitHub compares concurrency groups case-insensitively; this layout assumes no case-only alias of `main`.

## Debt (not blocking)

- The order of `epoch_check.json` `spot_check` rows comes from an unordered `select distinct` (`analysis/epoch_check.py:283`, closed G5 code). It churns bytes, not content.
- 11 build-time `npm audit` findings, all accepted (DECISIONS 2026-11-18).
- 2 NumPy DeprecationWarnings in `tests/analysis/test_event_study.py`. The 80% coverage tool has not been run.
- Earlier audit: incremental replay does not restore missing historical partitions; freshness checks the fetch time, not the age of the last fetch.

## Pitfalls (do not repeat them)

- **Codex sandbox:** plain `uv run` panicked (`Attempted to create a NULL object.`). Use `UV_OFFLINE=1 UV_NO_SYNC=1 uv run …` or `.venv/bin/…`. Network-bound fetches may need the sandbox's network permission.
- Node: `export PATH="$HOME/.nvm/versions/node/v24.20.0/bin:$PATH"`. Never change the default node. Playwright 1.62.1 uses the cached chromium 1234; never download browsers (P3).
- DuckDB: `SET TimeZone='UTC'` before any `::date`. `rel.arrow()` is one-shot, so use `.df()`. It allows a single writer.
- On the `:memory:` ci target, `dbt test --select <one>` errors. Use the full `dbt build --target ci`.
- Never leave uncommitted work while anything else edits the tree. A delegated worker once "reverted" an uncommitted README as churn.
- Public pages: every number comes from `site/src/data`, and no spec-internal text (E-IDs, "my call", gate codes). This caused the G7 BLOCK.
- `mart_cut_audit.lag_days` is announced − observed. Pages show its negative, "days after announcement".
- Plan text froze some numbers (coverage 218/303). Read the live marts.

## Return to Claude Code: review protocol

1. `git log --format='%h %(trailers:key=Agent,valueonly) %s' <checkpoint>..HEAD`: every commit should say `Codex` and carry a `Model:` trailer.
2. For each Codex gate, re-run its `Expected:` commands and its negative control, then run an independent `reviewer` pass on `git diff <checkpoint>..HEAD -- <gate paths>`.
3. Check the Codex rows in `docs/DECISIONS.md` (marked `(Codex)`) against the spec and the owner gates. Confirm no push, tag or global install happened without an owner approval recorded here.
