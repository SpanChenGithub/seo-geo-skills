---
name: tools-landing-page-generator
description: Research, plan, write, build, and validate complete static HTML landing pages for online tools, generators, makers, checkers, converters, calculators, analyzers, editors, and similar utilities. Use when a user supplies a target keyword plus a target website or intended page URL and wants keyword suitability analysis, Google organic competitor research, Reddit and Quora topic research, optional product-context intake, evidence-based American English copy, target-site visual-style extraction, on-page SEO and JSON-LD, an honest non-functional tool placeholder, retained intermediate artifacts, and a responsive brand-matched index.html. Also use to improve or audit such a page when the same full workflow is required; do not use it to implement the actual tool backend or fabricate missing product facts.
---

# Tools Landing Page Generator

## Objective

Turn one primary target keyword and one target website into an evidence-backed landing-page package. Research before drafting, resolve product truth before making claims, reproduce the site's visual language with original code, and deliver a responsive static `index.html` whose tool area is explicitly non-functional.

Process one primary keyword and one page per run. Preserve intermediate research, copy, SEO, design, and validation artifacts so every important decision remains reviewable.

## Non-negotiable rules

- Require one primary keyword and an official target website. Accept a final page URL when it exists; otherwise propose one canonical URL and obtain confirmation before final SEO or HTML.
- Ask once, near the start, whether the user can provide a knowledge base, product positioning, target users, use cases, features, differentiators, limitations, or brand guidance. Treat that context as optional, then research official sources before asking only for unresolved blocking facts.
- Never invent product behavior, features, workflows, limits, pricing, free access, registration rules, compatibility, privacy, security, ratings, dates, metrics, comparisons, or results.
- Never reuse VidMage or any other example brand's name, domain, logo, social links, rating, compatibility list, or structured-data values.
- Use only available first-party browser and web-search capabilities. Do not require or call Apify, Cloudflare, proxy, scraping, or paid research APIs.
- Use current external research. Attempt the first 15 distinct eligible Google organic results and inspect full accessible pages. If fewer than 7 usable distinct pages remain, report coverage and pause for the user's decision.
- Research both Reddit and Quora. Preserve direct URLs, visible engagement only when actually available, access dates, and limitations. Forum material may reveal concerns and language but never proves target-product facts.
- Apply the keyword suitability gate before drafting. When the keyword fails, stop, explain why, suggest up to 3 evidence-supported directions, and continue only after an explicit user override or revised keyword.
- Default to United States, English, desktop, Google organic results when the user gives no market override. Write the public page in American English and write research and QA artifacts in the user's language.
- Follow this precedence when rules conflict: factual accuracy and effective SEO, natural clear expression, writing style, page structure, then suggested length targets. Record justified length exceptions.
- Keep all 8 content sections once and in this exact order: HERO, Why Choose, Key Features, How to, Comparison, FAQ, Privacy and Data Security, Final CTA. Keep the tool placeholder inside HERO.
- Do not implement or imitate a working tool. Make the reserved tool region honest, visible, non-interactive, and easy for a developer to replace.
- Treat explicit user style guidance as authoritative. Otherwise inspect the intended URL, its origin, and up to 3 representative same-site pages. Extract design tokens and patterns; never copy a public page's DOM, stylesheet, scripts, tracking, or unauthorized assets.
- Do not hotlink sampled-site images, fonts, icons, stylesheets, or scripts. Use user-supplied or authorized local assets; otherwise use documented CSS, SVG, or neutral placeholders. Do not invoke image generation unless the user separately requests it.
- Produce semantic, responsive, keyboard-accessible HTML with inline CSS and only essential inline JavaScript. Use no UI framework, remote font service, external stylesheet, analytics, or tracking code.
- Do not overwrite an existing output. Create a versioned sibling after reporting the collision. Never delete prior output to make room.
- Run deterministic validation and browser rendering when available. Fix every error before delivery and disclose any remaining warning or unperformed visual check.

## Load references progressively

Read each file completely when its stage begins:

1. Read [references/facts-and-intake.md](references/facts-and-intake.md) before asking intake questions or classifying product evidence.
2. Read [references/keyword-research.md](references/keyword-research.md) before searching, browsing competitors, deciding keyword suitability, or drafting the research report.
3. Read [references/site-style-extraction.md](references/site-style-extraction.md) before inspecting the target site's visual system or choosing a fallback.
4. Read [references/writing-style.md](references/writing-style.md) and [references/page-structure.md](references/page-structure.md) before outlining, drafting, or polishing public copy.
5. Read [references/seo-elements.md](references/seo-elements.md) after copy stabilizes and before generating metadata or JSON-LD.
6. Read [references/output-contract.md](references/output-contract.md) before creating the package or HTML.
7. Read [references/qa-checklist.md](references/qa-checklist.md) before validation, browser rendering, or handoff.

Do not draft from memory when the applicable reference has not been loaded.

## Workflow

### 1. Establish the brief

Follow `facts-and-intake.md`.

- Record the exact keyword, official target website, URL role, page language, market, and user-provided context.
- Ask the optional product-background question once. Do not repeatedly ask for facts already supplied.
- If only a domain or nonexistent route is supplied, inspect verified site routing conventions and propose one complete HTTPS canonical. Do not finalize metadata or HTML until the user accepts it.
- Identify high-risk facts required by Why Choose, Key Features, How to, Comparison, Privacy, CTA, and structured data.

### 2. Decide keyword suitability

Follow `keyword-research.md` and perform a focused SERP intent check.

- Confirm that the dominant intent is to use, find, compare, or choose a utility and that the target product can genuinely satisfy the task.
- Treat another brand's navigational query, an information-dominant query, product mismatch, or evidence too weak to judge as a stop or confirmation point.
- Save the decision and supporting sources before doing full-page copy work.

### 3. Complete current research

- Attempt 15 distinct eligible Google organic sites and record ranks, URLs, access dates, page types, and access states.
- Use only pages whose bodies were actually inspected for copy frequency, topic coverage, value propositions, or competitor claims. Do not treat snippets as full-page evidence.
- Research recurring, high-engagement Reddit and Quora topics when accessible.
- Produce the required synthesis in the exact order defined by `keyword-research.md`: value propositions, topic gaps, forum topics, frequency language, user profiles, 6 use cases, 20 semantic terms, and 10 FAQ candidates.
- Preserve a source manifest. Label evidence-based audience or use-case conclusions as inference rather than known customer data.

### 4. Resolve product truth and page URL

- Merge user-approved facts, supplied files, the target site's official product/help/pricing/privacy pages, and current official brand-controlled sources.
- Maintain a fact ledger with claim, value, source, access date, confidence, public-use status, and affected sections.
- Ask a bounded follow-up containing only unresolved facts that block mandatory sections. Do not infer target facts from competitors or forum discussions.
- Require a verified brand, actual workflow, 6 supportable feature angles, 5 evidence-backed competitors, 4 publishable privacy or security facts, one CTA goal, and the confirmed canonical before formal drafting.
- Stop when those mandatory facts cannot be resolved without fabrication.

### 5. Extract the visual system

Follow `site-style-extraction.md`.

- Prefer explicit user guidance and local design-system evidence over inferred website patterns.
- Inspect rendered desktop and mobile views plus computed styles for typography, colors, spacing, geometry, controls, cards, navigation, footer, and responsive behavior.
- Save a style report with sampled URLs, observed tokens, synthesized tokens, component patterns, asset decisions, uncertainty, and intentional adaptations.
- If the site cannot be inspected, request screenshots, CSS/tokens, or a brand guide. Use a neutral fallback only after explicit user approval; otherwise pause.

### 6. Draft and stabilize visible copy

- Create `content/landing-page-copy.md` before HTML.
- Follow `writing-style.md` and the exact section/count/length contract in `page-structure.md`.
- Keep claims traceable to the fact ledger and research sources. Keep competitor evidence in research artifacts, not unsupported footnotes invented during assembly.
- Eliminate hype, repetition, keyword stuffing, unsupported superlatives, and dash punctuation in visible prose.
- Stabilize copy before deriving SEO fields. Any later substantive copy change invalidates metadata and JSON-LD until rechecked.

### 7. Generate technical SEO

Follow `seo-elements.md`.

- Create exactly one recommended Title and one Meta Description.
- Create `content/seo-elements-<keyword-slug>.md` containing the slug, confirmed canonical, Open Graph, Twitter Card, language, conditional hreflang, verified lifecycle dates, and separate JSON-LD entities.
- Keep canonical, Open Graph, Twitter, and `WebPage` identity values synchronized.
- Include only verified and visible facts. Omit unsupported ratings, reviews, offers, dates, Organization properties, social profiles, compatibility, and images.
- Keep each JSON-LD entity in its own script block in the HTML head. Never combine the blocks into one array.

### 8. Assemble the package and HTML

Follow `output-contract.md`.

- Write the package under `output/<keyword-slug>/` relative to the active project unless the user names another destination.
- Use the stabilized copy and SEO artifacts as the only sources for public text and metadata.
- Build one original `index.html` with the required validation hooks, inline CSS, an honest HERO tool placeholder, semantic landmarks, responsive behavior, visible focus states, and reduced-motion support.
- Use verified links and assets only. Do not leave internal TODO, example-domain, evidence, or unsupported placeholder text in publishable metadata or copy. The explicit tool integration placeholder is the only required public placeholder.

### 9. Validate, render, and hand off

Follow `qa-checklist.md`.

Run:

```bash
python3 "$SKILL_DIR/scripts/validate_landing_page.py" \
  "output/<keyword-slug>" \
  --keyword "<exact target keyword>" \
  --pretty \
  --output "output/<keyword-slug>/validation/validation-report.json"
```

- Fix every validation error. Review warnings one by one and record accepted exceptions with reasons.
- Render desktop and mobile views when a browser is available. Inspect layout, overflow, legibility, focus, keyboard flow, placeholder honesty, console errors, and similarity to the style report.
- Re-run the validator after every fix that changes HTML, visible copy, metadata, or JSON-LD.

## Failure and pause behavior

- **Missing keyword or official website:** ask for the missing required input.
- **No final URL:** propose one canonical from verified site conventions and wait for confirmation.
- **Unsuitable or mixed keyword:** save the suitability evidence, explain the issue, and wait for a revised keyword or explicit override.
- **Fewer than 7 usable organic sites:** report exact coverage and failures; do not continue without an explicit reduced-evidence decision.
- **Reddit or Quora unavailable:** record the attempted queries and limitation. Do not invent forum findings; this limitation alone need not block a passed SERP gate.
- **Missing product facts:** ask only for the smallest unresolved set. Stop before public copy when a mandatory section would otherwise be fabricated.
- **Target site or style unavailable:** request screenshots, a style guide, tokens, or representative local files. Do not claim brand fidelity without evidence.
- **Network use unavailable or declined:** produce a research plan and blocked status only. Do not fabricate research or generate formal copy and HTML.
- **Existing output path:** create `output/<keyword-slug>-v2`, then the next available version. Never remove or silently replace the existing package.

## Final handoff

Return links to the package root, `index.html`, research report, source manifest, fact ledger, style report, copy artifact, SEO artifact, validation report, and available screenshots.

State the research date, market, organic coverage, forum limitations, confirmed canonical, visual source, unresolved facts, fallback decisions, and validation status. If the workflow stopped at a gate, link only the completed evidence and status artifacts and state clearly that `index.html` was not generated.
