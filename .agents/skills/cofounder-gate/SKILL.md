---
name: cofounder-gate
description: Use when running any build-plan gate or task (G8–G9, Task 12, release prep) in this repo. It is the co-founder's operating loop for Codex: orient, branch, implement with TDD, verify against the plan's Expected lines, negative control, independent review, close with evidence, ask the owner only at the gates.
---

# Co-founder gate loop (Codex edition of `.claude/agents/cofounder.md`)

## 1. Orient
- `git status -sb && git log --oneline -5`, then `docs/HANDOFF.md` and `docs/STATUS.md` (`Now:`).
- Read the plan task's line range and the design section it cites. Check `docs/DECISIONS.md` for rulings that touch it.
- Check the plan's frozen numbers against live data before relying on them. The data drifts: G7 found coverage at 223/303, where the plan says 218/303.

## 2. Branch
`git switch -c codex/gN-<slug>` from an up-to-date `main`.

## 3. Pre-verify, then implement
- Verify live, before writing code: every package pin, action tag, URL and API you will use (npm registry, GitHub API, official docs). Record the evidence in the commit body.
- TDD: write the plan's tests, run them and see them fail, implement, then see them pass. Use `$ponytail`.
- If sub-agents or parallel sessions exist, give one implementer one plan task with a written brief file. Never run two writers on the same files or on the DuckDB warehouse.
- Commit after every plan step, with trailers `Agent: Codex` and `Model: <model id>`.

## 4. Verify (never accept "done" without output)
- Re-run every `Expected:` command of the task and paste expected against actual.
- Negative control: plant one defect the gate should catch, see the named test fail, revert, see it pass. Record both runs.
- UI changes: build the site, take headless screenshots at 1280 and 375 px, and look at them before review. In G7 this found 3 defects the tests missed.

## 5. Independent review
Required at high-risk gates and before any publish. Use a fresh session or sub-agent. Its brief contains only:
the design or plan line ranges, a diff file (`git diff BASE..HEAD -- <paths> > review.diff`), the golden fixture path, and a checklist.
Never include your own reasoning. Resolve every BLOCK. Each fix round ends with a scoped re-review of the fix diff.

## 6. Close
`make ci` green. Update `docs/STATUS.md` (Roadmap row and `Now:`) and the Codex change record in `docs/HANDOFF.md`. Add `docs/DECISIONS.md` rows, with `(Codex)` in the last column. Write `docs/drills/<slice>.md` with questions only (grain, one test it relies on, one failure mode), each answered `Answer: _pending_`. Put the gate evidence in the last commit's body. Then `git switch main && git merge --ff-only codex/gN-<slug>`.

## Speed without losing quality (lessons from G0–G7)
1. Pre-verify facts (pins, tags, URLs, live data) before implementing. Rework from wrong assumptions cost more than any build step.
2. Never leave uncommitted work while something else runs in the tree.
3. Every number a reader sees is computed from `site/src/data`. Public copy never carries spec-internal text. The G7 BLOCK came from copying spec text.
4. Batch plan steps that touch the same files into one implementation pass; split only where the files differ.
5. Run the reviewer in parallel with your own verification. Scoped briefs (a diff file plus line ranges) cost a fraction of open-ended review.
6. Run the negative control right after GREEN, while the context is fresh.
7. Cap command output (`| tail -30`). Read files by line range.
8. Keep one gate per session. At a gate close, update HANDOFF so a fresh session resumes in a single read.
