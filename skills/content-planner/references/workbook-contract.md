# Workbook Contract

Use this reference when generating the final `.xlsx`. Put the whole-site content plan first; put supporting strategy and methodology after it.

## Create one workbook per country

- Require target country and target language before research.
- Research every country independently and write a separate workbook. Never mix Volume, KD, CPC, Traffic Potential, SERPs, or priority percentiles across countries.
- Use `Volume (<country code>)` as the country-specific column header, for example `Volume (US)`.
- Save by default under `content-planner-output/<site-or-topic>-<country>-<YYYY-MM-DD>/`.
- Avoid overwriting an existing run; add a numeric suffix when needed.
- Keep the final workbook, one raw JSON checkpoint per 100 returned rows, clustered internal JSON, and a validation report in the run directory.

## Use exactly these visible sheets in this order

1. `Content Plan`
2. `Raw Keywords`
3. `Topic Map`
4. `Roadmap`
5. `Strategy Notes`
6. `Methodology`

Store long data-validation lists in hidden columns of `Methodology` when necessary; do not add a visible helper sheet.

## Content Plan columns

Use this exact order:

1. `Primary Keyword`
2. `Supporting Keywords`
3. `Topic`
4. `Funnel`
5. `Content Type`
6. `KD`
7. `Volume (<country code>)`
8. `Traffic Potential`
9. `Search Intent`
10. `CPC (USD)`
11. `Parent Topic`
12. `SERP Features`
13. `Existing/Planned URL`
14. `Action`
15. `Priority Score`
16. `Priority`

Write one planned page per row. Put the Primary Keyword's metrics in the row, join Supporting Keywords with line breaks, and retain individual supporting-term metrics in `Raw Keywords`. Do not add owner, status, publish date, or other project-management columns.

Use these controlled values:

- `Funnel`: `TOFU`, `MOFU`, `BOFU`
- `Action`: `New`, `Existing`, `Update`, `Consolidate`
- `Priority`: `P1`, `P2`, `P3`
- `Content Type`: use the exact values in `topic-funnel-and-content-types.md`

Keep Ahrefs Search Intent in its returned standard English labels. Format CPC in US dollars after converting Ahrefs cents to dollars. Keep true numeric zero as `0`; write an unavailable Ahrefs metric as `N/A` rather than zero.

## Supporting sheet contracts

### Raw Keywords

Preserve the auditable input and mapping with at least these columns:

`Keyword`, `Country`, `Language`, `Volume`, `KD`, `Traffic Potential`, `Search Intent`, `CPC (USD)`, `Parent Topic`, `SERP Features`, `Source Tool`, `Seed/Competitor`, `SERP Updated`, `Decision`, `Decision Reason`, `Mapped Primary Keyword`, `Needs Review`

Keep every returned candidate, including excluded and deferred rows. Record the Ahrefs MCP tool/source, seed or competitor path, inclusion/exclusion reason, and mapped planned page.

### Topic Map

Show the hierarchy and internal-link model with at least:

`Topic`, `Page Level`, `Primary Keyword`, `Page Role`, `Parent Page`, `Existing/Planned URL`, `Link Up To`, `Relevant Cross-Links`

Distinguish Pillar pages from Cluster pages and keep every URL consistent with `Content Plan`.

### Roadmap

Show a publishing sequence, not a staff calendar. Include at least:

`Phase`, `Sequence`, `Primary Keyword`, `Topic`, `Funnel`, `Content Type`, `Action`, `Priority Score`, `Priority`, `Dependency`, `Internal Link Targets`, `Reason`

Sequence prerequisites before dependent pages where practical. Do not add assignee, workflow status, or publication date.

### Strategy Notes

Place strategy after the plan. Cover:

- Content Marketing Mission
- ICP and primary user problems
- Pillar/Cluster structure
- Funnel distribution and content gaps
- Progression from keyword opportunities to user-journey coverage and content-brand assets
- Internal-link direction
- Roadmap rationale and dependencies
- SEO/GEO opportunities supported by Ahrefs SERP Features, including AI Overview when returned
- Repurposing ideas for formats that do not belong as separate plan rows

Do not generate article briefs, detailed outlines, or full drafts.

### Methodology

Record:

- site URL or new-site topic, project type, target country, target language, and generation timestamp
- Ahrefs-only data-source policy, MCP tools used, extraction date, returned fields, SERP dates, and checkpoint count
- clustering, SERP-overlap, content-type, priority-scoring, and missing-data rules
- unresolved `Needs Review` pairs, missing fields, partial-data limitations, and provisional scores
- workbook version and validation result

## Style and validation

- Freeze the top row, enable filters, and use a readable Excel table style on data sheets.
- Use a blue, high-contrast header; wrap long text; set practical column widths; and top-align multi-line cells.
- Apply data-validation dropdowns to Funnel, Content Type, Action, and Priority. Back them with hidden ranges in `Methodology` if inline validation would exceed Excel limits.
- Apply consistent conditional fills: distinguish TOFU/MOFU/BOFU, group Content Types by family, and show P1 in red, P2 in blue, and P3 in green.
- Keep numeric cells numeric when Ahrefs returned a value. Use an Excel-safe text value only for `N/A`.
- Avoid merged cells in sortable tables. Keep hyperlinks clickable and formulas minimal.
- Set workbook core metadata with a descriptive title, target country/language in the subject, generation details in comments, and `Span` as creator.
- Make the workbook readable in Microsoft Excel, LibreOffice, and common spreadsheet importers.

## Validate before delivery

- Confirm all six visible sheets exist in the required order and `Content Plan` is active.
- Confirm every accepted raw keyword maps to one planned page and every planned page has one Primary Keyword.
- Confirm controlled fields contain only allowed values and all planned URLs are unique or deliberately consolidated.
- Confirm missing metrics remain `N/A`, CPC conversion is correct, priority scores match the deterministic rubric, and country data is not mixed.
- Confirm filters, frozen rows, validation, conditional formatting, links, and workbook reopening work.
- Run the bundled validator with `--mark-valid`; require its second validation pass, write the JSON outcome to the run directory, and confirm `Methodology` contains `Validation Result = Valid`.

## Present the result

Lead with the workbook link, then report total returned keywords, planned pages, Topics, P1/P2/P3 distribution, TOFU/MOFU/BOFU distribution, important opportunities, and risks. Preview no more than the first 10 planned rows in the conversation. Keep the complete plan in the workbook.
