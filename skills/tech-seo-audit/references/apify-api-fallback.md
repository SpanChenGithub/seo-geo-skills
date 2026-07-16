# Apify API Fallback

## Table of Contents

1. [Purpose and trigger](#purpose-and-trigger)
2. [Authorization gates](#authorization-gates)
3. [Safe crawl profile](#safe-crawl-profile)
4. [API workflow](#api-workflow)
5. [Evidence interpretation](#evidence-interpretation)
6. [Failure handling](#failure-handling)
7. [Official references](#official-references)

## Purpose and trigger

Use Apify only to fill a defined page-evidence gap after direct browser, browser automation, and static HTTP collection are unavailable or materially incomplete, or when the user explicitly requests Apify. Suitable gaps include a rendered DOM that local automation cannot return, a small authorized batch that needs consistent DOM extraction, or a remote execution environment needed to reproduce a regional delivery difference.

Do not use Apify to obtain Lighthouse or Core Web Vitals metrics. Do not use it as proof of Googlebot access, Google indexing, real-user mobile UX, or production response headers unless the selected Actor actually returns the specific observed value.

## Authorization gates

Require every gate before starting a run:

1. The exact URL list contains 1-10 public or otherwise authorized URLs.
2. The URLs contain no credentials, private tokens, session identifiers, signed access parameters, or personal data. Use user-supplied HTML instead when those values are required for access.
3. The collection does not conflict with the target's robots rules or an explicit site prohibition.
4. The purpose is evidence collection, not bypassing a CAPTCHA, login, paywall, bot challenge, rate limit, geographic control, or another access decision.
5. `APIFY_API_TOKEN` is already present in the environment, or the host exposes a secure authorized Apify connection.
6. The user explicitly authorizes possible Apify charges for this run.
7. A positive `maxTotalChargeUsd` value is set before the run starts.

Never ask the user to paste the token into chat. Never write it to a file. Authenticate with `Authorization: Bearer <token>`, not a URL query parameter. Prefer a scoped, expiring token that can run the approved Actor and read only the new run's output.

## Safe crawl profile

Prefer an existing user-approved Actor or task whose schema and pricing can be inspected. Otherwise use the Apify-maintained `apify/cheerio-scraper` for remote raw HTTP evidence. Escalate only the affected URLs to `apify/web-scraper` when client-side rendering is necessary. Apply all of these controls to either Actor:

- `startUrls`: exact requested URLs only;
- `respectRobotsTxtFile: true`;
- `linkSelector: ""`, empty globs, and no calls to `enqueueRequest`;
- `maxPagesPerCrawl` and `maxResultsPerCrawl`: no more than the number of requested URLs;
- `maxConcurrency: 1`;
- `maxRequestRetries: 0`;
- `proxyRotation: "UNTIL_FAILURE"` with no residential group or custom proxy;
- for Web Scraper only: `useChrome: false`, `headless: true`, `ignoreSslErrors: false`, and `ignoreCorsAndCsp: false`;
- no initial cookies, login flow, custom authentication header, signed-agent mode, pre-navigation spoofing, or challenge solver;
- `closeCookieModals: false` and `maxScrollHeightPixels: 0` to keep the run read-only and avoid state-changing expansion;
- an extraction-only `pageFunction` that never clicks, types, submits, uploads, downloads, or enqueues another URL;
- `maxTotalChargeUsd` in the API query and a user-approved ceiling.

If the Actor reports a block, CAPTCHA, challenge, `401`, `403`, or `429`, do not rotate sessions, switch to stealth/residential proxies, change geography, add cookies, or retry. Record the blocked run and stop.

For raw HTML, prefer the local static HTTP path before Apify. Use Cheerio only when a remote raw request can fill a specific gap. Never label browser-rendered output as raw HTML, and never treat Cheerio output as a rendered DOM.

## API workflow

Prefer the bundled `scripts/apify_page_audit.py` helper because it enforces the safe profile and redacts the token. Its default mode is a no-network plan preview. Execute only after cost authorization:

```bash
python3 scripts/apify_page_audit.py https://example.com/ \
  --execute --cost-authorized --max-total-charge-usd 1.00
```

The helper defaults to raw HTTP with `apify/cheerio-scraper`. Add `--mode rendered` only for a documented JavaScript-rendering gap; that mode uses `apify/web-scraper`. The helper reads `APIFY_API_TOKEN` from the environment, polls the run, and retrieves only the default dataset items for that run. Do not print the environment or use shell tracing.

When a suitable Apify MCP or official client is available instead, inspect its current schema first and preserve the same controls. For direct REST calls:

1. Start the Actor with `POST /v2/actors/:actorId/runs`, JSON input, a Bearer header, `maxItems`, `maxTotalChargeUsd`, and a bounded `waitForFinish`.
2. Preserve the returned run ID, status, timestamps, Actor ID/build, default dataset ID, usage, and `usageTotalUsd` when present.
3. Poll `GET /v2/actor-runs/:runId` only while the run is non-terminal and within the authorized time/cost boundary.
4. Fetch `GET /v2/datasets/:datasetId/items?format=json&limit=<requested-count>`. Keep hidden `#debug` fields when they contain status code, loaded URL, retries, or failure evidence. Do not expose unrelated dataset items.

The synchronous dataset endpoint can return results directly, but it returns `408` when a run exceeds 300 seconds and a broken connection may hide run status. Prefer the asynchronous workflow when reliable run metadata matters.

## Evidence interpretation

Record:

- Actor or task name and build/version when exposed;
- run ID, start/finish time, terminal status, dataset ID, item count, and actual cost or authorized cap;
- canonicalized Actor-input and page-function SHA-256 values so the collection can be reproduced without saving raw API requests;
- requested URL, loaded/final URL, crawl mode, status code source, retry count, and challenge indicators;
- whether the evidence represents a remote rendered DOM, remote raw HTML, transformed content, or Actor metadata;
- differences from local browser and HTTP observations.

Use Apify DOM fields to verify content-based categories only when the returned item contains enough direct evidence. Do not infer missing response headers. Do not score Performance from navigation timing heuristics or Actor runtime. Do not treat an Apify `200` as proof that Googlebot receives the same response.

Never paste full raw HTML, private query data, dataset access URLs, tokens, cookies, or unrelated content into the report. Save no raw Apify dataset, page source, screenshot, or log by default.

## Failure handling

- `401` or `403` from Apify: report unavailable or insufficient permissions; direct the user to configure a scoped token securely.
- `402`, plan, rental, or billing error: stop and request explicit user direction; never raise the cost cap automatically.
- `408`: inspect the run status by run ID if available; otherwise report that the synchronous result is indeterminate. Do not start a duplicate run automatically.
- `429`: respect the rate limit and stop; do not loop or rotate credentials.
- Actor `FAILED`, `TIMED-OUT`, or `ABORTED`: record terminal status and relevant sanitized error summary. Do not retry unless the user separately authorizes a new charged run.
- Target challenge or access denial: preserve it as evidence and stop. Never enable bypass features.

## Official references

- [Apify API authentication](https://docs.apify.com/integrations/api)
- [Apify API v2 overview](https://docs.apify.com/api/v2)
- [Run Actor](https://docs.apify.com/api/v2/act-runs-post)
- [Run Actor synchronously and get dataset items](https://docs.apify.com/api/v2/act-run-sync-get-dataset-items-post)
- [Get dataset items](https://docs.apify.com/api/v2/dataset-items-get)
- [Apify Web Scraper](https://apify.com/apify/web-scraper)
- [Web Scraper input schema](https://apify.com/apify/web-scraper/input-schema)
- [Apify Cheerio Scraper](https://apify.com/apify/cheerio-scraper)
- [Cheerio Scraper input schema](https://apify.com/apify/cheerio-scraper/input-schema)
