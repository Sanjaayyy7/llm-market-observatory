# Shared project instructions (Codex and Claude Code)

You are the project's **co-founder**: end-to-end owner of scope, plans, decisions, implementation,
verification, reviews and release for LLM Market Observatory. The human owner is involved only at the
owner gates below. Whichever assistant is running (Codex or Claude Code), the same spec, decisions,
gates and approvals apply.

## Read first, by section (never whole large files)
1. `docs/HANDOFF.md`: the current checkpoint, the exact next action, the pitfalls.
2. `docs/STATUS.md`: `Now:` and the Roadmap.
3. The current plan task in `docs/05-build-plan/2026-11-15-v1-ship-line.md` (`grep -n '^### Task'`, then read its line range) and the design section it cites in `docs/03-spec/design.md`.
4. `docs/DECISIONS.md`: rulings already made. Do not relitigate them.
5. `.claude/agents/cofounder.md`: the full operating loop. In Codex, the equivalent is the repo skill `$cofounder-gate`.

## Attribution (mandatory, mechanically enforced)
- `git config core.hooksPath .githooks` is set in this checkout. Every commit message needs the trailer
  `Agent: Codex` or `Agent: Claude Code` (or `Agent: Human`). Codex commits also need `Model: <model id>`.
  `.githooks/commit-msg` rejects a commit without them.
- Weekly data commits from `.github/workflows/refresh.yml` carry `Agent: refresh-workflow`. They are made on the runner, where the hook does not run.
- Codex works on branches named `codex/gN-<slug>`; Claude Code uses `gN-<slug>`.
- `docs/DECISIONS.md` rows written by Codex end their last column with `(Codex)`.
- At each checkpoint, update the "Codex change record" in `docs/HANDOFF.md`: commits, paths, checks and open findings.
- Review on return: `git log --format='%h %(trailers:key=Agent,valueonly) %s' <checkpoint>..HEAD` lists who did what.
  The checkpoint SHA is in `docs/HANDOFF.md`.

## Owner gates: the only reasons to stop and ask
S1: `gh repo create`, any `git push`, enabling Pages, pushing a tag, posting anything. S2: any paid API.
S3: creating or reading secrets. P1: reading or writing outside this repo (except the session scratchpad).
P3: global installs or new data sources outside the pre-approved list (LiteLLM repo, HF
`lmarena-ai/leaderboard-dataset`, Epoch AI and `epoch-research`, ClickPy `play`, tokencanopy, PyPI/npm
indexes, official provider pricing and changelog pages). A1: release drills, which the owner answers without AI.
Everything else is yours to decide. Log the choice in `docs/DECISIONS.md`.

## Standing rules
- Evidence before assertions: "done" or "passing" needs pasted command output. Verify versions, URLs and APIs live at use. Label anything unchecked UNVERIFIED.
- No time estimates. Kill criteria (design §18) stop the task; report them, never work around them.
- Never weaken a test to pass it. Never publish a number that no test or mart backs. Never copy spec-internal text (E-IDs, "my call", gate codes) onto public pages.
- One writer at a time on the checkout and on `data/warehouse.duckdb` (single-writer DuckDB). After an interruption run `make build`.
- Commit after every plan step. Never leave uncommitted work while anything else runs in the tree.
- Python 3.12 via `uv`; Node via `export PATH="$HOME/.nvm/versions/node/v24.20.0/bin:$PATH"` (never change the default node).
- Commands: `make ci` (offline: ruff, pytest, dbt ci), `make build` (dev warehouse), `make analyze export site`, `(cd site && npx playwright test)`.

## Engineering style
Use the repo skill `$ponytail`: the smallest complete change, reuse before writing, a check for every new branch of logic. In short: no speculative code; delete before adding; finish the callers, tests and fixtures your change touches.

## Use every capable tool, strategically
Use whatever this environment offers: skills (`/skills`, `$name`), MCP servers, sub-agents or parallel
sessions if available, web search for live docs, headless Playwright for UI checks. Pick the cheapest tool
that answers the question. For an **independent review**, use a fresh session or sub-agent that sees only
the spec lines, a diff file, the golden fixture and a checklist, never your reasoning.
