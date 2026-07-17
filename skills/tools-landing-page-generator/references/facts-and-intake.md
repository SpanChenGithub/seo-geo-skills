# Facts and Intake Protocol

Use this protocol at the start of every landing-page generation run. Collect enough context to research the keyword, identify the correct brand and page, and prevent unsupported product, comparison, privacy, or structured-data claims.

## Contents

- [Required intake](#required-intake)
- [Optional product-background request](#optional-product-background-request)
- [Evidence hierarchy](#evidence-hierarchy)
- [High-risk fact rules](#high-risk-fact-rules)
- [Canonical proposal when no final page URL exists](#canonical-proposal-when-no-final-page-url-exists)
- [Pause conditions](#pause-conditions)
- [Intake record](#intake-record)

## Required intake

Ask for or confirm all of the following:

1. Primary target keyword: one exact keyword for one landing page.
2. Target website URL: the official site whose brand, product context, and design language the page must follow.
3. URL role: determine whether the supplied URL is the final landing-page URL, an existing reference page, or only the site or homepage used for design extraction.
4. Final landing-page URL: use it when it already exists or has already been chosen. If it does not yet exist, collect the site base URL and follow the canonical proposal process below.

Normalize obvious surrounding whitespace, but do not silently rewrite the user's keyword, domain, path, locale, or product name. Ask when an ambiguity could change search intent or the canonical URL.

## Optional product-background request

Ask the user once, in a single concise prompt, whether they can provide any of the following as generation context:

- Knowledge base, product documentation, help center, or relevant files.
- Product positioning and the problem it is intended to solve.
- Target users.
- Primary use cases.
- Features, differentiators, strengths, or limitations.
- Brand or design guidance beyond the supplied website.

Make clear that this background is optional and that the user may answer none. Missing optional background alone is not a reason to stop when the official site provides enough reliable evidence.

Also invite the user to provide operational facts that may be needed by the required page sections:

- Exact usage steps.
- Pricing, free plan, free trial, or payment conditions.
- Registration requirements and usage limits.
- Supported browsers, devices, operating systems, file types, inputs, and outputs.
- Privacy, storage, deletion, sharing, and security practices.
- CTA label and destination URL.
- Approved competitor set and comparison evidence.
- Verified ratings, review counts, awards, or adoption figures.
- Official OG image, logo, social profiles, publication date, and prior modification date.

Do not present this second list as permission to guess. It identifies facts that require evidence if they appear in copy, metadata, comparison tables, or JSON-LD.

## Evidence hierarchy

Use evidence in this order:

1. Explicit, current facts supplied or approved by the user, including provided internal documentation.
2. Current official pages on the target website, such as product, help, pricing, privacy, terms, security, developer, and release-note pages.
3. Current official brand-controlled sources, such as verified social profiles, official repositories, or official app-store listings.
4. For competitor facts, the competitor's own current product, pricing, help, privacy, and technical documentation.
5. Reputable independent sources for market context or corroboration.
6. Search snippets, forums, and user-generated discussions for discovering concerns and language only, not for asserting target-product facts.

For every material fact, retain its source URL or user-provided source name and the date it was accessed or supplied. Prefer the more recent and more specific authoritative source. If two authoritative sources conflict and the conflict affects the page, pause and ask the user which fact is current. Do not resolve a meaningful conflict by guessing.

Product facts and design cues are different evidence classes. A screenshot may support colors, spacing, and component style, but it does not prove pricing, privacy, functionality, ratings, or performance.

## High-risk fact rules

Never invent, extrapolate, or copy a value from an unrelated brand for any of the following:

- Price, free access, free trial, credits, subscriptions, refunds, or payment conditions.
- Data collection, storage, retention, automatic deletion, encryption, third-party sharing, training use, registration, privacy, or security practices.
- Legal, regulatory, certification, compliance, safety, or accessibility claims.
- Supported platforms, browsers, operating systems, devices, formats, integrations, limits, or availability.
- Processing speed, output quality, accuracy, realism, reliability, ranking, or superiority claims.
- Competitor features, prices, privacy practices, limits, or comparative advantages.
- Ratings, rating counts, reviews, testimonials, awards, user counts, download counts, customer names, or market adoption.
- Publication and modification dates for an existing page.

Apply these rules to visible copy, table cells, metadata, alt text, microcopy, and every JSON-LD block.

### Specific handling

- Use free only when authoritative evidence establishes what is free. Qualify free plan or free trial when that is the accurate claim.
- Include an aggregateRating only when the rating and count are real, current, attributable, and supported by a visible rating source appropriate to the page. Otherwise omit aggregateRating. Never use fixed placeholder ratings.
- Use privacy and data-security promises only when official policy or user-approved facts support each promise. If a mandatory privacy section cannot be supported, pause for facts instead of filling it with generic assurances.
- Populate Organization, WebSite, SoftwareApplication, Open Graph, and social-profile values from the target brand. Never carry VidMage or any other example brand into an unrelated site.
- State competitor facts only when each material comparison can be traced to current evidence. Use Not publicly documented when that is exactly what the evidence shows; do not convert missing evidence into a negative product claim.
- Do not claim that a CTA works, an upload is processed, or a generated interface is functional unless actual behavior or an integration was provided and verified.
- For a new unpublished page, use a proposed publication date only after the user confirms it represents the intended first publication date. For an existing page, obtain or verify the actual original publication date. Keep dateModified greater than or equal to datePublished.

Missing optional proof should normally cause the unsupported claim or optional schema field to be omitted. It should cause a pause when the fact is required by a mandatory section, is necessary to avoid misleading users, or the user explicitly requires the claim.

## Canonical proposal when no final page URL exists

When the user has no final landing-page URL:

1. Confirm the official site base URL and preferred locale.
2. Inspect the site's existing URL conventions when accessible, including locale prefixes, tools directories, trailing slashes, and keyword slug patterns.
3. Create a lowercase, concise, ASCII, hyphen-separated slug that represents the primary keyword. Remove punctuation and avoid filler words only when doing so preserves meaning.
4. Propose one complete HTTPS canonical URL that follows the observed site convention. If no convention can be verified, propose the conservative pattern https://domain.example/[keyword-slug]/.
5. Check for an obvious collision with an existing page when the site is accessible.
6. Present the proposed canonical to the user and obtain confirmation before finalizing SEO metadata or HTML.

Do not claim that the proposed URL exists, create the remote page, or publish anything. Once approved, keep the canonical link, og:url, WebPage.url, and any other page URL fields identical.

## Pause conditions

Pause the workflow and ask a focused question when any of the following occurs:

- The primary target keyword is missing, contains materially different intents, or cannot be identified.
- The official target website URL is missing or its role is unclear.
- The final URL is unknown and the proposed canonical has not been confirmed.
- The target brand or product cannot be identified reliably from the supplied context.
- The website cannot be inspected and the user has not supplied a usable screenshot, brand guide, product documentation, or other fallback evidence needed for the task.
- A mandatory section depends on an unverified high-risk fact, especially privacy, security, pricing, comparison, or operational claims.
- User-provided information conflicts materially with current official evidence.
- The requested competitor comparison cannot be supported with enough current evidence to avoid misleading claims.
- The keyword research suitability gate returns mixed intent, fail, or inconclusive and user direction is required.
- Fewer than 7 usable distinct organic websites remain after the documented collection attempt described in keyword-research.md.

When pausing, state exactly what is missing or contradictory, why it affects accuracy, and the smallest user response that will unblock the workflow. Do not continue into copy or HTML generation while the blocking issue remains.

## Intake record

Before research, retain a short intake record containing:

- Exact target keyword.
- Target website URL and its role.
- Confirmed final URL or pending canonical proposal.
- Brand and product name.
- User-provided background sources.
- Official sources discovered so far.
- Known high-risk facts and their evidence.
- Unknown facts that must be omitted or resolved.
- Any explicit user overrides or approvals.

Treat this record as the factual boundary for later copy, SEO elements, comparison tables, structured data, and HTML. Research may add evidence, but it may not turn an assumption into a product fact.
