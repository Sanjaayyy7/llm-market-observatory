# Shared assistant handoff

## Current ownership (2026-11-18)

- **Writer: Claude Code** (resumed 2026-11-18 at `b8c64b6`). G8–9 closed on `g9-closeout`, fast-forwarded into local `main`. See the Claude Code change record below.
- **Incoming Claude Code checkpoint:** `d403154`. Local `main` is at that commit and remains two commits ahead of `origin/main`. The owner approved pushing `c011cd0` and `d403154`. The terminal could not resolve `github.com`, and GitHub returned `404` for `d403154` on recheck. Approval is still scoped to those two commits.
- The range `d403154..codex/g12-refresh` contains the Codex work. Each commit carries `Agent: Codex` and `Model: gpt-6.2-sol`.
- Never run Codex and Claude Code writers on this checkout or `data/warehouse.duckdb` at the same time.

## Who did what so far

- **Codex, before this handoff:** one commit, `b41285b` (`docs: establish shared Codex and Claude handoff`, `Agent: Codex`). It touched only docs and process: `AGENTS.md`, one line of `CLAUDE.md`, `docs/HANDOFF.md`, `docs/README.md` and `docs/STATUS.md`. Its earlier audit made no tracked changes.
- **Claude Code:** the rest of the history through `d403154` (about 110 commits). Only 10 carry the `Agent: Claude Code` trailer. The others predate enforcement.
- **From now on** attribution is enforced: `.githooks/commit-msg` (`core.hooksPath` is set in this checkout) rejects commits without `Agent:`, and Codex commits also need `Model: <model id>`. Authors use the noreply email `151817974+Sanjaayyy7@users.noreply.github.com` (owner ruling 1a, 2026-11-18; earlier commits keep the old address, history is not rewritten).

## Project state

- Published: repo `Sanjaayyy7/llm-market-observatory` (public). Pages: `https://sanjaayyy7.github.io/llm-market-observatory/`. Check the first CI and Pages runs: `gh run list --limit 5`.
- Gates done: C0, C1, G0, G3a, G1, G3b, G2, Task 6, G4 (fallback), G5 (**kill tripped: no market estimate in v1.0**), G6 (KM as a dataset measurement, Methods only), G7 (site, exports, docs, security review, Opus review). G8–9 Steps 1–3 (prereg `67fcfb6`, 6 events, descriptive).
- Baselines at the checkpoint: `make ci` → ruff clean, 125 passed, dbt ci `PASS=197`. `make build` → `PASS=202 WARN=1` (the disclosed `crosswalk_coverage_overall`). Playwright 33 passed. `gitleaks git .` exit 0.

## Claude Code resume, in order

1. **Orient.** Open Claude Code from the repo. Its startup instructions point here and to STATUS. Confirm the branch and inspect `git log d403154..HEAD --format='%h %s%n%(trailers:key=Agent,key=Model)'`. Use a single writer and a Claude Code `gN-<slug>` branch for any new commits.
2. **Close G8–9 from a network-enabled shell.** Put Node 24 on `PATH`, run `make all`, then require `grep -c "Descriptive only: n=" site/dist/adoption.html` → `1`. Check that the verdict matches `site/src/data/event_study.json`. The cached reference is `k_a=6`, `k_b=3`, `matches_prereg=true`. If live inputs change the event list, review the audit before publishing. If a new top-tier first cut fails the dev audit, check the provider deprecations before updating audit or reroute seeds and rerunning. Record the live results and fast-forward local `main` after the gate holds.
3. **Publish under S1.** The approved docs-only push can target `d403154` explicitly once Git connectivity works. The Adoption and refresh commits need separate owner approval before a push. After owner approval for the first dispatch and a successful push, run `gh workflow run refresh.yml --ref main`, watch the refresh and Pages runs, and verify a new `site/src/data/stamp.json` commit on `main`.
4. **Release R.** Require `make drill-check STRICT=1` to exit `0`. The owner writes the drill answers **without AI** (A1). Pushing a release tag needs S1 approval. Using the owner’s desktop or Terminal through computer use also needs permission under the Claude cofounder’s P2 rule.

## Codex change record

- **G7 live check.** `gh run list --limit 5` and run details returned `success` for CI `44314513004` and Pages `44314512900` at `bc69e71`. Pages returned `HTTP/2 200` on both passes. Codex read the repo’s `cofounder-gate` and `ponytail` files. `/skills` remains unverified because the Codex TUI and app server exited with `Operation not permitted`.
- **`6daee7d` and `8b3b351`, Adoption.** Added the page, chart components, Home and Methods links, and browser tests. Charts show normalized download paths on both date bases and an event-selectable, same-SDK placebo distribution. The page includes incomplete windows, ratios, the `requests` control, a link to prereg `67fcfb6`, the preregistered Anthropic lag, and the verified missed cuts drawn from the export’s placebo exclusions. The displayed results are descriptive. Independent review inspected the diff and fixtures and prompted clearer disclosures, metric links, and a stronger group-change test. The browser test checks that the domain changes between groups. Exact bin-by-bin comparison remains untested.
- **`ff2b3a1`, Task 11 checkpoint and drill.** Added `docs/drills/g8-g9-adoption.md` with questions and pending answers. From cached inputs, `make build analyze export site` passed with dbt `PASS=202 WARN=1`, six primary and three announcement-date events, and `matches_prereg=true`. Verdict count expected `1`, actual `1`. Playwright `45 passed` at 1280/375 px and in dark mode using cached Chromium and in-memory routes to the built files. Removing the first-cut rule failed with expected `1`, actual `0`. Restoring it passed. `make ci` returned Ruff clean, 125 pytest passes and dbt `PASS=197`. Normal drill check exited `0`. Strict drill check exited `2` with answers pending.
- **`78330de`, Task 12.** Added `.github/workflows/refresh.yml` for Monday at 06:00 UTC and manual runs. It restores the LiteLLM and raw-input caches, runs `make all`, commits changed site data, and dispatches Pages. Independent review tightened ref-scoped concurrency and disabled persisted checkout credentials. YAML and Bash checks passed. A changed stamp yielded one commit and one mocked dispatch. No data changes yielded zero commits and one mocked dispatch. Simulated build and push failures each yielded zero dispatches. Hosted execution, cache restore, branch protection and whether bot commits keep the schedule active remain unverified. GitHub compares concurrency groups case-insensitively. The layout assumes no case-only alias of `main`.
- **Final co-founder recheck and handoff.** Retried `make all` and the approved docs-only push. LiteLLM Git fetch and the docs push both failed at DNS with Git exit `128`. A subsequent cached `make build` again returned `PASS=202 WARN=1 ERROR=0`. The co-founder’s read-only review checked hosted alternatives. Published CI and Pages build the site. Neither runs `make all` on the local branch. Gitleaks found no leaks in the four implementation and checkpoint commits before this handoff. Attempted remote writes were limited to the approved docs push. This handoff commit updates only HANDOFF and STATUS.

## Claude Code change record (2026-11-18 resume)

- **Review on return.** `d403154..b8c64b6`: all 5 commits carry `Agent: Codex` and `Model: gpt-6.2-sol`. `origin/main` was still `bc69e71`; no tags. No push or tag happened beyond the recorded approval.
- **`fdf1c8a`, Epoch duplicates.** The live fetch broke `unique_stg_epoch__models_model` (Magistral Small 1.1 repeated; Magistral Medium 1.1 with two dates). Staging now collapses copies and drops conflicts; `epoch_crosswalked_model_conflicts` errors if a dropped model is crosswalked.
- **`60818f9`, test harness.** The Codex Adoption test clicked the clean URL `./adoption`, which the stdlib test server 404s (Codex used in-memory routes). It now asserts the href and loads `adoption.html`.
- **`ddfacc3`, live data.** Replay 648 days; same 105 models and 9 cuts; KM 9.522%.
- **`7bcf6dc`, `bd767d2`, review fixes.** Independent Opus review: 0 BLOCK, 5 WARN, 4 fixed, 1 logged below.

## Debt (not blocking)
- Adoption smoke test checks that the placebo x-domain changes between groups, not that it equals the selected group's range (review WARN 2; the filter is one equality at `site/src/adoption.md:54`).

- The order of `epoch_check.json` `spot_check` rows comes from an unordered `select distinct` (`analysis/epoch_check.py:283`, closed G5 code). It churns bytes, not content.
- 11 build-time `npm audit` findings, all accepted (DECISIONS 2026-11-18).
- 2 NumPy DeprecationWarnings in `tests/analysis/test_event_study.py`. The 80% coverage tool has not been run.
- Earlier audit: incremental replay does not restore missing historical partitions; freshness checks the fetch time, not the age of the last fetch.

## Pitfalls (do not repeat them)

- **Codex sandbox:** plain `uv run` panicked (`Attempted to create a NULL object.`). Use `UV_OFFLINE=1 UV_NO_SYNC=1 uv run …` or `.venv/bin/…`. Network-bound fetches may need the sandbox's network permission.
- Node: `export PATH="$HOME/.nvm/versions/node/v24.20.0/bin:$PATH"`. Never change the default node. Playwright 1.62.1 uses the cached chromium 1234; never download browsers (P3).
- DuckDB: `SET TimeZone='UTC'` before any `::date`. `rel.arrow()` is one-shot, so use `.df()`. It allows a single writer.
- On the `:memory:` ci target, `dbt test --select <one>` errors. Use the full `dbt build --target ci`.
- Never leave uncommitted work while anything else edits the tree. A delegated worker once "reverted" an uncommitted README as churn.
- Public pages: every number comes from `site/src/data`, and no spec-internal text (E-IDs, "my call", gate codes). This caused the G7 BLOCK.
- `mart_cut_audit.lag_days` is announced − observed. Pages show its negative, "days after announcement".
- Plan text froze some numbers (coverage 218/303). Read the live marts.

## Return to Claude Code: review protocol

1. `git log d403154..codex/g12-refresh --format='%h %s%n%(trailers:key=Agent,key=Model)'`: every commit in this handoff should show `Agent: Codex` and `Model: gpt-6.2-sol`.
2. Re-run the gate’s expected commands and negative control as needed for closure. Use `git diff d403154..codex/g12-refresh -- <gate paths>` for an independent review of any changed scope.
3. Check the Codex rows in `docs/DECISIONS.md` (marked `(Codex)`) against the spec and the owner gates. Confirm no push, tag or global install happened without an owner approval recorded here.
