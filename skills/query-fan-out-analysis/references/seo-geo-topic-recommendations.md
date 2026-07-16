# SEO/GEO Page Topic Recommendations

Convert query clusters into an editorially useful page brief. Recommend topic families, not a dump of keywords or one heading per query.

## Evidence to use

Consider these inputs together:

- fit with the seed's primary intent and intended answer type;
- information-gap value, especially definition, comparison, workflow, trust, action, and risk needs;
- cross-model coverage and average within-provider recurrence;
- current SERP, People Also Ask, related-search, trend, or other external signals;
- visible page evidence and URL coverage when supplied;
- the site's ability to provide accurate, original, and supportable information.

Cross-model coverage and recurrence are ordering signals, not search volume or ranking probability. A low-coverage topic can still matter when it resolves a material legal, safety, privacy, compatibility, or purchase risk.

## Group topics before recommending them

- Merge clusters when they serve one retrieval task and can be answered coherently in one section.
- Keep separate intents, audiences, locales, formats, and journey stages separate when combining them would dilute the page's primary job.
- Do not copy queries verbatim into headings by default. Name the user need in natural page language.
- Write topic labels, guidance, and rationales in the report's target language while preserving representative original queries elsewhere in the report.
- Default to 5–8 topic families. Use fewer for a narrow intent; exceed eight only when the user explicitly asks for a broader content architecture.
- Assign each supporting cross-cluster to one primary recommendation so the list does not repeat itself.

## Priority and action

| Priority | Use |
|---|---|
| `P0` | Essential to satisfy the page's primary intent. Usually supported by high or medium coverage, strong external evidence, or a critical action/risk need. |
| `P1` | Supporting detail that improves comparison, implementation, trust, or decision quality. |
| `P2` | Conditional or adjacent need that belongs in a separate page or depends on off-page evidence. |

| Action | Meaning |
|---|---|
| `include_on_page` | Cover or strengthen the topic on the primary page. |
| `add_to_page` | Page evidence shows the relevant topic is missing; add it to the primary page. |
| `expand_on_page` | Page evidence shows partial coverage; deepen or clarify it. |
| `retain_on_page` | Page evidence shows sufficient coverage and the topic remains a priority. |
| `separate_page_candidate` | Create or use a focused supporting page and link it contextually. |
| `off_page_evidence` | Seek third-party reviews, citations, community evidence, or independent validation rather than imitating it with first-party claims. |

Every `P0` recommendation must use an on-page action: `include_on_page`, `add_to_page`, `expand_on_page`, or `retain_on_page`. Do not elevate a platform-specific or low-evidence angle to `P0` without a clear primary-intent, risk, or external-evidence reason.

## Make the rationale useful for both SEO and GEO

For each topic, explain:

- **SEO value:** which search intent or information gap it satisfies and why it belongs on this page;
- **GEO value:** which concise, factual, comparable, procedural, or evidence-backed answer units an AI system could retrieve and cite;
- **Suggested format:** for example a direct definition, step-by-step workflow, comparison table, feature/constraint matrix, examples block, FAQ, policy summary, or first-party evidence block.

Prefer supportable specifics such as definitions, inputs and outputs, steps, constraints, compatibility, prices with dates, ownership terms, measured results, examples, and clearly attributed evidence. Do not recommend keyword stuffing, unsupported superlatives, fabricated reviews, or generic FAQ padding. Covering the topics does not guarantee rankings or AI citations.

## With and without page evidence

- **No URL or page content:** set `basis` to `fanout_only` and use `include_on_page` for primary-page topics. Describe the list as a proposed page brief and state assumptions about page type and audience. Do not claim a topic is missing.
- **URL coverage completed:** set `basis` to `fanout_and_page_evidence`. Map `missing` to `add_to_page`, `partial` to `expand_on_page`, and high-priority `covered` topics to `retain_on_page`. Keep separate or off-page needs out of the primary page.
- **Page inaccessible:** use `fanout_only`, disclose that the existing page was not assessed, and avoid gap language.

## Required internal structure

Create `recommended_page_topics` with:

- `status`: `available` or `not_available`;
- `basis`: `fanout_only` or `fanout_and_page_evidence`;
- `unavailable_reason`: `null` when available, otherwise a concise reason;
- `items`: one to ten grouped recommendations when available, otherwise an empty array;
- for each available item: contiguous `rank`, unique `topic_id`, unique `label`, `priority`, `action`, non-empty `supporting_cross_cluster_ids`, optional `supporting_signal_ids`, `coverage_guidance`, `rationale`, and `suggested_format`.

Reference only valid cross-platform cluster IDs. Do not reuse one cross-cluster ID across multiple recommendations; assign it to the best-fitting topic family.

Use `not_available` only when no usable fan-out clusters exist, such as a completely failed observed-only analysis. Provide the reason and do not fabricate items.
