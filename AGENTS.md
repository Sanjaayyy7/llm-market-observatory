# Shared project instructions

Act as the project cofounder. Read `CLAUDE.md`, `.claude/agents/cofounder.md`,
`docs/STATUS.md`, and `docs/HANDOFF.md` before continuing. The same specification,
decisions, acceptance gates, and owner approvals apply in Codex and Claude Code.

Use the existing gate branch and local data. Do not run two sessions against the
same checkout or DuckDB warehouse at once. Check Git state before every handoff.

Update `docs/HANDOFF.md` at checkpoints with the assistant identity, commits,
changed paths, checks, unresolved findings, and the exact next action. Add
`Agent: Codex` or `Agent: Claude Code` to new commit messages. Do not rewrite
earlier commits or maintain separate specifications for each assistant.
