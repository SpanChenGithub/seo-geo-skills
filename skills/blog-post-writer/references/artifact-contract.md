# Article Package Contract

## Contents

- [Required files](#required-files)
- [Cross-file rules](#cross-file-rules)
- [Reference skeleton](#reference-skeleton)

Use UTF-8, valid JSON, ISO 8601 dates, absolute source URLs, and stable source IDs. Keep every artifact free of credentials, credential-shaped strings, full competitor pages, and private reasoning. The package is an audit trail, not a content warehouse.

For chat-only delivery, maintain the same logical records in memory and show the important research and quality limitations. The validator applies to file-based packages.

## Required files

### `brief.json`

Record:

- `schema_version`;
- `primary_keyword`;
- `language`;
- `region`: `{ "value": null, "status": "unspecified" }` when the user supplies no market, or `{ "value": "...", "status": "specified" }`;
- `audience` and `page_context`, using `null` when unknown;
- `optional_inputs` object plus `assumptions` and `open_risks` arrays;
- `output_mode`: `files` or `chat_only`.

### `serp-research.json`

Record:

- `schema_version`, `query`, `searched_at`, `language`, and the same `region` object;
- `queries`: one or more objects with `text`, `language`, and `purpose`;
- `search_environment`: a concise, non-sensitive description of the locale or host search environment actually used;
- `search_method`: `direct_search` or `user_supplied`;
- `result_count` and `results` with `rank`, `title`, `url`, a short `snippet`, and `observed_at`; add `page_type`, `intent`, and `topics` when known;
- `paa`, `related_searches`, and `communities` as arrays;
- `search_intent`, `format_recommendation`, and `limitations`;
- `reference_word_count`: a justified range such as `{ "min": 1800, "max": 2600, "rationale": "..." }`, not a ranking formula.

Use only ranks actually observed. A usable partial SERP must disclose missing data. If live SERP evidence is unavailable, stop formal generation and do not create a falsely complete package.

### `sources.json`

Use a top-level `sources` array. Each source includes:

- `id`, `title`, `url`, `publisher`, `source_type`, and `language`;
- `published_at` and `retrieved_at`, using `null` where unavailable;
- `supports`: one or more concise claim or section IDs;
- `notes`: a short evidence note, not copied page text.

Use `source_type` values that expose evidence quality, such as `primary`, `independent_expert`, `reputable_secondary`, `community`, `competitor_context`, or `internal`. Include every publishable Markdown URL in this manifest, including verified internal links, so the package has a complete link trail.

### `outline.json`

Record `primary_keyword`, `language`, `region`, `working_title`, `slug`, `meta_description`, `article_type`, `search_intent`, `sections`, `information_gain_plan`, `internal_link_plan`, and `faq_plan`.

Every section includes `heading`, `level`, `purpose`, `evidence_required`, and `sources`. A material factual section sets `evidence_required` to `true` and supplies at least one valid source ID. Add questions, claims to verify, examples, media, and reference length where useful.

Include:

```json
{
  "approval": {
    "status": "approved",
    "approved_at": "2026-01-15T10:30:00Z"
  }
}
```

Do not label an outline approved without an explicit user instruction.

### `draft.md`

Keep the approved full-article draft or the last pre-polish version. It may be omitted only when the user requests chat-only delivery or explicitly opts out of intermediate files.

### `article.md`

Include one H1, a coherent heading hierarchy, natural inline links at claim level, and a concise final `Sources` section containing only sources actually used. Do not leave `[NEEDS SOURCE]`, TODOs, invented URLs, or internal drafting notes.

### `meta.json`

Record exactly one `seo_title` string, one `meta_description` string, one `slug`, one `summary`, `language`, and the `region` object. Do not store alternatives in this file unless the user explicitly requested them.

### `media-plan.md`

Use one Markdown table with these columns:

| Asset ID | Placement | Purpose and what to show | Capture or annotation notes | Filename or real URL | Source or creation method | Alt text | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |

Include at least one substantive row. Use `real`, `generated`, `pending`, `omitted`, or `complete as text` for status. When no visual is useful, add one honest `omitted` row and explain why; do not submit an empty plan. Do not claim that a screenshot or original image exists before it does.

### `quality-report.json`

Record:

- `status`: `ready_for_final_approval`, `final_approved`, or `needs_revision`;
- `checked_at`;
- `factual_claims_checked`, `source_links_checked`, `search_intent_satisfied`, and `originality_reviewed` booleans;
- `information_gain_summary`;
- `limitations` and `remaining_risks` arrays;
- `structured_data_decision`;
- `validator`: the latest passing command result as `{ "status": "passed", "version": "1.0.0", "errors": 0, "warnings": ["warning-code-if-any"] }`;
- `approval`: `{ "status": "pending", "approved_at": null }` before final approval, then `{ "status": "approved", "approved_at": "<ISO 8601 timestamp>" }` after explicit approval.

`needs_revision` is a blocking state and must not pass validation. `ready_for_final_approval` pairs with pending approval; `final_approved` pairs with approved approval and a real timestamp.

For a new file package, run the validator once to expose all content errors, record the resulting version and warning codes after errors reach zero, then rerun. The delivery pass requires a non-empty current validator record; `{}` and `pending` are not valid final records.

Boolean checks assert that a review occurred, not that software proved truth or originality.

### `structured-data.json`

Normally store valid JSON-LD with an `Article`, `BlogPosting`, or more specific applicable article type. Prefer `@graph` when combining types. Values must match visible article content.

Add `FAQPage` or `HowTo` only when the visible content genuinely qualifies and a known target consumer supports the intended semantic use. Google's FAQ and HowTo rich-result documentation is removed or deprecated as of July 2026, so never add either type as a current Google rich-result tactic. A page containing a few questions is not automatically an FAQ page, and an article containing tips is not automatically a step-by-step how-to.

If no article node can be represented honestly or the requested target does not accept structured data, keep the required audit file but use an omission record instead of fabricated JSON-LD:

```json
{
  "status": "omitted",
  "reason": "No verified public URL, author, publisher, or deployment target was supplied.",
  "eligibility_checked_at": "2026-01-15T10:20:00Z"
}
```

If a non-article schema would be misleading or incomplete, omit that type and explain the decision in the quality report.

## Cross-file rules

- Use parseable ISO 8601 dates and timestamps throughout.
- Keep `primary_keyword`, language, and region consistent across brief, SERP, outline, and metadata.
- Keep all source IDs unique and resolve every outline source reference.
- Put every publishable Markdown URL in `sources.json`; never use an unmanifested external or internal link.
- Keep exactly one final title, meta description, and slug.
- Do not expose absolute local paths in the article, quality report, or validator output.
- A passing pre-approval package may be `ready_for_final_approval`; after explicit approval, update it to `final_approved` and validate again.

## Reference skeleton

```json
{
  "brief": {
    "schema_version": "1.0",
    "primary_keyword": "example keyword",
    "language": "en",
    "region": {"value": null, "status": "unspecified"},
    "output_mode": "files"
  },
  "serp": {
    "query": "example keyword",
    "searched_at": "2026-01-15T09:40:00Z",
    "queries": [{"text": "example keyword", "language": "en", "purpose": "primary SERP"}],
    "search_environment": "Host search environment; exact region unavailable",
    "search_method": "direct_search",
    "result_count": 8,
    "results": [{"rank": 1, "title": "Example", "url": "https://example.org/page", "snippet": "Short summary.", "observed_at": "2026-01-15T09:40:00Z"}]
  },
  "source": {
    "id": "s1",
    "title": "Example source",
    "url": "https://example.org/page",
    "source_type": "primary",
    "language": "en",
    "retrieved_at": "2026-01-15T09:45:00Z",
    "supports": ["claim-1"]
  }
}
```

The skeleton illustrates field shapes only; store each object in its named file rather than combining the package into one JSON document.
