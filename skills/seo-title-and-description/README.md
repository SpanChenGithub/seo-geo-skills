# SEO Title and Description

> Research, audit, rewrite, or generate five SEO Title and Meta Description pairs for one page or a batch of up to ten pages.

## English Guide

### Core capabilities

- Extract page truth and existing metadata from pasted copy, a product brief, a URL, or readable source code.
- Research the current top organic results and analyze Title and visible-snippet vocabulary separately.
- Infer search intent and page type, audit existing metadata, and identify keyword-to-page mismatches.
- Generate five materially distinct Title and Meta Description pairs, with the strongest pair first.
- Support multiple languages and batches of up to ten pages.

### When to use

Use it to create metadata for a new page, audit or rewrite current metadata, study intent for a keyword and URL, or process several SaaS, online-tool, or content pages together.

### Inputs

**Required:** one primary keyword and enough page evidence for every item.

**Conditionally required:** page type when page and SERP evidence do not agree clearly.

**Optional:** country or region, output language, secondary keywords, brand, benefits, audience, and existing Title and Meta Description.

### Installation and invocation

Clone the repository, then copy the complete `skills/seo-title-and-description` directory to the location shown above. Invoke it with `$seo-title-and-description` in Codex or `/seo-title-and-description` in Claude Code and Cursor.

Example:

```text
$seo-title-and-description Primary keyword: online invoice generator. Page: https://example.com/invoice-generator
```

### Output

Each successful item returns exactly five numbered Title and Meta Description pairs. Research notes, rationale, audit commentary, sources, and character counts remain internal.

### Dependencies, network access, and credential safety

Fresh SERP access through authorized host search or browser tools is mandatory. Python 3 can run the bundled metadata validator. No paid API is required. Never provide or commit API keys, cookies, login details, or private-page credentials.

### Limitations

The Skill stops when current SERP evidence is unavailable, never edits implementation code, does not invent product claims, normally omits terminal brand suffixes, and cannot guarantee how Google displays a title link or snippet.

Author: Span · License: MIT
