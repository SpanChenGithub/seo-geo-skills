---
name: blog-post-writer
description: Research, plan, write, edit, and package publish-ready SEO- and GEO-friendly blog posts from a target keyword. Use when a user wants a new article, a content brief and outline, or a researched refresh of an existing post for an explainer, how-to, listicle, roundup, product review, comparison, or alternatives query. Requires current SERP research, source-backed claims, an outline approval gate, and a final article approval gate.
---

# Blog Post Writer

## Objective

Turn a target keyword into a useful, trustworthy article that satisfies the current search intent, contributes information beyond a competitor summary, demonstrates earned authorial expertise, reads naturally for people, and is easy for search engines and answer engines to understand. Produce a traceable research and publication package without publishing it unless the user explicitly requests publication.

## Non-negotiable rules

- Require only a target keyword. Begin with sensible, explicit assumptions when optional context is absent.
- Conduct live SERP research before proposing the formal outline or article. If live search is unavailable, stop formal generation and ask for fresh ranked SERP evidence: a top-10 export, screenshots that preserve ranks, or copied ranked results with query, date, locale when known, titles, and URLs. Competitor URLs can support page inspection but do not satisfy the SERP gate without that ranked context. Do not disguise prior knowledge as current research.
- Detect the keyword language and write in that language unless the user requests another one.
- Honor an explicit country, region, or locale. Otherwise use the available search environment and record `region.status` as `unspecified`. Surface that limitation in the article only when it changes a reader-facing claim or recommendation; keep routine research context in the audit package. Never silently default to the United States.
- Let current intent and evidence determine the article type, depth, and reference word count. Treat length as guidance, not a quota.
- Never use a fixed keyword-density target, force the keyword into every section, or pad the article to exceed competitors.
- Never fabricate experience, tests, quotes, experts, customers, statistics, product behavior, or first-party data.
- Preserve a clear boundary between source evidence, reasonable synthesis, and the user's first-party knowledge.
- Write with earned authority. Show expertise through specific judgments, tradeoffs, examples, failure signals, and practical decision criteria. Use first-person experience only for actions and observations supported by a reviewable record.
- Keep the public article reader-centered. Do not lead with or repeatedly insert defensive process disclaimers such as "this is not a hands-on comparison," "we did not run a controlled test," or "we do not present a universal winner." Put routine evidence boundaries in the methodology, claims ledger, or quality report, and state only the limitations that materially change the reader's decision.
- Do not create a bold `Disclosure:` block merely because the publisher's product appears in an article. Unless the user supplies mandatory wording, identify the author, publisher, sponsorship, or commercial relationship in one concise, natural byline, author note, methodology sentence, or relevant product statement. Keep that attribution separate from non-testing caveats.
- Write public methodology as a compact account of work performed and criteria applied. Do not enumerate missing tests, unavailable inputs, hypothetical benchmark requirements, or reasons the publisher's product appears first. Keep those details in the brief, claims ledger, outline, or quality report. Organize the visible list by a reader-centered principle and move directly to useful judgments.
- Require explicit approval of the outline before drafting. Require final approval before treating the article as complete or handing it to a publishing workflow.
- Do not publish, upload, send, or modify a website unless the user separately asks for that action.
- Do not expose, echo, save, or commit API keys. Use environment variables only. Obtain explicit authorization before paid API calls.
- Use the host's available search, browser, file, and editing capabilities. Do not depend on editor-specific commands, model names, hidden reasoning, or a particular agent runtime.

## Intake

Accept one required input:

- `primary_keyword`

Accept optional context without blocking a keyword-only run:

- target language, country, region, locale, audience, and funnel stage;
- site, domain, page URL, existing draft, brand, product, value proposition, proof, and CTA;
- desired article type, reference length, format, tone, author, or deadline;
- secondary keywords, entities, questions, internal links, and competitors;
- first-party experience, tests, data, expert input, examples, screenshots, and media;
- output location or chat-only delivery.

Ask a follow-up only when an ambiguity would materially change the research or create a factual, legal, safety, or brand risk. Otherwise state the assumption and proceed. Read [references/intake-and-workflow.md](references/intake-and-workflow.md) for the operating sequence and approval gates.

## Workflow

### 1. Establish the brief

Classify the likely audience, task, intent, article family, decision stage, authorial basis, and product relationship. If a site or product is supplied, inspect its relevant public pages and any local project context. Do not invent a brand voice, credential, or product claim when none is provided; use a clear, decisive, evidence-led editorial voice.

For an existing article, retain accurate, useful material but research the query from scratch. Treat the work as a refresh, not a cosmetic rewrite.

### 2. Research the live search landscape

Read [references/research-and-source-policy.md](references/research-and-source-policy.md) before researching or citing.

Search the target keyword in the requested locale when possible and inspect up to the first 10 organic results, prioritizing the top three and any lower-authority page that ranks unusually well. Record the actual results available rather than inventing a complete top 10.

Analyze:

- dominant and secondary intent;
- result and article formats;
- recurring topics, entities, questions, proof types, and decision criteria;
- what the leading pages answer well, weakly, or not at all;
- People Also Ask, related searches, and query refinements when visible;
- relevant discussions on Reddit, Quora, YouTube, forums, or communities;
- freshness needs and claims that require primary or authoritative sources;
- a justified article format, coverage plan, and reference length range.

Save structured summaries and short compliant excerpts only. Do not mirror or store full competitor articles. Use competitor pages to understand intent and coverage, never as text to reproduce.

### 3. Plan information gain

Ask whether the user has first-party experience, internal data, real tests, case studies, screenshots, examples, customer questions, or expert views. Use only what is genuinely supplied and attributable. For reviews and roundups, build a creator-authority record: verified author or team, relevant role, products or workflows actually used, date and context, concrete success or failure observations, and supporting screenshots, outputs, notes, or logs. Also record research performed, workflows inspected, tests run, and expert or customer inputs.

If genuine experiential material would materially improve the article but is absent, request it or perform a documented test only when the user has authorized the action and the required inputs are permitted. Otherwise use decisive research-based authority without experiential claims.

If first-party evidence is unavailable, create value through source triangulation, current workflow inspection, clearer frameworks, worked examples, practical decision criteria, and primary sources. Express this work as confident editorial analysis, not simulated hands-on experience or a paragraph of credibility-reducing disclaimers. Record opportunities for future original research separately; do not write them as completed work.

### 4. Select the article format

Read [references/outline-and-formats.md](references/outline-and-formats.md). Choose among:

- explainer or informational guide;
- how-to;
- listicle;
- roundup review;
- single-product review;
- comparison or versus article;
- alternatives article.

Use a case study, original-research article, or first-person opinion piece only when the necessary real evidence or experience exists. Use PAS or PAES only when it improves the opening for the selected query; do not force it into every article. When PAES is selected or requested, map all four beats in the outline, make the Expertise or Experience beat traceable, and make the Solution deliver the direct answer and transition into the article.

### 5. Produce the outline and pause

Create a source-mapped outline that includes:

- keyword, language, region status, audience, intent, article type, and reference length;
- one working title, slug, and meta-description direction;
- H1/H2/H3 structure and the purpose of every section;
- questions to answer, claims to verify, examples, decision criteria, sources, and media needs;
- information-gain plan, internal-link plan, CTA placement, and FAQ plan when justified;
- authorial voice, genuine experience inputs, and the professional judgments the article will contribute;
- omissions, assumptions, risks, and items requiring user input.

Show the outline in a readable form and request approval. Do not draft the formal article until the user approves it. Record the approval in `outline.json`.

### 6. Draft for humans and retrieval systems

After approval, read [references/writing-and-editing.md](references/writing-and-editing.md). Write the complete article, not isolated sections generated in unrelated contexts.

- Answer the main question early and make each section independently understandable.
- Establish a clear expert point of view through specific recommendations and reasons. Lead with what the reader should choose, do, notice, or avoid, then support that judgment.
- Use first person precisely: reserve "we tested," "we used," and "we observed" for documented firsthand work; use "we compared," "we reviewed," or "our analysis" only for research and evaluation actually performed.
- Use descriptive headings, short paragraphs, concrete examples, tables, steps, definitions, summaries, and FAQs only when they help the reader.
- Use the primary keyword and close variants naturally. Cover the important entities and relationships revealed by research without turning them into a checklist.
- Link factual claims to the strongest available source in natural Markdown. Distinguish facts from recommendations and judgment.
- Discuss a supplied product only where it genuinely fits. Explain strengths, limitations, and fit; avoid unsupported promotion.
- Use real internal URLs when a domain is available. Otherwise suggest anchors and page topics without fabricating URLs.
- Default to avoiding em dashes; honor a supplied style guide if it chooses otherwise.

### 7. Edit, verify, and package

Read [references/seo-geo-and-delivery.md](references/seo-geo-and-delivery.md) and [references/artifact-contract.md](references/artifact-contract.md).

Run distinct editorial passes for:

1. intent coverage, usefulness, and information gain;
2. factual accuracy, citation support, freshness, and limitations;
3. structure, coherence, repetition, scannability, and accessibility;
4. natural SEO/GEO language, entities, direct answers, and internal links;
5. brand fit, earned authorial authority, defensive meta-language, claims, CTA restraint, grammar, and publication readiness.

Remove placeholders such as `[NEEDS SOURCE]`, unsupported claims, fake links, and unresolved TODOs. If a required claim cannot be sourced, remove it or ask the user for evidence.

Create one final SEO title, one meta description, one slug, a concise summary, a Sources section, a media plan with alt text, an internal-link plan, a quality report, and applicable JSON-LD. Do not add title alternatives unless the user explicitly requests them.

### 8. Validate and request final approval

Resolve the skill directory to the directory containing this file and validate the package with the bundled script. Use the Python launcher available on the host. Fix errors before delivery; explain any remaining warnings or research limitations.

```bash
python3 "<skill-directory>/scripts/validate_article_package.py" "<article-directory>" --pretty
```

PowerShell:

```powershell
py "<skill-directory>\scripts\validate_article_package.py" "<article-directory>" --pretty
```

For a new file package, use two passes: run once to expose content errors, record the passing validator version and warning codes in `quality-report.json` after errors reach zero, then rerun. Do not deliver a package with an empty, pending, failed, or stale validator record.

Present the completed article and package for final approval. A passing validator is a consistency check, not proof of ranking, citation, originality, or factual truth.

## Default deliverables

Use chat-only output when requested. Otherwise create `articles/<keyword-slug>-<YYYY-MM-DD>/` beneath the user's project, or use the explicit output path. Never write project-specific brand settings into this public skill directory.

The lean audit package contains the following. Keep `article.md` as the canonical audit copy even when the user also requests HTML, DOCX, or CMS-ready fields.

- `brief.json`
- `serp-research.json`
- `sources.json`
- `outline.json`
- `draft.md`
- `article.md`
- `meta.json`
- `media-plan.md`
- `quality-report.json`
- `structured-data.json`

The user-facing delivery should foreground the publishable Markdown article, one final title and meta description, slug, summary, relevant sources, media and alt-text plan, internal links, justified FAQ, quality findings, and eligible structured data. Keep audit detail available without overwhelming the final response.

## Optional companion skills

- Use `query-fan-out-analysis` when installed and useful for additional SEO/GEO topic discovery.
- Use `seo-title-and-description` when installed and useful for metadata research or review.
- Treat both as optional. Continue with this skill's self-contained workflow when they are unavailable.

Do not invoke paid APIs merely because credentials exist. State the call plan and obtain authorization unless the user has explicitly authorized those calls in the current request.

## Attribution

Author: Span. Licensed under the repository MIT License. Copyright (c) 2026 SpanChenGithub.
