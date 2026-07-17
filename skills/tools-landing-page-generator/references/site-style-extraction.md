# Site Style Extraction

Use this reference when a landing page must visually belong to an existing site. Extract a reusable visual language, then create an original implementation. Do not clone a page, copy proprietary source code, or hotlink site assets.

## Contents

- [Priority order](#priority-order)
- [Page sampling](#page-sampling)
- [Capture process](#capture-process)
- [Design tokens and patterns](#design-tokens-and-patterns)
- [Implementation boundaries](#implementation-boundaries)
- [Assets and placeholders](#assets-and-placeholders)
- [Inaccessible-site fallback](#inaccessible-site-fallback)
- [Verification](#verification)

## Priority order

Resolve style decisions in this order:

1. Explicit user instructions, supplied brand guidelines, and supplied assets.
2. The user's local project design system, tokens, components, and existing landing-page conventions.
3. The rendered final landing-page URL, when that URL already exists.
4. The target site's origin and representative same-site pages.
5. A neutral, accessible fallback explicitly approved by the user and documented as an inference.

More specific and newer explicit guidance wins over a conflicting website pattern. Preserve accessibility and usability even when a sampled page does not.

Separate visual direction from product facts. A color, icon, screenshot, or layout never proves pricing, privacy, feature, performance, or compatibility claims.

## Page sampling

1. Normalize the user-supplied URL and identify its origin and intended final page URL.
2. Open the final URL first. If it is a new or unavailable path, open the origin homepage.
3. Inspect up to three additional representative pages on the same site. Prioritize, in order:
   - an existing tool or product landing page closest to the requested page type
   - the homepage or primary marketing page
   - a pricing, features, use-case, or other conversion page
4. Prefer pages on the same origin. Follow an official same-site subdomain only when it clearly shares the same product and brand system.
5. Avoid account dashboards, user-generated pages, temporary campaigns, experiments, and pages that visibly use a different sub-brand unless the requested landing page belongs to that system.
6. Record every sampled URL, page role, access date, viewport, and reason for selection.

Do not broaden the sample merely to find a preferred aesthetic. The goal is to represent the supplied site accurately.

## Capture process

Use a real rendered browser when available. Do not rely on HTML source alone for a JavaScript-rendered site.

For each selected page:

1. Capture a desktop screenshot around 1440 pixels wide and a mobile screenshot around 390 pixels wide. Capture the full page when practical and focused screenshots for headers, heroes, forms, cards, and CTAs.
2. Inspect the rendered DOM and computed styles for representative elements: `body`, navigation, H1, H2, body copy, links, primary and secondary buttons, form controls, cards, section wrappers, footer, and notices.
3. Read exposed CSS custom properties and design tokens when available. Treat them as evidence, not code to copy.
4. Observe responsive changes, sticky behavior, menus, grids, stacking, spacing compression, and content order.
5. Observe hover, focus, active, disabled, loading, error, and reduced-motion states when they are safely accessible.
6. Record recurring patterns and outliers. Prefer values repeated across multiple representative pages over one-off campaign styling.

Screenshots are evidence for analysis. Do not ship them as page assets unless the user owns them and explicitly requests their use.

## Design tokens and patterns

Create a compact style extraction report before writing final HTML. Include:

### Provenance

- explicit user requirements
- local project files inspected
- sampled URLs and screenshots
- inaccessible or uncertain sources
- conflicts and how priority resolved them

### Computed token table

Record observed and normalized values for:

- color roles: page, surface, elevated surface, text, muted text, border, primary, accent, success, warning, and error
- typography: font families, fallbacks, weights, H1 to H3 sizes, body size, small text, line heights, and letter spacing
- layout: content max width, grid columns, gutters, section spacing, and breakpoints
- shape: radii, border widths, dividers, shadows, and focus rings
- controls: button heights, padding, input heights, icon sizes, and state treatments
- motion: duration, easing, reveal pattern, and reduced-motion behavior

Distinguish exact computed observations from synthesized implementation tokens. Consolidate near-duplicate values into a small usable scale rather than reproducing every sampled pixel value.

### Component and composition patterns

Describe the site's recurring:

- header, navigation, logo treatment, and footer
- hero alignment, content width, tool placement, and CTA grouping
- buttons, links, forms, upload areas, cards, tables, accordions, badges, and notices
- section rhythm, backgrounds, dividers, decorative treatments, and density
- illustration, photography, icon, and screenshot style
- mobile stacking and responsive behavior

Describe patterns in words and tokens. Do not copy DOM trees, class names, selectors, scripts, or large CSS declarations from the public site.

## Implementation boundaries

- Write original semantic HTML and CSS from the extracted design system.
- Reuse local project components only when they are inside the user's authorized workspace and reuse is within task scope.
- Do not copy public-site HTML, JavaScript, framework bundles, hashed class structures, or proprietary component code.
- Do not recreate a sampled page section-for-section or pixel-for-pixel. Preserve the visual language while designing the requested content and information hierarchy.
- Do not copy trademarks, illustrations, photos, icons, or distinctive artwork unless the user supplies or authorizes those assets.
- Do not copy trackers, analytics identifiers, consent scripts, API keys, forms, or external integrations.
- Do not weaken contrast, focus visibility, keyboard access, semantic structure, or responsive usability to match an inaccessible source.
- Honor `prefers-reduced-motion` and avoid motion that blocks reading or interaction.

## Assets and placeholders

Prefer assets in this order:

1. User-supplied or local project assets with known intended use.
2. Newly created original assets authorized by the task.
3. Clearly documented local placeholders.

Never hotlink images, fonts, icons, videos, stylesheets, or scripts from the sampled website. Do not download and republish them without clear authorization.

For each required asset, create or request an asset manifest entry containing:

- role and intended section
- proposed local path and filename
- width, height, aspect ratio, and format
- alt text or empty alt rationale
- source or creation method
- loading behavior
- replacement status

If a logo is unavailable, use a text brand treatment or a clearly labeled neutral placeholder. If a content image is unavailable, use an original CSS or SVG abstraction that does not imitate protected artwork. Do not leave broken image URLs.

For a required production asset such as a logo or OG image, ask the user for the file or permission to create an original replacement. Keep temporary placeholders visibly documented in intermediate artifacts; do not present them as final brand assets.

## Inaccessible-site fallback

Do not bypass authentication, CAPTCHAs, paywalls, robots restrictions, or other access controls.

When the final URL or site cannot be rendered:

1. Try the public origin and the permitted representative pages.
2. Use accessible local project CSS, tokens, components, screenshots, or brand documents.
3. Ask the user for screenshots, a style guide, exported design tokens, or representative page files.
4. Ask whether the user wants to pause or explicitly approve a neutral accessible tool-page system. Do not continue with a neutral fallback without that approval. If approved, label every style decision as fallback rather than extracted fact.

An appropriate neutral fallback uses system fonts, restrained colors, clear hierarchy, visible focus states, responsive spacing, and original simple decoration. Do not guess a brand palette from a favicon or domain name.

## Verification

After generating HTML:

- Render at desktop and mobile widths and capture verification screenshots.
- Compare hierarchy, typography, color roles, spacing rhythm, component shapes, and responsive behavior against the extraction report.
- Verify that explicit user style instructions still take priority.
- Check semantic headings, landmarks, keyboard navigation, focus states, contrast, touch targets, and reduced motion.
- Confirm that no copied source code, external-site asset hotlinks, tracking IDs, or broken resources remain.
- Confirm that all fonts and assets are local, user-authorized, newly created, or clearly marked placeholders.
- List intentional differences from the sampled site, unresolved asset needs, and fallback decisions.
