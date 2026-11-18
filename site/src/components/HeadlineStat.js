import {html} from "npm:htl";

export const pct = (x, digits = 1) => `${(x * 100).toFixed(digits)}%`;

// parts: strings or {text, href}; testid is optional.
export function HeadlineStat(parts, {testid} = {}) {
  const kids = parts.map((p) => (typeof p === "string" ? p : html`<a href=${p.href}>${p.text}</a>`));
  return html`<p class="headline" data-testid=${testid ?? null}>${kids}</p>`;
}
