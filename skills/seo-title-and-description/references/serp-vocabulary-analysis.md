# SERP Vocabulary Analysis

Use the current organic SERP to identify recurring user language without copying competitors or turning frequency into keyword stuffing.

## Collect the two corpora

For up to the first 10 organic results, record internally:

- Observed position
- URL
- Visible title link
- Visible description or snippet, or `missing`

Exclude ads, People Also Ask, related searches, navigation labels, and other SERP modules from both counts. Analyze ads separately only for optional copy inspiration.

Treat the visible text below a result as a query-dependent SERP snippet, not as the source page's verified Meta Description. Do not replace a missing snippet with metadata fetched from the ranking page.

Create two independent corpora:

1. **Title corpus:** organic title links only.
2. **Snippet corpus:** organic visible descriptions or snippets only.

Never merge the corpora. Keep a separate usable-result denominator for each when some fields are missing.

## Normalize and count

Count meaningful single terms and meaningful two- or three-term phrases. Use document frequency: count a term at most once per result, then record the number of distinct results that contain it.

Apply these normalization rules:

- Normalize case, Unicode form, punctuation, and repeated whitespace.
- Use language-appropriate tokenization. For CJK text, identify meaningful words and phrases instead of counting isolated characters or relying on spaces.
- Merge only obvious singular, plural, or inflectional variants when their search meaning is unchanged. Do not aggressively stem terms that express different intents.
- Remove stop words, punctuation-only tokens, URL fragments, domain names, and generic site boilerplate.
- Exclude brand and product names unless the query is branded, navigational, comparative, or the named entity is essential to intent.
- Separate the primary keyword and its trivial variants as baseline vocabulary. Use frequency analysis mainly to discover supporting concepts, qualifiers, formats, audiences, inputs, outputs, and benefits.
- Keep numbers, years, prices, `free`, `best`, `instant`, and similar claim-bearing words in a separate claims bucket. Do not approve them merely because they recur.
- When SERP bolding or highlighting is visible, record it as a weak relevance clue without changing the frequency count.

Build one internal table for each corpus using this structure:

```text
term or phrase | results containing it | usable-result total | observed positions | classification | page-supported? | use?
```

Classify each item as primary-keyword baseline, supporting vocabulary, brand, boilerplate, or claim-bearing language.

## Interpret the counts

- Treat appearance in at least two distinct results as recurring when at least five usable results are available. Treat three or more as stronger evidence, not as a mandatory inclusion rule.
- Prefer a specific, intent-bearing phrase over a more frequent but generic word.
- Treat frequency as evidence of shared vocabulary or result-format conventions, never as a ranking factor.
- Reject any frequent term that conflicts with the target page, target audience, locale, or dominant intent.
- Verify claim-bearing language against the target page and authoritative product evidence before approving it.
- Do not copy a competitor phrase merely because it is frequent. Rewrite the concept in original, natural language.

If fewer than five usable entries exist for either corpus, treat its frequency evidence as weak. Try another authorized search view or use user-provided SERP evidence. If no usable snippet corpus is available, stop formal Meta Description generation and request a SERP screenshot, export, or the top 10 visible titles, snippets, and URLs.

## Apply the vocabulary

For Titles:

- Draw recurring supporting vocabulary only from the Title table.
- Combine the primary keyword with at most one or two accurate Title-table terms or phrases.
- Do not add a snippet-only term to a Title solely because it was frequent in snippets.

For Meta Descriptions:

- Draw recurring supporting vocabulary only from the snippet table.
- Combine the primary keyword or a close semantic variant with at most two or three accurate snippet-table terms or phrases.
- Do not add a Title-only term to a Meta Description solely because it was frequent in Titles.

When a term independently recurs in both corpora and the page supports it, it may appear in both fields. Do not force the same terms into all five pairs. Use the strongest accurate cluster in pair 1 and vary legitimate supporting angles in the remaining pairs.

Prioritize page truth, natural language, intent fit, and clarity over frequency. Editorial length targets never justify awkward repetition or unsupported wording.
