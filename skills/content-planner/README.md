# Content Planner

> Build country-specific, whole-site SEO/GEO strategies and validated Excel content plans for SaaS, online tools, and content sites using Ahrefs MCP evidence.

## English Guide

### Core capabilities

- Collect keyword, demand, difficulty, CPC, intent, Parent Topic, competitor, and SERP evidence through Ahrefs MCP.
- Build keyword universes, topic clusters, pillar structures, funnels, internal-link directions, and publishing roadmaps.
- Consolidate same-intent terms into one planned indexable page and flag ambiguous clustering decisions.
- Map pages to TOFU, MOFU, BOFU, content type, existing-site action, and a deterministic P1/P2/P3 priority.
- Generate a separate, styled, validated `.xlsx` workbook for every country.

### When to use

Use it for whole-site planning, keyword discovery, content and competitor gaps, page consolidation, topic clusters, funnel balance, internal linking, priority scoring, and publishing sequence.

### Inputs

**Required:** project type, target language, target country or market, website theme or product description, and a website URL for an existing-site project.

**Optional:** ICP, business model, conversion goal, seed keywords, competitors, exclusions, content capacity, and content-type constraints.

### Installation and invocation

Clone the repository, then copy the complete `skills/content-planner` directory to the location shown above. Invoke it with `$content-planner` in Codex or `/content-planner` in Claude Code and Cursor.

Example:

```text
$content-planner New site. Language: English. Market: Canada. Product: an online subtitle editor for creators.
```

### Output

The primary deliverable is one validated Excel workbook per country, with `Content Plan`, `Raw Keywords`, `Topic Map`, `Roadmap`, `Strategy Notes`, and `Methodology` sheets. Versioned JSON, resumable checkpoints, and a validation report provide the audit trail.

### Dependencies, network access, and credential safety

Ahrefs MCP is mandatory and is the exclusive source for SEO metrics and SERP evidence. Use OAuth where possible or configure `AHREFS_MCP_KEY` locally without revealing its value. Python 3 and `openpyxl` are required for workbook generation and validation. Never commit credentials or local environment files.

### Limitations

The Skill cannot replace missing Ahrefs evidence with web search or model estimates, pauses after each 100 newly persisted keyword rows, separates every country into its own research run, does not claim absolute keyword exhaustiveness, and does not write articles or modify the target site.

Author: Span · License: MIT
