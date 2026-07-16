# Research and Source Policy

Apply this policy to every researched article, regardless of the execution environment.

## Live SERP gate

- Retrieve live search-engine results during the current task before writing the outline or formal article. Model memory, an old cache, and a generic source list do not satisfy this requirement.
- Record each query, query language, search intent, retrieval time, result rank, and locale in the audit artifact.
- If live search is unavailable, stop before formal writing. Ask the user for a fresh SERP export, pasted results, or screenshots that preserve the query, retrieval date, locale if known, ranks, titles, URLs, and snippets. A keyword plan or research checklist may be prepared while blocked; an article draft may not.
- Treat user-supplied SERP evidence as live only when its retrieval date and result context are present. Mark its acquisition method in the audit.

## Language and locale

- Research and write in the requested content language. Search in that language, in English when it broadens primary-source coverage, and in relevant local/source languages when the topic warrants it.
- Record the language of every query and source. When translating, preserve the original meaning, units, currencies, dates, and qualifications; identify translated quotations.
- If no region is supplied, set `locale` to `unspecified` in the brief and audit. Do not silently assume the United States or any other market. Use region-neutral wording, label geographically variable facts, and ask for a locale only when it materially changes the answer.

## Source hierarchy and freshness

Prefer the highest suitable tier; authority must match the claim.

1. **Primary:** official documentation, product or pricing pages for the provider's own offering, laws and regulators, standards bodies, original datasets, peer-reviewed research, filings, and direct interviews or transcripts.
2. **Independent expert:** original analysis, testing, or research by identifiable specialists and credible institutions with a disclosed method.
3. **Reputable secondary:** established newsrooms, trade publications, and high-quality reference databases that identify their evidence.
4. **Community:** Reddit, Quora, forums, social posts, and comments. Use these for firsthand experience, recurring questions, language, and leads—not as sole proof of universal facts.

Use competitor articles to discover subtopics, gaps, and claims to verify. Do not treat them as authoritative merely because they rank.

For Google-facing work, re-check the current official guidance when it affects the recommendation. Start with [helpful, reliable, people-first content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content), [optimization for generative AI search](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide), [generative AI content guidance](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content), and the current [structured-data feature gallery](https://developers.google.com/search/docs/appearance/structured-data/search-gallery). Treat these as policy inputs, not as promises of ranking or citation. In particular:

- do not claim that Google prefers a fixed word count;
- do not create separate pages for every fan-out query or mechanically “chunk” text for AI systems;
- do not confuse E-E-A-T with a single measurable ranking factor;
- do not assume a structured-data feature remains supported merely because its Schema.org type still exists.

- Verify prices, specifications, availability, policies, and other changeable facts in the current research session, preferably from a primary source. Record currency, plan or model, billing cadence, region, and observation date where relevant.
- Prefer recent sources for news, trends, product comparisons, and market conditions. Older sources are acceptable for stable foundational facts when still authoritative.
- Record publication and update dates when available. Flag undated sources and corroborate consequential claims.
- When credible sources conflict, show the disagreement or resolve it explicitly using recency, primary evidence, scope, and methodology.

## Community and video sources

- Search Reddit and Quora when real-user problems, objections, workflows, or terminology would improve the article. Attribute individual experiences and never convert a few posts into prevalence claims.
- Search YouTube when a demonstration, walkthrough, talk, interview, or creator workflow is relevant. Prefer the original channel and record the video date and a timestamp or transcript location for the cited point.
- Verify hard facts found on community or video pages against a suitable primary or independent source whenever possible.

## Traceability and retention

- Make every statistic, price, specification, benchmark, and expert opinion traceable to the exact supporting URL and its access date. The cited page must support the specific claim, not merely discuss the topic.
- For calculations, retain the source inputs and formula. For expert views, retain the person's name, relevant role or credentials, original publication, and date. Do not invent quotations, credentials, tests, surveys, or consensus.
- Retain source metadata, concise evidence notes, and only the minimum excerpt required for verification. Never save or deliver a complete competitor article, full-page copy, mirrored HTML, or bulk page text.

## Links, source list, and information gain

- Add natural inline links on descriptive anchor text at the point a source supports a claim. Avoid raw URLs, vague anchors, and citation dumping.
- End the article with a `Sources` section containing only sources actually used. Keep it concise; give the title or publisher and the natural link. Inline links remain the primary claim-level trail.
- Create information gain through evidenced synthesis: clearer decisions, comparisons, workflows, caveats, original calculations, or connections among sources. Label calculations and inferences. Never fabricate experience or facts to make the article appear more original.
