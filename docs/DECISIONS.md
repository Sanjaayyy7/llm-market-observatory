# Decisions log

One row per choice the plan left open, or per deviation from the plan (plan Global Constraints). E-ID cites the evidence in `docs/01-research/research-brief.md`; `owner` marks a decision the owner made directly.

| Date | Choice | Rejected alternative | Why | E-ID |
|---|---|---|---|---|
| 2026-11-16 | Model split: the co-founder plans, decides and verifies on Opus at xhigh effort. Sonnet `builder` subagents implement strictly to plan. Opus `reviewer` checks the high-risk gates | One model for everything | Frontier reasoning goes where errors compound (plans, foundations, review). Cheap models execute a fully specified plan. Fits the Pro usage limit | owner |
| 2026-11-16 | GateGuard's first-edit check is skipped for project files (`.claude/settings.json` env). ECC's destructive-command guard stays on | Disabling ECC in this project | Removes about 60 fact-forcing round trips across the build without dropping a safety net | owner |
| 2026-11-16 | G2 crosswalk approval is delegated to the co-founder. A deterministic test requires a source URL and a name-match score on every manual row; low-score rows get an Opus reviewer pass; the owner gets an FYI. Overrides plan l.222 and l.332 | The owner approves all ~100 rows | Owner HITL scope is safety and permissions only. A deterministic evidence test catches more than a one-time manual skim | owner |
| 2026-11-16 | No deadline. Ship continuously, G0–G7 first | A fixed date with PRD cut-order pressure | Owner: "ship, ship, ship as soon as possible" | owner |
| 2026-11-16 | Non-safety hard stops (Epoch GPQA scores missing at G1; G5 failing after one diagnosis pass) become co-founder decisions through the mini-council, with an owner FYI. Overrides plan l.24, l.159 and l.292 | Stopping for the owner | They are scope and correctness calls, not safety or permission. A mini-council (3 Opus lenses) provides the second opinion | owner |
