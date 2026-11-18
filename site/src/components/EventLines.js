import * as Plot from "npm:@observablehq/plot";

export function EventLines(panel, width) {
  const paths = [
    ["A", "LiteLLM date", "var(--accent)", null],
    ["B", "Announcement date", "var(--ink-2)", "5 4"]
  ].map(([series, label, stroke, strokeDasharray]) => Plot.lineY(panel, {
    filter: (d) => d.series === series,
    x: "rel_day", y: "norm", z: "event_id", sort: "rel_day", stroke, strokeDasharray,
    ariaLabel: (d) => `${d.sdk_group} · ${d.event_date.toISOString().slice(0, 10)} · ${label} path`,
    title: (d) => `${d.sdk_group} · ${d.event_date.toISOString().slice(0, 10)}`
  }));
  const chart = Plot.plot({
    width, height: 320, marginLeft: 48, marginRight: 18,
    ariaLabel: "Daily SDK downloads relative to their pre-cut average. Each path is a cut event. The vertical rule marks the cut.",
    style: {background: "transparent", color: "var(--ink-2)"},
    x: {label: "Days from first price cut"}, y: {label: "Downloads / pre-cut mean", grid: true},
    marks: [Plot.ruleY([1], {stroke: "var(--muted)"}), ...paths,
      Plot.ruleX([0], {stroke: "var(--ink-2)", strokeDasharray: "2 3", ariaLabel: () => "First cut"})]
  });
  chart.setAttribute("data-testid", "event-paths");
  return chart;
}
