# Priority Scoring

Use this reference after clustering and page mapping. Calculate priority inside one country workbook only; never compare percentiles across countries.

Before running the deterministic scorer, assign `commercial_relevance_score` and `strategic_value_score` to every planned page using the discrete rubrics below. Let `scripts/score_content_plan.py` calculate Funnel points, demand percentiles, KD/DR feasibility, provisional caps, total score, and P1/P2/P3. Do not hand-edit the resulting total unless the inputs change and the script is rerun.

## Calculate the 100-point score

| Component | Maximum | Rule |
|---|---:|---|
| Commercial relevance | 30 | Assign one discrete relevance score from the rubric below. |
| Funnel and conversion potential | 25 | Assign the fixed score for TOFU, MOFU, or BOFU. |
| Demand | 20 | Combine within-country Volume and Traffic Potential percentiles. |
| Feasibility | 15 | Use KD; for an existing site, adjust with Ahrefs DR. |
| Strategic value | 10 | Assign the page's cluster and dependency role. |

Add the five component scores. Do not add undocumented bonuses or penalties.

### Commercial relevance: 0, 8, 15, 22, or 30

| Score | Evidence |
|---:|---|
| 0 | Unrelated to the product, audience, or content mission. Exclude the row rather than plan it. |
| 8 | Tangential awareness value with no credible path to the product or core audience problem. |
| 15 | Relevant industry or problem context, but weak product or use-case proximity. |
| 22 | Strong match to a product-supported problem, audience use case, or solution category. |
| 30 | Exact product, feature, tool, high-value use case, integration, comparison, alternative, or purchase/try intent. |

Use the lowest score fully supported by the available product and audience evidence.

### Funnel: fixed score

| Funnel | Score |
|---|---:|
| `TOFU` | 8 |
| `MOFU` | 16 |
| `BOFU` | 25 |

### Demand: 0–20

Calculate Volume and Traffic Potential separately among the accepted planned pages in the same country. Use the Primary Keyword's Ahrefs metrics and do not sum supporting terms.

1. Calculate an inclusive percentile rank for every non-missing numeric value in each metric. Keep true zero values in the distribution.
2. Convert each percentile to points:

| Value or percentile | Points per metric |
|---|---:|
| True value `0` | 0 |
| Greater than `0`, percentile at or below 25 | 2 |
| Percentile above 25 and at or below 50 | 5 |
| Percentile above 50 and at or below 75 | 8 |
| Percentile above 75 | 10 |

3. Add Volume points and Traffic Potential points for a maximum of 20.
4. If one demand metric is `N/A`, double the available metric's points, cap at 20, and flag the score as based on one signal.
5. If both demand metrics are `N/A`, set Demand to `N/A` and apply the missing-data procedure below. Never convert a missing metric to zero.

Use stable average ranks for ties. Recalculate percentiles only after the accepted page set is final so batch order does not change scores.

### Feasibility: 0–15

For a new site, or when Ahrefs DR is unavailable, score KD directly:

| KD | Score |
|---:|---:|
| 0–10 | 15 |
| 11–20 | 13 |
| 21–30 | 11 |
| 31–40 | 8 |
| 41–50 | 5 |
| 51–70 | 2 |
| 71–100 | 0 |

For an existing site with Ahrefs DR, calculate `difficulty gap = KD - DR` and use:

| Difficulty gap | Score |
|---:|---:|
| at or below -20 | 15 |
| -19 to -10 | 13 |
| -9 to 0 | 11 |
| 1 to 10 | 8 |
| 11 to 20 | 5 |
| 21 to 30 | 2 |
| above 30 | 0 |

Treat DR as a planning proxy, not a ranking guarantee. If KD is `N/A`, set Feasibility to `N/A`; do not infer KD from the SERP or DR.

### Strategic value: 2, 5, 8, or 10

| Score | Role |
|---:|---|
| 2 | Isolated page with little cluster or internal-link contribution. |
| 5 | Ordinary supporting page in a useful cluster. |
| 8 | Important cluster page that closes a journey gap or supports several relevant pages. |
| 10 | Pillar page, core product page, or key dependency required before multiple other pages can work well. |

## Convert score to priority

| Priority | Total score |
|---|---:|
| `P1` | 75–100 |
| `P2` | 50–74 |
| `P3` | below 50 |

Allow a strategically foundational Pillar page to reach P1 through the normal scoring rubric; do not manually force its label.

## Handle missing data deterministically

- Keep missing Ahrefs metric cells as `N/A`; keep a genuine reported zero as `0`.
- If Demand or Feasibility is `N/A`, calculate a provisional total as `round(known component points / known component maximums * 100)`, then cap the displayed provisional score at `74`.
- Mark the provisional calculation in a cell comment and list it under data gaps in `Methodology`.
- Cap a provisional priority at `P2` until the missing Ahrefs evidence is restored. Keep the capped numeric provisional score visible in `Priority Score` and record the uncapped calculation in the comment or Methodology.
- Never guess a metric or silently treat missing data as poor performance.

## Score zero-volume opportunities fairly

Keep a Volume-0 page when it has clear product relevance, BOFU intent, a strategic cluster role, or an emerging/narrow use case. Give Volume zero demand points, score every other supported component normally, and let the same P1/P2/P3 thresholds decide the result. Document why a high-priority zero-volume page remains in the plan.

## Sort the plan

Sort `Content Plan` by `P1`, `P2`, `P3`; then by Priority Score descending; then by Topic and Volume. Do not let sorting alter the scores or percentile population.

Run the scorer before the workbook builder:

```bash
python3 <skill-dir>/scripts/score_content_plan.py \
  --input <unscored-artifact.json> \
  --output <content-plan-data.json>
```

On Windows, use `py` instead of `python3`. The script never calls a network service and refuses to overwrite its output unless `--overwrite` is explicitly passed.
