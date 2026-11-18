import * as Plot from "npm:@observablehq/plot";

export function PlaceboHist(pool, event, label, width) {
  const chart = Plot.plot({
    width, height: 270, marginLeft: 48, marginRight: 18,
    ariaLabel: `Placebo ratios for ${label}. The vertical line marks the cut-window ratio of ${event.ratio.toFixed(2)}×.`,
    style: {background: "transparent", color: "var(--ink-2)"},
    x: {label: "Post / pre download ratio"}, y: {label: "Placebo dates", grid: true},
    marks: [
      Plot.rectY(pool, Plot.binX({y: "count"}, {x: "ratio", fill: "var(--muted)", tip: true})),
      Plot.ruleY([0]),
      Plot.ruleX([event.ratio], {stroke: "var(--surface)", strokeWidth: 5, ariaHidden: true}),
      Plot.ruleX([event.ratio], {stroke: "var(--accent)", strokeWidth: 2, ariaLabel: () => "Selected cut ratio"})
    ]
  });
  chart.setAttribute("data-testid", "placebo-histogram");
  return chart;
}
