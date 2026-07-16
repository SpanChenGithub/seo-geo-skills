# Query Fan-Out Taxonomy

Use two independent classification layers. Assign one primary value from each layer to every query. Add a journey stage only when it improves interpretation.

This taxonomy adapts the patterns described by [Ahrefs](https://ahrefs.com/blog/query-fan-out/) and the workflow in [Zyppy Signal](https://signal.zyppy.com/p/fan-out-framework). Treat it as an analysis framework, not a description of any provider's private implementation.

## Layer 1: construction form

| Value | Use when the query | Example for `project management software` |
|---|---|---|
| `related_topic` | Adds a closely connected subject needed for context | `project planning workflow templates` |
| `implicit_question` | Makes an unstated concern or criterion explicit | `does project management software reduce missed deadlines` |
| `comparison` | Compares entities, categories, or approaches | `asana vs monday for small teams` |
| `recency` | Requires current, dated, or recently changed information | `best project management software 2026` |
| `reformulation` | Restates the same information need without adding a new constraint | `tools for managing team projects` |
| `contextual_variation` | Changes locale, persona, industry, device, budget, or another meaningful context | `project management software for construction teams` |
| `next_step` | Covers an action that normally follows the seed request | `how to migrate projects from spreadsheets` |

### Construction rules

- Use `reformulation` only when the expected answer remains substantially the same.
- Do not label a query `recency` merely because the current year appears; the answer must genuinely depend on current information.
- Keep a contextual variation only when the modifier changes sources, evaluation criteria, or the answer.
- A comparison may also be a decision-stage query, but its primary construction form remains `comparison`.
- Do not force all seven forms into every run.

## Layer 2: information-gap function

| Value | Information gap closed | Typical query angle |
|---|---|---|
| `disambiguation` | Resolves an ambiguous term, entity, scope, or interpretation | definition, entity identity, category boundary |
| `entity_attribute` | Retrieves features, specifications, compatibility, availability, or properties | capabilities, formats, integrations, requirements |
| `journey_stage` | Supports a distinct step in learning, evaluating, adopting, or using | setup, migration, implementation, troubleshooting |
| `trust_signal` | Seeks external validation, evidence, experience, authority, or policy | reviews, research, credentials, privacy, reputation |
| `comparison_criteria` | Retrieves a decision dimension used to compare choices | price, accuracy, speed, limitations, total cost |
| `action_and_risk` | Tests feasibility, consequences, restrictions, safety, legal, or operational risk | how-to, failure modes, rights, refunds, compliance |

### Information-gap rules

- Assign the gap the query primarily closes, not every theme it mentions.
- Use `trust_signal` for evidence-seeking, not for a product's own unsupported marketing claim.
- Use `action_and_risk` when the answer changes a decision or prevents harm; use `journey_stage` for ordinary progression through a task.
- Do not treat a citation source or related-search suggestion as proof that the gap matters to every platform.

## Optional journey stage

Use one of:

- `awareness`
- `education`
- `evaluation`
- `decision`
- `implementation`
- `troubleshooting`

Set the value to `null` when no stage is useful. Do not manufacture a funnel stage for a purely factual or navigational query.

## Natural-query quality rules

- Write something a retrieval system could actually search.
- Keep the query tightly connected to the original information need.
- Mix short, mid-tail, and long-tail forms only when they add distinct retrieval value.
- Avoid answer fragments, article headings, editorial commands, keyword stuffing, and repetitive paraphrases.
- Preserve important negation, dates, regions, audiences, products, platforms, prices, and risk qualifiers.
- Avoid unsupported `best`, `free`, `safe`, `legal`, `latest`, or superlative wording unless the seed and intent justify those searches.

## Grounding versus fan-out

A fan-out query expands or decomposes the user's information need. A grounding query may instead verify a claim that the model already intends to make. One query can serve both functions, but the report must not assume that every observed search-tool query is a deliberate fan-out branch. Classify its role from the query and surrounding request, and disclose uncertainty.
