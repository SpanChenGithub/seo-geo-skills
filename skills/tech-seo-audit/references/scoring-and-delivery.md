# Scoring and Delivery

## Table of Contents

1. [Severity](#severity)
2. [Category weights](#category-weights)
3. [Calculation](#calculation)
4. [Evidence coverage](#evidence-coverage)
5. [Issue counts](#issue-counts)
6. [Report path](#report-path)
7. [Delivery checks](#delivery-checks)

## Severity

Assign severity from observed impact and page intent:

- **Critical:** Prevents or directly contradicts intended crawling, indexability, safe access, or usable page delivery. Examples include an unintended `noindex`, a blocking error status on the canonical page, or an infinite redirect.
- **High:** Materially weakens discovery, canonical consolidation, rendered primary content, mobile access, or production performance. It requires prompt remediation but does not fully block the intended page.
- **Medium:** Creates a meaningful quality, relevance, efficiency, accessibility, or rich-result eligibility problem with limited immediate blocking impact.
- **Low:** A hygiene, consistency, or optimization issue with modest expected impact.

Adjust severity to the intended page state. A `noindex` is not a defect on a page intentionally excluded from search. Do not use severity to imply a guaranteed ranking gain.

Record one scored finding per root cause. Mention downstream symptoms under that finding rather than charging the same issue repeatedly.

## Category weights

Use these weights, totaling 100:

| Protocol category | Key | Weight |
| --- | --- | ---: |
| HTTP and indexability | `http_indexability` | 22 |
| Robots and sitemaps | `robots_sitemaps` | 8 |
| HTML head and metadata | `head_metadata` | 12 |
| Content structure and headings | `content_headings` | 8 |
| Internal and external links | `links` | 8 |
| Images and media | `images_media` | 7 |
| Structured data | `structured_data` | 8 |
| Performance and Lighthouse | `performance` | 15 |
| Mobile and UX | `mobile_ux` | 5 |
| Internationalisation | `internationalisation` | 3 |
| Security and miscellaneous | `security_misc` | 4 |

## Calculation

Start each verified category at its full weight. Deduct a fraction of that category's weight for each distinct finding:

| Severity | Deduction from category weight |
| --- | ---: |
| Critical | 100% |
| High | 40% |
| Medium | 20% |
| Low | 8% |

Cap deductions at the category's full weight. A category cannot fall below zero.

For every category, assign one evidence status:

- `Verified`: enough direct evidence exists to assess the category;
- `Not applicable`: the category genuinely does not apply and receives its full weight;
- `Unavailable`: evidence is insufficient, so exclude the category from both earned points and available points.

Calculate:

```text
earned_category_points = weight - min(weight, sum(issue deductions))
evidence_coverage = verified_or_not_applicable_weights / 100 * 100
overall_score = round(sum(earned_category_points) / sum(verified_or_not_applicable_weights) * 100)
```

Show a compact scoring breakdown in the report so another reviewer can recompute the result.

Use these non-official labels only for triage:

| Score | Label |
| --- | --- |
| 90-100 | Strong |
| 75-89 | Needs attention |
| 50-74 | Poor |
| 0-49 | Critical |

State that this is the Skill's audit score, not a Google or Lighthouse score.

## Evidence coverage

Provide an overall score only when:

1. `http_indexability` is Verified; and
2. evidence coverage is at least 60%.

Otherwise report `Not available - insufficient evidence` instead of forcing a number. Still list verified issues and Lighthouse results.

Never use a bare `Not available` in the opening summary. Add the attempted evidence source, the failure or absence reason, and the exact next action required to obtain the data.

Mark `performance` Unavailable when no measured lab or field performance evidence exists. Heuristics may be reported, but they do not make numeric performance evidence available.

Apify can make a content-based category `Verified` only when the returned raw or rendered item contains enough direct, page-specific evidence for that category and the run did not surface challenge indicators. Cheerio status and whitelisted headers may support HTTP checks, but missing redirect hops or headers remain unavailable. Web Scraper DOM output does not establish raw HTML, complete response headers, real mobile layout, or performance. Actor runtime, compute usage, and navigation timing are not Lighthouse or Core Web Vitals evidence.

When a category is `Unavailable`, describe useful static clues as **Unscored advisory** items. Do not assign Critical, High, Medium, or Low severity to those advisories, do not include them in issue counts, and do not deduct points for them. If direct evidence is sufficient to verify an actual defect, mark the category `Verified` and score it normally instead of mixing scored and unscored severity labels.

## Issue counts

Count each deduplicated negative finding once at its assigned severity. Do not count:

- correctly implemented checks;
- limitations;
- `Not applicable` categories;
- Unscored advisory items from `Unavailable` categories;
- the same root cause repeated in the summary and details.

Ensure the Executive Summary counts, Top Priorities, Detailed Findings, and score breakdown agree.

## Report path

Use the user's active project or workspace as the root. Never save a report into the installed Skill directory.

Create:

`audits/tech-seo/<host>-<path-slug>-<YYYY-MM-DD>.md`

Normalize as follows:

- lowercase the hostname and remove the scheme;
- omit query strings and fragments from the filename;
- map the root path to `home`;
- remove leading and trailing slashes from other paths;
- replace slashes, whitespace, and cross-platform unsafe filename characters with one hyphen;
- collapse repeated hyphens;
- retain the exact requested URL, including safe query context, inside the report.

Example:

`https://example.com/online-tool` becomes `audits/tech-seo/example.com-online-tool-2026-07-15.md`.

Before writing, check whether the path exists. If it exists, use:

`<host>-<path-slug>-<YYYY-MM-DD>-<HHmmss>.md`

If that also exists, append `-2`, `-3`, and so on. Never overwrite any existing report.

For batch audits, also follow `batch-audit.md`. Keep scores and evidence coverage per URL. Do not create a synthetic batch score or deduct the same template issue from one page's score more than once; each page independently receives the appropriate root-cause deduction in its own report.

## Delivery checks

- Save only the final UTF-8 Markdown report by default.
- Do not retain screenshots, raw HTML, network archives, trace files, or raw Lighthouse JSON unless the user requests them.
- Do not retain raw Apify datasets, page source, logs, screenshots, dataset access URLs, or API responses unless the user requests them; keep only the summarized evidence in the report.
- Present the complete report in the conversation and link or state the saved path.
- For a batch, present the substantive batch summary and link every complete individual report; do not flood the conversation with all full page reports unless requested.
- Place immediate recommendations beside the opening dimension scores before the detailed findings.
- If the report cannot be saved, keep the full conversational report and disclose the intended path and failure.
- Do not claim that saving the audit changed, fixed, submitted, or published anything.
