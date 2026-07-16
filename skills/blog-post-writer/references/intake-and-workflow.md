# Intake and Workflow

## Minimal-start rule

A target keyword is enough to begin. Do not turn optional context into a setup questionnaire. Infer the language, record unknowns, and start research. Ask only for information that would materially alter the result or prevent a misleading claim.

When no brand material exists, use a direct, decisive, evidence-led editorial voice. Sound authoritative through specific analysis and useful judgment, not invented credentials or simulated product use. Persist a project-local brand profile only when the user explicitly asks. Never save brand configuration or user content in the skill directory.

## Intake record

Capture the following in `brief.json`:

- primary keyword;
- detected or requested language;
- requested region, or `unspecified` plus the search environment actually used;
- likely audience, task, and journey stage;
- supplied site, page, product, CTA, and existing draft;
- supplied first-party evidence and its owner;
- verified author or creator team when supplied, relevant role, products or workflows actually used, date and context, concrete success or failure observations, supporting records, research performed, tests run, interviews, customer questions, and professional experience;
- requested output path or chat-only mode;
- assumptions and open risks.

Do not infer the target country solely from the keyword language. Language and market are separate fields.

## Operating sequence

1. **Intake**: capture the keyword and optional context.
2. **Context inspection**: inspect supplied site pages, local content, or existing draft when available.
3. **Live research**: research the current SERP and supporting sources.
4. **Synthesis**: identify intent, winning formats, gaps, information-gain opportunities, and a reference length.
5. **Outline**: produce a source-mapped outline and pause for approval.
6. **Draft**: write the full article after approval.
7. **Editorial challenge**: test every important claim, recommendation, and section against the brief and sources.
8. **Package**: produce metadata, sources, media, internal links, quality findings, and applicable structured data.
9. **Validation**: run the package validator and resolve errors.
10. **Final gate**: request approval before declaring completion or entering any publishing workflow.

## Search failure gate

Live SERP evidence is mandatory. If the host cannot search, access results, or inspect enough result context to infer intent responsibly:

1. state what failed;
2. do not create a formal outline or article;
3. ask the user for a top-10 export, screenshots, or copied ranked results that preserve the query, capture date, locale when known, rank, title, and URL;
4. resume only after the supplied evidence is adequate;
5. label user-supplied results and their capture date in the research record.

A partial SERP may be usable when it contains enough diverse, current results to establish intent. Record the missing ranks and limitation; never fabricate them.

Competitor URLs without current rank, query, capture date, and search context are useful for page research but do not satisfy the live SERP gate.

## Outline approval gate

The outline response should make approval easy by showing:

- the recommended format and why it matches the live SERP;
- the reader promise and direct-answer strategy;
- the authorial point of view, genuine experience inputs, and concrete professional judgments the article will contribute;
- the proposed H1/H2/H3 structure;
- sources, examples, proof, and media planned for each material section;
- information-gain elements and any evidence still needed;
- one working metadata direction;
- region, freshness, and research limitations.

Wait for an explicit approval such as “approved,” “continue,” or a clear instruction to draft. Incorporate requested changes and ask again when the revised structure materially differs.

## Final approval gate

Deliver the article with a compact readiness summary:

- validator result;
- resolved and unresolved factual risks;
- sources and freshness limits;
- original-information inputs actually used;
- media or screenshots still needed;
- structured-data eligibility decisions;
- publication actions not taken.

Ask for final approval. Do not treat silence or outline approval as publication approval.

Keep audit limitations in the readiness summary unless they materially change a claim the reader must evaluate. The public article should not read like an internal QA report.

## Refreshing an existing article

For a refresh:

1. research the current query independently;
2. inventory accurate sections, stale facts, unsupported claims, weak intent coverage, and useful links;
3. preserve distinct first-party insights and valid rankings-related strengths where possible;
4. propose structural changes in the outline;
5. keep an audit note of material additions, removals, and claim updates;
6. never overwrite the source file until the user has asked for an in-place edit.

## Optional companion skills and APIs

Companion skills may expand topic discovery or metadata work, but their absence must not block this workflow. Before any paid API call, state the providers, models when known, expected number of calls, and fallback. Ask once for authorization unless the current request already grants it. Read credentials only from environment variables and never include credential values in artifacts, logs, prompts, or reports.
