---
name: ponytail
description: Use on every coding change in this repo (writing, fixing, refactoring, reviewing). Enforces the smallest complete change: reuse before writing, no speculative code, and a check for every new branch of logic. Do not use for owner-facing prose.
---

# Ponytail: the smallest complete change

The best code is code you never write. Solve the whole problem with the least new code.

## Before writing
List every place the change must reach: callers, tests, fixtures, config, exports, the pages that read the data.
That list is the scope. Features nobody asked for are not.

## Pick the first option that fully works
1. Does it need to exist? Skip options and flexibility nobody asked for, and name what you skipped in one line.
2. Is it already in this repo (a helper, a macro, a component, `analysis/*`, `dbt/macros/*`, `site/src/components/*`)? Use it the way the surrounding code does.
3. Is it in the standard library or the platform (DuckDB SQL, dbt tests, Observable Plot, Playwright)? Use it.
4. Is it in an installed dependency? Use it. Never add a dependency for a few lines.
5. Can it be one line a reader understands at a glance? Then one line.
6. Otherwise, write the minimum code that works.

## Rules
- Be lazy about the solution, never about the change: finish every caller, test and fixture it breaks.
- No wrapper, option, config or "for later" code. Deletion beats addition. Keep the existing layers: ingest → dbt → analysis → export → site.
- Comment only the *why* the code cannot show, in one line.
- Bug fix: grep every caller first, then fix the root cause once, in the shared code.
- New non-trivial logic (a branch, a loop, a parser, a statistic, a security check) leaves one small test, and you see it fail once (RED) before it passes.
- A shortcut with a known limit gets a comment: `shortcut: <limit>, <when to upgrade>`.
- Never cut: validation at trust boundaries (the export approval gate, the https URL guard), error handling that prevents data loss, security, accessibility, anything the owner asked for.

## Reply
End each change report with one or two lines: what you skipped or did not check, and any risk the owner must know.
