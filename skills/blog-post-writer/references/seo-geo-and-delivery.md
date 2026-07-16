# SEO, GEO, and Delivery

Use this reference after editorial revision to prepare discoverable, citation-friendly, portable delivery files and obtain final approval. SEO and generative retrieval must reinforce reader value and factual clarity rather than add mechanical repetition.

## Contents

- [Optimize for search and generative retrieval](#optimize-for-search-and-generative-retrieval)
- [Deliver one final metadata set](#deliver-one-final-metadata-set)
- [Use only real links](#use-only-real-links)
- [Qualify structured data](#qualify-structured-data)
- [Finalize the media plan](#finalize-the-media-plan)
- [Assemble a portable delivery package](#assemble-a-portable-delivery-package)
- [Run pre-delivery QA](#run-pre-delivery-qa)
- [Enforce final approval](#enforce-final-approval)

## Optimize for search and generative retrieval

Make the article easy for people, search systems, and answer systems to understand and verify.

- Satisfy the dominant intent and chosen format established from the current SERP.
- Put concise answers, definitions, recommendations, or actions at the start of relevant sections.
- Make the author's expertise extractable through concrete judgments, reasons, tradeoffs, examples, failure signals, and next actions. Do not substitute research-process narration for subject expertise.
- Use descriptive headings and self-contained paragraphs whose subject remains clear when excerpted.
- Name important entities, attributes, criteria, steps, units, dates, and limitations explicitly.
- Use lists, tables, examples, and summaries only when they improve comprehension.
- Keep evidence and citations close to the claims they support.
- Distinguish facts, firsthand observations, attributed opinions, and inferences.
- Add original tests, data, examples, or useful synthesis when real and documented.
- Keep important text in accessible, indexable content rather than only inside images or scripts.
- Preserve a logical heading hierarchy and descriptive link text.

Do not optimize for a fixed keyword density. Do not require the primary keyword in every section. Do not create repetitive question-and-answer blocks, artificial definitions, or choppy fragments solely in hopes of appearing in an AI answer.

Do not promise rankings, snippets, citations, inclusion in an AI answer, or rich results. Treat "GEO" as clear, well-sourced, entity-specific, answerable publishing practice. Do not claim that a special file, schema type, density rule, or formatting trick guarantees retrieval.

For material platform or search-engine requirements that may change, verify current official documentation before making an eligibility or implementation claim.

## Deliver one final metadata set

Deliver exactly one final title, one final meta description, and one final slug. Do not include option sets, alternates, or discarded candidates in the public delivery package.

### Final title

- Describe the actual article and align with its H1 and intent.
- Include the primary query or a natural equivalent when useful.
- Put the differentiating value in concrete language.
- Keep it concise enough for the target platform without treating a character target as a ranking rule.
- Exclude unsupported superlatives, dates, numbers, prices, and freshness claims.
- Do not append a brand by default. Add one only when the user requests it, the project convention requires it, or the brand is sufficiently well known that identification materially helps the reader.

### Final meta description

- Summarize the article's real answer, scope, or decision value.
- Use the primary query or a close natural equivalent once when it reads well.
- Match visible content and include material qualifications when omission would mislead.
- Keep it concise for the target platform without promising that a search engine will display it unchanged.
- Avoid keyword lists, duplicate title phrasing, and unsupported calls to action.

### Final slug

- Use the project's real URL conventions and target language.
- Keep it readable, stable, lowercase when the platform convention supports it, and free of filler.
- Prefer hyphens when the platform uses word separators.
- Omit dates and volatile qualifiers unless the content is intentionally date-bound.
- Do not change an existing published slug without an approved redirect and migration plan.
- Do not invent the domain, directory, or canonical URL.

If the final URL is unknown, deliver only the approved relative slug and mark canonical implementation as pending. Do not emit a placeholder canonical URL.

## Use only real links

Every publishable internal link must point to a real, confirmed destination. Verify the URL, page purpose, language or locale, and whether the page is intended to be indexable.

Maintain a link map:

| Link ID | Destination URL | Internal or external | Proposed anchor | Placement | Reader benefit | Verified status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Apply these rules:

- Use descriptive anchors that explain the destination.
- Link where the destination advances the current task, not to meet a link count.
- Avoid repeated exact-match anchors when natural wording differs.
- Link to the most specific relevant page.
- Keep links crawlable in the target publishing format.
- Check redirects, fragments, locale mismatches, and obvious broken destinations.
- Do not use empty links, `#`, invented routes, search-result URLs, or private local file paths in public copy.
- Do not imply that a suggested page already exists.

When a useful internal destination is missing, place it in a separate `recommended future links` note with the proposed page topic and anchor. Keep it out of the publishable article until a real URL is supplied.

Use external links for primary evidence, necessary attribution, standards, definitions, or useful reader continuation. Do not add or remove them based on a fixed quota. Disclose affiliate or commercial relationships and follow the target platform's link-policy requirements.

## Qualify structured data

Add JSON-LD only when the markup describes visible, verified content. Include an eligible `Article` node in the formal article package when its values can be verified, even if a target CMS will require later implementation. If no type can be represented honestly or the requested delivery excludes structured data, put the explicit omission record defined in the artifact contract into `structured-data.json` instead of fabricating fields. Do not add a type merely because its name matches an internal content format.

Use one coherent `@graph` when multiple eligible nodes share entities. Use absolute public URLs only when they are known. Omit unknown optional properties rather than filling them with placeholders. Validate syntax and check that every value matches visible content.

### Eligibility matrix

| Type | Use only when | Required content checks | Do not use when |
| --- | --- | --- | --- |
| `Article` | The page is a real editorial article with a clear headline and body | Headline matches the page; author identity, dates, main page URL, publisher, and representative image are included only when verified; claims and byline are visible or supported by page context | The page is primarily a product, category, tool, forum, or thin index page; author or publisher details would be invented |
| `FAQPage` | A useful visible FAQ contains site-authored questions with one authoritative answer each | Every marked question and answer is visible verbatim in substance; the FAQ is relevant and not duplicated only for markup | FAQ is unnecessary, user-generated, hidden, promotional, repeated from the body without value, or added only to pursue a rich result |
| `HowTo` | The article's main purpose is teaching a real sequential task and the complete visible process can be represented as steps | Outcome, prerequisites, supplies or tools when applicable, ordered steps, images, time, and costs are marked only when visible and verified | The page is mainly an explainer, roundup, review, comparison, alternatives list, or a loose set of tips; steps or properties would be invented |

Use the most specific valid article subtype only when the platform or project requires it. Do not combine `FAQPage` or `HowTo` with `Article` automatically. Add conditional nodes only when they represent substantial visible content and do not misstate the page's primary purpose.

For `Article`, do not invent an author, author credentials, publisher, logo, publication date, modification date, or image. Update `dateModified` only for a substantive documented revision.

For `FAQPage`, keep the visible FAQ because it helps readers, not because markup exists. As of July 2026, Google's former FAQ rich-result documentation redirects to a removal notice, so do not describe `FAQPage` as eligible for a Google FAQ rich result. Re-check the target consumer's current documentation before including the node for another purpose.

For `HowTo`, Google's former HowTo rich-result documentation redirects to its deprecation notice as of July 2026. Do not describe it as eligible for a Google HowTo rich result. Valid Schema.org semantics may remain useful to other consumers, but confirm the project's need and the target consumer's current support first.

Do not add ratings, reviews, offers, prices, organization claims, or breadcrumbs unless the relevant visible facts and real URLs are verified. Never make hidden JSON-LD more promotional or specific than the article.

## Finalize the media plan

Deliver a final media manifest even when some proposed assets remain pending. Use the exact portable columns required by the artifact contract:

| Asset ID | Placement | Purpose and what to show | Capture or annotation notes | Filename or real URL | Source or creation method | Alt text | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use `real`, `generated`, `pending`, `omitted`, or `complete as text` for status. Use portable relative asset paths for packaged files. Do not expose private absolute paths. Confirm that filenames, URLs, captions, and alt text match the delivered article. Keep missing assets clearly marked as pending rather than substituting fake screenshots, stock proof, or invented results.

Include accessibility and web-performance notes when relevant: responsive sizes, intrinsic dimensions, compression, modern formats, lazy loading below the first viewport, and a text alternative for charts or diagrams. Do not lazy-load a critical first-viewport image by default.

## Assemble a portable delivery package

Deliver in the user's requested format, such as Markdown, HTML, a document file, or CMS-ready fields. When no format is specified, use portable UTF-8 Markdown and separate clearly labeled implementation blocks. Avoid dependencies on a specific operating system, local application, vendor, or private path.

Include:

1. **Status:** `Draft awaiting final approval` until approval is explicit.
2. **Final article:** one clean version with no unresolved editorial tokens and a concise Sources section containing only sources actually used.
3. **Final metadata:** exactly one title, meta description, and slug.
4. **Source and claims record:** citations or the platform-appropriate reference form, plus limitations that belong in the audit record rather than the public article.
5. **Internal-link map:** real verified links and a separate future-link recommendation list when needed.
6. **Final media manifest:** real, generated, pending, or omitted status for every planned asset.
7. **JSON-LD:** only eligible, valid types, or a short statement that none qualifies or the platform does not support it.
8. **Implementation notes:** language, locale, canonical status, redirect need, disclosures, and any platform-specific formatting.
9. **QA summary:** checks completed and non-blocking limitations.
10. **Approval request:** a concise summary of material editorial and implementation decisions.

Keep research notes, rejected metadata candidates, inaccessible source copies, private data, and internal reasoning outside the public article. Include them only in a private handoff when the user requests them and permissions allow it.

## Run pre-delivery QA

Treat the following as blockers:

- [ ] The draft matches the explicitly approved outline or a later approved revision.
- [ ] The chosen format fulfills its required editorial logic.
- [ ] Every material claim is verified, qualified, attributed, or removed.
- [ ] Firsthand experience, testing, interviews, data, and quotes are real and documented.
- [ ] The article demonstrates earned authorial authority through specific judgments and practical reasoning.
- [ ] First-person experiential verbs match a reviewable record; research and synthesis are not presented as hands-on use.
- [ ] The authorial basis and every material firsthand claim are traceable in the brief, claims ledger, or supplied test record; confident tone never substitutes for evidence.
- [ ] The opening and body do not contain defensive meta-disclaimers, repeated non-testing caveats, or internal QA narration.
- [ ] The methodology describes work performed and criteria applied without listing missing tests, unavailable inputs, hypothetical benchmark requirements, or publisher-placement defenses.
- [ ] Information gain is identifiable and does not depend on fabricated evidence.
- [ ] The direct answer appears early in the article and in important sections.
- [ ] Paragraphs are readable and not expanded to satisfy a word count.
- [ ] No fixed keyword-density rule or section-by-section keyword quota was applied.
- [ ] The configured em-dash policy is satisfied.
- [ ] FAQ, PAA, methodology, tables, and other conditional sections are justified.
- [ ] Exactly one final title, meta description, and slug are delivered.
- [ ] Every publishable internal link has a real verified destination.
- [ ] External sources support the claims attached to them.
- [ ] Media assets are real or honestly labeled, rights status is recorded, and alt text is useful.
- [ ] JSON-LD is eligible, visible-content-aligned, parseable, and free of placeholders, or is correctly omitted.
- [ ] No ranking, snippet, citation, rich-result, or traffic guarantee appears.
- [ ] No private local path, credential, personal data, unresolved token, or invented URL appears.
- [ ] Language, locale, names, dates, numbers, and regional conventions are consistent.

Do not hand off as complete while a blocker remains. State non-blocking limitations plainly in the delivery summary or quality report. Put them in the article only when they materially affect a reader-facing claim or decision.

## Enforce final approval

After delivering the fully edited package with `quality-report.json.status` set to `ready_for_final_approval` and `approval.status` set to `pending`, stop and request explicit final approval. Summarize the final format, scope, title, meta description, slug, evidence limitations, media status, internal links, and structured-data decision so the user can review the actual deliverable.

Do not treat outline approval as final approval. Do not treat silence, an automated workflow transition, or approval of one field as approval of the full article. When the user requests changes, revise the affected article and delivery fields, rerun relevant QA, and request final approval again.

Until explicit final approval, keep the public status `Draft awaiting final approval`. After approval, set `quality-report.json.status` to `final_approved`, set `approval.status` to `approved` with the real approval timestamp, rerun validation, label the package `Final approved`, and preserve only the one approved title, meta description, and slug.

Final approval authorizes the content package, not publication, CMS edits, deployment, outreach, or other external writes. Perform those actions only when the user separately requests them and the available platform permits them.
