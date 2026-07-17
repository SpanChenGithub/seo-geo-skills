# Query Fan-Out Analysis

> Map the likely subqueries behind a keyword or prompt across AI search workflows while keeping observed API traces, provider-generated candidates, and heuristic simulations explicitly separate.

## English Guide

### Core capabilities

- Compare likely fan-outs across OpenAI/ChatGPT-style API, Gemini API, Google AI Mode simulation, Claude API, and Perplexity API.
- Run repeated independent analyses and calculate within-provider recurrence and cross-model coverage.
- Preserve exact structured API search traces as `observed_tool_query` and keep provider-generated and host-simulated candidates separately labeled.
- Classify, normalize, deduplicate, cluster, and prioritize query families.
- Add current SERP, PAA, and related-search signals without mislabeling them as provider queries.
- Assess optional URL coverage and finish with prioritized SEO/GEO page-topic recommendations.

### When to use

Use it to understand how AI search may decompose a request, compare platform angles, discover content gaps, or plan topics, FAQs, comparisons, workflows, trust signals, and supporting pages.

### Inputs

**Required:** `seed_input`, either a keyword or a complete prompt.

**Optional:** language, locale, location, audience or persona, brand or business context, freshness, answer type, URL or pasted page content, providers, models, run count, query target, and execution mode.

### Installation and invocation

Clone the repository, then copy the complete `skills/query-fan-out-analysis` directory to the location shown above. Invoke it with `$query-fan-out-analysis` in Codex or `/query-fan-out-analysis` in Claude Code and Cursor.

Example:

```text
$query-fan-out-analysis Analyze "best accounting software for freelancers" and recommend the topics a landing page should cover.
```

### Output

The default output is a concise Markdown report covering method, intent, evidence provenance, provider clusters, recurrence, cross-model coverage, coverage matrix, optional page coverage, limitations, and prioritized SEO/GEO topics. Validated JSON or formula-safe CSV is available on request.

### Dependencies, network access, and credential safety

The default is API-first hybrid execution. Available provider credentials can trigger ordinary default-scope API calls and provider charges; request simulated-only, no-network, or no-paid-API mode when needed. Python 3 supports collection and validation. Keep provider credentials only in local environment variables and never paste or commit their values.

### Limitations

The Skill does not expose hidden reasoning, does not reproduce consumer-product behavior, treats Google AI Mode as simulation, and does not interpret recurrence as volume or probability. No query set can guarantee ranking or AI citation.

Author: Span · License: MIT
