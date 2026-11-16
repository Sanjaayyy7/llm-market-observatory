# PRD: LLM Market Observatory

**Status:** v1.2, feasibility spike applied (`docs/04-feasibility-spike/feasibility-spike.md`); design approved by delegation (user, 2026-11-15: "take over from here") · **Date:** 2026-11-15 · **Deadline:** original Sun 2026-11-15 passed; the user sets the new date
**Inputs:** `docs/01-research/research-brief.md` (E1–E31, R1–R12) · `docs/02-council/04-chair-verdict.md` (go-with-changes, gates G0–G10)
**Traceability:** every requirement cites the evidence it rests on (E/R) and the gate that proves it (G). Items marked *(my call)* are defaults set by Claude for the user to check.

## 1. Problem and why now
- Hiring teams for product-facing data roles want the same core: modeled data, one-definition metrics, tests, SLAs, plus experimentation and causal work for DS and evals for AI-facing teams (E1, E2, E3a–d, E17–E19).
- Portfolios built with heavy AI help are judged on authenticity. The candidate must defend every decision without AI (E5a–c, E16).
- Typical portfolios are static, saturated snapshots (E6). Standout projects pair one specific number with a one-command rebuild, metric definitions, and a ground-truth check (E7).
- The LLM price-vs-quality story is already well covered. Epoch owns the decline rate, Artificial Analysis and llmpricing chart it (E22, E31). Still open: a governed **price history panel back to 2023**, and **adoption** joined to it (E20, E31).

## 2. Readers
| Reader | Time with it | What they must get |
|---|---|---|
| Hiring manager | Skims the README + first dashboard screen | The question, the number, the chart, and proof it's real (data stamp, tests) |
| Interviewer | Probes the work | Grain, SCD2 logic, cut definition, causal design, and the null result defended without AI |
| Recruiter | Scans keywords | Role map: one artifact per role |
| Memo reader (persona) | Reads the decision memo | A product lead deciding: "buy at launch price, or wait for the first cut?" |

## 3. Headline
- **Question (v1.2):** Do top-tier LLMs ever cut their launch price, and what happens to developer adoption when one does?
- **Number shape (v1.2):** "**Y%** of top-tier models cut their list price within 365 days of listing (Kaplan–Meier 1 − S(365), 95% CI, n=k, commit lag ±d)". Models never cut are censored.
  - The spike (`docs/04-feasibility-spike/feasibility-spike.md`) found most top-tier models never cut, so the KM median is undefined and the v1.1 fallback becomes the headline. If a median exists at G6, it is a secondary number.
  - Framing, paired with the Epoch check (A2): the price at fixed capability falls fast, yet same-model list prices rarely move, so the decline arrives through new models. Stated as consistent with both results, not as a separately tested claim.
- The value is unknown until G6. It is never invented, and any placeholder is visibly marked TBD.

## 4. Goals, non-goals, anti-goals
**Goals**
- One defensible number on real, licensed data.
- A governed price panel, rebuildable with one command.
- An honest, pre-registered adoption study.
- An offline-tested eval of semantic-layer vs text-to-SQL.

**Non-goals** (cut by the council, with reasons in DECISIONS.md)
- Price-per-Elo (R9).
- Synthetic control (weak identification, R4).
- A live chat agent (R7).
- BigQuery (E10c), hub-stats (E26), Elementary (E10b).
- Any "daily refresh" claim (R10).
- Closing the A/B-experimentation gap. We disclose it instead.

**Anti-goals** (failure even if it runs)
- A headline number that can't be traced to a model plus a test.
- A causal claim stronger than the pre-registration allows.
- Any Gemini spend the user didn't approve.
- A repo the candidate can't explain without AI.
- Republishing data whose license doesn't allow it.

## 5. Role map (one artifact per role)
| Role | Artifact |
|---|---|
| DE (analytics) | Git-replay SCD2 price pipeline: freshness table, tests, CI, weekly cron (G0–G4) |
| Product Analyst | Headline dashboard + decision memo + metric definitions (G6–G7) |
| Product DS | Survival analysis + pre-registered event study with placebos (G6, G8–G9) |
| AI / evals (candidate's edge) | Static eval: semantic layer vs text-to-SQL, scorer tests, spend ledger (G10) |

## 6. Definitions (*all thresholds are my call* unless noted)
- **Price:** first-party, standard-tier list price. Blended per 1M tokens at **3:1 input:output**: `(3·in + 1·out)/4 × 1e6`.
  - First-party = the provider's own API (e.g. `openai`, `anthropic`, `gemini`, `mistral`, `deepseek`, `xai`). Resellers and clouds (Bedrock, Azure, Vertex, OpenRouter, Together, …) are excluded.
  - Standard tier = base per-token fields only. Batch, cached, priority, and long-context tiers are excluded.
- **Listing:** the first LiteLLM commit time a canonical model has a first-party standard price. This is *observed* time, not the provider's effective date (E20).
- **Cut:** a blended-price drop of **≥10%** on the same canonical model versus its previous price version. Excluded as **corrections:** a change reverted within 14 days, or a change within 7 days of listing.
- **Top-tier:** Arena text "overall" **rank percentile ≤ 25%** on the first leaderboard snapshot within 60 days after listing. Rank is taken within that snapshot, never raw Elo across snapshots (R9, E21). Models unranked in that window are excluded and counted.
- **Commit lag:** announced effective date minus observed commit time, measured on an audited sample (G4).

## 7. Requirements
**Data**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| D1 | Replay LiteLLM price-file history from git (`--follow`, deletions handled), one snapshot per UTC day | E20 | G3 |
| D2 | Ingest LMArena leaderboard history (text configs), handling the 2026-10-20 slug→display rename | E21 | G1 |
| D3 | Ingest Epoch AI CSVs (models + benchmark data if available) | E22 | G1, G5 |
| D4 | Ingest ClickPy daily downloads for provider SDKs; sum the two Google SDKs | E23, E24 | G1, G8 |
| D5 | ~~OpenRouter `rankings-daily`~~ **Dropped (v1.1):** the user chose not to provide a key, so adoption = PyPI only (R11) | E25, R11 | — |
| D6 | Freshness table: rows + max date per source per run; SLA = measured cadence | R10 | G1 |
| D7 | DATA.md: license and attribution per source; only CC BY / MIT / Apache sources | E8a–e, R5 | G1 |

**Modeling**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| M1 | Crosswalk seed: Claude drafts, candidate approves; unique, not-null, coverage ≥90% of in-scope top-tier models and ≥80% of closed ones. Otherwise panel-only scope, disclosed | E30, R2 | G2 |
| M2 | SCD2 price dimension: no overlaps, one current row per key, replay hash stable across two runs | E20 | G3 |
| M3 | Declared grain for every model, enforced by tests | E1, E7 | G3 |
| M4 | Event-date audit table over a declared sample of cuts | E20 | G4 |

**Analysis**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| A1 | Headline survival analysis per §3. The hand-written SQL equals the model output | E7, R1 | G6 |
| A2 | Epoch check: reproduced fixed-capability decline within ×/÷2 of Epoch's ~13×/yr (*my call*); otherwise no headline. Plus a price-level spot-check against tokencanopy | E22, E31 | G5 |
| A3 | Pre-registration committed before any event-study code | R4 | G8 |
| A4 | Event study, results and placebos published whatever they show; below the power floor, descriptive only. **v1.2: the spike counted 3–6 isolated events vs the floor of 8, so descriptive case studies only (per-event download plots, one placebo), no inference** | R4, E24 | G9 |

**Surface**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| S1 | GitHub Pages first screen shows the question, number, chart and data stamp | E7 | G7 |
| S2 | Decision memo for the persona, with caveats | E7 | G7 |
| S3 | README: the number up top, each number linked to its model and test, the role map, one-command rebuild | E7 | G7 |

**Eval** (last; first to cut)
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| V1 | Fixed question set with hand-verified gold answers; scorer unit-tested offline | E3c, E11 | G10 |
| V2 | Two arms on the same questions: MetricFlow (`mf query`) vs text-to-SQL; report accuracy plus a failure taxonomy | E11, E4 | G10 |
| V3 | Gemini guardrails per design.md §13. **Free tier only, $0 (user decision v1.1):** key from a project with no billing; no calls before G9 or from CI/cron/page; `count_tokens` check that the run fits free-tier limits; hard stop on any billing signal | R7, R12, E27 | G10 |

**Defensibility and ops**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| X1 | DECISIONS.md: each choice, the rejected alternative, and the E-ID | E5a–c | all |
| X2 | AI_USAGE.md: honest account of what AI wrote and how it was verified | E5a | all |
| X3 | No-AI drills, **batched at the end (user decision v1.1)**: for each slice, explain grain, one test, one failure mode; hand-write the SCD2 and headline SQL, and `make drill-check` matches it to the models. Required before the v1.0 release tag and before the link is shared. Never blocks a merge | E5b, E5c, E16 | release |
| O1 | STATUS.md updated every session; `main` stays shippable; a gate failing twice triggers the next cut; one gate per merge; the v1.0 ship line is §11 (the original Sat 2026-11-14 cutoff passed) | R6 | all |

## 8. Pre-registration skeleton (filled in and committed at G8, before any code)
- **Unit:** provider SDK group (`openai`, `anthropic`, `google-genai`+`google-generativeai`, `mistralai`, …). Providers without their own SDK are excluded.
- **Event:** **each top-tier model's first cut**, assigned to its provider's SDK group. Cuts in the same group within ±28 days merge into one clustered event, dated by the earliest cut. *(Builder-check resolution, my call; one event per provider would cap n at about 5–6 and make the floor impossible.)*
- **MDE:** computed **before** the prereg commit, from download variance at placebo dates only. Event windows are never looked at before the prereg is committed.
- **Window:** −28…+28 days. Outcome: log daily downloads with day-of-week fixed effects; installer filter fixed after the G1 probe.
- **Comparison:** other SDK groups with no event within ±28 days.
- **Power floor:** ≥8 non-clustered events (no other event for the same group within ±28 days) and MDE ≤20%. Otherwise descriptive only.
- **Placebos:** 100 random pseudo-dates per group, plus one non-AI control package.
- **Known limitation (disclosed):** events are model-level but the outcome is provider-level (SDK downloads). The OpenRouter model-level outcome was dropped in v1.1.
- **v1.2 spike result (event counts only; no download data seen):** 3 isolated events under the versioned rule, 6 under the relaxed rule. Below the floor, so the G8 commit pre-registers a descriptive plan.

## 9. Success metrics
- G0–G9 pass by the deadline; G10 if not cut.
- `git clone && make all` succeeds on a clean machine; CI is green.
- Every README number traces to a dbt model and a test.
- The candidate passes the drills (if adopted).
- The eval reports per-arm accuracy with a failure taxonomy, and spend ≤ the approved cap.
- Stars and views are not success metrics; we can't control them.

## 10. Gates
G0–G10 exactly as in `chair-verdict.md` §Gates; design.md defines each check.

## 11. Cut order
Under usage limits, cut in this order:
1. MetricFlow and the eval (there is no paid run: free tier only). **Applied v1.2: G10 deferred past v1.0.**
2. Event-study inference (keep the descriptive plot and one placebo). **Applied v1.2: triggered by the spike's event count.**
3. Cron (fall back to a static snapshot)

**v1.0 ship line (v1.2):** G0–G7 plus descriptive G8–G9. Never cut: crosswalk tests, the panel, the Epoch check.

## 12. User decisions (v1.1, 2026-11-11)
- **Drills:** batched at the end, before the release tag (X3).
- **Crosswalk:** the user approves the canonical model list plus `manual` (judgment) matches. `exact`/`hf_id` matches are approved by tests. Dev builds may run on draft rows. Published outputs require approval to be complete (M1).
- **OpenRouter:** no key, so D5 is dropped.
- **Gemini:** free tier only, $0 (V3).
- **Approved at the time they're reached:** a public repo `llm-market-observatory` under the user's GitHub account, GitHub Pages, and the weekly auto-refresh Action.

**Still needs the user:**
- ~~Approve design.md (hard gate)~~ delegated 2026-11-15 (§13).
- Approve the crosswalk at G2.
- Provide a Gemini key from a no-billing project at G10 *(deferred with G10)*.
- Do the drills before release.

## 13. v1.2 decisions (2026-11-15, delegated by the user: "take over from here")
Source: `docs/04-feasibility-spike/feasibility-spike.md`.
- **D1 ID rule:** versioned IDs **and** stable undated IDs count as canonical models; moving aliases are excluded by rule (design.md §6). Reason: since 2025-11 only 25/139 big-4 chat models have dated IDs, so v1.1 dropped the 2026 frontier.
- **D2 Headline:** §3 v1.2 (KM 365-day cut share).
- **D3 Event study:** descriptive only (A4, §11 cut 2).
- **D4 Eval:** deferred past v1.0 (§11 cut 1). The design stays in design.md §13.
- **D5 Kill criteria:** design.md §18, written before any product data is analysed.
- **Unchanged:** the user approves the crosswalk at G2, confirms before the first push, and does the drills.
