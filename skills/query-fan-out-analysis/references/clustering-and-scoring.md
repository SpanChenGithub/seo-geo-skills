# Clustering and Scoring

## Exact normalization

Create an exact-deduplication key with this deterministic sequence:

1. Unicode NFKC normalization;
2. trim leading and trailing whitespace;
3. collapse internal whitespace to one space;
4. Unicode case-folding.

Do not remove punctuation, stem words, delete stop words, translate, or strip modifiers during exact normalization. Those operations can merge different intents.

Deduplicate an identical key within one provider run. Preserve the same key across independent runs.

## Semantic clustering

Put queries in the same cluster only when they share:

- the core retrieval task;
- expected answer type;
- entity and meaningful constraints;
- audience or locale when material;
- user journey stage.

Example that can merge:

- `best CRM for startups`
- `top CRM software for a startup`

Example that must remain separate:

- `CRM pricing for startups`
- `best CRM for startups`

Keep separate queries that differ materially in:

- negation;
- current versus historical information;
- year or freshness;
- country, city, or language;
- audience or industry;
- platform or device;
- comparison target;
- price or plan;
- legal, safety, privacy, or operational risk;
- informational versus transactional intent.

Translations can join one semantic cluster when they express the same task. Preserve each original query and language.

## Within-model stability

For one provider cluster:

```text
within_model_stability =
  distinct valid runs containing the cluster
  / total valid analysis runs for that provider
```

A failed run that produced no observed, provider-synthetic, or heuristic queries is not a valid analysis run. A degraded heuristic fallback run is valid when it produced queries and is clearly labeled.

Count a run once even if several queries from that run belong to the cluster.

Use six decimal places in JSON and show the fraction in Markdown.

- `high`: score >= 0.8
- `medium`: 0.5 <= score < 0.8
- `low`: score < 0.5

With three runs, these normally correspond to 3/3, 2/3, and 1/3.

## Cross-model coverage

For one cross-platform cluster:

```text
cross_model_coverage =
  distinct participating platforms containing the cluster
  / total participating platforms
```

A platform participates when at least one observed, provider-synthetic, or heuristic run produced queries. Exclude a completely failed platform from the denominator and list that failure separately.

Count each platform once, regardless of how many runs or queries it contributes.

Use the same high/medium/low thresholds. Call the result `cross-model coverage`, never consensus probability.

## Consensus and platform-specific clusters

- **Cross-model consensus**: prefer clusters with medium or high cross-model coverage and clear fit to the seed intent.
- **Platform-specific angle**: a cluster appearing on only one platform in this analysis. Do not claim it is unique to that provider generally.
- **Exploratory cluster**: low recurrence or low cross-model coverage, retained because it closes a meaningful gap.

Observed provenance is stronger evidence about one invocation, but it does not automatically raise a cluster's recurrence or intent priority.

## Optional priority heuristic

Use a priority score only when the user needs ranking. Keep each component visible:

```text
priority_score =
  0.40 * seed_intent_fit
  + 0.25 * information_gap_value
  + 0.20 * cross_model_coverage
  + 0.15 * average_within_model_stability
```

Score each component from 0 to 1. State that this is the skill's report-ordering heuristic, not a provider algorithm. Do not use provenance as a direct bonus and do not invent precision unsupported by the judgments.
