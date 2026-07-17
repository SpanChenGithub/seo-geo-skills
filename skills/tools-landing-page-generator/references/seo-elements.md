# SEO Elements and Structured Data

Use this reference when generating the technical SEO portion of a landing page. Apply it to arbitrary sites. Never carry example brands, domains, ratings, dates, social profiles, compatibility claims, or asset URLs into an output.

## Contents

- [Source of truth](#source-of-truth)
- [Title and description](#title-and-description)
- [URL and canonical](#url-and-canonical)
- [Open Graph and Twitter](#open-graph-and-twitter)
- [Language and hreflang](#language-and-hreflang)
- [Publication dates](#publication-dates)
- [JSON-LD](#json-ld)
- [Cross-format invariants](#cross-format-invariants)
- [Current primary references](#current-primary-references)
- [Validation checklist](#validation-checklist)

## Source of truth

Use this evidence order for metadata and structured data:

1. Explicit, current facts supplied by the user.
2. Current project files and local brand, product, pricing, privacy, and legal documentation.
3. Facts visibly stated on the target site's official pages.
4. Omission.

Never infer a product fact from a keyword, a competitor, a common industry practice, or a visual design. Never invent or silently reuse:

- brand or legal organization names
- ratings, review counts, prices, currencies, or offers
- claims such as free, fastest, safest, private, or no signup
- deletion periods, storage practices, third-party sharing, or compliance claims
- operating systems, browsers, devices, integrations, or technical limits
- publication dates, social profiles, logos, or image URLs

When a required fact is unavailable, ask for it if it blocks an accurate deliverable. Otherwise omit the affected field or entity. Do not leave fabricated defaults in publishable HTML.

## Title and description

### Title tag

- Target 50 to 60 characters, including spaces. Treat this as an editorial target, not a search-engine limit.
- Write a unique, concise description of this page's actual tool and value.
- Include the target keyword near the beginning when it reads naturally. Use a close grammatical variant when an exact match would be awkward or misleading.
- Do not include the brand name. If the target keyword itself is a brand query, resolve keyword suitability before drafting rather than silently dropping part of the keyword.
- Use terms such as `free`, `online`, `secure`, or `fast` only when the page and verified product facts support them.
- Avoid keyword lists, repeated variants, unsupported superlatives, and clickbait.
- Allow a justified exception to the target range when the keyword, language, or established site convention requires it. Record the exception in the check report.

### Meta description

- Target 150 to 160 characters, including spaces. Treat this as an editorial target, not a search-engine limit.
- Summarize the page accurately, match search intent, state the primary benefit, and include the target keyword or a natural close variant.
- Keep every factual claim consistent with visible page copy.
- Do not stuff related terms or add facts that exist only in metadata.
- Allow a justified length exception when accuracy and readability would otherwise suffer.

## URL and canonical

### Slug

- Follow the site's existing routing and trailing-slash convention.
- Prefer a short, descriptive, lowercase slug with hyphens between words.
- Remove tracking parameters and avoid fragments as page identifiers.
- Preserve meaningful localized words when the site uses localized URLs. Percent-encode characters correctly.
- Do not assume that the supplied site URL is the final landing-page URL. Obtain or derive the full production URL before emitting a canonical.

### Canonical

- Use one absolute production URL, preferably HTTPS.
- Use a self-referencing canonical for the final landing page unless the user or project explicitly identifies another canonical.
- Exclude tracking parameters, session identifiers, and fragments.
- Match the site's chosen host, path casing, and trailing-slash convention.
- Do not point a new landing page to the homepage merely because the final path is unknown.

## Open Graph and Twitter

Generate only supported values. Use absolute, crawlable production URLs.

### Open Graph baseline

```html
<meta property="og:type" content="website">
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="https://example.com/final-path/">
<meta property="og:image" content="https://example.com/assets/page-share-image.png">
<meta property="og:image:alt" content="...">
```

- Add `og:site_name` only when the public site name is verified.
- Add `og:locale` only when the page locale is known. Add alternates only for real localized versions.
- Add image type, width, and height only when verified.
- Prefer a purpose-built social preview image. Do not substitute an unrelated logo or another site's image.

### Twitter card baseline

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="...">
<meta name="twitter:description" content="...">
<meta name="twitter:image" content="https://example.com/assets/page-share-image.png">
<meta name="twitter:image:alt" content="...">
```

- Use `summary_large_image` only when a suitable large image exists; otherwise use `summary` or omit the card.
- Add `twitter:site` or `twitter:creator` only for verified handles belonging to the site or product.
- Never hotlink an image from a competitor or unrelated host.

## Language and hreflang

- Set the HTML `lang` attribute from the actual page language and locale.
- Keep `WebPage.inLanguage` consistent with the page language. Prefer a valid BCP 47 tag such as `en-US` when the locale is known.
- Emit `hreflang` only when real alternate-language or alternate-region pages exist at known production URLs.
- Use fully qualified URLs. Include the current page itself and every alternate in the set.
- Require reciprocal annotations on the alternate pages. Do not emit a one-sided set that the skill cannot substantiate.
- Add `x-default` only when a real fallback or language-selector URL exists.
- Omit `hreflang` for a single-language page or when alternate URL mapping is incomplete.

## Publication dates

- Use ISO 8601 for `datePublished` and `dateModified`; include a timezone when time is present.
- Set `datePublished` to the page's actual first publication date. Do not use the generation date unless publication happens on that date.
- Set `dateModified` only after a real substantive update and ensure it is not earlier than `datePublished`.
- Treat changes to the title, meta description, H1, hero copy, key features, FAQ, comparison, privacy copy, or section set as substantive. Do not refresh the date for typo-only, style-only, or placeholder-image changes.
- If dates appear in JSON-LD, keep equivalent visible dates on the page consistent with them.
- Use page publication dates on `WebPage`. Add dates to `SoftwareApplication` or `WebApplication` only when they describe the application's own release or update and are separately verified.
- Omit unknown dates. Never emit a future date or a guessed historical date.

## JSON-LD

Place JSON-LD inside the HTML `head`. Keep each entity in its own valid `<script type="application/ld+json">` block and connect related entities with stable `@id` values. Include only properties that are accurate and represented by visible page content where applicable.

### WebPage

Use `WebPage` for the page itself. Recommended baseline:

- `@id`: canonical URL plus `#webpage`
- `name`: the title tag
- `url`: the canonical URL
- `description`: the meta description
- `inLanguage`: actual page language or locale
- `datePublished` and `dateModified`: only when verified
- `primaryImageOfPage`: only when a relevant, crawlable page image exists
- `isPartOf`: only when the site's `WebSite` identity is verified
- `publisher`: only when an appropriate verified organization or person exists

### SoftwareApplication

Emit this entity only when the landing page describes an actual software tool.

- Use `SoftwareApplication` as the entity type for the tool page. Describe browser delivery through accurate properties and visible copy rather than replacing the Google-supported type with a fabricated category.
- Use the real product or tool name, page URL, and description.
- Choose `applicationCategory` from the product's actual purpose and, when Google rich-result eligibility is a goal, use a currently supported category. Do not use `WebApplication` as a generic category value.
- Add `operatingSystem` only for verified supported or required systems. Do not treat browser names as operating systems.
- Add `offers` only when current price and currency facts are visible and verified. A genuinely free offer may use price `0`.
- Add `aggregateRating` only for genuine user ratings that are visible on the page and have a verified source, current `ratingValue`, `ratingCount`, and scale. Never default to a rating or review count.
- Add `review` only for a real, attributable, visible review.

Google's Software App rich-result eligibility requires `offers.price` and either a qualifying rating or review. Missing those fields does not justify inventing them. Keep the completed tool page's accurate `SoftwareApplication` semantic markup without unsupported rich-result fields and disclose that it may not be eligible for that rich result. Never promise that a rich result will appear.

### FAQPage

Emit `FAQPage` for this skill's required visible FAQ only when:

- the questions and answers are visible on the page
- each question has one site-authored answer
- JSON-LD text matches the visible copy
- every answer is factual and non-misleading

For ordinary commercial tool sites, do not claim that FAQ markup will produce a Google FAQ rich result. Because this skill requires a visible FAQ and matching FAQPage object, stop and resolve any factual mismatch before final HTML instead of emitting incomplete or hidden schema.

### Organization

Organization markup is conditional, not a landing-page default.

- Prefer existing sitewide Organization markup on the official homepage or about page instead of duplicating it on every landing page.
- Emit it here only when the page is on the organization's official site and its public name, URL, logo, and any `sameAs` profiles are verified.
- Omit unknown or irrelevant properties. Do not infer a legal entity from a domain or copy social links merely because icons appear in a footer.
- Reference an existing organization with its stable `@id` when the project already defines one.

## Cross-format invariants

Enforce these equalities unless the project deliberately supplies platform-specific variants:

- canonical URL = `og:url` = `WebPage.url`
- title tag = `og:title` = `twitter:title` = `WebPage.name`
- meta description = `og:description` = `twitter:description` = `WebPage.description`
- HTML language = compatible `WebPage.inLanguage` and `og:locale`
- verified public brand name, site name, organization name, and logo remain internally consistent
- ratings, prices, dates, privacy statements, and compatibility facts match visible page content
- default OG image = default Twitter image = `primaryImageOfPage` when one shared asset is used

Use consistent `@id` references such as `#webpage`, `#website`, `#organization`, and `#app`. Do not create duplicate entities with conflicting values.

## Current primary references

Recheck current official documentation during a formal run when structured-data or international-targeting rules may have changed. These sources were verified on 2026-07-17:

- [Google structured data general guidelines](https://developers.google.com/search/docs/appearance/structured-data/sd-policies): keep structured data current, visible, relevant, and non-misleading; valid markup does not guarantee a rich result.
- [Google Software App structured data](https://developers.google.com/search/docs/appearance/structured-data/software-app): rich-result eligibility requires the documented required fields, including `offers.price` and either a qualifying rating or review. This does not authorize invented offers, ratings, or reviews.
- [Google localized page guidance](https://developers.google.com/search/docs/specialty/international/localized-versions): use complete fully qualified self-referencing alternate sets with return links.

Treat official current documentation as higher priority than an old template. Preserve accurate semantic markup or omit an unsupported rich-result field instead of fabricating eligibility.

## Validation checklist

Before finalizing:

- Confirm that no example brand, domain, logo, social profile, rating, date, price, or operating-system list remains.
- Count title and meta-description characters and record any justified exception to the target ranges.
- Confirm that canonical, OG, Twitter, and JSON-LD invariants hold.
- Confirm that every emitted URL is absolute, production-ready, and belongs to an authorized or intended host.
- Parse every JSON-LD block as JSON and validate applicable schema types.
- Confirm that structured data describes visible, current page content and contains no guessed facts.
- Confirm that ratings and reviews are genuine, sourced, visible, and current.
- Confirm that hreflang is complete, self-referencing, reciprocal, and omitted when unsupported.
- Confirm that dates are real, consistent, non-future, and semantically attached to the correct entity.
- Confirm that the HTML contains one clear H1, descriptive image alt text, semantic headings, crawlable links, and no accidental `noindex`.
- Report omitted fields and the facts needed to add them later. Do not disguise omissions with placeholders in publishable metadata.
