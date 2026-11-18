import {html} from "npm:htl";

export const pct = (x, digits = 1) => `${(x * 100).toFixed(digits)}%`;

// mart_cut_audit.lag_days is announced − observed (negative = LiteLLM recorded it later); readers get days after.
export const lagAfter = (lag) => {
  if (lag == null) return "n/a";
  const d = -lag;
  return `${d} day${Math.abs(d) === 1 ? "" : "s"} after the provider's announcement`;
};

// parts: strings or {text, href}; testid is optional.
export function HeadlineStat(parts, {testid} = {}) {
  const kids = parts.map((p) => (typeof p === "string" ? p : html`<a href=${p.href}>${p.text}</a>`));
  return html`<p class="headline" data-testid=${testid ?? null}>${kids}</p>`;
}
