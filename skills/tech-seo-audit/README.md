# Technical SEO Audit

> Audit one to ten authorized URLs with real page evidence and deliver reproducible technical SEO scores, prioritized fixes, and saved Markdown reports.

## English Guide

### Core capabilities

- Inspect HTTP behavior, redirects, crawl and indexability signals, canonicals, robots.txt, and sitemaps.
- Audit metadata, rendered content, headings, links, images, media, and structured data.
- Run separate mobile and desktop Lighthouse audits when supported and keep lab and field evidence distinct.
- Review mobile UX, internationalization, security, and rendering-related failures.
- Add optional read-only GSC, Ahrefs MCP, user-export, and controlled Apify evidence.
- Calculate a transparent weighted score and evidence coverage, then prioritize deduplicated root causes.
- Produce one report per URL and an additional batch summary for two to ten URLs.

### When to use

Use it for a technical SEO health check, multi-page comparison, crawl or indexability investigation, metadata and schema review, performance and mobile analysis, or evidence-backed remediation planning.

### Inputs

**Required:** one explicit URL or a list of two to ten explicit URLs.

**Optional:** keyword, locale, expected page purpose or indexability, an authorized browser session, supplied HTML or exports, authorized GSC or Ahrefs access, and an authorized Apify connection with a positive per-run cost cap.

### Installation and invocation

Clone the repository, then copy the complete `skills/tech-seo-audit` directory to the location shown above. Invoke it with `$tech-seo-audit` in Codex or `/tech-seo-audit` in Claude Code and Cursor.

Example:

```text
$tech-seo-audit Audit https://example.com/category for technical SEO. Target keyword: online design tools.
```

### Output

The Skill returns and saves a complete five-section Markdown report for each URL under `audits/tech-seo/` without overwriting earlier runs. Batch work also creates a cross-page summary. Reports include evidence coverage, a reproducible technical score when enough evidence exists, device-specific Lighthouse results, prioritized findings, implementation guidance, and verification steps.

### Dependencies, network access, and credential safety

A real browser or equivalent inspection capability provides the strongest evidence; browser automation and limited static inspection are supported fallbacks. Lighthouse, GSC, Ahrefs, and Apify are optional evidence sources. Apify requires a securely configured `APIFY_API_TOKEN`, explicit charge authorization, and a positive cost cap. Never paste or commit credentials, cookies, private URLs, environment files, or dataset access links.

### Limitations

The Skill never bypasses access controls, cannot prove sitewide conditions from one page, cannot claim Google indexing without direct evidence, never invents unavailable metrics, audits only the URLs placed in scope, and remains read-only unless implementation is separately requested.

Author: Span · License: MIT
