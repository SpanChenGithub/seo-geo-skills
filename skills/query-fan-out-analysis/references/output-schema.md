# Report Structure

Build a valid internal JSON report before rendering Markdown. The report contract is schema `1.2`; collector request envelopes remain schema `1.0`. Use [report-schema.json](report-schema.json) as the machine-readable contract and `scripts/validate_report.py` for semantic checks that JSON Schema alone cannot enforce.

## Markdown display template

```markdown
# Query Fan-Out Analysis

## Method
- Seed:
- Language / locale:
- Context / persona:
- Providers and exact models:
- Runs per provider:
- Observed, provider-synthetic, and heuristic modes:
- Live research:
- Assumptions:
- Failures or fallbacks:

## Intent and information gaps
- Primary intent:
- Secondary intents:
- Ambiguities:
- Important attributes:
- Journey, trust, action, and risk needs:

## External search signals
| Type | Signal | Source | Retrieved | Language / locale |

## OpenAI / ChatGPT-style API
| Cluster | Representative original query | Form | Information gap | Runs | Source |

## Gemini API
...

## Google AI Mode simulation
...

## Claude API
...

## Perplexity API
...

## Cross-model consensus
| Cluster | Participating platforms | Coverage | Why it matters |

## Platform-specific angles
| Platform | Cluster | Evidence level | Interpretation |

## Coverage matrix
| Cluster | OpenAI | Gemini | Google AI Mode | Claude | Perplexity |

## Page coverage
| Cluster | Coverage | Page evidence | Recommendation |

## Limitations

## Recommended page topics for SEO/GEO
| Rank | Priority | Recommended topic | Action | What to cover | Why it matters for SEO/GEO | Suggested format |
```

Omit the external-signal section when no current external evidence was used. Omit the page-coverage section when no URL or page content was provided. Preserve every observed query verbatim; use a separate translation column only when necessary.

Always keep `Recommended page topics for SEO/GEO` as the final section. When no URL was supplied, introduce it as a proposed content brief rather than an audit of missing content. When recommendations are unavailable, show the validated reason instead of a table.

## Required JSON concepts

The report contains:

- `input`: seed, detected language, locale, optional context, and optional URL;
- `intent_analysis`: primary intent, secondary intents, ambiguities, important attributes, and journey/trust/action/risk needs;
- `configuration`: requested and participating platforms, run target, query target, time, `api_first` execution policy, network/paid-API permissions, expanded-scope authorization, and live-research status;
- `external_search_signals`: separately sourced SERP, PAA, related-search, trend, or current-fact evidence; use an empty array when none was used;
- `platforms`: exact requested/actual model data, execution mode, run records, query provenance, and platform clusters;
- `cross_platform_clusters`: semantic consensus and provider-specific clusters;
- `coverage_matrix`: explicit platform presence for each cross-platform cluster;
- `page_coverage`: optional assessment of a URL or supplied page content; its `url` is `null` for pasted-content-only analysis;
- `recommended_page_topics`: a validated, prioritized set of grouped topics for the primary page, separate supporting pages, or off-page evidence;
- `assumptions`, `limitations`, and `failures`;
- `provenance`: persistence and key-safety declarations.

## Recommended-page-topic fields

`recommended_page_topics` includes:

- `status`: `available` or `not_available`;
- `basis`: `fanout_only` or `fanout_and_page_evidence`;
- `unavailable_reason`: `null` for an available list, otherwise a non-empty explanation;
- `items`: one to ten topic recommendations when available, otherwise an empty array.

Each topic item includes:

- contiguous `rank`, beginning at 1;
- unique `topic_id`;
- natural-language `label`;
- `priority`: `P0`, `P1`, or `P2`;
- `action`: `include_on_page`, `add_to_page`, `expand_on_page`, `retain_on_page`, `separate_page_candidate`, or `off_page_evidence`;
- one or more valid `supporting_cross_cluster_ids`;
- zero or more valid `supporting_signal_ids`;
- concrete `coverage_guidance` describing what the page should answer;
- an SEO/GEO `rationale` grounded in those clusters and available evidence;
- a concrete `suggested_format` such as a definition, workflow, comparison table, FAQ, policy summary, or evidence block.

Every `P0` item must use an on-page action. Assign each cross-cluster to at most one recommendation so the final list groups rather than repeats information needs. See [seo-geo-topic-recommendations.md](seo-geo-topic-recommendations.md) for selection rules.

## Per-query fields

Each query record includes:

- stable `query_id`;
- original `text`;
- deterministic `normalized_text`;
- `source_type`: `observed_tool_query`, `synthetic_provider_query`, or `heuristic_simulation`;
- one `form` from the taxonomy;
- one `information_gap` from the taxonomy;
- optional journey stage;
- language;
- optional translation, while retaining the original text and language;
- platform cluster ID;
- run index;
- `trace_path` for observed queries, otherwise `null`.

An observed query without a provider-valid structured trace path is invalid. A synthetic or heuristic query with a trace path is invalid. `observed_queries_preserved_verbatim` applies to retained observed records; unsafe or invalid values are dropped whole and recorded in failures or limitations rather than rewritten.

Each external signal includes a unique ID, signal type, text, source URL and title when available, retrieval time when available, language, and locale. `configuration.external_search_signals_used` must equal whether this array is non-empty.

Each run records `api_attempted` and `fallback_reason` in addition to its query provenance. An observed or provider-synthetic query requires `api_attempted: true`. A heuristic simulation may have `api_attempted: false` when no provider call was possible, or `true` when it follows a failed/empty API attempt; its attempt count must preserve that history. Any run containing synthetic or heuristic queries must state why observed API evidence was not used. `run.attempts` counts total HTTP attempts for the observed request plus any same-provider synthetic fallback and must be zero only when no API was attempted. The maximum is 6 for non-Claude providers and 12 for Claude because one bounded provider-synthetic fallback may follow the observed request and Claude's `pause_turn` continuations can each retry.

Every provider-specific `run.failure` must appear once in the top-level `failures` list with the same provider, run index, and code; do not add orphan provider failures. A global failure may use `null` for both provider and run index. Any report containing a nested or top-level failure has `status: partial`.

## CSV export safety

When the user requests CSV, use Python's `csv` module. Prefix cells beginning with `=`, `+`, `-`, or `@` with a single quote before writing so spreadsheet software cannot interpret query text as a formula. Do not include credentials, raw headers, or raw response bodies.

The CSV export is query-row oriented but emits one `run_without_query` metadata row for a failed or empty run. Every row retains API/network/scope policy, run status, API-attempt, fallback, failure, execution-mode, and observability fields. Use validated JSON when the user needs the complete many-to-one topic-recommendation structure.

Resolve `SKILL_DIR` to the directory containing `SKILL.md`. Export a validated report from stdin to stdout by default, or to an explicitly requested file:

```bash
python3 "$SKILL_DIR/scripts/export_report_csv.py" -
python3 "$SKILL_DIR/scripts/export_report_csv.py" - --output fan-out.csv
```
