---
name: seo-title-and-description
description: Research, generate, audit, and rewrite SEO title tags and meta descriptions for SaaS, online tools, content sites, and related page types. Use when a user wants five optimized Title and Meta Description pairs, wants existing metadata reviewed or rewritten, provides a page URL, source code, or pasted content, supplies a target keyword for live SERP intent and recurring-vocabulary research, or needs a batch of up to 10 pages. Require current authorized web search or user-provided SERP evidence, and never edit implementation code.
---

# SEO Title and Meta Description

## Objective

Produce five accurate, natural, search-intent-aligned Title and Meta Description pairs for each page. Put the strongest pair first. Perform research, extraction, auditing, and length checks internally; return only the five pairs after a successful run.

## Non-negotiable behavior

- Require a primary keyword and enough page or product evidence for every item.
- Complete current SERP research before formal generation. Never substitute model memory for live results.
- Use only web search, browser, or URL-fetch capabilities already authorized by the host.
- Never scrape Google with custom scripts, bypass a CAPTCHA, or claim a rank that was not directly observed.
- Read current pages or source code when useful, but never modify page files, metadata, or implementation code.
- Process one to ten pages per request. Ask the user to split larger batches.
- Use only claims, benefits, dates, prices, offers, and features supported by the supplied page or verified sources.
- Do not add a terminal brand or site-name suffix to a Title unless the brand is exceptionally well known in the target language audience and its recognition materially improves the result.
- Prefer one natural occurrence of the primary keyword, or a semantically close secondary keyword, in every Meta Description.
- Treat the recommended length ranges as editorial targets, not Google limits.
- Keep successful output to five pairs per page. Do not expose research notes, audit findings, rationale, sources, or character counts.

## Intake

Normalize the request into one or more page items. Collect:

- **Required:** primary keyword.
- **Required:** page evidence from pasted content, a product brief, a URL, readable source code, or authorized web research that establishes what the page genuinely offers.
- **Conditionally required:** page type. Infer it only when the page and SERP show a clear consensus; otherwise ask the user to choose.
- **Optional:** target country or region, explicit output language, secondary or long-tail keywords, brand name, core benefits, and target audience.
- **For an audit:** current Title and Meta Description, or a URL/source file from which they can be extracted.

Detect the primary keyword's dominant language and writing system automatically unless the user overrides them. Do not ask for a target country or market when it is missing. Use the detected keyword language for SERP research and metadata output. Treat the inferred market as a language audience, not evidence of a specific country: when no region is supplied, use the host's current geographic search environment without naming or silently assuming a country. If the user supplies a country, region, or language, use it as an explicit refinement.

If the keyword language and the target page's primary language conflict, report the mismatch and ask for localization direction instead of generating metadata that the visible page does not support. For mixed-language keywords, use the language of the meaningful non-brand terms; if that remains indeterminate, fall back to the page's primary language without asking for a country.

For a batch, detect each item's keyword language independently. Apply one shared language or region only when the user clearly intends it for every item.

## Workflow

### 1. Establish page truth

Use the strongest available evidence:

1. Inspect pasted page copy or the product brief.
2. Fetch the target URL when provided.
3. In a code workspace, locate and read the relevant route, metadata configuration, visible headings, and page copy.
4. If the page is accessible, extract the existing `<title>`, `meta[name="description"]`, H1 or main visual title, `og:title`, brand, primary offer, audience, and important visible copy.
5. If a URL cannot be accessed or critical facts remain unclear, ask the user to paste the relevant content. Do not invent missing product details.

Do not confuse the page's `<title>` with its H1 or with Google's displayed title link. Do not confuse a page's meta description with a query-dependent Google snippet.

### 2. Research the live SERP

Research each primary keyword in its detected or explicitly supplied language using the host's current authorized capabilities. Apply an explicitly supplied country or region when present; otherwise use the host's current geographic search environment without pausing for location input.

- Inspect up to the top 10 organic results when available.
- Record each organic result's visible title link and visible description or snippet separately.
- Inspect visible People Also Ask questions, related searches, and ads when available.
- Keep organic observations and ad-copy inspiration separate.
- Open enough result pages to understand the dominant intent, content format, audience, recurring concepts, and meaningful differentiators.
- Record the query, research date, detected or supplied language, explicit region or current-environment state, and observed result URLs internally.
- Read [references/serp-vocabulary-analysis.md](references/serp-vocabulary-analysis.md) and build separate internal frequency tables for organic Titles and organic snippets. Count how many distinct results contain each meaningful term or phrase, not how many raw times it appears.
- Use Title-table vocabulary only to inform Titles and snippet-table vocabulary only to inform Meta Descriptions. Let a term inform both fields only when it independently qualifies in both tables.
- Treat recurring wording as evidence of user vocabulary and intent, not as text to copy or as proof that a claim is true.

If live search is unavailable, permission is denied, the required keyword language or an explicitly requested region cannot be represented, or a CAPTCHA blocks research, stop formal generation for that item. Request a SERP screenshot, a SERP export, or the top 10 titles, snippets, and URLs. In a batch, continue the items that still have sufficient live or user-provided SERP evidence.

### 3. Infer intent and page type

Classify the dominant intent as informational, commercial investigation, transactional, navigational, or local. Identify the result format that best satisfies it.

Infer the page type only when the SERP and page evidence agree. Ask for confirmation when intent is mixed or the intended page would conflict with the dominant results.

Read [references/page-types.md](references/page-types.md) after selecting or inferring the page type. Use its patterns as directions, never as rigid formulas.

### 4. Audit internally

Read [references/seo-rules.md](references/seo-rules.md) before auditing or generating.

Check the current metadata, when present, for accuracy, uniqueness within the supplied set, clarity, natural keyword use, locale fit, search-intent fit, stale dates, unsupported claims, terminal brand suffixes, keyword stuffing, boilerplate, and alignment with the H1 and visible page copy.

Use the audit to guide the new candidates. Do not show the audit in a successful final response.

### 5. Draft five distinct pairs

Read [references/copy-pattern-examples.md](references/copy-pattern-examples.md) before drafting. Use the examples only to recognize reusable structures and candidate angles. Never copy their wording, brands, dates, numbers, or claims into an output.

- Draft exactly five complete Title and Meta Description pairs per successful item.
- Make pair 1 the strongest overall recommendation without adding a `Recommended` label.
- Give the remaining pairs meaningfully different but still valid angles. Do not produce trivial word swaps.
- Use the primary keyword naturally in the Title. Favor earlier placement when it improves clarity, but never force it.
- Use one or two secondary keywords only when they fit naturally and accurately.
- Use no more than one or two validated Title-table terms or phrases in a Title, and no more than two or three validated snippet-table terms or phrases in a Meta Description. Use fewer whenever that reads more naturally.
- Vary useful vocabulary clusters across the five pairs instead of forcing the same frequent terms into every candidate.
- Include the primary keyword once in each Meta Description when it reads naturally. Otherwise use a semantically close secondary keyword that expresses the same search intent. Revise descriptions that contain neither unless adding one would make the copy inaccurate, repetitive, or unnatural.
- Match the detected keyword language and writing system while staying consistent with the page's primary language, brand style, and search intent.
- Do not end a Title with the brand or site name, including suffixes such as `| Brand`, `- Brand`, or `: Brand`. Allow this only when current target-language evidence shows that the brand is exceptionally well known and its recognition adds meaningful clarity, trust, or navigational value. Treat this as a strict exception: owning the page, supplying a brand name, or seeing competitors append brands is not enough. If uncertain, omit the brand suffix.
- When a brand is necessary to identify a pricing, login, profile, or other navigational page, place it naturally as the subject instead of adding it as boilerplate at the end.
- Use benefits, formats, numbers, brackets, dates, urgency, or calls to action only when the page genuinely supports them.
- Never invent freshness, discounts, free access, delivery promises, statistics, ratings, or product capabilities.
- Do not copy a competitor's Title or Meta Description.

### 6. Validate internally

Use the editorial targets below while prioritizing truth and readability:

- Latin-script Title: 50–60 characters.
- Latin-script Meta Description: 120–158 characters.
- CJK or other full-width text: use approximate display-width equivalents, commonly about 25–30 full-width characters for a Title and 60–79 for a Meta Description.

When Python 3 is available, run `scripts/validate_metadata.py` on the five pairs. The script uses Unicode display units and labels these ranges as editorial targets. Revise avoidable misses. If meeting a range would make the copy inaccurate, repetitive, or unnatural, keep the closest natural version.

Pass UTF-8 JSON by file or stdin using this schema:

```json
{
  "schema_version": "1.0",
  "pages": [
    {
      "page_id": "the URL or keyword",
      "candidates": [
        {"title": "...", "meta_description": "..."}
      ]
    }
  ]
}
```

Supply exactly five candidates for each of one to ten pages. Treat exit code `0` as structurally valid and within the editorial targets, `1` as valid with editorial advisories, and `2` as a schema or content error. The script does not validate facts, search intent, or writing quality.

Do not display the validator output or character counts to the user.

### 7. Return only the results

For a single page, use exactly this structure:

```text
1.
Title: ...
Meta Description: ...

2.
Title: ...
Meta Description: ...

3.
Title: ...
Meta Description: ...

4.
Title: ...
Meta Description: ...

5.
Title: ...
Meta Description: ...
```

For a batch, identify each page only with its supplied URL or primary keyword, then use the same five-pair structure. Add no research summary, rationale, warnings, sources, character counts, preface, or conclusion to a successful result.

End every output line after its final visible character. Do not add trailing whitespace or Markdown hard-break spaces.

If an item is blocked or missing required input, ask only for the missing evidence instead of producing unresearched metadata.
