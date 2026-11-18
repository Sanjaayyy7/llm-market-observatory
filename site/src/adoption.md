---
title: Adoption
toc: false
---

# SDK downloads around price cuts

```js
import {rows} from "./components/StepChart.js";
import {lagAfter, pct} from "./components/HeadlineStat.js";
import {EventLines} from "./components/EventLines.js";
import {PlaceboHist} from "./components/PlaceboHist.js";
const study = await FileAttachment("data/event_study.json").json();
const panel = rows(await FileAttachment("data/event_panel.parquet").parquet());
const placebos = rows(await FileAttachment("data/placebo.parquet").parquet());
const scoredCuts = rows(await FileAttachment("data/cut_audit.parquet").parquet()).filter((d) => d.is_scored_event);
const eventPaths = panel.filter((d) => d.sdk_group !== "control");
const comparable = study.events.filter((d) => d.ratio != null && d.placebo_share_le != null);
const dateBasis = {A: "LiteLLM record", B: "Provider announcement"};
const ratio = (value) => value == null ? "—" : `${value.toFixed(2)}×`;
const eventLabel = (d) => `${d.sdk_group} · ${d.event_date} · ${dateBasis[d.series]}`;
const prereg = `https://github.com/Sanjaayyy7/llm-market-observatory/commit/${study.prereg_commit}`;
const definition = (value) => html`<a href="./methods#adoption">${value}</a>`;
```

<p><a href="./methods#adoption"><strong data-testid="adoption-verdict">Descriptive only: n=${study.verdict.slice(study.verdict.indexOf("=") + 1)}</strong></a></p>

```js
display(html`<p>Primary dates come from LiteLLM’s price history. The provider-announcement series contains ${definition(study.k_b)} events. ${study.matches_prereg ? "" : "The event list has changed since pre-registration."} <a href=${prereg}>Pre-registration</a></p>`);
```

## Download paths

<p class="takeaway">Each line compares daily downloads with that SDK’s own pre-cut average.</p>

```js
display(EventLines(eventPaths, width));
```

<div class="legend"><span><svg width="24" height="10" aria-hidden="true"><line x1="0" x2="24" y1="5" y2="5" stroke="var(--accent)" stroke-width="2"/></svg>LiteLLM date</span><span><svg width="24" height="10" aria-hidden="true"><line x1="0" x2="24" y1="5" y2="5" stroke="var(--ink-2)" stroke-width="2" stroke-dasharray="5 4"/></svg>Announcement date</span></div>
<p class="source">Source: ClickPy PyPI downloads, LiteLLM price history and provider announcements. The vertical rule marks the first cut in each event.</p>

## Comparison with placebo dates

<p class="takeaway">The cut-window ratio is shown against ratios for other dates in the same SDK group.</p>

```js
const event = view(Inputs.select(comparable, {label: "Compare cut event", format: eventLabel}));
```

```js
if (event) {
  const pool = placebos.filter((d) => d.sdk_group === event.sdk_group && d.ratio != null);
  display(PlaceboHist(pool, event, eventLabel(event), width));
  display(html`<p>Cut-window ratio <strong>${definition(ratio(event.ratio))}</strong>. ${definition(pct(event.placebo_share_le))} of placebo ratios were at or below it.</p>`);
} else {
  display(html`<p>No cut event has both a complete window and a placebo pool.</p>`);
}
```

<p class="source">Source: ClickPy PyPI downloads. Placebo dates exclude windows around recorded and verified cuts.</p>

## All cut events

<p class="muted adoption-table-hint">Scroll the table to see all columns.</p>

```js
display(html`<table class="adoption-events" tabindex="0" aria-label="SDK download ratios by cut event">
  <thead><tr>${["SDK", "Date", "Date source", "Models", "Post/pre", "Placebos at or below", "requests control"].map((label) => html`<th scope="col">${label}</th>`)}</tr></thead>
  <tbody>${study.events.map((d) => html`<tr>
    <td>${d.sdk_group}</td><td>${d.event_date}</td><td>${dateBasis[d.series]}</td><td>${d.members.join(", ")}</td>
    <td>${d.incomplete_window ? "Incomplete window" : definition(ratio(d.ratio))}</td>
    <td>${d.placebo_share_le == null ? "—" : definition(pct(d.placebo_share_le))}</td>
    <td>${d.control_ratio == null ? "—" : definition(ratio(d.control_ratio))}</td>
  </tr>`)}</tbody>
</table>`);
```

```js
const undated = scoredCuts.filter((d) => d.announced_date == null).length;
const longestLag = scoredCuts.filter((d) => d.lag_days < 0).sort((a, b) => a.lag_days - b.lag_days)[0];
const missed = study.verified_missed_cuts.map((d) => `${d.model} (${d.date})`).join(", ");
display(html`<p class="caveat" data-testid="adoption-limits">${definition(`${undated} of ${scoredCuts.length}`)} recorded cuts lack a dated provider announcement. ${longestLag ? html`LiteLLM recorded the ${longestLag.canonical_model_id} cut ${definition(lagAfter(longestLag.lag_days))}. ` : ""}There is no window for the ${definition(study.verified_missed_cuts.length)} verified cuts LiteLLM missed: ${missed}.</p>`);
```

<p class="caveat">Cuts apply to individual models. Downloads cover provider SDKs and include CI and mirror traffic. These comparisons do not establish that price changes caused any download changes. <a href="./methods#adoption">Read the definitions and limits.</a></p>
