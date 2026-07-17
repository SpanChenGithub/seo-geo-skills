# Blog Post Writer

> Turn one target keyword into a researched, approval-gated, publish-ready SEO/GEO article and an auditable content package.

## English Guide

### Core capabilities

- Research the current SERP, ranking pages, People Also Ask, related searches, and relevant community discussions.
- Determine search intent, article format, useful depth, and information-gain opportunities.
- Support explainers, how-tos, listicles, roundups, single-product reviews, comparisons, and alternatives articles.
- Produce a source-mapped outline first and draft only after explicit outline approval.
- Verify material claims, citations, internal links, media plans, SEO metadata, and eligible JSON-LD.
- Create a new article or perform a researched refresh of an existing one.

### When to use

Use it for a complete blog post, a content brief and outline, a researched article refresh, or content that needs stronger SEO, GEO, evidence, and original editorial value.

### Inputs

**Required:** `primary_keyword`.

**Optional:** language, country or region, audience, funnel stage, site or page URL, existing draft, brand and product context, value proposition, evidence, CTA, article type, reference length, format, tone, author, deadline, secondary keywords, entities, questions, internal links, competitors, first-party experience, tests, data, expert input, examples, screenshots, media, and output location.

### Installation and invocation

Clone the repository, then copy the complete `skills/blog-post-writer` directory to the location shown above. Invoke it with `$blog-post-writer` in Codex or `/blog-post-writer` in Claude Code and Cursor.

Example:

```text
$blog-post-writer Write a researched how-to for the keyword "reduce podcast background noise". Audience: beginners.
```

### Output

The normal workflow delivers a researched outline for approval, then a complete article for final approval. File mode produces an auditable package containing research, sources, the approved outline, draft, canonical Markdown article, one metadata set, media plan, quality report, and eligible structured data. Chat-only delivery is also supported.

### Dependencies, network access, and credential safety

Current SERP access through an authorized host search or browser capability is mandatory for formal generation. Python 3 is used to validate file packages. Companion skills are optional. Never paste or commit credentials; use secure host connections or environment variables, and authorize paid API calls before execution.

### Limitations

The Skill stops formal generation when fresh SERP evidence is unavailable, never fabricates experience or claims, does not guarantee rankings or AI citations, and does not publish or modify a website without a separate explicit request.

Author: Span · License: MIT
