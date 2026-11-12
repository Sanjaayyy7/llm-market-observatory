# PRD: LLM Market Observatory

**Status:** v1 draft, waiting on builder check and user approval · **Date:** 2026-11-11 · **Deadline:** Sun 2026-11-15
**Inputs:** `validation/research-brief.md` (E1–E31, R1–R12) · `validation/council/chair-verdict.md` (go-with-changes, gates G0–G10)
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
- **Question:** How long does a newly listed top-tier LLM keep its launch price, and does the first cut move developer adoption?
- **Number shape:** "**X days** (IQR a–b, n=k, commit lag ±d)". This is the Kaplan–Meier median from first observed listing to first observed cut; models never cut are censored.
  - Fallback if the median is undefined (most models never cut): "**Y%** of top-tier models cut price within 365 days."
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
| D5 | *Optional:* OpenRouter `rankings-daily` (needs the user's free API key) | E25, R11 | G1 |
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
| A4 | Event study, results and placebos published whatever they show; below the power floor, descriptive only | R4, E24 | G9 |

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
| V3 | Gemini guardrails per design.md §13: no calls before G9 or from CI/cron/page; user-approved `count_tokens` estimate; hard cap | R7, R12, E27 | G10 |

**Defensibility and ops**
| ID | Requirement | Evidence | Gate |
|---|---|---|---|
| X1 | DECISIONS.md: each choice, the rejected alternative, and the E-ID | E5a–c | all |
| X2 | AI_USAGE.md: honest account of what AI wrote and how it was verified | E5a | all |
| X3 | No-AI drill per slice before merge: explain grain, one test, one failure mode. Hand-write the SCD2 and headline SQL. **(Pending user decision, §12)** | E5b, E5c, E16 | G6 |
| O1 | STATUS.md updated every session; `main` stays shippable; a gate failing twice triggers the next cut; no new slice starts after Sat 2026-11-14 | R6 | all |

## 8. Pre-registration skeleton (filled in and committed at G8, before any code)
- **Unit:** provider SDK group (`openai`, `anthropic`, `google-genai`+`google-generativeai`, `mistralai`, …). Providers without their own SDK are excluded.
- **Event:** first cut of a top-tier model by that provider.
- **Window:** −28…+28 days. Outcome: log daily downloads with day-of-week fixed effects; installer filter fixed after the G1 probe.
- **Comparison:** other SDK groups with no event within ±28 days.
- **Power floor:** ≥8 non-clustered events (no other event for the same group within ±28 days) and MDE ≤20%. Otherwise descriptive only.
- **Placebos:** 100 random pseudo-dates per group, plus one non-AI control package.
- **Optional secondary outcome:** OpenRouter model-level token share, which addresses the unit mismatch.

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
1. Paid Gemini run
2. MetricFlow and the eval
3. OpenRouter
4. Event-study inference (keep the descriptive plot and one placebo)
5. Cron (fall back to a static snapshot)

Never cut: crosswalk tests, the panel, the Epoch check.

## 12. Needs the user
- Approve design.md (hard gate).
- Decide on the no-AI drill (X3).
- Approve crosswalk rows (M1).
- Optional OpenRouter key (D5).
- Gemini spend cap and the go before the first paid call (V3).
- Go for creating the public GitHub repo and Pages.
