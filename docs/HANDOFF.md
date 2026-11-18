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

## Next action and known limits

Claude Code, 2026-11-17. **G6 is closed** (KM as a dataset measurement, Methods only). See STATUS "Done" for the evidence.
- G5's kill was re-verified at the owner's request and stands (DECISIONS "G5 kill re-verified").
- Next action: commit the G8 prereg (`docs/prereg/event-study.md`) **alone**, then Task 11 Steps 2–3 (dbt panels, `analysis/event_study.py`, tests). Task 11 Step 4 (`make all`, the Adoption page) waits for G7.
- G7 waits on the owner's P3 batch: `nvm alias default 24` (v24.20.0 is already installed under nvm) and `brew install gitleaks`. Chromium 1234 is already cached for Playwright.

Prior audit findings (not repaired by the audit): incremental replay does not
restore missing historical partitions when its directory and checkpoint remain;
freshness checks lag at fetch time, not the age of the last fetch; several future
Makefile targets are empty. These are separate from G5 unless they block its gate.

No push, publication, global install, secret access, or human drill answers are
authorized by this handoff. Existing owner gates still apply.
