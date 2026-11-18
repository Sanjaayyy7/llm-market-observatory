---
title: Price explorer
toc: false
---

# Price explorer

```js
import * as Plot from "npm:@observablehq/plot";
import {StepChart, rows} from "./components/StepChart.js";
import {pct} from "./components/HeadlineStat.js";
const models = rows(await FileAttachment("data/models.parquet").parquet());
const daily = rows(await FileAttachment("data/price_daily.parquet").parquet());
const changes = rows(await FileAttachment("data/price_changes.parquet").parquet());
const audit = rows(await FileAttachment("data/cut_audit.parquet").parquet());
const providerOf = new Map(models.map((m) => [m.canonical_model_id, m.provider]));
const cuts = changes.filter((c) => c.is_cut && !c.is_correction);
const corrections = changes.filter((c) => c.is_correction);
const pricedIds = [...new Set(daily.map((d) => d.canonical_model_id))].sort();
const cutIds = new Set(cuts.map((c) => c.canonical_model_id));
const defaultModel = pricedIds.find((id) => cutIds.has(id));
const providers = [...new Set(pricedIds.map((id) => providerOf.get(id)))].sort();
const usd = (x) => `$${x.toFixed(2)}`;
const day = (d) => d.toISOString().slice(0, 10);
```

<p class="takeaway" data-testid="takeaway">${cutIds.size} of ${pricedIds.length} priced models had a recorded list-price cut; the rest had no recorded cut (corrections, listed below, are not cuts).</p>

```js
const provider = view(Inputs.select(providers, {label: "Provider", value: providerOf.get(defaultModel)}));
```

```js
const ids = pricedIds.filter((id) => providerOf.get(id) === provider);
const model = view(Inputs.select(ids, {label: "Model", value: ids.includes(defaultModel) ? defaultModel : ids[0]}));
```

```js
const series = daily.filter((d) => d.canonical_model_id === model)
  .map((d) => ({x: d.date, y: d.blended_per_mtok})).sort((a, b) => a.x - b.x);
const myCuts = cuts.filter((c) => c.canonical_model_id === model);
const cutPoints = myCuts.map((c) => ({x: c.change_ts, y: c.blended, label: `−${pct(-c.pct)}`}));
const chart = StepChart({
  width,
  lines: [{data: series, stroke: "var(--accent)", tip: (d) => `${day(d.x)}\n${usd(d.y)} per 1M tokens`}],
  marks: [
    Plot.dot(cutPoints, {x: "x", y: "y", r: 5, fill: "var(--accent)", stroke: "var(--surface)", strokeWidth: 2}),
    Plot.text(cutPoints, {x: "x", y: "y", text: "label", dy: -14, fill: "var(--ink)", fontWeight: 600})
  ],
  xType: "utc", xLabel: null, yLabel: "USD per 1M tokens (blended 3:1)",
  yDomain: [0, Math.max(0, ...series.map((d) => d.y)) * 1.15],
  ariaLabel: `Step chart of the blended list price of ${model}, ${series.length} daily points, ${myCuts.length} recorded cut${myCuts.length === 1 ? "" : "s"}.`
});
chart.setAttribute("data-testid", "price-chart");
display(html`<p class="takeaway">${model}: ${myCuts.length ? `list price cut ${myCuts.length} time${myCuts.length === 1 ? "" : "s"}, ${myCuts.map((c) => `${pct(-c.pct)} on ${day(c.change_ts)}`).join("; ")}.` : "no recorded list-price cut."}</p>`);
display(chart);
```

<p class="source">Source: LiteLLM price file git history, daily last snapshot; fct_model_price_daily, fct_price_change.</p>

## All recorded cuts

```js
const auditKey = new Map(audit.map((a) => [`${a.canonical_model_id}|${+a.observed_ts}`, a]));
const matched = cuts.filter((c) => auditKey.has(`${c.canonical_model_id}|${+c.change_ts}`)).length;
const cutRows = cuts.map((c) => {
  const a = auditKey.get(`${c.canonical_model_id}|${+c.change_ts}`);
  return {model: c.canonical_model_id, provider: providerOf.get(c.canonical_model_id), date: day(c.change_ts),
    "from → to (USD/1M)": `${usd(c.prev_blended)} → ${usd(c.blended)}`, depth: pct(-c.pct),
    audit: a?.verdict ?? "not audited", "days after announcement": a?.lag_days == null ? null : -a.lag_days, source: a?.source_url ?? null};
}).sort((a, b) => a.date.localeCompare(b.date));
const link = (u) => (u ? html`<a href=${u}>source</a>` : "–");
display(Inputs.table(cutRows, {format: {source: link, "days after announcement": (v) => v ?? "–"}, layout: "auto"}));
```

## Corrections (not counted as cuts)

```js
display(Inputs.table(corrections.map((c) => ({model: c.canonical_model_id, provider: providerOf.get(c.canonical_model_id),
  date: day(c.change_ts), "from → to (USD/1M)": `${usd(c.prev_blended)} → ${usd(c.blended)}`, label: "correction"})), {layout: "auto"}));
```
