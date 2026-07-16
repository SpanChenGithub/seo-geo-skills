# Connected Data Sources

## Google Search Console

Use an authorized GSC connector, MCP server, host integration, or user export when available. Keep access read-only.

1. Match the audited URL to an accessible property. Prefer the narrowest valid property and record whether it is a Domain or URL-prefix property.
2. For page performance, request the audited canonical URL using the most recent complete 28 days and compare with the preceding 28 days when the tool supports it. Record timezone, search type, country, device, and query filters.
3. Collect clicks, impressions, CTR, average position, leading queries, leading countries, and device split only when returned by GSC.
4. Use URL Inspection evidence for Google's selected canonical, coverage/indexing state, last crawl, crawl allowance, page fetch, and rich-result observations when the connector exposes them.
5. Never equate zero rows with zero demand or a non-indexed page. GSC may suppress low-volume data, lag, aggregate canonical URLs, or lack permission.
6. Never claim live indexing from a performance row alone. Attribute URL Inspection results and their inspection time.

If no GSC connection is callable, say `Not connected` or describe the permission/tool failure. Continue the audit and state which conclusions remain unverified. Do not ask for passwords, OAuth tokens, service-account JSON, or API keys in chat; direct the user to configure the host's secure connector or provide a redacted export.

## Ahrefs MCP

Use an authorized Ahrefs MCP server or user export read-only when available. Inspect the callable tool schema first because MCP method names and subscription coverage vary.

For the audited URL or its verified target, retrieve only relevant available evidence:

- organic keywords, estimated traffic, ranking URL, position, country/database, and snapshot date;
- referring domains and backlinks, including lost/new status when available;
- URL Rating or equivalent Ahrefs metric, explicitly labeled as an Ahrefs metric rather than a Google signal;
- competing pages, keyword gaps, content gaps, or SERP competitors when a target keyword is supplied;
- Site Audit issues only when the project and crawl snapshot are authorized and their crawl date is recorded.

Do not treat Ahrefs estimates as GSC measurements, a live crawl, Google index confirmation, or Lighthouse/Core Web Vitals data. Preserve database, country, date, target mode, and row limits. Separate page-level results from domain/subdomain/prefix results. Do not silently widen scope.

If the MCP server is absent, unauthorized, quota-limited, or lacks the requested endpoint, record the exact limitation and continue without fabricated data. Do not require Ahrefs for completion.

## Cross-source interpretation

- Keep live-page, Apify crawl, GSC, Ahrefs, Lighthouse, and user-export evidence in separately labeled rows or paragraphs. Apify is a page-collection source, not an SEO performance database; follow `apify-api-fallback.md`.
- Explain material discrepancies instead of forcing the numbers to agree. Common causes include different dates, country databases, canonical aggregation, estimation, filters, and crawl freshness.
- GSC and Ahrefs findings may change priority and recommendations, but missing connector data does not reduce the technical score. Only verified technical defects use the scoring rubric.
- Never include credentials, private property lists, account identifiers, raw access tokens, Apify dataset access URLs, or unrelated query data in the saved report.
