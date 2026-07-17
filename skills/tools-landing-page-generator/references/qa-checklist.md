# Quality Assurance Checklist

Use this checklist after the research, copy, SEO, style, and HTML stages. Run deterministic checks first, then perform a rendered visual and interaction review. Do not treat a validator pass as proof of factual accuracy or design fidelity.

## Contents

- [Gate audit](#gate-audit)
- [Research audit](#research-audit)
- [Fact and claim audit](#fact-and-claim-audit)
- [Copy and structure audit](#copy-and-structure-audit)
- [Technical SEO audit](#technical-seo-audit)
- [HTML and accessibility audit](#html-and-accessibility-audit)
- [Design fidelity audit](#design-fidelity-audit)
- [Responsive and browser audit](#responsive-and-browser-audit)
- [Asset and security audit](#asset-and-security-audit)
- [Final artifact audit](#final-artifact-audit)
- [QA report](#qa-report)

## Gate audit

- Confirm one exact primary keyword and one official target website.
- Confirm the keyword suitability decision passed or record the user's explicit mixed-intent or reduced-evidence override.
- Confirm at least 7 distinct usable organic pages were inspected, or record the explicit user decision to continue with fewer.
- Confirm the canonical URL is complete, HTTPS, production-intended, and user-approved.
- Confirm the brand and product identity are unambiguous.
- Confirm the mandatory sections can be written without inventing features, workflow, comparisons, privacy, or CTA facts.
- Confirm the style source is available or the user explicitly approved a neutral fallback.
- Stop the audit and return to the applicable gate when any required confirmation is absent.

## Research audit

- Confirm the research scope states market, language, device, search engine, result type, and actual access date.
- Confirm the first 15 distinct eligible organic sites were attempted and all exclusions or access failures were recorded.
- Confirm snippets were not treated as full page bodies.
- Confirm Reddit and Quora were both attempted and limitations were disclosed.
- Confirm visible engagement values were recorded only when observable.
- Confirm source URLs and access dates support every material research conclusion.
- Confirm the final report includes, in order, up to 5 core value propositions, up to 10 high-value gaps, forum topics, up to 30 meaningful words or phrases, user profiles, 6 use cases, 20 semantic terms, and 10 FAQ candidates.
- Confirm audience and use-case inferences are labeled rather than presented as known customer data.

## Fact and claim audit

- Trace every material product statement to `fact-ledger.json`.
- Verify price, free access, trial, credits, registration, limits, formats, compatibility, speed, accuracy, quality, privacy, storage, deletion, security, sharing, ratings, dates, and metrics against authoritative evidence.
- Confirm no competitor pattern or forum statement became a target-product fact.
- Confirm every comparison cell has current evidence or accurately says `Not publicly stated`.
- Confirm missing evidence never became a negative competitor claim.
- Confirm no example brand, fixed rating, compatibility list, social profile, or logo leaked into the page.
- Confirm the tool placeholder does not imply working upload, generation, preview, result, or download behavior.

## Copy and structure audit

- Confirm the 8 top-level content sections appear exactly once in the required order.
- Confirm the tool placeholder is inside HERO.
- Confirm one H1 contains the target keyword naturally and excludes the brand name.
- Confirm the HERO description states function plus benefit.
- Confirm Why Choose contains the brand and target keyword in a neutral heading plus exactly 4 distinct points.
- Confirm Key Features contains exactly 6 supported feature blocks and one CTA per block.
- Confirm How to appears immediately after Key Features and contains 3 or 4 verified action-led steps.
- Confirm Comparison contains the target product plus exactly 5 real competitors.
- Confirm FAQ contains 8 to 10 questions with direct answers.
- Confirm Privacy contains exactly 4 verified points.
- Confirm Final CTA uses one real conversion goal or a clearly documented integration destination.
- Count all specified copy lengths and record justified exceptions.
- Confirm the public copy is American English, conversational, direct, simple, and about seventh-grade reading level or lower.
- Confirm each section adds new value and the page contains no unnecessary repetition, hype, keyword stuffing, or unsupported superlative.
- Confirm user-visible headings and prose contain no em dash, en dash, or spaced hyphen punctuation.

## Technical SEO audit

- Confirm exactly one Title and one Meta Description.
- Confirm the Title does not contain the brand name.
- Record Title and Meta Description character counts and any justified exception to the 50 to 60 and 150 to 160 targets.
- Confirm the Title and Meta Description match visible page content and search intent.
- Confirm the target keyword or a justified close grammatical variant appears naturally.
- Confirm the canonical is absolute, clean, and self-referencing for the intended production page.
- Confirm canonical URL, `og:url`, and `WebPage.url` are identical.
- Confirm Title, `og:title`, `twitter:title`, and `WebPage.name` are identical unless an intentional platform variant is documented.
- Confirm Meta Description, `og:description`, `twitter:description`, and `WebPage.description` are identical unless documented.
- Confirm `html[lang]`, `WebPage.inLanguage`, and any locale metadata are compatible.
- Confirm `hreflang` is omitted unless complete, self-referencing, reciprocal production mappings are known.
- Parse every JSON-LD block. Confirm each is one JSON object in its own script.
- Confirm completed tool pages contain one `WebPage`, one `SoftwareApplication`, and one visible-copy-matched `FAQPage`; treat `Organization` as conditional.
- Confirm visible FAQ copy and FAQPage JSON-LD match when FAQPage is emitted.
- Confirm rating, review, offer, price, Organization, social, image, date, and compatibility fields appear only when verified.
- Confirm `dateModified` is not earlier than `datePublished` and neither date is guessed or future-dated.
- Confirm there is no accidental `noindex`, canonical mismatch, example domain, missing URL, or hidden metadata alternative.

## HTML and accessibility audit

- Confirm valid HTML5 structure, UTF-8 charset, viewport metadata, and one main landmark.
- Confirm heading levels are logical and there is exactly one H1.
- Confirm navigation, header, main, sections, table, FAQ, and footer use semantic elements where appropriate.
- Confirm every control and link has an accessible name and a visible focus state.
- Confirm keyboard order follows visual and reading order.
- Confirm FAQ disclosure works with keyboard and native semantics.
- Confirm images have correct informative or decorative alt treatment.
- Confirm comparison headers associate correctly with rows and columns.
- Confirm color is not the only way information is conveyed.
- Confirm touch targets, text size, line height, and content width remain usable on mobile.
- Confirm motion respects `prefers-reduced-motion`.
- Confirm the page remains understandable with CSS disabled and does not require JavaScript for core copy.

## Design fidelity audit

- Compare the rendered page with `style-report.md`, not with memory.
- Confirm palette roles, typography, spacing rhythm, radii, borders, shadows, controls, cards, table treatment, navigation, footer, and responsive patterns reflect the selected visual source.
- Confirm explicit user style instructions override lower-priority website observations.
- Confirm the result is an original implementation rather than a copied page structure or stylesheet.
- Confirm fallback tokens are clearly labeled and were explicitly approved.
- Record every intentional deviation and its accessibility, licensing, or content reason.

## Responsive and browser audit

When browser rendering is available:

- Render a desktop viewport around 1440 pixels wide and save `validation/desktop.png`.
- Render a mobile viewport around 390 pixels wide and save `validation/mobile.png`.
- Inspect the complete page, not only the first viewport.
- Check for horizontal page overflow, clipped headings, overlapping layers, broken grids, table overflow, unreadable controls, orphaned headings, and excessive empty space.
- Check that navigation, comparison table, FAQ, and CTA remain usable on mobile.
- Tab through interactive elements and confirm visible focus and sensible order.
- Check console errors and failed network requests.
- Verify no external framework, remote font, unauthorized asset, analytics, or tracker loads.
- If rendering is unavailable, record that visual, responsive, and interaction checks were not performed.

## Asset and security audit

- Confirm every asset appears in `asset-manifest.json`.
- Confirm every local path exists and every production URL is intentional.
- Confirm no sampled-site image, font, icon, video, script, or stylesheet is hotlinked.
- Confirm public-site source code, framework bundles, tracking identifiers, API keys, forms, and consent scripts were not copied.
- Confirm no secrets, tokens, private notes, raw provider responses, or local filesystem paths appear in public HTML.
- Confirm no executable network call, storage access, upload behavior, or functional-tool simulation was added.
- Confirm no broken image reference or unauthorized trademark treatment remains.

## Final artifact audit

- Confirm all required complete-run files in `output-contract.md` exist.
- Confirm `manifest.json` paths, keyword, canonical, research coverage, style mode, and validation status match the package.
- Confirm `landing-page-copy.md`, SEO artifact, and HTML contain the same final copy and identity fields.
- Confirm the deterministic validator reports zero errors.
- Re-run validation after the last HTML or metadata change.
- Confirm every warning is resolved or documented with evidence and an acceptance reason.
- Confirm the handoff lists unresolved facts, omitted optional SEO fields, fallback decisions, and unperformed checks.
- Confirm an existing output was not overwritten or deleted.

## QA report

Write `validation/qa-report.md` with:

1. Overall status: pass, pass with documented warnings, or blocked.
2. Research date, market, coverage, and forum access summary.
3. Keyword suitability decision and any override.
4. Confirmed canonical and product-fact status.
5. Copy structure and measured length results.
6. SEO invariant and JSON-LD results.
7. Accessibility and responsive results.
8. Visual source, fidelity findings, and intentional deviations.
9. Asset, licensing, security, and privacy findings.
10. Deterministic validator result.
11. Remaining warnings, omissions, and exact next actions.

Do not mark the page as passed when a blocking evidence, canonical, research, style, or factual gate remains unresolved.
