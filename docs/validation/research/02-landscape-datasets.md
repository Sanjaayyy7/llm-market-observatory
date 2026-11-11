<!-- Raw research-agent report, captured verbatim 2026-11-10. Source of E-IDs in ../research-brief.md -->

# Analytics engineering portfolio projects: landscape and datasets (as of 2026-11-10)

"acc." means I accessed the page on 2026-11-10. Saturation ratings are my judgment. They rest on rough proxies: Kaggle download counts, GitHub repo-search counts, and existing products built on the data.

## 1. DataCamp's list, grouped by level

The article was published 2022-12-21 and last modified 2026-02-27, by Abid Ali Awan ([DataCamp](https://www.datacamp.com/blog/data-analytics-projects-all-levels), acc.). It has 30 projects. Most do not name a dataset source.

- **Beginner (1–9):**
  - NYC Airbnb listings
  - Word frequency in *Moby Dick* (scraped from Project Gutenberg)
  - NYC public school SAT scores
  - Motorcycle-parts sales database (SQL joins and window functions)
  - Bitcoin and crypto market caps
  - Nobel Prize winners
  - Fast-food stock prices (Plotly)
  - COVID-19 cases (R)
  - Super Bowl viewership and ads (R)
- **Advanced (10–17):**
  - "On the Road" car-insurance claims (logistic regression)
  - International soccer results (hypothesis testing)
  - World Bank international debt (SQL)
  - LAPD crime incidents
  - Netflix movies and *The Office* guest stars
  - Fast-food POS sales forecasting (R)
  - E-commerce purchase behavior
  - Credit-card approvals
- **Final-year students (18–24):**
  - Transport for London journeys 2010–2022, in a cloud warehouse
  - US traffic mortality (regression and KMeans)
  - Kidney-stone treatments (Simpson's paradox)
  - E-commerce demand forecasting (PySpark)
  - Twitter follower network
  - World population (Kaggle)
  - Data science and MLOps survey (Kaggle)
- **AI-powered (25–26):**
  - Customer-review sentiment
  - Kaggle "Store Sales" (Ecuadorian grocery chain) forecasting with Prophet
- **End-to-end (27–30):**
  - Unicorn companies (SQL)
  - UK-bank fraud model monitoring
  - Furniture and office-supplies sales with ARIMA
  - Otto e-commerce sessions recommender

What the list shows: almost every project uses a static snapshot. Only the TfL project uses a warehouse. None involves incremental loads, tests, or a modeling layer, which are the things that mark analytics engineering work.

## 2. Oversaturated topics and why each is a weak signal

**Kaggle's own numbers** (Kaggle datasets API, acc.):
- The all-time most-voted list includes Netflix Movies & TV Shows (822,847 downloads, last updated 2021-09-27), Iris (963,206), Credit Card Fraud (1,220,908), Video Game Sales (818,445), Olist (696,157), TMDB 5000 (554,781), and two COVID sets frozen in 2021–22 ([API](https://www.kaggle.com/api/v1/datasets/list?sortBy=votes), acc.).
- In searches, the top Superstore dataset has 355,323 downloads, NYC Airbnb has 258,370, and "Most Streamed Spotify Songs 2023" has 135,256 ([superstore](https://www.kaggle.com/api/v1/datasets/list?sortBy=votes&search=superstore), [airbnb](https://www.kaggle.com/api/v1/datasets/list?sortBy=votes&search=airbnb), [spotify](https://www.kaggle.com/api/v1/datasets/list?sortBy=votes&search=spotify), acc.).

**What Kaggle is trending now:** the "hottest" list is almost entirely support files for ML competitions, such as "Name That LLM" passage pools and CASMI26 chemistry assets. None of it is business data an analyst could model ([API](https://www.kaggle.com/api/v1/datasets/list?sortBy=hottest), acc.).
- In 2025 Kaggle ran 68 competitions, 34 of them community-hosted. Jane Street's market forecasting drew the most teams, 3,700+ ([ML Contests](https://mlcontests.com/state-of-machine-learning-competitions-2025), figures as of 2026-02-02).
- 2026 competitions include ARC Prize 2026, BirdCLEF+ 2026, CSIRO Image2Biomass, and Enveda CASMI 2026 ([search summary](https://www.refontelearning.com/blog/best-kaggle-competitions-for-beginners-2026), acc.). All are modeling contests, not analytics engineering work.

**Other portfolio lists reuse the same data:**
- Dataquest (updated 2026-03-03) uses Kaggle Hacker News posts, a FiveThirtyEight Star Wars survey, Kickstarter, Adventure Works, and Gapminder ([Dataquest](https://www.dataquest.io/blog/data-analyst-projects-for-beginners/)).
- Maven's Data Playground has 68 datasets, including Spotify Top 100, Airbnb listings, NYC Taxi Trips, Northwind, and pizza sales ([Maven](https://mavenanalytics.io/data-playground), acc.).
- The DataTalksClub Zoomcamp (46.8k stars) builds a dbt project called `taxi_rides_ny` in its analytics engineering module ([repo](https://github.com/DataTalksClub/data-engineering-zoomcamp/tree/main/04-analytics-engineering), acc.).

**GitHub repo-search counts** (acc.): titanic 107,499; superstore 38,420; "netflix analysis" 24,786; "covid dashboard" 14,515; "nyc taxi" 12,645; "airbnb analysis" 12,035; "spotify analysis" 11,516 ([e.g.](https://api.github.com/search/repositories?q=titanic&per_page=1)).

**Why each is weak:**
- **Titanic and Iris:** the known tutorial defaults. Every answer has already been published.
- **Netflix titles:** a single table with no facts or events and nothing to measure over time.
- **Superstore:** a Tableau sample with no real refresh.
- **COVID:** the sources stopped updating. CORD-19 was last updated 2022-06-06.
- **Airbnb, IMDB/TMDB, Spotify top songs:** one-off scrapes from 2017–2023, too small to need incremental models.
- **NYC taxi:** the data is excellent, but it is the default teaching dataset.

Caveat: claims that "recruiters dislike X" come from opinion pieces, not surveys ([Statology](https://www.statology.org/what-titanic-iris-and-house-prices-say-about-your-portfolio/), acc.).

## 3. Candidate datasets

| Dataset | Size | Freshness | License / terms | Access / cost | Questions it supports | Saturation |
|---|---|---|---|---|---|---|
| **GH Archive** | 15+ event types since 2011-02-12 ([site](https://www.gharchive.org/), acc.). About 1.5B events and 7 TB a year, a third-party estimate ([DevConf 2026](https://pretalx.devconf.info/devconf-cz-2026/talk/9XRAV8/)) | Hourly files; BigQuery updated hourly | No explicit data license; "may be subject to third party rights"; code is MIT ([repo](https://github.com/igrigorik/gharchive.org), acc.) | Free HTTP; BigQuery free up to 1 TB a month | Star velocity, fake stars, contributor churn, issue response time | Low–med: 120 repos match "gharchive" ([search](https://api.github.com/search/repositories?q=gharchive)), but OSS Insight already turns it into a product ([VLDB 2024](https://www.vldb.org/pvldb/vol17/p4321-ghazal.pdf)) |
| **Hacker News** | About 49.9M items. Item IDs run in sequence, and ID 49,856,688 was posted 2026-09-26 ([Algolia](https://hn.algolia.com/api/v1/search?query=dbt%20duckdb&tags=show_hn)); this is my inference | API is "near real time" with "no rate limit" ([API](https://github.com/HackerNews/API), acc.). BigQuery freshness unverified | Repo is MIT; no data terms stated | Free Firebase API plus Algolia search | How topics rise and fade, launch-to-traction, hiring-thread trends | Med: a Dataquest project; 429 repos for "hacker news analysis" |
| **Stack Exchange dump** | 91.6 GB compressed, 362 files, for the 2025-12-31 dump ([archive.org mirror](https://archive.org/details/stackexchange_20251231), 2026-01-06) | Quarterly | Content is CC BY-SA 4.0. Since July 2024 you must log in and affirm you won't train an LLM, and official archive.org uploads stopped ([DevClass](https://www.devclass.com/development/2024/07/30/stack-exchange-restricts-access-to-dump-of-user-contributed-data-critics-complain-this-contradicts-license/1625192), 2024-07-30). The 2025-06-30 dump contains planted bogus rows (archive.org) | Free with an account; SEDE for live SQL | Q&A decline, answer latency, tag migration | Med: the decline headline is widely covered, 207,204 questions in March 2014 vs 1,442 in July 2026 ([PPC Land](https://ppc.land/stack-overflow-drops-to-1-442-questions-in-july-down-99-from-2014-peak/), 2026-08-08) |
| **Wikipedia pageviews** | 33–71 MB gzipped per hour, about 1 GB+ a day ([Oct 2026 listing](https://dumps.wikimedia.org/other/pageviews/2026/2026-10/)) | Hourly since May 2015; API from 2015-07-01 | CC0 ([readme](https://dumps.wikimedia.org/other/pageviews/readme.html)) | Free; API requires a User-Agent ([policy](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html)) | Attention spikes, lag from news to public interest | Low–med |
| **NYC TLC trips** | 3B+ trips since 2009 ([repo](https://github.com/toddwschneider/nyc-taxi-data)) | Monthly Parquet, about 2 months behind; `cbd_congestion_fee` column from 2025 ([TLC](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page), acc.) | No license on the page; TLC disclaims accuracy | Free | Effect of congestion pricing, ride-hail vs taxi share | **High** |
| **Citi Bike** | Monthly zips; months over 1M trips are split ([system data](https://citibikenyc.com/system-data)) | Monthly, plus a real-time GBFS 2.3 feed | Bans redistributing the data as a stand-alone dataset; trademark limits ([license](https://www.citibikenyc.com/data-sharing-policy)) | Free | Rebalancing, e-bike mix | **High**: 4,581 repos |
| **FEC** | Transaction-level files, "very large"; Postgres dumps from 1975 ([FEC](https://www.fec.gov/data/browse-data/?tab=bulk-data)) | Daily to weekly | Contributor names can't be used commercially or to solicit donations | Free; api.data.gov key gives 1,000 requests/hour, DEMO_KEY 30/hour ([api.data.gov](https://api.data.gov/docs/developer-manual)) | Donor geography, small-dollar share, money flows between committees | Low–med |
| **SEC EDGAR XBRL** | Financial statement data sets: quarterly zips of 62–122 MB, 2009Q1–2026Q3 (page updated 2026-09-30) ([FSDS](https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets)) | APIs real-time (XBRL under a minute); `companyfacts.zip` rebuilt nightly around 3am ET ([APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)) | US government data | Free, no key; at most 10 requests/second ([SEC](https://www.sec.gov/about/developer-resources)) | Filing lag, restatements, peer KPI comparisons | Low–med: 280 repos, mostly libraries |
| **Open Food Facts** | About 4.99M products ([HF](https://huggingface.co/datasets/openfoodfacts/product-database)) | Nightly dumps plus 14-day delta files | ODbL/DbCL; images CC BY-SA ([data](https://world.openfoodfacts.org/data)) | Free; the API is not for scraping | Data completeness, reformulation over time | Low–med |
| **OpenAlex** | "Half a billion" works ([openalex.org](https://openalex.org/)) | Free snapshot quarterly; daily updates need Member+ at $10k/year | CC0 ([pricing](https://help.openalex.org/access/pricing/), 2026-11-03) | Free key with a $1/day budget | Citation lag, growth of AI papers | Low |
| **Hugging Face Hub** | 3.23M models, 1.12M datasets, 1.52M Spaces ([hub-stats](https://huggingface.co/datasets/cfahlgren1/hub-stats)) | "Updated Daily" | apache-2.0 | API free at 1,000 requests per 5 minutes ([limits](https://huggingface.co/docs/hub/rate-limits), Sep 2025) | Adoption by model family, license drift | Low–med |
| **OpenRouter** | Model list with per-token prices, including cache and reasoning fields ([docs](https://openrouter.ai/docs/guides/overview/models), acc.) | Live only; you have to snapshot it yourself to get history | Terms (updated 2026-08-31) ban scraping the site; the Rankings data has no reuse grant ([terms](https://openrouter.ai/terms)) | Models endpoint docs show no key | How prices fall over time, price spread across providers | Low–med but rising: 266 repos; a Kaggle snapshot with 1,581 downloads |
| **PyPI downloads** | 3.70T downloads across 1.09M packages ([ClickPy](https://clickpy.clickhouse.com/)) | Streamed to BigQuery; ClickPy daily | CC BY 4.0 ([PyPI docs](https://docs.pypi.org/api/bigquery/)) | BigQuery free up to 1 TB a month; some queries scan over 500 GB ([PyPA](https://packaging.python.org/en/latest/guides/analyzing-pypi-package-downloads/)) | AI SDK adoption, Python version churn | Low–med: 296 repos |
| **npm downloads** | Daily counts per package since 2015-01-10 | Daily, shortly after UTC midnight | Not stated | Free; 18-month window; bulk calls up to 128 packages and 365 days ([docs](https://github.com/npm/registry/blob/main/docs/download-counts.md)) | JavaScript framework share | Low |
| **LMArena** | Leaderboard history: 2.72M rows; latest publish date 2026-11-08 ([HF](https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset)). Also 136k votes from Apr–Jul 2025 ([140k](https://huggingface.co/datasets/lmarena-ai/arena-human-preference-140k)) | History released 2026-04-02 ([blog](https://arena.ai/blog/arena-leaderboard-dataset/)); update cadence not stated | CC BY 4.0; model outputs fall under each provider's terms | Free | Price per Elo point, gaps between categories | Med: third-party Elo history trackers already exist |
| **Epoch AI** | 17 datasets; the AI models dataset tracks 3,700+ models | Most updated in Nov 2026 | CC BY ([data](https://epoch.ai/data)) | Free | Compute trends, lab revenue | Low |
| **FRED / BLS** | — | Varies by series | FRED needs a key; series marked "Copyright" need the owner's permission; apps must show a non-endorsement notice ([terms](https://fred.stlouisfed.org/docs/api/terms_of_use.html)) | BLS v2: 500 queries/day, 50 series, 20 years per query ([FAQ](https://www.bls.gov/developers/api_faqs.htm)) | Macroeconomic context to join against | Med |
| **NOAA GHCN-Daily** | Yearly CSVs, 1763 to present | Daily | CC0 ([AWS](https://registry.opendata.aws/noaa-ghcn/)) | S3 needs no account; CDO API limited to 5 requests/second and 10k/day ([CDO](https://www.ncei.noaa.gov/cdo-web/webservices/v2)) | Weather as a control variable | Med |
| **Reddit API** | — | — | Self-service access closed Nov 2025; new tokens need approval ([r/redditdev mirror](https://r.datuan.dev/r/redditdev/s/gquSJqMgrM), 2025-11-11) | Gated | — | Avoid |
| **GitHub Innovation Graph** (added) | Activity by economy since 2020 | Quarterly | CC0 ([repo](https://github.com/github/innovationgraph)) | Free | Developer growth by country | Low |

## 4. Praised portfolio projects and what made them stand out

"Praised" here means stars, Hacker News points, press coverage, or an official listing. None of these sources reports a hiring outcome.

1. **Todd Schneider, NYC taxi** (2015-11-17, updated 2016 and 2018).
   - It answers sharp, specific questions, such as "the median trip leaving Midtown headed for JFK Airport between 4 and 5 PM takes 64 minutes!" ([post](https://toddwschneider.com/posts/analyzing-1-1-billion-nyc-taxi-and-uber-trips-with-a-vengeance/)).
   - Everything is reproducible from the repo (2.1k stars), and a companion dashboard refreshes monthly ([repo](https://github.com/toddwschneider/nyc-taxi-data), acc.).
2. **Jacob Matson, MDS-in-a-box / nba-monte-carlo.**
   - DuckDB published it as a guest post on its official blog (2022-10-12). The pipeline "runs in under 8 seconds" ([DuckDB](https://duckdb.org/2022/10/12/modern-data-stack-in-a-box)).
   - The repo has 610 stars and 984 commits. It runs locally, in Docker, or in a devcontainer. A GitHub Action deploys the live site, mdsinabox.com, and the dbt docs are published ([repo](https://github.com/matsonj/nba-monte-carlo), acc.).
3. **Make Open Data.**
   - dbt Labs lists it as an official example: "production-grade ELT with tests, documentation, and CI/CD" on messy French government data ([dbt FAQ](https://docs.getdbt.com/faqs/Project/example-projects), acc.).
   - It has `dbt test` suites and a public data catalogue, and a full production run takes about an hour ([repo](https://github.com/make-open-data/make-open-data), acc.).
4. **StarScout (CMU and collaborators).**
   - Built on GH Archive data from July 2019 to December 2024. It flags 6.0M suspected fake stars across 18,617 repos, and it checked its detector against a confirmed malware campaign (81% of repos and 76% of accounts caught). Accepted at ICSE'26 ([arXiv](https://arxiv.org/abs/2412.13459), v2).
   - It stands out for a crisp claim, a validation step, and stated false-positive caveats.
5. **Two Show HN projects: praised for timeliness, criticized on method.**
   - "State of the Art of Coding Models, According to HN Commenters" got 168 points and 87 comments (2026-05-02). Commenters said it defined "state of the art" as "popular," noted fewer than 300 mentions in total, and called the chart unreadable ([HN](https://hn.algolia.com/api/v1/items/47990708)).
   - "Arena AI Model ELO History" got 70 points (2026-05-14). The main critique was that Elo is relative, so a falling score doesn't prove a model got worse ([HN](https://hn.algolia.com/api/v1/items/48130711)).

**Two public yardsticks for what reviewers look for:**
- The DataTalksClub Zoomcamp rubric scores problem description, cloud and IaC, orchestration, warehouse partitioning "with explanation," dbt, dashboard, and reproducibility ([rubric](https://github.com/DataTalksClub/data-engineering-zoomcamp/blob/main/projects/README.md), acc.).
- The DataTalksClub podcast wiki says a strong project "starts with a repeated business question and ends with a trusted analytical surface." It warns against "KPI screenshots without source caveats" ([podwiki](https://datatalksclub.github.io/podwiki/wiki/analytics-engineering-portfolio-projects/), acc.).

**What the standouts share:** one surprising, specific number; a single command to rebuild everything; an artifact that keeps refreshing; written metric definitions and caveats; and a check against ground truth. Every critique of the weaker projects was about whether the metric meant what it claimed.

## Top 5 under-explored angles with strong data

1. **LLM price and performance tracker.**
   - Take a daily snapshot of OpenRouter's `/api/v1/models` and keep the price history as slowly changing dimension rows. Join it to LMArena's leaderboard history (CC BY) and Epoch's AI models data (CC BY).
   - Questions: price per Elo point over time; how fast prices fall after a model launches; the open vs closed gap.
   - Don't scrape OpenRouter's Rankings page; its terms forbid it.
2. **Open-source popularity vs real usage.**
   - Join GH Archive (hourly) with PyPI or ClickPy and npm downloads (daily).
   - Questions: does star growth predict downloads? Which repos are flagged by StarScout-style anomaly rules? How fast are AI SDKs being adopted?
3. **XBRL "as-reported vs as-restated" warehouse.**
   - Combine the nightly SEC `companyfacts` file, the real-time submissions API, and the quarterly financial statement data sets.
   - Build point-in-time snapshots to measure restatements and filing lag. This shows real modeling depth, and few portfolio projects do it.
4. **2026 midterms: money vs attention.**
   - Join the FEC 2025–26 cycle data (daily to weekly) with hourly Wikipedia pageviews for candidates. Election day was 2026-11-03.
   - Keep contributor names out of anything public, given the FEC's commercial-use rule.
5. **Where developer Q&A went.**
   - Combine the Stack Exchange quarterly dump (filter out the watermark rows), the HN API, and GitHub issue events from GH Archive.
   - The decline headline is well covered; a multi-source model of where the questions moved is not.

## Where evidence is thin

- **Recruiter preferences:** no surveys exist; the claims are opinion pieces. The "praise" in section 4 is stars, points, and press, not hiring results.
- **Unverified freshness:** HN's BigQuery table, and the update cadence of LMArena's history dataset.
- **Sizes not from the owners:** GH Archive's size is a third-party estimate; PyPI's BigQuery table size is unknown; the hub-stats README doesn't say how the data is collected.
- **License gaps:**
  - GH Archive and NYC TLC state no data license.
  - Citi Bike's carve-out for analyses and reports seems tied to non-commercial use.
  - OpenRouter's terms don't say explicitly whether you may republish data pulled from its API.
- **Second-hand sources:**
  - I couldn't fetch any Stack Exchange site, so the dump agreement comes from press coverage.
  - Reddit's policy comes from community mirrors.
  - Kaggle's competition list comes from third-party pages, because the competitions API needs a login.
- **Saturation counts:** these are rough keyword searches, and they include libraries as well as analyses.

I checked no Reddit, LinkedIn, or Kottke posts directly. Before you publish anything built on GH Archive or OpenRouter data, read their terms yourself.