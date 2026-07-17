# Keyword Research Protocol

Use this protocol before writing copy or generating HTML. Its purpose is to determine whether the target keyword deserves a tool landing page and to build an evidence-backed research report for the later copy, SEO, and design stages.

## Contents

- [Required inputs](#required-inputs)
- [Fixed search scope](#fixed-search-scope)
- [Suitability gate](#suitability-gate)
- [Top organic result collection](#top-organic-result-collection)
- [Reddit and Quora research](#reddit-and-quora-research)
- [Analysis method](#analysis-method)
- [Required report structure](#required-report-structure)

## Required inputs

- One exact primary target keyword.
- The target website URL from the intake process.
- Any product facts or context already collected through facts-and-intake.md.

If the user supplies several keywords, ask them to select one primary keyword or run this protocol separately for each keyword. Do not blend different search intents into one report.

## Fixed search scope

Research the keyword with these settings unless the user explicitly requests a different market:

- Market: United States.
- Language: English.
- Device context: desktop.
- Search engine: Google.
- Result type: organic web results only.
- Research date: record the actual access date in YYYY-MM-DD format.

Do not count ads, sponsored placements, shopping blocks, local packs, People Also Ask boxes, AI summaries, image packs, video packs, news modules, or other SERP features as organic ranking pages. A page linked inside a SERP feature may be used as supporting evidence, but it does not occupy a position in the top organic set.

When the same domain ranks more than once, retain its highest-ranking directly relevant page for the distinct-site analysis and continue down the results until reaching 15 distinct eligible websites or exhausting the accessible results. Record any repeated rankings separately when they materially reveal search intent.

## Suitability gate

Evaluate suitability before producing the full report or writing the landing page.

A keyword is suitable when all of the following are true:

1. The dominant organic intent is to use, find, compare, or choose an online tool, generator, checker, converter, calculator, analyzer, editor, or similar utility.
2. The proposed product can genuinely complete the task or satisfy the need implied by the keyword.
3. A dedicated landing page can offer specific utility or product value rather than merely restating general information.
4. The keyword is not primarily navigational for another brand and is not dominated by unrelated news, local, academic, or purely informational intent.

Use the first 10 distinct eligible organic results as a minimum observable format signal. At least 3 of those 10 must be genuine tool interfaces, tool landing pages, or product pages that directly satisfy the task. If fewer than 3 qualify, classify the keyword as Fail unless access limitations leave fewer than 10 results available, in which case classify it as Inconclusive and apply the coverage rule.

Classify the gate as:

- Pass: tool or product intent is dominant and the product is a credible fit. Continue.
- Mixed intent: both tool and informational or other intents are material. Explain the split and ask the user whether to continue with the tool angle or revise the keyword.
- Fail: tool landing page intent is not dominant, or the product cannot honestly fulfill it. Stop before copy and HTML generation. Explain the evidence and suggest better-aligned keyword alternatives when the evidence supports them.
- Inconclusive: there is not enough reliable SERP coverage to judge. Follow the coverage pause rule below.

Do not declare a keyword suitable merely because its wording contains words such as tool, generator, free, online, or AI. Base the decision on observed SERP intent and product fit.

## Top organic result collection

Attempt to collect and inspect the first 15 distinct eligible organic websites.

For every candidate, record:

- Organic rank.
- Page title.
- Page URL.
- Domain.
- Page type and apparent intent.
- Access status.
- Access date.
- Whether the page was fully inspected or only visible in the SERP.

Open and read the ranking page before using it to support page-copy frequency, features, value propositions, or topic coverage. Search snippets alone may support a preliminary intent observation, but they are not evidence that the page contains a topic or phrase.

If a result is inaccessible, irrelevant, non-English, duplicate, or too thin to analyze, state the exclusion reason and continue down the organic results in an effort to reach 15 usable distinct websites.

### Coverage rule

- With 15 usable websites, complete the report and state full coverage.
- With 7 to 14 usable websites after a documented top-15 attempt and reasonable continuation through the results, complete the report but disclose the reduced sample and lower confidence wherever it matters.
- With fewer than 7 usable websites, pause. Report what was attempted, list the access or eligibility failures, and ask the user whether to change the keyword or market, provide sources, or explicitly accept a reduced-evidence analysis. Do not silently continue and do not invent missing observations.

## Reddit and Quora research

Search Reddit and Quora for discussions closely related to the target keyword, its task, and its common problems. Use query variants when useful, including the exact keyword and natural-language versions of the user need.

Prioritize recurring topics and discussions with visible engagement. For each supporting discussion, record:

- Platform.
- Thread or question title.
- Direct URL.
- Publication or update date when visible.
- Visible vote, score, answer, or comment signal when available.
- The user concern or use case it supports.
- Access date.

Never invent vote counts, engagement, dates, or frequency. If a platform hides a metric, label it unavailable. If Reddit or Quora cannot be accessed or provides too little relevant evidence, disclose that limitation and avoid calling a topic frequent unless multiple observable sources support it.

Forum content is evidence of user concerns, language, and scenarios. It is not authoritative evidence for the target product's features, pricing, privacy, security, or performance.

## Analysis method

Use the inspected ranking pages and forum evidence to produce the following analyses.

### 1. Core value propositions

- Identify no more than 5 value propositions shared across the ranking pages.
- For each proposition, list the associated recurring English words and phrases.
- Explain which inspected pages support the pattern.
- Keep a distinction between observed competitor patterns and verified capabilities of the target product.

### 2. High-value topic gaps

- Identify no more than 10 topics that users appear to care about but the ranking pages cover poorly or inconsistently.
- Support each gap with SERP, forum, related-query, or other observable evidence.
- Do not label a topic a gap until the inspected page set has been checked for it.

### 3. Forum topics

- Summarize recurring Reddit and Quora concerns, questions, objections, workflows, and desired outcomes.
- Distinguish recurring themes from isolated anecdotes.
- Include the direct supporting discussion links.

### 4. High-frequency language

- List up to 30 meaningful English words or phrases that recur in the main landing-page copy of the inspected pages.
- Ignore articles, prepositions, conjunctions, cookie text, legal boilerplate, navigation, footer text, and other non-substantive interface text.
- Normalize obvious singular and plural or capitalization variants when useful, but do not merge terms that change meaning.
- Describe the counting method and sample coverage. Use exact counts only when they were actually measured.

### 5. User profiles

- Infer the primary audience groups from the tasks, examples, positioning, and forum concerns in the evidence.
- Clearly label these as evidence-based inferences rather than known customer data.

### 6. Use cases

- Provide the 6 most representative, concrete use cases.
- State the user, situation, task, and desired result for each use case.

### 7. Semantic terms

- List 20 semantically related terms, entities, concepts, and natural-language variants.
- Use the report label LSI and Semantic Terms when compatibility with the original workflow matters, but do not claim that a proprietary LSI metric was calculated.
- Select terms for topical relevance, not keyword stuffing.

### 8. FAQ suggestions

- Propose 10 FAQ questions based on long-tail queries, semantic terms, topic gaps, forum concerns, and product-relevant search intent.
- Do not imply an answer or product capability that has not been verified through facts-and-intake.md.

## Required report structure

Save the intermediate report as keyword-research-[keyword-slug].md and include these sections in order:

1. Research scope and date.
2. Suitability decision and evidence.
3. Coverage summary and limitations.
4. Organic result source table.
5. Forum source table.
6. Core value propositions and associated recurring language.
7. High-value topic gaps.
8. Forum topics.
9. High-frequency words and phrases.
10. User profiles.
11. Six use cases.
12. Twenty LSI and semantic terms.
13. Ten FAQ suggestions.

Every material claim must be traceable to a listed source, a clearly identified user-provided fact, or an explicitly labeled inference. Include direct URLs and access dates. Never hide weak coverage behind confident language.
