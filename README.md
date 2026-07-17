# SEO/GEO Skills

Reusable, evidence-first Agent Skills for SEO and GEO work in Codex, Claude Code, and Cursor.

> These Skills assist research and production; they do not guarantee rankings, traffic, or AI citations.

## Skills at a glance

| Skill | Best for | Main output | Data requirement |
| --- | --- | --- | --- |
| [`blog-post-writer`](skills/blog-post-writer/) | Researched SEO/GEO articles and content refreshes | Publish-ready article package | Current SERP evidence required |
| [`content-planner`](skills/content-planner/) | Whole-site content strategy by country | Validated `.xlsx` content plan | Ahrefs MCP required |
| [`query-fan-out-analysis`](skills/query-fan-out-analysis/) | Multi-provider fan-out and page-topic analysis | Provenance-labeled Markdown report | APIs optional; simulation available |
| [`seo-title-and-description`](skills/seo-title-and-description/) | SEO metadata generation, audit, and rewrite | Five ranked metadata pairs | Current SERP evidence required |
| [`tech-seo-audit`](skills/tech-seo-audit/) | Evidence-backed technical SEO audits | Prioritized Markdown audit report | Accessible URL or supplied evidence |
| [`tools-landing-page-generator`](skills/tools-landing-page-generator/) | Researched landing pages for online tools | Validated static HTML package | Keyword, official site, and current web evidence |

## Installation

Clone the repository first:

```bash
git clone https://github.com/SpanChenGithub/seo-geo-skills.git
cd seo-geo-skills
```

Copy the complete directory of the Skill you need into a supported Agent Skills directory. Common locations are:

| Host | Project scope | User scope |
| --- | --- | --- |
| Codex | `.agents/skills/<skill-name>/` | `$CODEX_HOME/skills/<skill-name>/`, commonly `~/.codex/skills/<skill-name>/` |
| Claude Code | `.claude/skills/<skill-name>/` | `~/.claude/skills/<skill-name>/` |
| Cursor | `.cursor/skills/<skill-name>/` or `.agents/skills/<skill-name>/` | `~/.cursor/skills/<skill-name>/` or `~/.agents/skills/<skill-name>/` |

Example: install one Skill at project scope for Codex or Cursor:

```bash
SKILL_NAME="query-fan-out-analysis"
TARGET_PROJECT="/path/to/your/project"

mkdir -p "$TARGET_PROJECT/.agents/skills"
cp -R "skills/$SKILL_NAME" "$TARGET_PROJECT/.agents/skills/"
```

For Claude Code, change the destination to `$TARGET_PROJECT/.claude/skills/`. Restart the agent session if the host does not discover a newly installed Skill automatically.

## Invocation

You can ask the agent in natural language to use an installed Skill. Explicit invocation commonly uses `$skill-name` in Codex and `/skill-name` in Claude Code or Cursor when the host exposes installed Skills as slash commands.

```text
Use $seo-title-and-description.

Primary keyword: audio to text converter
Page URL: https://example.com/audio-to-text
```

```text
Use /tech-seo-audit to audit:
https://example.com/product
```

## Skill guide

### `blog-post-writer`

Researches the current search landscape, creates a source-mapped outline, writes the article after outline approval, and packages the final SEO/GEO assets after a second approval gate. It supports explainers, how-to guides, listicles, roundups, product reviews, comparisons, alternatives articles, and researched refreshes of existing posts.

**Use it for**

- Creating a new article from a target keyword
- Refreshing an existing article with current evidence
- Producing a researched outline before drafting

**Inputs**

- Required: `primary_keyword`
- Optional: language, market, audience, site or draft, brand/product context, article type, tone, reference length, first-party evidence, internal links, CTA, and output location

```text
Use $blog-post-writer to create a publish-ready article.

Primary keyword: best AI music video generator
Audience: independent musicians
```

The Skill first presents live SERP findings and the source-mapped outline, then pauses for approval. It never treats outline approval as permission to publish.

**Output**

By default, it creates `articles/<keyword-slug>-<YYYY-MM-DD>/` with a brief, SERP research, source records, approved outline, draft, final `article.md`, one metadata set, media plan, quality report, and applicable structured data. Chat-only delivery is also supported.

**Network**

Current SERP evidence is mandatory before the formal outline or article. If live search is unavailable, the Skill asks for a fresh ranked top-10 export, screenshots, or copied results with query context and date. Paid APIs and companion Skills are optional and require authorization unless the current request already grants it.

### `content-planner`

Builds a country-specific, whole-site SEO/GEO content strategy for a new or existing website. It clusters same-intent keywords into planned pages, maps funnel and content types, identifies existing-page actions, calculates priorities, and generates a validated Excel workbook.

**Use it for**

- Keyword universes, topic clusters, pillar pages, and content gaps
- TOFU, MOFU, BOFU planning and publishing roadmaps
- Existing-page update, consolidation, and internal-link decisions

**Inputs**

- Required: existing or new site, target language, target country/market, and website theme or product description
- Additionally required for an existing site: website URL
- Optional: ICP, business model, conversion goal, seed keywords, competitors, exclusions, content capacity, and content-type constraints

```text
Use $content-planner to create a whole-site content plan.

Project type: Existing site
Website: https://example.com
Website theme: AI music creation tools
Target country: United States
Target language: English
```

**Output**

Each country receives a separate non-overwriting run directory under `content-planner-output/`. The validated workbook contains these visible sheets in order: `Content Plan`, `Raw Keywords`, `Topic Map`, `Roadmap`, `Strategy Notes`, and `Methodology`. JSON checkpoints and validation artifacts remain beside the workbook.

**Network and dependencies**

- An authenticated Ahrefs MCP connection is mandatory. Ahrefs is the exclusive source of keyword, competitor, ranking, and SERP metrics
- Authentication uses OAuth or the locally configured `AHREFS_MCP_KEY`; never paste its value into chat
- Ahrefs MCP requires an eligible paid Ahrefs plan and may consume API units
- Collection pauses after every 100 newly persisted keyword rows and asks whether to continue
- Workbook generation requires Python and `openpyxl`; missing dependencies are reported rather than installed silently

See [`Ahrefs MCP setup`](skills/content-planner/references/ahrefs-mcp-setup.md) for Codex, Claude Code, and Cursor configuration.

### `query-fan-out-analysis`

Maps the likely search subqueries used to resolve a keyword or prompt across OpenAI/ChatGPT-style APIs, Gemini, a Google AI Mode simulation, Claude, and Perplexity. It separates exact queries exposed by structured API traces from provider-generated candidates and host-model heuristic simulations.

**Use it for**

- Provider-specific fan-out queries and cross-model consensus
- Repeated-run stability and platform-specific angles
- Optional URL topic-gap analysis
- Prioritized topics a page should cover for SEO/GEO

**Inputs**

- Required: `seed_input`, either a target keyword or a complete prompt
- Optional: language, locale, persona, business context, freshness, desired answer type, URL or pasted page, providers, model IDs, run count, query target, and execution mode

```text
Use $query-fan-out-analysis to analyze "best CRM for startups"
across all supported providers and recommend topics for the primary page.
```

**Output**

The default Markdown report contains method and assumptions, intent gaps, optional external signals, provider-specific clusters, recurrence, cross-model consensus, a coverage matrix, optional page coverage, limitations, and prioritized SEO/GEO page topics. Validated JSON or CSV is returned only when requested.

**Network and credentials**

The default mode is API-first hybrid: three runs per provider and 10–15 generated candidates per run. If a documented API route and its environment credential are available, the Skill shows a sanitized plan and executes the ordinary default scope. Missing or failed APIs fall back to clearly labeled heuristic simulation unless the user requested observed-only mode. Google AI Mode has no corresponding consumer API here and is always labeled as simulation.

Optional credentials are read only from these environment variables:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `PERPLEXITY_API_KEY`

Use simulated-only, offline, no-network, or no-paid-API mode when desired. A larger-than-default run plan requires explicit authorization.

### `seo-title-and-description`

Researches, audits, rewrites, and generates SEO Title tags and Meta Descriptions for SaaS, online tools, content sites, and related page types. It reads supplied content, URLs, or source code for page truth but never edits the implementation.

**Use it for**

- Creating metadata for a new page
- Auditing and rewriting current metadata
- Processing a batch of up to 10 pages

**Inputs**

- Required: primary keyword and enough page evidence from pasted copy, a product brief, a URL, readable source code, or authorized web research
- Conditionally required: page type when page and SERP evidence cannot infer it reliably
- Optional: country or region, output language, secondary keywords, brand, core benefits, audience, and existing Title/Meta Description

```text
Use $seo-title-and-description.

Primary keyword: audio to text converter
Page type: Online tool
Page brief: A browser-based tool that converts audio files into editable text.
```

**Output**

For each successful page, the Skill returns exactly five distinct Title and Meta Description pairs. Pair 1 is the strongest recommendation. Successful output intentionally omits character counts, audit notes, research rationale, sources, and internal reasoning.

**Network**

Current SERP research is mandatory. The Skill inspects up to the top 10 organic results when available and analyzes Title vocabulary separately from snippet vocabulary. If live SERP access is unavailable or blocked, it pauses formal generation and asks for a SERP screenshot, export, or the top 10 titles, snippets, and URLs. It never bypasses CAPTCHA or scrapes Google with a custom script.

### `tech-seo-audit`

Audits one accessible URL or a batch of up to 10 explicit URLs using observed browser, HTTP, rendered DOM, Lighthouse, and authorized connector evidence. It keeps the audit read-only and separates confirmed defects from unavailable checks.

**Use it for**

- Crawlability and indexability reviews
- Metadata, headings, links, images, and structured data
- Mobile and desktop performance checks
- Internationalization, security, and batch root-cause analysis

**Inputs**

- Required: one `url`, or `urls` containing 2–10 explicit URLs
- Optional: target keyword, country or locale, expected page purpose or indexability, authenticated browser access already available, supplied HTML/headers/crawl exports/Search Console evidence/Lighthouse reports, and authorized GSC, Ahrefs, or Apify connections

```text
Use $tech-seo-audit to audit:
https://example.com/product

Target keyword: example product
Expected state: indexable
```

**Output**

For one URL, the complete five-section Markdown report is returned in the conversation and saved without overwriting to `audits/tech-seo/<host>-<path-slug>-<YYYY-MM-DD>.md`. A batch creates one complete report per URL plus a cross-page summary. Reports include evidence coverage, a reproducible Skill score when sufficient evidence exists, separate mobile and desktop results, prioritized findings, fixes, and limitations.

**Network and credentials**

The Skill prefers a real browser with DevTools-equivalent evidence, then browser automation, then limited static HTTP inspection. GSC and Ahrefs are optional read-only evidence sources. Apify is used only as a controlled fallback or when explicitly requested; every possibly chargeable Apify run requires explicit authorization and a positive cost cap. Its token is read only from `APIFY_API_TOKEN` or a secure host connection.

### `tools-landing-page-generator`

Researches a tool-style keyword, verifies product claims from official evidence, studies the current organic landscape and public discussion, extracts the target site's visual language, and creates a responsive static landing-page package with retained research, copy, SEO, design, and validation artifacts. The page includes an honest non-functional tool placeholder for later product integration.

See the [complete user guide](skills/tools-landing-page-generator/README.md) for installation, prompt templates, pause points, output structure, validation, and troubleshooting.

**Use it for**

- Building a new SEO landing page for a generator, maker, checker, converter, calculator, analyzer, editor, or similar utility
- Replacing or improving an existing tool page through the same evidence-first workflow
- Producing an auditable package instead of only final-page copy

**Inputs**

- Required: one primary keyword and one official target website; provide the final page URL when it already exists
- Optional: product knowledge base, positioning, target users, use cases, differentiators, limitations, market, language, canonical URL, and brand guidance

```text
Use $tools-landing-page-generator.

Primary keyword: ai music video generator
Official website: https://example.org
Final page URL: https://example.org/ai-music-video-generator
Market and language: United States / English

Product context:
- Real input and output: <...>
- Actual workflow: <...>
- Verified features and official sources: <...>
- Primary CTA goal: <...>
```

**Output**

By default, the Skill creates a non-overwriting directory under `output/<keyword-slug>/` containing source and fact records, keyword and product research, final copy, SEO elements, design notes, asset records, responsive `index.html`, deterministic validation results, a QA report, and browser screenshots when rendering is available.

**Network and limits**

Current organic results, Reddit, Quora, the official site, and representative same-site pages are researched through available first-party browser and web-search capabilities. The workflow does not require paid research APIs, does not bypass access controls, does not invent product claims, and does not implement the real tool backend. It stops for confirmation when the keyword is unsuitable, evidence coverage is insufficient, or a canonical URL must be chosen.

## Credential and data safety

- Never paste API keys, OAuth tokens, cookies, authorization headers, service-account files, or signed URLs into a prompt, issue, commit, or generated artifact
- Configure credentials through the host's OAuth flow, secure connector, or environment variables only
- Keep `.env`, `.local.env`, credential exports, raw provider responses, browser profiles, and private crawl data out of Git
- Review `git status` and staged changes before every commit; use a secret scanner when available
- A configured credential does not override a Skill's scope, access-control, cost, or approval rules
- Do not use these Skills to bypass CAPTCHA, login, paywall, robots restrictions, rate limits, or another access decision

## Design principles

- Evidence before claims
- Explicit provenance for observed, sourced, and simulated data
- Read-only by default; publishing and implementation require separate instructions
- No invented metrics, product facts, rankings, tests, or user experience
- Outputs are validated where a bundled deterministic validator exists

## Author

Span

## License

Licensed under the [MIT License](LICENSE).

Copyright (c) 2026 SpanChenGithub.
