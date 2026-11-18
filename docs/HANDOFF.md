# Shared assistant handoff

## Current ownership

- Assistant: **Claude Code**, acting as cofounder, resumed 2026-11-17 after Codex handoff `b41285b` (no Codex writer active).
- Checkout: `/Users/sanjaym/Projects/llm-market-observatory`.
- Branch: `main` after each gate merge (gate branches `gN-<slug>`).
- Claude Code checkpoint: `3a3d5f5d7d8fcbabfcfe82718fec2c2c11b30b46`.
- Current task: see STATUS `Now:` and "Next action" below.
- Earlier implementation belongs to Claude Code. The preceding Codex audit made
  no tracked changes. Codex implementation starts after the checkpoint above.

## Resume in either assistant

1. Read `AGENTS.md`, `CLAUDE.md`, `docs/STATUS.md`, then this file.
2. Run `git status -sb` and `git log -8 --format='%h %s%n%b'`.
3. Read the current plan task and the relevant `docs/DECISIONS.md` rows.
4. Use the same branch and data. Never run Claude Code and Codex writers together.
5. Rebuild with `make build` before trusting the local warehouse after interruption.
6. Resume the next action below; do not repeat completed gates or edit a committed
   preregistration. Record amendments in new files.

## Codex change record

Commit trailers identify each assistant. For the complete Codex-session path list,
run `git diff --name-status 3a3d5f5..HEAD` and inspect `git diff --name-status` for
unfinished changes. This avoids maintaining a second, stale file inventory.

- Startup: add shared instructions and this handoff, link them from the existing
  entry points, preserve Claude Code agent settings and the existing branch.
- G5: completed by Claude Code after this handoff (see "Next action" below).
- Verification: Python baseline `45 passed`; development baseline `PASS=163
  WARN=1 ERROR=0` (the disclosed overall coverage warning). Plain `uv run` panics
  in this Codex sandbox (`Attempted to create a NULL object.`); installed `.venv`
  commands work, as does `UV_OFFLINE=1 UV_NO_SYNC=1 uv run ...`. No dependency pins
  changed. Preserve this environment note when returning to Claude Code.
- Commit list: inspect `git log 3a3d5f5..HEAD`; every Codex commit has `Agent: Codex`.

## Fresh-terminal resume (Claude Code)

```bash
cd ~/Projects/llm-market-observatory && claude
```

Start inside the repo. Only then do the `cofounder`, `builder` and `reviewer` agent types load (`.claude/agents/`). The `cofounder` `initialPrompt` orients itself; if it does not start, type `go`.

**Checkpoint, 2026-11-18:**
- `main` @ `f61d5df` plus this handoff commit, clean tree, no open gate branch.
- `make ci`: ruff clean, 119 passed, dbt ci `PASS=191`.
- Dev build: `PASS=195 WARN=1`. The warning is the disclosed `crosswalk_coverage_overall`.

## Next action and known limits

Claude Code, 2026-11-17/18. **G6 is closed** (KM as a dataset measurement, Methods only; `787ebcc`). See STATUS "Done" for the evidence.
- G5's kill was re-verified at the owner's request and stands (DECISIONS "G5 kill re-verified").
- G8–9 Steps 1–3 are done on main: prereg `67fcfb6`, then the panel and analysis; `k_a = 6`, `k_b = 3`. Steps 4–5 need the G7 site.

**Next action: G7, plan Task 10** (`grep -n '^### Task 10' docs/05-build-plan/2026-11-15-v1-ship-line.md`).
1. Orient and rebuild:
   - `git switch -c g7-site`;
   - `make build`;
   - `make analyze`, which regenerates the gitignored `exports/headline.json`, `epoch_check.json` and `event_study.json`.
2. Step 0, toolchain (DECISIONS "G7 toolchain"): no owner action is needed until Step 5.
   - Node: `export PATH="$HOME/.nvm/versions/node/v24.20.0/bin:$PATH"` in each G7 command. Never `nvm alias default`.
   - Pin `@observablehq/framework` `1.13.4`.
   - Pin `@playwright/test` at the newest 1.62.x patch. Check that its `playwright-core` `browsers.json` still says chromium `1234` (cached); the 1.65 line needs `1255`, which is not cached.
3. Steps 1–2: builder, `analysis/export.py` and its 3 tests (TDD).
4. Step 3: the pages.
   - Copy under the G5 kill: plan Task 10 Step 3, plus DECISIONS "G5 kill action". Home shows the question and the "Validation against Epoch AI failed (pre-registered)…" line, with no market number. The KM measurement, the verified-only KM, the G5 recall line (no CI, per "G5 kill re-verified") and the competing-risk note (9.31% vs 9.54%) go on Methods.
   - Invoke the `dataviz` and `frontend-design` skills before the builder brief.
   - Also on Methods, from DECISIONS: the LiteLLM delisting lag (197 days on `gemini-3-pro-preview`); the reroute-censoring line; coverage 85.3% closed and the "Pre-set overall bar 90%: FAILED (218/303)" line.
5. Step 4: Playwright at 1280 and 375 px, plus axe contrast, against `site/dist`.
6. Step 5: the README, then `gitleaks git -v .`. **This needs the owner's P3 first: `brew install gitleaks`.**
7. Step 6: the `security-review` skill and an Opus reviewer pass, then **S1** (owner approves `gh repo create`, the push and Pages). Stop there.
8. After G7: Task 11 Steps 4–5 (the Adoption page: `site/src/adoption.md`, `components/EventLines.js`, `PlaceboHist.js`; `make all` prints the verdict line), then the G8–9 drill file and the gate close.

**Pitfalls hit this session (don't repeat them):**
- duckdb 1.5.6 `rel.arrow()` returns a one-shot `RecordBatchReader`. Registering it and querying it twice hangs. Use `.df()`.
- The DuckDB Python client renders timestamps in the local zone (America/New_York) unless `SET TimeZone='UTC'`. Every `::date` in analysis code needs UTC, or `at time zone 'UTC'` (the G8 prereg BLOCK came from this).
- On the `:memory:` ci target, `dbt test --select <unit>` errors because no upstream models exist. Run negative controls with a full `dbt build --target ci`.
- macOS has no `timeout` binary. Use the Bash tool's timeout instead.
- A pytest mutant has to change the decision being tested. A "chained clustering" mutant that only changed the assigned anchor survived, because it was not chained.
- GateGuard asks for facts before the first Bash command of a session and before each new file. State them and retry.
- Reviewer briefs stay scoped (spec §, diff command, golden, checklist). One unscoped pass once cost about 350k tokens.

**Debt noted, not blocking:** 2 NumPy "generic unit for timedelta" DeprecationWarnings from `tests/analysis/test_event_study.py`; the 80% coverage tool has not been run.

Prior audit findings (not repaired by the audit): incremental replay does not
restore missing historical partitions when its directory and checkpoint remain;
freshness checks lag at fetch time, not the age of the last fetch; several future
Makefile targets are empty. These are separate from G5 unless they block its gate.

No push, publication, global install, secret access, or human drill answers are
authorized by this handoff. Existing owner gates still apply.
