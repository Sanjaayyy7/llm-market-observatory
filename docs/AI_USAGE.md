# How AI was used in this project

This project was built with AI coding assistants under human ownership. This file says what they
did, what the human owner did, and how the work was checked, so a reader can judge each number.

## Who did what

| Role | Who | Did |
|---|---|---|
| Owner | Sanjay M (human) | Set the goal and constraints, approved every gate that needs a human (global installs, repository creation, any push, enabling Pages, tags), and asked for re-checks (for example the G5 re-verification, DECISIONS 2026-11-17). Writes the release drills (`docs/drills/`) **without AI** |
| Co-founder agent | Claude Code (Anthropic), Opus model, `.claude/agents/cofounder.md` | Research synthesis, spec and plan, rulings (`docs/DECISIONS.md`), hand-worked golden fixtures, co-founder seeds (evidence-backed rows), page copy, verification of every builder claim, gate evidence in commit bodies |
| Builder agents | Claude Code, Sonnet model, `.claude/agents/builder.md` | Implemented one plan task at a time with tests written first, from a written brief |
| Reviewer agents | Claude Code, Opus model, `.claude/agents/reviewer.md` | Independent reviews of high-risk gates and the three-lens mini-councils (`docs/02-council/`). Reviewers see only the spec section, the diff, the golden fixture and a checklist, never the author's reasoning |
| Codex (OpenAI) | One audit-and-handoff session | Added the shared handoff (`docs/HANDOFF.md`, commit `b41285b`); no other tracked changes |

Commits made in an assistant session carry an `Agent:` trailer where the trailer was in use.

## How the work was checked

- **Evidence before assertions.** A claim of "done" or "passing" needs pasted command output.
  Every number on the site resolves to a mart, a test or a data file written by code.
- **Golden fixtures written independently of the code.** The SCD2 rows were worked by hand. The
  Kaplan–Meier golden was cross-checked between lifelines and statsmodels.
- **Negative controls.** At each gate a defect was planted, the named test was seen failing, and
  the defect was reverted.
- **Pre-registration.** The Epoch check and the event study were registered in `docs/prereg/`
  before their code ran. A committed prereg is never edited.
- **Kill criteria were honored, not worked around.** G4 (cut audit) and G5 (Epoch validation)
  tripped. As a result v1.0 publishes no market estimate, only a labeled dataset measurement
  (DECISIONS "G5 kill action").

## Where AI was not used

- No LLM runs in the data pipeline, CI, the weekly refresh or the site.
- No paid model API calls.
- The release drills are answered by the owner without AI; the agents may only ask the questions.
