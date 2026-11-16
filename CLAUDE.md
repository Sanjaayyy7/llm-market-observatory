# LLM Market Observatory

Governed SCD2 history of first-party LLM API list prices, rebuilt from LiteLLM git history. Headline: Kaplan–Meier share of top-tier models that cut list price within 365 days.

- **Start here:** `docs/STATUS.md` (Now, Roadmap). Every doc is mapped in `docs/README.md`.
- **Roles** (`.claude/agents/`):
  - `cofounder` runs every session and owns the project.
  - `builder` (Sonnet) implements one plan task.
  - `reviewer` (Opus) does independent review or acts as a council lens.
- **Spec:** `docs/03-spec/` (PRD, design v1.2). **Plan:** `docs/05-build-plan/2026-11-15-v1-ship-line.md`. **Decisions:** `docs/DECISIONS.md`.
- **Commands** (from G0 on): `make test`, `make ci`, `make build`. Python 3.12 via `uv`; dbt project in `dbt/`.
- **Never:**
  - push, tag, create repos, or post anything without owner approval;
  - read or create secrets;
  - touch files outside this repo, except the session scratchpad, `~/.claude/session-data/`, and the owner's Claude memory and plans dirs;
  - weaken a test to make it pass;
  - write time estimates.
- **Evidence before assertions:** paste command output for any "done" or "passing". Verify versions, URLs and APIs live, never from memory.
- **Overrides:** global ruflo instructions don't apply (not installed). Subagents are only `builder` and `reviewer`, dispatched by `cofounder`.
