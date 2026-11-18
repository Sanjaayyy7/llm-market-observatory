# Shared assistant handoff

## Current ownership (2026-11-18)

- **Next writer: Codex**, acting as co-founder. Claude Code handed over after closing G7 and publishing it (owner S1, 2026-11-18).
- Checkout: `/Users/sanjaym/Projects/llm-market-observatory`. Branch: `main`. Codex gate branches are `codex/gN-<slug>`.
- **Claude Code checkpoint:** the latest commit titled `docs: record Claude Code checkpoint for the Codex handoff`. Local `main` may be ahead of `origin/main`; pushing is owner gate S1. Everything after it belongs to Codex.
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

1. **Verify the publish.** `gh run list --limit 5`: ci and pages should be green. `curl -sI https://sanjaayyy7.github.io/llm-market-observatory/` should return 200. If a run failed, read it with `gh run view <id> --log-failed`. Fix on a `codex/` branch. Pushing the fix is owner gate S1.
2. **G8–9 Steps 4–5** (plan Task 11, `grep -n '^### Task 11'`):
   - `site/src/adoption.md`, `site/src/components/EventLines.js` and `PlaceboHist.js` (design §12 item 3);
   - add the page to `site/observablehq.config.js` and to `site/tests/smoke.spec.js`;
   - `make all`, then `grep -c "Descriptive only: n=" site/dist/adoption.html` → `1`.
   Data is already exported: `event_panel.parquet`, `placebo.parquet`, `event_study.json`. Then write the drill `docs/drills/g8-g9-adoption.md` and close the gate.
3. **Task 12, weekly refresh:** `.github/workflows/refresh.yml` (cron `0 6 * * 1` plus `workflow_dispatch`). Pushing it and the first `gh workflow run refresh.yml` are owner gate S1.
4. **Release R:** `make drill-check STRICT=1` must exit 0. The owner answers every `docs/drills/*.md` **without AI** (A1); you may quiz, never draft answers. The tag push is S1.

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
