# Internal JSON Artifact Contract

Use this contract between Ahrefs analysis and deterministic workbook generation. Save UTF-8 JSON with `schema_version: "1.0"`. Use `null` for a missing Ahrefs metric; use numeric `0` only when Ahrefs returned zero. The workbook builder renders missing metrics as `N/A`.

## Top-level object

```json
{
  "schema_version": "1.0",
  "metadata": {},
  "content_plan": [],
  "raw_keywords": [],
  "topic_map": [],
  "roadmap": [],
  "strategy_notes": [],
  "methodology": []
}
```

Do not add credentials, authorization headers, account identifiers, or unrelated Ahrefs rows.

## Metadata

Require:

| Key | Type | Rule |
|---|---|---|
| `project_name` | string | Human-readable site or topic name. |
| `country` | object | `{ "name": "United States", "code": "US", "volume_label": "US" }`; one market only. |
| `language` | object | `{ "name": "English", "code": "en" }`; one language only. |
| `data_source` | string | Must be exactly `Ahrefs MCP`. |
| `ahrefs_tools_used` | array of strings | Non-empty list of callable MCP tools actually used. |
| `frontier_items` | array of objects | Non-empty auditable request-partition log; schema below. |

Optional metadata may include `project_type`, `site_url`, `generated_at`, `data_date`, `run_id`, `checkpoint_count`, `validation_result`, `data_status`, `frontier_status`, `ahrefs_units_before`, `ahrefs_units_after`, and `site_domain_rating`. Use `Existing` or `New` for `project_type`; a site URL is required by the workflow for an existing site. Do not infer unavailable values. Put the Content Mission and limitations in Strategy Notes or Methodology rather than undocumented metadata keys.

Each `frontier_items` object requires `frontier_id`, `source_tool`, `target`, and `status`. The source tool must be present in `ahrefs_tools_used`; status is `Queued`, `Completed`, `Exhausted`, `Failed`, or `Partial`. Record `mode`, tool-supported `filters`, `selected_fields`, `returned_rows`, `new_unique_rows`, `duplicate_rows`, `included_rows`, `excluded_rows`, `units_before`, `units_after`, and `collected_at` whenever available. Serialize filters as a JSON object or a stable string. Use a stable unique `frontier_id` so a resumed run cannot replay the same request partition silently.

## Content plan rows

Use one row per planned page:

```json
{
  "primary_keyword": "ai music generator",
  "supporting_keywords": ["music generator ai"],
  "topic": "AI Music Creation",
  "funnel": "BOFU",
  "content_type": "Tool",
  "kd": 42,
  "volume": 12000,
  "traffic_potential": 31000,
  "search_intent": ["informational", "transactional"],
  "cpc_usd": 1.25,
  "parent_topic": "ai music generator",
  "serp_features": ["ai_overview", "video"],
  "url": "https://example.com/ai-music-generator",
  "action": "Existing",
  "commercial_relevance_score": 30,
  "strategic_value_score": 10,
  "priority_score": 86,
  "priority": "P1",
  "score_is_provisional": false
}
```

The numbers in this snippet illustrate structure only; actual keyword metrics must come from Ahrefs MCP. Assign `commercial_relevance_score` and `strategic_value_score` from the fixed rubrics, then run `scripts/score_content_plan.py` to populate `priority_score`, `priority`, `score_is_provisional`, and `score_breakdown`. Use only the enums defined in `topic-funnel-and-content-types.md` and `workbook-contract.md`. Sort only after the complete accepted set is scored.

## Raw keyword rows

Preserve every returned candidate and its decision. `source_tool` is mandatory and may be one tool string or an array when duplicate-source provenance was merged; every named tool must appear in `metadata.ahrefs_tools_used` and in at least one `Completed`, `Partial`, or `Exhausted` frontier item:

```json
{
  "keyword": "ai music generator",
  "country": "US",
  "language": "English",
  "volume": 12000,
  "kd": 42,
  "traffic_potential": 31000,
  "search_intent": ["informational", "transactional"],
  "cpc_usd": 1.25,
  "parent_topic": "ai music generator",
  "serp_features": ["ai_overview", "video"],
  "source_tool": "keywords-explorer-matching-terms",
  "seed_or_competitor": "ai music",
  "serp_updated": "2026-07-01T00:00:00Z",
  "decision": "Include",
  "decision_reason": "Direct product intent",
  "mapped_primary_keyword": "ai music generator",
  "needs_review": false
}
```

Allow only `Include`, `Exclude`, and `Defer`. Merge duplicate-source provenance into the retained normalized row rather than adding a duplicate raw row. Require `mapped_primary_keyword` for every `Include` row; leave it empty or null for excluded rows.

## Topic Map rows

Use:

`topic`, `page_level`, `primary_keyword`, `page_role`, `parent_page`, `url`, `link_up_to`, `relevant_cross_links`

Represent multi-value link fields as arrays.

## Roadmap rows

Use:

`phase`, `sequence`, `primary_keyword`, `topic`, `funnel`, `content_type`, `action`, `priority_score`, `priority`, `dependency`, `internal_link_targets`, `reason`

Keep `sequence` numeric. Represent dependency and link targets as arrays when several values apply.

## Strategy Notes and Methodology

Use ordered `Strategy Notes` rows with `section`, `item`, and `details` strings. Use ordered `Methodology` rows with `field`, `value`, and `notes` strings. Keep one logical point per row so the workbook remains readable.

`Strategy Notes` must cover Content Mission, ICP, Pillar/Cluster structure, funnel gaps, user journey, content-brand progression, internal linking, roadmap rationale, SEO/GEO SERP opportunities, risks, and repurposing.

`Methodology` must cover project/country/language, Ahrefs source policy, tools and dates, 100-row checkpoints, clustering rules, scoring, missing data, `Needs Review`, frontier status, schema version, and validation status.

## Formula and secret safety

- Prefix strings beginning with `=`, `+`, `-`, or `@` with an apostrophe before writing them to cells.
- Keep URLs as values or safe hyperlinks, never as dynamic formulas.
- Reject keys or values that appear to contain passwords, API keys, Bearer headers, or authorization fields.
- Keep checkpoint artifacts and final JSON outside the installed skill directory.
- Checkpoints retain the normalized frontier log, a continuously increasing `checkpoint_index`, immutable row ranges, and per-range Include/Exclude/Defer plus source-tool counts.
- Resume only when schema and checkpoint versions, project identity, run ID, site, country, language, data source, retained frontier identity, tool identity, prior row ranges, and batch statistics match. Refuse to attach another project's checkpoint even when its country and language are the same.
- Treat `frontier_id`, source tool, target, mode, filters, and selected fields as immutable request identity. Allow status to move forward from `Queued` to an executed state and allow its counts/timestamps to be populated; reject identity changes or status regression.
