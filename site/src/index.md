---
title: Do top-tier LLMs ever cut their launch price?
toc: false
---

```js
import {HeadlineStat, pct, lagAfter} from "./components/HeadlineStat.js";
import {DataStamp} from "./components/DataStamp.js";
import {CaveatNote} from "./components/CaveatNote.js";
const headline = await FileAttachment("data/headline.json").json();
const stamp = await FileAttachment("data/stamp.json").json();
```

<h1 data-testid="question">Do top-tier LLMs ever cut their launch price?</h1>

```js
const numberLine = headline.validation === "failed"
  ? HeadlineStat([
      "Validation against Epoch AI failed (pre-registered): no market estimate in v1.0. LiteLLM's price file missed provider cuts we could verify. ",
      {text: "See Methods", href: "./methods#validation"}
    ], {testid: "headline"})
  : HeadlineStat([
      `${pct(headline.share_cut_365)} cut within 365 days (95% CI ${pct(headline.ci_low)}–${pct(headline.ci_high)}, n=${headline.n}, median commit lag ${lagAfter(headline.commit_lag_median_days)})`
      + (headline.method === "exact" ? ": too few cuts for a curve" : "")
    ], {testid: "headline"});
display(numberLine);
display(DataStamp(stamp));
display(CaveatNote("Prices are first-party list prices as recorded in LiteLLM's public price file, not provider announcements. Read the limits on", "./methods"));
```

<nav class="links"><a href="./prices">Price explorer</a> <a href="./methods">Methods &amp; data</a></nav>
