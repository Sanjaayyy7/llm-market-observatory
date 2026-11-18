// style.css replaces `theme` (the two are exclusive in Framework); it imports air + near-midnight itself.
export default {
  title: "LLM Market Observatory",
  root: "src",
  style: "style.css",
  globalStylesheets: [], // drop the default Google Fonts link (dist/config.js:185): system fonts only, no third-party request
  pages: [
    {name: "Home", path: "/index"},
    {name: "Price explorer", path: "/prices"},
    {name: "Adoption", path: "/adoption"},
    {name: "Methods & data", path: "/methods"}
  ],
  sidebar: false,
  toc: false,
  footer: "Data: see Methods → Sources.",
  // link previews (LinkedIn, Slack, X) and the tab icon; the icon is inline so no extra request
  head: `<meta name="description" content="Daily history of first-party LLM API list prices since 2023, rebuilt from LiteLLM's git history, with tested methods and a pre-registered validation against Epoch AI.">
<meta property="og:type" content="website">
<meta property="og:title" content="LLM Market Observatory">
<meta property="og:description" content="Daily history of first-party LLM API list prices since 2023, rebuilt from LiteLLM's git history, with tested methods and a pre-registered validation against Epoch AI.">
<meta property="og:url" content="https://sanjaayyy7.github.io/llm-market-observatory/">
<meta name="twitter:card" content="summary">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='6' fill='%23111827'/%3E%3Cpath d='M6 9h7v7h6v7h7' fill='none' stroke='%2360a5fa' stroke-width='3'/%3E%3C/svg%3E">`
};
