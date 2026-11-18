import * as Plot from "npm:@observablehq/plot";

const DATE_KEY = /(_ts|_at|date|listed)$/;

// Arrow rows -> plain objects: BigInt -> number, epoch-ms in date-like columns -> Date.
export function rows(table) {
  return Array.from(table, (r) => {
    const o = typeof r.toJSON === "function" ? r.toJSON() : r;
    return Object.fromEntries(Object.entries(o).map(([k, v]) => {
      const n = typeof v === "bigint" ? Number(v) : v;
      return [k, typeof n === "number" && DATE_KEY.test(k) ? new Date(n) : n];
    }));
  });
}

// lines: [{data: [{x, y, ...}], stroke, dash?, band?: {y1, y2}, tip?: (d) => string}]
// Shared by the KM chart and the price explorer. Extra marks go in `marks`.
export function StepChart({lines, marks = [], width, height = 360, xLabel, yLabel, ariaLabel,
  xType, yTickFormat, xDomain, yDomain, marginRight = 80}) {
  const body = lines.flatMap(({data, stroke, dash, band, tip}) => [
    band && Plot.areaY(data, {x: "x", y1: band.y1, y2: band.y2, curve: "step-after", fill: stroke, fillOpacity: 0.15}),
    Plot.lineY(data, {x: "x", y: "y", curve: "step-after", stroke, strokeWidth: 2, strokeDasharray: dash ?? null}),
    Plot.tip(data, Plot.pointerX({x: "x", y: "y", title: tip, stroke: "var(--muted)", fill: "var(--surface)"}))
  ].filter(Boolean));
  return Plot.plot({
    width, height, marginRight, marginLeft: 56, ariaLabel, ariaDescription: ariaLabel,
    style: {background: "transparent", color: "var(--ink-2)", fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
      fontVariantNumeric: "tabular-nums", overflow: "visible"},
    x: {label: xLabel, type: xType, domain: xDomain, stroke: "var(--muted)", grid: false},
    y: {label: yLabel, tickFormat: yTickFormat, domain: yDomain, grid: true, nice: true},
    marks: [Plot.gridY({stroke: "var(--grid)", strokeOpacity: 1, strokeWidth: 1}), ...body, ...marks]
  });
}
