# Optional URL Coverage Analysis

Use this workflow only when the user supplies a URL, source file, or pasted page content.

## Establish page evidence

Read the accessible page with the host's browser or URL-fetch capability. Inspect:

- Title and Meta Description;
- H1–H3 headings;
- visible body copy;
- FAQs;
- tables, lists, examples, and product attributes;
- visible authorship, credentials, policies, reviews, and trust evidence;
- important internal and external links;
- structured data, while keeping it distinct from visible content.

Do not send arbitrary page URLs to the credential-bearing API collector. If access fails, ask for pasted content. Continue the query-only analysis when possible.

## Coverage labels

| Label | Meaning |
|---|---|
| `covered` | The page directly and sufficiently answers the cluster's information need. |
| `partial` | The page mentions the topic but omits material detail, evidence, constraints, or next steps. |
| `missing` | The cluster fits the page's intent but has no meaningful coverage. |
| `separate_page_candidate` | The cluster represents a distinct intent, audience, journey stage, or format that should not be forced into the page. |
| `off_page_signal` | The need depends on third-party reviews, forums, external validation, or another source the site cannot satisfy alone. |
| `not_assessable` | Page access or evidence is insufficient for a responsible judgment. |

For each assessed cluster return:

- cluster ID and label;
- representative original queries;
- coverage label;
- page evidence and location;
- missing information;
- recommendation: `update_existing_page`, `create_new_page`, `off_page_action`, `no_action`, or `manual_review`.

Set `page_coverage.url` to the supplied URL. For pasted-content-only or source-file analysis without a URL, set it to `null` and keep `input.page_content_provided: true`.

## Decision rules

- Recommend an update only when the cluster shares the page's main intent and audience.
- Recommend a separate page when satisfying the cluster would change the page's primary job or content format.
- Use `off_page_signal` for independent reviews, community experiences, directories, citations, or authority signals that on-page copy cannot credibly replace.
- Do not recommend thin pages for every fan-out query.
- Do not expand a page into an unfocused omnibus merely to increase cluster count.
- Align proposed coverage with a real user need, original evidence, and the page's ability to rank or be cited.

## Optional coverage score

Calculate a coverage score only when the user asks for one:

```text
covered = 1
partial = 0.5
missing = 0
```

Exclude `separate_page_candidate`, `off_page_signal`, and `not_assessable` from the denominator, then use the unweighted mean of the remaining values. Keep cluster priority as a separate editorial judgment rather than hiding it inside this score. Call the result an editorial coverage heuristic, not a platform score.
