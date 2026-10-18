# Data sources

The toolkit's public data connectors, what each one is for, and how they were checked. Each connector lives in `connectors/`, is listed in `connectors/registry.yaml`, and has a recorded-response test in `tests/connectors/`.

**Last verified: 2026-10-18.** Each source's endpoint was called live. Access terms, key requirements and rate limits were checked against the provider's own pages where they could be loaded. Where a page couldn't be loaded, the rate limit says "see docs".

## How sources switch on

- **No sign-up:** works as soon as setup finishes.
- **No sign-up (free key raises limits):** works without a key; adding one gives more requests.
- **Free key:** off until you add the key to your `.env` file. Each line in `.env.example` explains where to sign up.
- **SEC EDGAR** also needs `ILA_CONTACT_EMAIL` in `.env`. SEC asks every user of its data service to identify themselves, and refuses requests that don't.

Check what's on at any time:

```
.venv/bin/python scripts/connectors/check.py
```

A source that isn't available never stops a run: research continues with web search and the gap is noted (FR-API-03).

## The sources

| Source | Connector id | Access | Key in `.env` | Used for | Limits | Docs |
|---|---|---|---|---|---|---|
| SEC EDGAR | `sec-edgar` | No sign-up | n/a | Filings, risk factors, reported financials (XBRL) of public companies | SEC fair-access limit (max 10 requests per second); contact email required in ILA_CONTACT_EMAIL | [docs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) |
| Wikipedia | `wikipedia` | No sign-up | n/a | Background on companies and technologies (Tier 3) | polite use; descriptive User-Agent | [docs](https://api.wikimedia.org/wiki/Core_REST_API) |
| GitHub | `github` | No sign-up (free key raises limits) | `GITHUB_TOKEN` | Open-source momentum | 10 searches a minute without a token, 30 with one | [docs](https://docs.github.com/en/rest) |
| Arbeitnow | `arbeitnow` | No sign-up | n/a | Hiring signals (mostly European jobs) | free public API; please do not abuse | [docs](https://www.arbeitnow.com/blog/job-board-api) |
| GDELT | `gdelt` | No sign-up | n/a | Recent news coverage, mainly for refresh | one request every 5 seconds | [docs](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/) |
| Hacker News | `hackernews` | No sign-up | n/a | Technology community discussion (Tier 3) | polite use | [docs](https://hn.algolia.com/api) |
| Currents API | `currents` | Free key | `CURRENTS_API_KEY` | Recent news from many publishers | free plan: 250 requests a day, 20 results each | [docs](https://currentsapi.services/en/docs/) |
| Federal Register | `federal-register` | No sign-up | n/a | US rules, proposed rules and notices | polite use | [docs](https://www.federalregister.gov/developers/documentation/api/v1) |
| EUR-Lex | `eurlex` | No sign-up | n/a | EU legislation (via the EU Publications Office SPARQL endpoint) | polite use | [docs](https://op.europa.eu/en/web/cellar/cellar-data/metadata/knowledge-graph) |
| Regulations.gov | `regulations-gov` | Free key | `REGULATIONS_GOV_API_KEY` | Federal dockets and public comments | api.data.gov hourly limit (see docs) | [docs](https://open.gsa.gov/api/regulationsgov/) |
| Congress.gov | `congress-gov` | Free key | `CONGRESS_GOV_API_KEY` | US bills and their status | 5,000 requests an hour | [docs](https://github.com/LibraryOfCongress/api.congress.gov) |
| U.S. Bureau of Labor Statistics | `bls` | No sign-up (free key raises limits) | `BLS_API_KEY` | Employment, wages and prices by industry | small daily limit without a key, higher with a free key (see docs) | [docs](https://www.bls.gov/developers/) |
| U.S. Census Bureau | `census` | Free key | `CENSUS_API_KEY` | Business counts, employment, demographics | key required for all queries since 2026-05-12 | [docs](https://www.census.gov/data/developers/guidance/api-user-guide.html) |
| Data USA | `datausa` | No sign-up | n/a | Ready-made US statistics | polite use | [docs](https://datausa.io/about/api/) |
| World Bank | `worldbank` | No sign-up | n/a | Country-level economic indicators | polite use | [docs](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392) |
| OECD | `oecd` | No sign-up | n/a | Cross-country statistics | rate-limited; keep requests few (see docs) | [docs](https://gitlab.algobank.oecd.org/public-documentation/dotstat-migration/-/raw/main/OECD_Data_API_documentation.pdf) |
| FRED | `fred` | Free key | `FRED_API_KEY` | Economic time series | see docs | [docs](https://fred.stlouisfed.org/docs/api/fred/) |
| USAspending | `usaspending` | No sign-up | n/a | Federal contract and grant awards | polite use | [docs](https://api.usaspending.gov/docs/endpoints) |
| SAM.gov | `sam-gov` | Free key | `SAM_GOV_API_KEY` | Federal contract opportunities | daily limit depends on your SAM.gov role (low for new accounts) | [docs](https://open.gsa.gov/api/get-opportunities-public-api/) |
| NPPES NPI Registry | `nppes` | No sign-up | n/a | US provider landscape | polite use | [docs](https://npiregistry.cms.hhs.gov/api-page) |
| openFDA | `openfda` | No sign-up (free key raises limits) | `OPENFDA_API_KEY` | Device and drug recalls, adverse events | 1,000 requests a day without a key, 120,000 with one (240 a minute) | [docs](https://open.fda.gov/apis/) |
| CMS Provider Data | `cms` | No sign-up | n/a | Medicare data on hospitals and providers | polite use; can be slow | [docs](https://data.cms.gov/provider-data/docs) |
| ClinicalTrials.gov | `clinicaltrials` | No sign-up | n/a | Research activity | polite use (see docs) | [docs](https://clinicaltrials.gov/data-api/api) |
| HealthData.gov | `healthdata` | No sign-up | n/a | HHS datasets | polite use | [docs](https://dev.socrata.com/) |
| FDIC BankFind | `fdic` | No sign-up | n/a | Bank landscape | polite use | [docs](https://api.fdic.gov/banks/docs/) |
| CFPB Consumer Complaints | `cfpb` | No sign-up | n/a | Complaint themes | polite use | [docs](https://cfpb.github.io/api/ccdb/api.html) |
| FCC Open Data | `fcc` | No sign-up | n/a | Coverage, complaints, licensing data | polite use | [docs](https://opendata.fcc.gov/) |
| US DOT Open Data | `us-dot` | No sign-up | n/a | Transportation statistics (DOT and BTS) | polite use | [docs](https://data.transportation.gov/) |

## Changes from the original plan, with reasons

The build plan listed 40 sources. After checking each one on 2026-10-18, the owner approved these changes:

| Source | Change | Why |
|---|---|---|
| U.S. Census Bureau | Moved to "free key" | Census requires a key for all Data API queries since 2026-05-12. |
| EUR-Lex | Moved to "no sign-up" | The EU Publications Office's public SPARQL endpoint answers without registration. |
| Econdb | Not included | Its API answers automated requests with a bot challenge. |
| OpenCorporates | Not included | No free self-serve API: paid plans only, with free access only for journalists, NGOs and academics. |
| Product Hunt | Not included | Its API terms say it "must not be used for commercial purposes". |
| PatentsView | Not included | The legacy API was retired in Feb 2025 and the newer one did not respond. The replacement (USPTO Open Data Portal) needs a verified USPTO.gov account. |
| Jooble | Not included | Its API documentation was behind a bot check and couldn't be verified. |
| The Guardian | Not included | The free developer key is "for any non-commercial usage". |
| GNews | Not included | The free plan is "Non-commercial use only". |
| Financial Modeling Prep | Not included | The free licence is for personal, non-business use. |
| New York Times | Not included | Its APIs are licensed for non-commercial use. |
| Adzuna | Not included | Commercial organisations need a licence after a trial. |
| TheNewsAPI | Not included | Its terms forbid use "in connection with any commercial endeavors" without approval. |
| Alpha Vantage | Not included | The free licence is personal, non-commercial; use on behalf of a company counts as commercial. |

**Rule used:** the toolkit is for product marketers doing their job, which is business use. A source is only included if its free access allows that.

## Known quirks

- **GDELT** allows one request every 5 seconds per address and may refuse requests for a while after heavy use. The connector waits between calls and reports the limit when it hits it.
- **CMS Provider Data** can be slow to answer.
- **Arbeitnow** has no search: it lists recent jobs (mostly in Europe), and the connector filters them by your query words. US hiring signals come from web search.
- **Congress.gov** has no keyword search: the connector filters the most recently updated bills by title.
- **openFDA** answers "not found" when nothing matches; the connector treats that as no results.
- **Series IDs change.** If a suggested series in an industry pack returns nothing, search the source for its replacement.

## Terms

You're responsible for using each source within its terms. Check them again before relying on a source commercially. Terms change, and this page reflects what was checked on the date above.
