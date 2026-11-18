import {html} from "npm:htl";

const LABELS = {litellm: "LiteLLM", arena: "Arena", epoch: "Epoch", pypi: "PyPI", tokencanopy: "tokencanopy"};

export function DataStamp(stamp) {
  // one unbreakable span per source so a date never wraps mid-value at 375 px
  const dates = Object.entries(stamp.max_dates).flatMap(([k, v], i) =>
    [i ? ", " : "", html`<span style="white-space:nowrap">${LABELS[k] ?? k} ${v}</span>`]);
  const run = stamp.run_ts.slice(0, 16).replace("T", " ");
  return html`<p class="stamp" data-testid="stamp">Data as of ${dates} · LiteLLM commit ${stamp.litellm_sha7} · rebuilt ${run} UTC</p>`;
}
