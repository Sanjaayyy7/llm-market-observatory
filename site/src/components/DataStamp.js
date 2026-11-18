import {html} from "npm:htl";

const LABELS = {litellm: "LiteLLM", arena: "Arena", epoch: "Epoch", pypi: "PyPI", tokencanopy: "tokencanopy"};

export function DataStamp(stamp) {
  const dates = Object.entries(stamp.max_dates).map(([k, v]) => `${LABELS[k] ?? k} ${v}`).join(", ");
  const run = stamp.run_ts.slice(0, 16).replace("T", " ");
  return html`<p class="stamp" data-testid="stamp">Data as of ${dates} · LiteLLM commit ${stamp.litellm_sha7} · rebuilt ${run} UTC</p>`;
}
