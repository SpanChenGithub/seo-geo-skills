# Batch Audit

Use this workflow for 2-10 URLs.

## Scope and execution

1. Normalize and deduplicate exact URLs while preserving their first input order. Keep meaningful query strings in evidence but omit them from filenames.
2. Record a status for every URL: `Completed`, `Partially completed`, or `Failed`, with the exact limitation. A failed URL never stops the remaining batch.
3. Audit URLs sequentially unless the available browser and performance tools explicitly support safe isolated parallel sessions. Avoid bursts that trigger rate limits.
4. Shared same-host evidence such as robots.txt and sitemap responses may be fetched once and reused only when the response and applicable scope are identical. Record that reuse. Never reuse page status, redirects, canonical, robots meta, DOM, schema, mobile layout, Lighthouse, CWV, GSC page data, or Ahrefs URL data across URLs.
5. Run separate mobile and desktop Lighthouse for every URL when available. If resource limits prevent complete coverage, do not choose only the first URL without disclosure. Record which URL/mode was attempted and why each remaining run is unavailable.
6. Apply shared target country or language to the batch only when the user supplied it as shared context. Map keywords or expected purposes per URL when supplied; do not force one keyword onto unrelated pages.
7. When an authorized Apify fallback is necessary, submit only the deduplicated requested URLs in one bounded run, disable link following, cap pages/results at the input count, use concurrency `1`, and keep one evidence/status record per URL. A missing or canonical-deduplicated Actor item makes that URL partial; it is never silently borrowed from another page. Escalate from raw Cheerio to rendered Web Scraper only for affected URLs and only under a separately authorized charge cap.

## Individual reports

Create one complete five-section report per URL using `audit-protocol.md` and the normal scoring rubric. Save each under the standard non-overwriting page-report path. A batch score is never substituted for an individual URL score.

## Batch summary

Save an additional UTF-8 Markdown report under:

`audits/tech-seo/batch-<shared-host-or-mixed-sites>-<YYYY-MM-DD>.md`

Use `mixed-sites` when the URLs span multiple hosts. If the path exists, append local time and then a numeric suffix. Never overwrite an existing file.

Use exactly these five level-two sections:

### 1. Batch Executive Summary

State scope, date, access modes, completed/partial/failed counts, and the most important shared conclusion. Include:

| URL | Status | Technical score | Evidence coverage | Mobile Lighthouse | Desktop Lighthouse | Indexability | Critical | High | Medium | Low | Immediate recommendation | Individual report |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- | --- |

Use `Not available - <reason>` rather than a bare unavailable value. Do not calculate an average score when page evidence coverage differs; if an average is useful, label it as descriptive and show how unavailable scores were excluded.

### 2. Cross-Page Priorities

Rank up to 10 root causes by severity, number of affected URLs, and likely implementation leverage. State `Affected: X/Y URLs` and list the URLs. Do not merge superficially similar issues when their causes or fixes differ.

### 3. Page Exceptions and Patterns

Summarize repeated metadata, canonical, robots, schema, link, image, performance, mobile, hreflang, or security patterns. Explicitly identify pages that do not share a common problem so a sitewide fix is not over-applied.

### 4. Consolidated Action Checklist

Separate sitewide/template work from page-specific work. Every item must name affected URLs and a verification method.

### 5. Assumptions and Limitations

State sampling, rate limits, unavailable tools/data, reused same-host evidence, GSC/Ahrefs scope, Apify Actor/run/mode/cost scope when used, failed URLs, and why the batch is not a full-site crawl. End with the batch summary path, the directory containing individual reports, and confirmation that no website or code was modified.

In the actual summary, render these five section names as level-two headings (`##`), not the level-three headings used to describe them above.

## Reconciliation checks

- The URL table contains every deduplicated input URL exactly once.
- Each completed or partial row links to an existing individual report.
- Severity counts and score values match the individual reports.
- Cross-page affected counts match the listed URLs.
- Missing evidence never becomes a pass and never lowers a score.
- The conversation links the batch summary and every individual report.
