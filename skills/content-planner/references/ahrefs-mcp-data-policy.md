# Ahrefs MCP Data Policy

Use Ahrefs MCP as the sole source of keyword, ranking, competitor, and SERP facts in this skill. Keep analyst-created strategy fields clearly separate.

## Enforce source ownership

| Field or evidence | Owner |
|---|---|
| Keyword, Volume, KD, CPC, Traffic Potential, Search Intent, Parent Topic, SERP Features, SERP date | Ahrefs MCP |
| Organic keywords, ranking URL/position, Top Pages, competitors, Domain Rating, SERP Top 10 | Ahrefs MCP |
| Topic, Primary/Supporting mapping, Funnel, Content Type, Action, planned URL, Priority Score, Priority | Skill analysis |
| Product facts, ICP, business model, exclusions | User input or the target website, used only as context |
| Content Mission, hierarchy, roadmap, internal-link direction, risks | Skill analysis |

Never use web search, another SEO provider, model memory, or invented values to fill an Ahrefs-owned field. A direct read of the target website may establish product context but not keyword metrics.

## Use only the configured MCP connection

Connect to the official hosted server at `https://api.ahrefs.com/mcp/mcp` through the host application's supported MCP client. Prefer OAuth when available or a locally configured MCP-scoped key.

- Never call the hosted MCP endpoint through a custom HTTP script, bridge, `curl`, or standalone JSON-RPC client.
- Never read, echo, log, checkpoint, or write the key value.
- Never ask the user to paste a key into chat.
- Refer only to the environment-variable name `AHREFS_MCP_KEY` in setup examples.
- Keep calls read-only. Do not create or modify Ahrefs projects or lists.

See `ahrefs-mcp-setup.md` for host-specific setup.

## Discover capabilities at runtime

Inspect the callable MCP tools and their input schemas before making requests. Tool names and subscription coverage can vary. Common capability labels currently include:

- `subscription-info-limits-and-usage`
- `keywords-explorer-overview`
- `keywords-explorer-matching-terms`
- `keywords-explorer-related-terms`
- `keywords-explorer-search-suggestions`
- `site-explorer-domain-rating`
- `site-explorer-top-pages`
- `site-explorer-organic-keywords`
- `site-explorer-organic-competitors`
- `serp-overview-serp-overview`

Treat these as capability hints, not hard-coded guarantees. Use the exposed schema for `country`, `target`, `target mode`, `select`, `where`, `order`, and limits.

## Preserve metric semantics

- Use country-specific Ahrefs Volume: the estimated monthly average over the latest known 12 months.
- Set `volume_mode=average` on Site Explorer calls whenever the exposed schema supports it; its default can represent the latest month instead.
- Preserve a real returned `0`; write an unavailable metric as `N/A`.
- Treat KD as Ahrefs's 0–100 top-10 difficulty estimate, not a ranking guarantee.
- Convert Ahrefs CPC from USD cents to USD exactly once.
- Preserve all true Ahrefs intent labels when several are returned.
- Use Parent Topic as a signal, not an automatic page-clustering decision.
- Record `serp_last_update` or the closest available snapshot date.
- Label Domain Rating as an Ahrefs planning proxy, not a Google signal.

Do not sum supporting-keyword Volume or Traffic Potential in the main plan. Report the Primary Keyword's metrics and keep every supporting keyword's individual metrics in `Raw Keywords`.

## Minimize API-unit consumption

Ahrefs charges according to returned rows and selected fields, subject to plan limits and minimum request costs.

1. Call the available equivalent of `subscription-info-limits-and-usage` before research and around every 100-row batch; report the actual usage difference when returned.
2. Use `limit=100` or the exposed equivalent for collection calls.
3. Request only required fields and explain that Volume, KD, Intent, and Traffic Potential materially increase unit cost.
4. Test the connection with the free limits action when available; otherwise disclose that the minimal test may consume units.
5. Run SERP Overview selectively for ambiguous clusters, high-priority opportunities, and cannibalization decisions.
6. Reuse checkpointed results instead of repeating calls.
7. Stop before opening the next 100-row batch and ask the user whether to continue.

## Fail without contaminating evidence

| Condition | Required behavior |
|---|---|
| MCP absent or authentication fails | Stop before research and provide setup guidance. |
| Quota exhausted, 429, timeout, or tool failure | Save the current checkpoint, report the exact limitation, and stop the affected chain. |
| Required endpoint unavailable | Explain which fields or decisions cannot be supported and ask whether to create a partial version. |
| A field is null or absent for a returned keyword | Keep the keyword when relevant, write `N/A`, and apply the documented provisional scoring rule. |
| SERP data insufficient | Mark the cluster `Needs Review`; do not substitute ordinary web results. |

Never silently downgrade evidence quality. Label partial workbooks and list every material limitation in `Methodology`.

## Official references

- Ahrefs MCP introduction and authorization: https://docs.ahrefs.com/en/mcp/docs/introduction
- Ahrefs Keywords Explorer endpoints: https://docs.ahrefs.com/en/api/reference/keywords-explorer
- Ahrefs SERP Overview: https://docs.ahrefs.com/en/api/reference/serp-overview/get-serp-overview
- Ahrefs Site Explorer endpoints: https://docs.ahrefs.com/en/api/reference/site-explorer
- Ahrefs API limits and cost guidance: https://docs.ahrefs.com/en/api/docs/introduction
- Ahrefs API changelog, including removal of `offset`: https://docs.ahrefs.com/en/api/docs/changelog
