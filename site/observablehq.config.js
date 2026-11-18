// style.css replaces `theme` (the two are exclusive in Framework); it imports air + near-midnight itself.
export default {
  title: "LLM Market Observatory",
  root: "src",
  style: "style.css",
  pages: [
    {name: "Home", path: "/index"},
    {name: "Price explorer", path: "/prices"},
    {name: "Methods & data", path: "/methods"}
  ],
  sidebar: false,
  toc: false,
  footer: "Data: see Methods → Sources."
};
