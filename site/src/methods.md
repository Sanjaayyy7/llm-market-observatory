---
title: Methods & data
toc: false
---

# Methods & data

```js
import * as Plot from "npm:@observablehq/plot";
import {StepChart, rows} from "./components/StepChart.js";
import {HeadlineStat, pct} from "./components/HeadlineStat.js";
const H = await FileAttachment("data/headline.json").json();
const M = await FileAttachment("data/methods.json").json();
const E = await FileAttachment("data/epoch_check.json").json();
const km = rows(await FileAttachment("data/km_curve.parquet").parquet());
const survival = rows(await FileAttachment("data/survival.parquet").parquet());
const reroute = rows(await FileAttachment("data/reroute_lag.parquet").parquet());
const coverage = rows(await FileAttachment("data/coverage.parquet").parquet());
const uncovered = rows(await FileAttachment("data/uncovered.parquet").parquet());
const freshness = rows(await FileAttachment("data/freshness.parquet").parquet());
const epochAudit = rows(await FileAttachment("data/epoch_audit.parquet").parquet());
const day = (d) => d.toISOString().slice(0, 10);
const link = (u) => (u ? html`<a href=${u}>source</a>` : "–");
```

<section id="measurement">

## Dataset measurement: cuts recorded in LiteLLM's public price file

<p class="muted" data-testid="scope-label">Scope: dataset measurement · Validation: failed</p>

```js
display(HeadlineStat([`${pct(H.share_cut_365)} cut within 365 days (95% CI ${pct(H.ci_low)}–${pct(H.ci_high)}, n=${H.n}, median commit lag ${H.commit_lag_median_days} days)`], {testid: "measurement-stat"}));
display(html`<p class="takeaway">About ${Math.round(H.share_cut_365 * 10)} in 10 top-tier models had a list-price cut recorded within a year of listing; ${H.n_data_fix} of the ${H.n_audited} recorded first cuts could not be verified on a provider page.</p>`);
```

```js
const curve = (name) => km.filter((r) => r.series === name).sort((a, b) => a.days - b.days)
  .map((r) => ({x: r.days, y: 1 - r.survival, lo: 1 - r.ci_upper, hi: 1 - r.ci_lower}));
const obs = curve("observed");
const ver = curve("verified_only");
const atDay = (d) => (obs.filter((p) => p.x <= d).at(-1) ?? obs[0]).y;
const ticks = survival.filter((s) => s.censored).map((s) => ({x: s.days_at_launch_price, y: atDay(s.days_at_launch_price)}));
const xMax = Math.max(...obs.map((p) => p.x));
const yMax = Math.max(...obs.map((p) => p.hi), ...ver.map((p) => p.hi)) * 1.1;
const tipFor = (name) => (d) => `${name}\nday ${d.x}: ${pct(d.y)} cut`;
const kmChart = StepChart({
  width, marginRight: 110,
  lines: [
    {data: obs, stroke: "var(--accent)", band: {y1: "lo", y2: "hi"}, tip: tipFor("All recorded cuts")},
    {data: ver, stroke: "var(--muted)", dash: "6 4", tip: tipFor("Verified-only")}
  ],
  marks: [
    Plot.ruleX([365], {stroke: "var(--ink-2)", strokeOpacity: 0.6}),
    Plot.text([{x: 365, y: yMax}], {x: "x", y: "y", text: () => "365 days", textAnchor: "start", dx: 4, dy: 8, fill: "var(--ink-2)"}),
    Plot.ruleX(ticks, {x: "x", y1: (d) => d.y - 0.012, y2: (d) => d.y + 0.012, stroke: "var(--accent)", strokeWidth: 1.5}),
    Plot.text([{x: xMax, y: obs.at(-1).y, t: "All recorded cuts"}], {x: "x", y: "y", text: "t", textAnchor: "start", dx: 6, fill: "var(--accent)"}),
    Plot.text([{x: xMax, y: ver.at(-1).y, t: "Verified-only"}], {x: "x", y: "y", text: "t", textAnchor: "start", dx: 6, dy: 12, fill: "var(--ink-2)"})
  ],
  xLabel: "Days since listing", yLabel: "Share cut (%)", yTickFormat: (v) => `${(v * 100).toFixed(0)}%`,
  yDomain: [0, yMax],
  ariaLabel: `Cumulative share of top-tier models with a recorded list-price cut by days since listing. At 365 days ${pct(H.share_cut_365)}, 95% CI ${pct(H.ci_low)} to ${pct(H.ci_high)}; verified-only ${pct(H.verified_only.share_cut_365)}. ${ticks.length} censored models are marked with ticks.`
});
kmChart.setAttribute("data-testid", "km-chart");
display(kmChart);
display(html`<div class="legend" data-testid="km-legend">
  <span><svg width="28" height="10" aria-hidden="true"><line x1="0" x2="28" y1="5" y2="5" stroke="var(--accent)" stroke-width="2"/></svg>All recorded cuts (95% CI band)</span>
  <span><svg width="28" height="10" aria-hidden="true"><line x1="0" x2="28" y1="5" y2="5" stroke="var(--muted)" stroke-width="2" stroke-dasharray="6 4"/></svg>Verified-only</span>
  <span><svg width="10" height="14" aria-hidden="true"><line x1="5" x2="5" y1="1" y2="13" stroke="var(--accent)" stroke-width="1.5"/></svg>Censored model</span></div>`);
```

<p class="source">Source: km_curve.parquet, survival.parquet (analysis/survival.py, lifelines KaplanMeierFitter).</p>

```js
const V = H.verified_only;
display(html`<p>Verified-only lower bound: ${pct(V.share_cut_365)} (95% CI ${pct(V.ci_low)}–${pct(V.ci_high)}, ${V.events} cuts). A cut that no provider page confirms counts as no change.</p>
<p>Audit: ${H.n_data_fix} of ${H.n_audited} recorded first cuts are data fixes (no dated statement on the provider's domain).</p>
<p>Kaplan–Meier treats a delisting or reroute as non-informative censoring, but a retirement can stand in for a cut. Of ${H.n} models, ${M.outcome_counts.still_listed} are still listed, ${M.outcome_counts.ended} ended by delisting or reroute, and ${M.outcome_counts.cut} were cut. Aalen–Johansen cut incidence at 365 days is ${(M.aj_cut_365 * 100).toFixed(2)}%, against 1 − KM ${(M.km_cut_365 * 100).toFixed(2)}%.</p>
<p>A pinned model ID that its provider documents as now serving another model is censored at that date and never scored as a cut.</p>`);
const top = [...reroute].sort((a, b) => b.lag_days - a.lag_days)[0];
display(html`<p>LiteLLM can keep a retired model listed long after its provider retires it: ${top.canonical_model_id} stayed listed ${top.lag_days} days past its ${day(top.reroute_date)} reroute. Exposure ends at LiteLLM's delisting, so that extra cut-free time biases this share down.</p>`);
display(Inputs.table(reroute.map((r) => ({model: r.canonical_model_id, "reroute date": day(r.reroute_date), "last listed": day(r.last_listed),
  "LiteLLM delisted": day(r.litellm_delisted), "lag days": r.lag_days, evidence: r.evidence_url})), {format: {evidence: link}, layout: "auto"}));
```

</section>

<section id="validation">

## Validation against Epoch AI

```js
const aud = E.audited.map((r) => {
  const a = epochAudit.find((x) => x.model_name === r.model_name && String(x.obs_date).slice(0, 10) === r.obs_date);
  return {model: r.model_name, "observation date": r.obs_date, "Epoch price": r.epoch_price, "our price": r.our_price_at_start ?? "–",
    verdict: r.verdict, source: a?.source_url ?? null};
});
display(html`<p>Validation: failed (pre-registered, 2026-11-17).</p>
<p>On the ${E.n_headline} headline models Epoch AI observed, ${E.n_panel_error_headline} rows are panel errors as pre-registered: 3 rows come from 2 provider cuts LiteLLM never recorded (Gemini 1.5 Pro, 2024-10-01, on both versions; Mistral Large 2, 2024-09-17), and 1 row's price change has no provider source. Of the 3 cuts on those models that we verified on provider pages, LiteLLM recorded 1, 87 days late.</p>
<p>Limits: the check sees a miss only when Epoch's price is post-cut; the sample is 2023–25 models from 5 providers.</p>
<p>Epoch AI estimates that the price of GPT-4-level GPQA-Diamond performance fell about ${Math.round(E.epoch_published_factor)}× per year (their 90% CI ${E.epoch_ci90[0].toFixed(1)}–${Math.round(E.epoch_ci90[1])}, n=${E.epoch_n}; Epoch AI, 2025). That trend is theirs, not ours. Our panel's list prices agree with Epoch's on ${E.n_compared - E.n_mismatch} of ${E.n_compared} comparable price observations; ${E.n_mismatch} disagreements are listed below with sources. ${E.n_headline} of our headline models are among Epoch's candidates.</p>`);
display(Inputs.table(aud, {format: {source: link}, layout: "auto"}));
```

</section>

<section id="coverage">

## Coverage

```js
const scope = coverage.length, covered = coverage.filter((c) => c.covered).length;
const closedRows = coverage.filter((c) => c.closed);
const scopeClosed = closedRows.length, coveredClosed = closedRows.filter((c) => c.covered).length;
const CODES = {
  no_first_party_key: "LiteLLM never listed this model under a first-party provider (all replayed snapshots checked).",
  alias_only: "the provider's API served this checkpoint only through a moving alias (deepseek-chat, deepseek-reasoner, deepseek-coder), which the panel excludes.",
  candidate_key_unverified: "LiteLLM lists a first-party key with a similar name, but no provider page we fetched ties it to this Arena name, so it stays unmapped.",
  variant_of_mapped: "an Arena label (effort mode or rename) of a model already mapped under another name; leaving it unmapped changes no top-tier class."
};
const codeRows = Object.entries(CODES).map(([code, definition]) => ({"reason code": code, count: uncovered.filter((u) => u.reason_code === code).length, definition}));
display(html`<p>Population: top-tier models with a first-party list price.</p>
<p>${covered}/${scope} in-scope Arena names map to a priced first-party model (${pct(covered / scope)}).</p>
<p>${covered / scope < 0.90 ? `Pre-set overall bar 90%: FAILED (${covered}/${scope})` : "Pre-set overall bar 90%: passed"}</p>
<p>Closed models: ${coveredClosed}/${scopeClosed} (${pct(coveredClosed / scopeClosed)}); 166/211 = 78.7% before the co-founder's hand matches (G2, 2026-11-17).</p>
<p>${M.unranked_count} priced models had no Arena rank within 60 days of listing and are left out of the top-tier set.</p>`);
display(Inputs.table(codeRows, {layout: "auto", width: {definition: 520}}));
display(html`<details><summary>All ${uncovered.length} uncovered names</summary>${Inputs.table(uncovered.map((u) => ({name: u.model_name, provider: u.provider,
  weights: u.closed ? "closed" : "open", reason: u.reason_code, evidence: u.evidence_url})), {format: {evidence: link}, layout: "auto"})}</details>`);
```

</section>

<section id="data-quality">

## Data quality

```js
const sc = E.spot_check.rows;
const nDiff = sc.filter((r) => Math.abs(r.pct_diff) > 0.01).length;
const n2x = sc.filter((r) => Math.abs(r.pct_diff - 1) < 1e-9).length;
display(html`<p>LiteLLM replay: ${M.replay_days} daily snapshots from 2023-09-06; ${M.replay_error_days} days had an unparseable price file.</p>
<p>tokencanopy spot-check: tokencanopy's rows for first-party platforms come from its ${M.tokencanopy_sources.join(", ")} feed, not from provider pages. ${nDiff} of ${sc.length} price fields differ from ours, ${n2x} of them by exactly 2×. We treat this as a check on that feed, not on our panel.</p>`);
```

</section>

<section id="definitions">

## Definitions

### Data model (grain declared, each enforced by a uniqueness test)

| Model | Grain (one row per) | Notes |
|---|---|---|
| `stg_litellm__snapshots` | snapshot_date × model_key | from replay |
| `stg_arena__leaderboard` | snapshot_date × arena_model × category | text configs; rank recomputed within snapshot |
| `stg_epoch__models` / `stg_epoch__benchmarks` | epoch model / model × benchmark | |
| `stg_pypi__downloads` | date × package (× installer if available) | |
| `dim_model` | canonical_model_id | from seeds |
| `dim_model_price` | model_key × valid_from | SCD2 (§5) |
| `fct_model_price_daily` | canonical_model_id × date | first-party, standard tier, blended 3:1; date spine from listing to delist/today |
| `fct_price_change` | canonical_model_id × change_ts | pct change, `is_cut` (≥10%), `is_correction` |
| `fct_arena_rank` | canonical_model_id × snapshot_date | rank, rank_percentile, method_era (splits at Jan-2024, May-2025, Jul-2025; E21) |
| `mart_launch_price_survival` | top-tier canonical_model_id | listed_at, first_cut_at, days_at_launch_price, censored |
| `mart_cut_audit` | audited cut | observed_ts, announced_date, lag_days, source_url (seed `seed_cut_audit.csv`) |
| `fct_sdk_downloads_daily` | sdk_group × date | Google SDKs summed (E24) |
| `mart_event_study_panel` | event_id × sdk_group × rel_day | built only after prereg commit (G8) |
| `source_freshness` | source × run_ts | rows, max_date, sla_days, is_stale |

**Event-date audit (G4):**

- Sample: 20 cuts stratified by provider *(my call)*. For each, Claude finds the provider's announcement (changelog or pricing page) and records its URL. The candidate spot-checks.
- Output: the commit-lag distribution `±d` in the headline.

### Metric definitions (one definition each)

| Metric | Definition |
|---|---|
| `blended_price_per_mtok` | `(3·input + 1·output)/4 × 1e6`, first-party standard tier |
| `days_at_launch_price` | first_cut_at − listed_at (days); censored at today or at the final delisting (the model's last version is `delisted` and no later version exists; a temporary absence does not censor, v1.2.1) |
| `km_median_days_at_launch_price` | Kaplan–Meier median over top-tier models, with IQR and n |
| `share_cut_within_365d` | KM-estimated 1 − S(365) (the fallback headline) |
| `cut_depth_pct` | price drop at the first cut |
| `commit_lag_days` | announced − observed, over the audited sample |
| `sdk_downloads_7d` | trailing 7-day sum of downloads, per SDK group |

MetricFlow semantic models mirror these for G10 only. If G10 is cut, the definitions still live in dbt docs and the Methods page.

</section>

<section id="freshness">

## Freshness

```js
const nFresh = freshness.filter((f) => !f.is_stale).length;
display(html`<p class="takeaway">${nFresh} of ${freshness.length} sources are within their freshness SLA.</p>`);
display(Inputs.table(freshness.map((f) => ({source: f.source, run_ts: f.run_ts.toISOString().slice(0, 16).replace("T", " ") + " UTC", rows: f.rows,
  max_date: f.max_date, sla_days: f.sla_days, is_stale: f.is_stale})), {layout: "auto"}));
```

</section>

<section id="sources">

## Sources

Sources and licenses are listed in docs/DATA.md in this project's repository. AI use is disclosed in docs/AI_USAGE.md.

</section>
