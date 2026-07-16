# Keyword Discovery and 100-Row Collection

Use this reference to build a broad, auditable keyword frontier without pretending that Ahrefs endpoints support pagination they do not expose.

## Build the discovery frontier

Represent every collection task as a stable frontier item:

```text
source capability + country + target/seed + mode + filters + selected fields
```

Hash or serialize that tuple to prevent the same request from being issued twice. Start with the smallest useful set and expand only from newly validated topics.

### Existing site

Use available Ahrefs MCP capabilities for:

1. Domain Rating for planning context.
2. Top Pages and Organic Keywords for current coverage.
3. Organic Competitors for competitor discovery.
4. Competitor Organic Keywords to derive gaps against the target.
5. Keywords Explorer ideas for important existing topics and uncovered competitor themes.

Keep domain, subdomain, prefix, and exact-URL modes distinct. Record the mode on every request and never widen it silently.

### New site

1. Generate a small set of exploratory seed phrases from the product description, ICP, and conversion goal.
2. Validate seeds through Ahrefs Keywords Overview.
3. Expand only validated or clearly relevant seeds through Matching Terms, question terms, Related Terms, and Search Suggestions.
4. Discover likely competitors from Ahrefs SERP or Organic Competitors evidence when the available tool supports the required target.

An exploratory model seed is not an Ahrefs keyword row and must not enter the final dataset unless Ahrefs returns it.

## Request only needed fields

For keyword-idea and overview calls, request only the available equivalents of:

`keyword`, `volume`, `difficulty`, `cpc`, `intents`, `parent_topic`, `traffic_potential`, `serp_features`, `serp_last_update`

For existing-site and competitor calls, add only fields needed for the current task, such as ranking URL, position, traffic, target mode, Domain Rating, or top keyword. Request a maximum of 100 rows per collection call.

## Persist and pause every 100 rows

Count newly persisted raw Ahrefs keyword rows, not the number of planned pages. Deduplicate before increasing the cumulative unique count, but record duplicate-source provenance on the retained row.

After each group of 100 newly persisted rows:

1. Write non-overwriting `raw-keywords-<START>-<END>.json` files in the run directory without credentials or raw authorization headers; the bundled checkpoint writer uses six-digit row ranges such as `raw-keywords-000001-000100.json`.
2. Record batch ID, request frontier items, country, language, timestamp, source tools, row counts, and cumulative counts.
3. Report returned rows, new unique rows, duplicates, relevant/excluded counts, a concise Topic distribution, and Ahrefs API-unit usage before/after when the limits action returns it.
4. Ask the user whether to continue.
5. Do not make the next keyword-data request until the user answers.

If one source returns fewer than 100 rows, keep those rows in the in-progress artifact and continue through the remaining approved frontier. Write an immutable partial checkpoint only when the user stops, the frontier ends, or collection fails. Ask the continuation question when cumulative newly persisted rows reach each 100-row boundary or before opening another material expansion branch. The checkpoint writer validates any existing contiguous prefix and appends only new row ranges, so a later resume never overwrites the retained partial batch.

## Continue without fake offsets

Ahrefs removed `offset` from its API endpoints. Inspect the current MCP schema for a cursor or another explicit continuation mechanism and use it only when actually present.

When no cursor or offset exists:

- never rerun the same first-page request and call it a new page;
- expand from uncovered validated seeds, question mode, related terms, suggestions, competitors, or Topics;
- use non-overlapping tool-supported filters only when their semantics are understood;
- deduplicate every result across all checkpoints;
- record the exact frontier coverage and limitations.

Do not claim literal exhaustiveness. Describe the result as complete for the user-approved Ahrefs frontier, accessible plan limits, country, language, and collection date.

## Normalize and deduplicate

Create a comparison key with Unicode NFKC normalization, whitespace collapse, trim, and case folding. Preserve the original Ahrefs keyword spelling for display.

Treat two rows as the same keyword only inside the same country and language. Merge source provenance without overwriting non-missing Ahrefs fields. If two calls return conflicting non-missing values, retain the newest Ahrefs timestamp when available and record the conflict in Methodology.

Do not deduplicate distinct intents merely because strings are similar. String deduplication precedes page clustering; it does not replace SERP-based clustering.

## Filter by language and relevance

- Keep the user-specified language as a hard planning boundary.
- Use an Ahrefs language field when returned. Otherwise classify the keyword text conservatively and flag uncertain cases.
- Preserve excluded, wrong-language, and deferred rows in `Raw Keywords` with a decision reason. Merge duplicate-source provenance into the retained normalized keyword row rather than emitting a second duplicate string.
- Retain relevant Volume-0 terms, narrow BOFU use cases, and competitor alternative/comparison terms.
- Exclude unrelated high-volume terms rather than distorting the content mission.

## Stop or resume safely

Stop collection when the user says stop, the frontier is exhausted, or Ahrefs becomes unavailable. Preserve the latest checkpoint. A later run must validate matching schema/checkpoint versions, project and run identity, site, country, language, data source, prior rows, tools, and immutable frontier items before resuming.

Treat two consecutive completed expansion branches that add no new relevant Topic and fewer than 5% new relevant keywords as saturation. Report that signal and ask whether to stop; do not stop silently.
