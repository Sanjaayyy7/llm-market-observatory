# Council Protocol (Bloom-style, run manually)

**Purpose:** attack the idea before users do. This file is the audit trail: "we ran it through council" refers to this exact process.

## Inputs
- Decision question + idea: `../01-research/research-brief.md` (the only document each advisor sees).
- Each advisor sees the brief and nothing else. No conversation history and no other memos.

## Stage 1: Independent perspectives (parallel)
Five lenses (from Bloom). Each runs as a separate subagent; models are mixed to add error diversity (Karpathy llm-council).

| Lens | Brief | Model |
|---|---|---|
| Contrarian | Find the strongest reasons this fails | opus |
| First principles | Rebuild the answer from the goal + constraints, ignoring the proposed design | fable |
| Expansionist | Find the biggest upside the plan is under-reaching for | sonnet |
| Outsider | Read as a non-expert skimming the project cold | opus |
| Executor | Make it shippable: sequence, cut list, failure points under usage limits | sonnet |

**Memo format** (at most 400 words): Position · 3 strongest arguments (cite E-/R-IDs) · Key risk · What would change my mind · Recommendation (build as-is / build with changes / pivot B / pivot C), with concrete scope.

## Stage 2: Peer review (blind)
- Memos are shuffled and relabeled A-E. The label-to-lens map is stored in `map.json` and never shown to reviewers.
- Each lens reviews all five memos, its own included but unidentified.
  - Per memo: one strength and one weakness.
  - Blind spots no memo covers.
  - `FINAL RANKING:` 1-5, best first.
  - A lean on the decision: support / mixed / reject.
- Aggregation: average rank per memo, with each reviewer's rank of its own memo dropped (fixes llm-council's self-ranking gap).

## Stage 3: Chair synthesis
The chair reads the de-anonymized memos, all reviews and the rank table, and returns:
- Verdict (go / go-with-changes / pivot / no-go)
- Where the council agrees
- Where it diverges
- What's missing
- Next actions (scope that survives, cuts)
- Confidence

## Outputs
`01-memos/memo-<lens>.md` ×5 · `02-blind-review/map.json` · `02-blind-review/review-<lens>.md` ×5 · `03-ranks.md` · `04-chair-verdict.md`
