# Tools Landing Page Generator

`tools-landing-page-generator` helps you turn one tool-style keyword and one official website into an evidence-backed static landing-page package. It researches current search results and public discussions, verifies product claims, follows the target site's visual language, writes American English copy by default, and validates the final responsive HTML.

> The generated tool area is intentionally non-functional. This Skill creates the page, copy, SEO assets, research records, and a clearly marked integration boundary; it does not build the product backend.

## Before you start

Prepare these two required inputs:

- One primary keyword, such as `ai music video generator`
- The official target website, such as `https://example.org`

If the final page URL already exists, include it. Otherwise, the Skill will inspect the site's URL conventions, propose a canonical URL, and wait for your confirmation before final SEO and HTML generation.

The following context is optional but reduces follow-up questions and makes the page more accurate:

- Product positioning and target users
- Real input, output, and workflow
- Verified features, differentiators, and limitations
- Pricing, signup, privacy, or security facts with official sources
- CTA goal, brand guide, screenshots, design tokens, or authorized assets
- Target market and page language when different from the US and English defaults

Do not paste API keys, login cookies, private credentials, or confidential customer data into the prompt.

## Install

Copy the complete Skill directory into a supported Agent Skills location. Do not copy only `SKILL.md`, because the references and validator are required by the workflow.

Common project-level locations:

| Host | Destination |
| --- | --- |
| Codex | `.agents/skills/tools-landing-page-generator/` |
| Claude Code | `.claude/skills/tools-landing-page-generator/` |
| Cursor | `.cursor/skills/tools-landing-page-generator/` or `.agents/skills/tools-landing-page-generator/` |

Restart the agent session if the host does not discover a newly installed Skill automatically.

## Quick start

Explicitly invoke the Skill and provide the required inputs:

```text
Use $tools-landing-page-generator.

Primary keyword: ai music video generator
Official website: https://example.org
Final page URL: https://example.org/ai-music-video-generator
```

In Claude Code or Cursor, use `/tools-landing-page-generator` when the host exposes installed Skills as slash commands. Natural-language invocation also works when the host supports Agent Skills.

## Recommended prompt

Use this template when you already have product and brand context:

```text
Use $tools-landing-page-generator to create one static tool landing page.

Primary keyword: <one keyword>
Official website: <https://official-site.example>
Final page URL: <existing or intended HTTPS URL>
Market and language: <for example, United States / English>

Product context:
- Product name and positioning: <...>
- Target users: <...>
- Real input and output: <...>
- Actual workflow: <3-4 steps>
- Verified features and differentiators: <...>
- Known limitations: <...>
- Privacy or security facts and official sources: <...>
- Primary CTA goal: <...>

Brand context:
- Representative same-site pages: <URLs>
- Brand guide, screenshots, tokens, or authorized local assets: <paths or links>

Output destination: <optional; default is output/<keyword-slug>/>
```

You may provide files or links instead of rewriting a knowledge base in the prompt. Clearly identify which facts are approved for public use.

## What happens during a run

The Skill processes one keyword and one page per run:

1. Records the brief and asks once for optional product context
2. Checks whether the keyword matches tool-page search intent
3. Researches current organic results, Reddit, and Quora
4. Verifies publishable product facts from official evidence
5. Extracts the target site's design language
6. Writes and stabilizes the visible copy
7. Generates metadata and JSON-LD
8. Builds and validates the static package

The agent may pause for your decision. A pause protects factual accuracy; it is not a failed run.

| Pause reason | What you need to decide or provide |
| --- | --- |
| No final page URL | Confirm the proposed canonical URL |
| Keyword is unsuitable or mixed | Revise the keyword or explicitly approve continuing |
| Fewer than 7 usable organic pages | Accept reduced evidence or stop |
| Product facts are insufficient | Supply the smallest missing set of official facts |
| Target-site style cannot be inspected | Provide screenshots, tokens, CSS, or a brand guide; or approve a neutral fallback |

## Output

The default destination is `output/<keyword-slug>/`. Existing output is never overwritten; a versioned sibling such as `-v2` is created instead.

```text
output/<keyword-slug>/
├── index.html
├── manifest.json
├── research/
│   ├── intake.md
│   ├── keyword-research-<keyword-slug>.md
│   ├── sources.json
│   ├── fact-ledger.json
│   └── style-report.md
├── content/
│   ├── landing-page-copy.md
│   └── seo-elements-<keyword-slug>.md
├── assets/
│   └── asset-manifest.json
└── validation/
    ├── validation-report.json
    ├── qa-report.md
    └── screenshots/  # when browser rendering is available
```

The package keeps research, fact, design, copy, and QA artifacts separate so reviewers can trace important claims and decisions before publication.

## Validate an output package

The Skill runs its validator before handoff. You can run it again after manual edits:

```bash
python3 ".agents/skills/tools-landing-page-generator/scripts/validate_landing_page.py" \
  "output/<keyword-slug>" \
  --keyword "<exact primary keyword>" \
  --pretty \
  --output "output/<keyword-slug>/validation/validation-report.json"
```

Replace the Skill path when you installed it elsewhere. Fix all errors before publishing; review warnings individually and document any accepted exception.

## Scope and limitations

- Creates a static, responsive HTML page and supporting artifacts
- Does not implement the actual generator, checker, converter, calculator, or other backend
- Does not guarantee rankings, traffic, conversions, or AI citations
- Does not fabricate prices, limits, privacy promises, ratings, performance, or product features
- Does not bypass CAPTCHA, login, paywalls, robots restrictions, or other access controls
- Does not hotlink third-party assets or copy another site's DOM, CSS, scripts, or tracking

## Troubleshooting

**The Skill asks many factual questions.**

Provide official product, pricing, help, privacy, and brand sources at the start. The Skill asks only for unresolved facts that block required sections.

**The workflow stopped after keyword research.**

The keyword may be navigational, informational, mismatched with the product, or supported by too little accessible evidence. Review the saved suitability decision, then revise the keyword or explicitly approve the documented reduced-evidence path when offered.

**No `index.html` was created.**

The workflow does not generate public copy or HTML when mandatory facts, canonical confirmation, evidence coverage, or visual guidance remains blocked. Resolve the handoff's listed blockers and resume the same task.

**The page has a tool box but it does not work.**

This is expected. The placeholder is a safe integration boundary for developers. Ask separately for implementation of the real tool and provide its API, component, or backend requirements.
