# Clustering and Page Mapping

Use this reference when turning Ahrefs keyword rows into planned pages or mapping opportunities to an existing site.

## Source boundaries

- Use only Ahrefs MCP responses for keyword facts and metrics, including keyword suggestions, Volume, KD, CPC, Traffic Potential, Search Intent, Parent Topic, SERP Features, competitors, rankings, and SERP results.
- Allow model-generated phrases only as seeds sent to Ahrefs. Do not place an unreturned seed in the plan as a validated keyword.
- Read an existing site only to understand its product, audience, features, current pages, and information architecture. Do not derive keyword facts or metrics from page text or ordinary web search.
- Never fill a missing Ahrefs fact with an estimate. Write `N/A` and preserve the data gap.
- Cluster only inside one target-country and target-language dataset. Research every country independently and create a separate workbook for it.

## Process Ahrefs results in controlled batches

- Request and process no more than 100 returned keyword rows per batch.
- After each batch, save a JSON checkpoint and report the batch count, cumulative count, and a concise Topic distribution.
- Ask whether to continue before requesting the next batch. If the user stops, cluster the data already collected and generate a clearly labeled partial plan.
- Continue from an explicit Ahrefs cursor only when the current MCP schema actually exposes one. Otherwise expand from uncovered seeds, tools, competitors, filters, or Topics and deduplicate against every prior checkpoint; never emulate the removed `offset` parameter.
- Do not imply that a stopped or API-limited run represents every available keyword.

## Build one row per planned page

Treat one row in `Content Plan` as one indexable page, not one raw keyword.

1. Preserve every Ahrefs keyword row in `Raw Keywords` before clustering.
2. Group synonyms, close variants, and phrases that share the same search intent and expected page type.
3. Select one `Primary Keyword` that is semantically accurate for the page and, among equally accurate candidates, has the stronger Ahrefs demand.
4. Put the remaining same-page terms in `Supporting Keywords`.
5. Report the Primary Keyword's metrics in `Content Plan`; never sum supporting-keyword Volume or Traffic Potential because those audiences may overlap.
6. Map every accepted raw keyword to exactly one planned Primary Keyword. Record excluded terms and their exclusion reason.

Use Ahrefs Parent Topic as a clustering signal, not as an automatic decision. Override it when SERP evidence or intent clearly requires a different page.

## Validate clusters with Ahrefs SERPs

Use Ahrefs MCP SERP Overview and compare the normalized URLs of the top 10 organic results for the same country. Ignore ads and non-organic modules. Normalize protocol, `www`, trailing slash, fragments, and tracking parameters before comparing; retain a path difference that represents a different page.

| Shared top-10 organic URLs | Decision |
|---:|---|
| 5 or more | Merge the keywords into one planned page unless their language meaning makes the merge unsafe. Document any override. |
| 0–2 | Split into separate planned pages. |
| 3–4 | Judge Search Intent, expected page type, wording, and Parent Topic together. Flag `Needs Review` even after choosing a provisional mapping. |

- Mark `Needs Review` when Ahrefs does not return enough SERP data. Do not use another search source as a substitute.
- Recheck the highest-priority, ambiguous, and cannibalization-prone pairs first; do not spend API units comparing every obviously distinct pair.
- Store the comparison count, decision, and evidence in clustering data and surface review items in `Methodology` or workbook comments.

## Map an existing site

Assign one `Action` per planned page:

| Action | Use when | URL handling |
|---|---|---|
| `Existing` | An existing page clearly and adequately targets the cluster. | Keep the existing URL. |
| `Update` | A relevant page exists but needs a target-keyword, intent, content-type, or coverage change. | Keep the existing URL unless a separate technical reason requires migration. |
| `Consolidate` | Two or more existing pages compete for the same cluster or should become one stronger page. | Choose the strongest destination URL and identify the pages to merge in the supporting data. |
| `New` | No existing page adequately covers the cluster. | Generate a concise planned URL in the target language. |

- Put the chosen URL in `Existing/Planned URL`.
- Do not change the site. Deliver only the plan and recommendations.
- Avoid creating a new page when an update or consolidation would satisfy the same intent.
- Flag uncertain mappings for review instead of inventing certainty.

## Retain strategically valuable low-demand terms

- Do not exclude a relevant term only because Ahrefs reports Volume `0`.
- Retain high-fit BOFU terms, narrow use cases, emerging features, and relevant competitor `alternative`, `vs`, or comparison terms when they support a real page.
- Let low measured demand reduce only the Demand component of priority; let commercial fit, funnel stage, feasibility, and strategic role contribute normally.
- Exclude high-volume terms that lack a meaningful relationship to the product, audience, or content mission.
