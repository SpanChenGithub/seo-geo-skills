# Official Standards Baseline

Baseline checked: 2026-07-15. Recheck current official documentation whenever a rule, metric, rich-result feature, or browser behavior may have changed.

## Core interpretation rules

- Treat Googlebot access, an HTTP `200` response, and indexable content as Google's minimum technical eligibility requirements. Passing them does not prove indexing or ranking.
- A robots.txt disallow controls crawling, not guaranteed indexing. A crawler must be allowed to fetch a page to observe a page-level `noindex` rule.
- Do not put `noindex` in robots.txt. Use a robots meta tag or `X-Robots-Tag`. A normal robots.txt `4xx` generally means no crawl restrictions, while a robots.txt `5xx` can interrupt crawling and requires investigation.
- Treat a declared canonical as a signal, not an absolute directive. Check redirects, HTML or HTTP canonicals, sitemap entries, internal links, protocol, host, path, and rendered content for consistency.
- Do not make a missing self-canonical a critical failure on an otherwise unique page. Treat it according to duplicate-URL risk and signal consistency.
- Include in XML sitemaps the canonical URLs the site wants in search. Sitemap presence does not guarantee crawling or indexing, and a small well-linked site may not require one.
- Avoid fixed title or meta-description character limits as Google rules. Evaluate clarity, relevance, duplication evidence, likely truncation risk, and consistency with visible content.
- Ignore `meta keywords` for Google SEO scoring.
- Require crawlable `<a href>` links for dependable discovery. JavaScript-only click handlers may not provide equivalent crawlability.
- Evaluate structured data against the visible page and Google's feature-specific requirements. Valid Schema.org vocabulary alone does not guarantee rich-result eligibility.
- Prefer meaningful alt text for informative images and empty alt text for decorative images. Do not require descriptive alt text on decorative images.
- Evaluate mobile content and signals for parity because Google uses mobile-first indexing. Do not infer mobile usability solely from the viewport tag.
- For international pages, validate language-region codes, self-references, return links, canonicals, and `x-default` where it genuinely represents a fallback.

## Current Core Web Vitals

Assess field Core Web Vitals at the 75th percentile, separately for mobile and desktop:

| Metric | Good | Needs improvement | Poor |
| --- | ---: | ---: | ---: |
| LCP | `<= 2.5 s` | `> 2.5 s` and `<= 4.0 s` | `> 4.0 s` |
| INP | `<= 200 ms` | `> 200 ms` and `<= 500 ms` | `> 500 ms` |
| CLS | `<= 0.1` | `> 0.1` and `<= 0.25` | `> 0.25` |

Require all three metrics to be in the Good range for a passing Core Web Vitals assessment. Label Lighthouse data as lab data. Lighthouse navigation audits normally use TBT as a responsiveness diagnostic and do not supply real-user INP.

Treat Lighthouse's SEO score as a limited automated checklist, not a complete technical SEO verdict. Keep PageSpeed Insights and CrUX field data separate from Lighthouse lab data; field data may be unavailable and represents an aggregation period rather than the current audit visit.

## Primary references

### Crawling, indexing, and page signals

- [Google Search technical requirements](https://developers.google.com/search/docs/essentials/technical)
- [Google crawling and indexing overview](https://developers.google.com/search/docs/crawling-indexing)
- [Robots.txt introduction](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Block indexing with noindex](https://developers.google.com/search/docs/crawling-indexing/block-indexing)
- [Robots meta and X-Robots-Tag specifications](https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag)
- [Canonical URL guidance](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [HTTP status, network, and DNS errors](https://developers.google.com/search/docs/crawling-indexing/http-network-errors)
- [Build and submit a sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)
- [JavaScript SEO basics](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics)
- [Mobile-first indexing best practices](https://developers.google.com/search/docs/crawling-indexing/mobile/mobile-sites-mobile-first-indexing)
- [Localized versions and hreflang](https://developers.google.com/search/docs/specialty/international/localized-versions)

### Search appearance and page content

- [Title link guidance](https://developers.google.com/search/docs/appearance/title-link)
- [Snippet and meta-description guidance](https://developers.google.com/search/docs/appearance/snippet)
- [Supported Google meta tags](https://developers.google.com/search/docs/crawling-indexing/special-tags)
- [Crawlable link guidance](https://developers.google.com/search/docs/crawling-indexing/links-crawlable)
- [Outbound link qualification](https://developers.google.com/search/docs/crawling-indexing/qualify-outbound-links)
- [Image SEO best practices](https://developers.google.com/search/docs/appearance/google-images)
- [Structured data introduction](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [General structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org validator](https://validator.schema.org/)

### Performance

- [Google Search Core Web Vitals guidance](https://developers.google.com/search/docs/appearance/core-web-vitals)
- [Web Vitals and current thresholds](https://web.dev/articles/vitals)
- [How Core Web Vitals thresholds are defined](https://web.dev/articles/defining-core-web-vitals-thresholds)
- [INP became a Core Web Vital](https://web.dev/blog/inp-cwv-march-12)
- [Lighthouse performance scoring](https://developer.chrome.com/docs/lighthouse/performance/performance-scoring)
- [Lighthouse Time to Interactive legacy documentation](https://developer.chrome.com/docs/lighthouse/performance/interactive)
- [Chrome UX Report methodology and tools](https://developer.chrome.com/docs/crux/methodology/tools)
- [Lighthouse crawlability audit limitations](https://developer.chrome.com/docs/lighthouse/seo/is-crawlable)

Use these references to interpret evidence, not to claim that every recommendation is a direct ranking factor. Treat the Skill's score as a reproducible triage device, never as a Google score or ranking prediction.
