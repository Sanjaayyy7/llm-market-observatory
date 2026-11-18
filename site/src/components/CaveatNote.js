import {html} from "npm:htl";

export function CaveatNote(text, href) {
  return html`<p class="caveat" data-testid="caveat">${text} <a href=${href}>Methods</a></p>`;
}
