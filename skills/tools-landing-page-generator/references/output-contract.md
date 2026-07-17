# Output Package and HTML Contract

Use this contract after research, product-fact resolution, style extraction, visible copy, and SEO elements have stabilized. Keep public HTML, intermediate artifacts, and machine-checkable hooks synchronized.

## Contents

- [Package location](#package-location)
- [Required package tree](#required-package-tree)
- [Artifact requirements](#artifact-requirements)
- [HTML document contract](#html-document-contract)
- [Section hooks](#section-hooks)
- [Tool placeholder](#tool-placeholder)
- [CSS and JavaScript](#css-and-javascript)
- [Links and assets](#links-and-assets)
- [Collision handling](#collision-handling)
- [Blocked-run output](#blocked-run-output)

## Package location

Write a completed run under `output/<keyword-slug>/` relative to the active project unless the user selects another destination.

Create `<keyword-slug>` from the exact primary keyword:

- lowercase ASCII when the keyword is English
- words separated with single hyphens
- punctuation removed unless it changes meaning
- no leading, trailing, or repeated hyphens

Do not confuse the output directory with the production URL path. Record both independently.

## Required package tree

```text
output/<keyword-slug>/
├── index.html
├── manifest.json
├── research/
│   ├── intake.md
│   ├── keyword-research-<keyword-slug>.md
│   ├── sources.json
│   ├── fact-ledger.json
│   └── style-report.md
├── content/
│   ├── landing-page-copy.md
│   └── seo-elements-<keyword-slug>.md
├── assets/
│   └── asset-manifest.json
└── validation/
    ├── validation-report.json
    ├── qa-report.md
    ├── desktop.png          # when browser rendering is available
    └── mobile.png           # when browser rendering is available
```

Keep `assets/` even when no raster asset is needed. In that case, record an empty asset list and the deliberate CSS, SVG, text-brand, or placeholder decisions in `asset-manifest.json`.

## Artifact requirements

### `manifest.json`

Use these stable top-level fields:

```json
{
  "schemaVersion": "1.0",
  "keyword": "exact target keyword",
  "keywordSlug": "keyword-slug",
  "brandName": "Verified Brand",
  "productName": "Verified Product",
  "canonicalUrl": "https://example.test/keyword-slug/",
  "pageLanguage": "en-US",
  "visualSourceMode": "site-extracted",
  "research": {
    "market": "United States",
    "language": "English",
    "device": "desktop",
    "date": "2026-07-17",
    "organicUsableCount": 15,
    "serpGatePassed": true,
    "redditStatus": "accessible",
    "quoraStatus": "accessible"
  },
  "artifacts": {},
  "validation": {"status": "pending"}
}
```

Record:

- schema version `1.0`
- exact target keyword and keyword slug
- brand and product name
- research market, language, device, and date
- confirmed canonical URL
- public page language
- visual source mode: `user-supplied`, `local-project`, `site-extracted`, or `user-approved-neutral-fallback`
- paths to every required artifact
- organic usable-page count and whether the 7-page gate passed
- Reddit and Quora access states
- validation state and timestamp

### Research artifacts

- Keep intake facts and unresolved questions in `intake.md`.
- Follow the exact report order in `keyword-research.md`.
- Store every cited URL, source type, organic rank when applicable, access date, access status, and supported claims in `sources.json`.
- Store claim text, normalized value, source identifier, locator or note, access date, risk class, affected sections, and public-use decision in `fact-ledger.json`.
- Store style provenance, sampled URLs, screenshot paths, computed observations, synthesized tokens, assets, uncertainty, and fidelity notes in `style-report.md`.

### Content artifacts

- Treat `content/landing-page-copy.md` as the source of truth for every visible marketing sentence.
- Treat `content/seo-elements-<keyword-slug>.md` as the source of truth for the document title, metadata, canonical, language alternates, dates, and JSON-LD.
- Do not create hidden alternate titles or descriptions in the final package.

### Validation artifacts

- Save deterministic validator output to `validation/validation-report.json`.
- Save human review findings, exceptions, evidence gaps, and visual checks to `validation/qa-report.md`.
- Save desktop and mobile screenshots when a rendered browser is available. If unavailable, state that limitation in both reports instead of creating fake images.

## HTML document contract

Create one complete HTML5 document with:

- `<!doctype html>`
- one `<html lang="en-US">` by default or the confirmed language override
- one `<head>` with charset, viewport, Title, Meta Description, canonical, supported social tags, and separate JSON-LD scripts
- one visible `<body>` with semantic `header`, `main`, and `footer` when those elements fit the extracted site pattern
- one `<main id="main-content">`
- one H1
- semantic H2 and H3 hierarchy
- inline `<style>`
- no external stylesheet, framework bundle, remote font service, analytics, or tracking code

For a completed tool page, include separate verified JSON-LD objects for `WebPage`, `SoftwareApplication`, and the visible `FAQPage`. Add `Organization` only when its identity fields are verified and the page should carry that entity. Missing rich-result-only offer, rating, or review data does not authorize invented values.

Header and footer do not count toward the eight required content sections. Use only verified navigation and footer destinations. Omit an unknown link instead of inventing it.

## Section hooks

Place the following eight top-level elements inside `main` exactly once and in this order:

```html
<section data-section="hero">...</section>
<section data-section="why-choose">...</section>
<section data-section="key-features">...</section>
<section data-section="how-to">...</section>
<section data-section="comparison">...</section>
<section data-section="faq">...</section>
<section data-section="privacy">...</section>
<section data-section="final-cta">...</section>
```

Use these machine-checkable child hooks:

- HERO: `data-hero-description` and `data-tool-placeholder`
- Why Choose: one `data-why-point` per point
- Key Features: one `data-feature` per feature, containing one `data-feature-description` and one `data-feature-cta`
- How to: one `data-how-step` per step
- Comparison: one `data-comparison-product` for the target product and each of the five competitors
- FAQ: one `data-faq-item` per question, containing one `data-faq-question` and one `data-faq-answer`
- Privacy: one `data-privacy-point` per verified point
- Final CTA: one `data-final-cta`

Hooks do not replace semantic HTML. Use headings, paragraphs, lists, tables, links, buttons, `details`, and other native elements appropriately.

## Tool placeholder

Place the tool placeholder inside the HERO section and give it:

- `id="tool-root"`
- `data-tool-placeholder`
- `role="region"`
- a specific non-empty `aria-label`
- visible text that makes its integration status honest
- a source comment describing the intended replacement boundary

Do not place a form, file input, enabled button, fake progress state, generated result, download control, or script-driven simulation inside it. It may use static decorative layers and explanatory text that do not imply the tool currently works.

## CSS and JavaScript

- Implement the design in original inline CSS derived from the style report.
- Use CSS custom properties for the synthesized palette, type scale, spacing, radius, shadow, and control tokens.
- Use system font stacks unless the user supplies an authorized local font asset.
- Support narrow mobile widths without horizontal page overflow.
- Provide clear focus styles, adequate touch targets, readable contrast, and `prefers-reduced-motion` handling.
- Use JavaScript only for a necessary presentational behavior that native HTML and CSS cannot provide.
- Prefer native `details` and `summary` for FAQ disclosure. Do not add JavaScript merely to imitate an accordion.
- Keep all JavaScript inline and free of network calls, tracking, storage, and functional-tool simulation.

## Links and assets

- Use only confirmed CTA and navigation destinations.
- Use absolute production URLs in canonical, social metadata, and JSON-LD.
- Use user-supplied, authorized local, or newly created original assets only.
- Do not hotlink sampled-site assets or remote fonts.
- Do not reference a missing local file.
- Give every informative image descriptive alt text. Use empty alt text for decorative images.
- Omit `og:image` and related fields until a real crawlable production image URL exists.
- Record each asset's role, source, path, dimensions, format, alt text, loading behavior, and status in `asset-manifest.json`.

## Collision handling

Before writing, check whether the intended package directory exists.

- Do not delete, empty, or overwrite it.
- Choose the next available sibling name: `<keyword-slug>-v2`, then `-v3`, and so on.
- Record the originally requested path and selected versioned path in the new manifest.
- Never batch-delete prior runs.

## Blocked-run output

When a required gate blocks formal generation, do not create a misleading `index.html`. Preserve the completed evidence under the proposed package root and add:

```text
validation/blocked-status.json
```

Record the blocked stage, exact reason, missing evidence, smallest user action needed, completed artifacts, and explicit statement that HTML was not generated. Do not populate missing formal artifacts with fabricated placeholder content merely to satisfy the complete-package tree.
