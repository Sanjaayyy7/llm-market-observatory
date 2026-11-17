# Shared assistant handoff

## Current ownership

- Assistant: **Claude Code**, acting as cofounder, resumed 2026-11-17 after Codex handoff `b41285b` (no Codex writer active).
- Checkout: `/Users/sanjaym/Projects/llm-market-observatory`.
- Branch: `g5-epoch-check`.
- Claude Code checkpoint: `3a3d5f5d7d8fcbabfcfe82718fec2c2c11b30b46`.
- Current task: G5 / plan Task 8. Resume at Step 0; no G5 analysis has run.
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
- G5: pending. Claude's three Epoch seeds remain unchanged.
- Verification: Python baseline `45 passed`; development baseline `PASS=163
  WARN=1 ERROR=0` (the disclosed overall coverage warning). Plain `uv run` panics
  in this Codex sandbox (`Attempted to create a NULL object.`); installed `.venv`
  commands work, as does `UV_OFFLINE=1 UV_NO_SYNC=1 uv run ...`. No dependency pins
  changed. Preserve this environment note when returning to Claude Code.
- Commit list: inspect `git log 3a3d5f5..HEAD`; every Codex commit has `Agent: Codex`.

## Next action and known limits

Claude Code, 2026-11-17. G5 Steps 0–4 are done:
- council resolution `c525b10`;
- prereg `bd9ea16`, a single commit;
- builder `5346cb1`..`6912a00`.

Analysis: factor 42.0190; 27 of 30 rows compared; 9 audit rows (5 of them headline).

Step 4a is in progress. `seed_epoch_mismatch_audit.csv` has draft verdicts, with `approved_by` blank until the Opus reviewer passes. Three headline rows are verified LiteLLM misses of real provider cuts:
- `gemini-1.5-pro-001` and `-002`: Google, −64% input / −52% output, effective 2024-10-01;
- `mistral-large-2407`: Mistral, $3/$9 → $2/$6 on 2024-09-17.

`mistral-large-2402` is unaudited, because no provider page states its price. Expected: `passed: false` after one audit pass. That is the G5 kill: a mini-council (3 Opus lenses), an owner FYI, and the site shows "validation pending". Next: the reviewer result, then set `approved_by`, re-run `python -m analysis.epoch_check`, then the kill council.

Prior audit findings (not repaired by the audit): incremental replay does not
restore missing historical partitions when its directory and checkpoint remain;
freshness checks lag at fetch time, not the age of the last fetch; several future
Makefile targets are empty. These are separate from G5 unless they block its gate.

No push, publication, global install, secret access, or human drill answers are
authorized by this handoff. Existing owner gates still apply.
