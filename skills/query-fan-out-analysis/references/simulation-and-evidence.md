# Simulation and Evidence Rules

## Evidence levels

| Source type | Meaning | Permitted claim |
|---|---|---|
| `observed_tool_query` | A structured provider API or authorized tool trace returned the exact query string executed in that invocation | "This query was observed in this configured API run." |
| `synthetic_provider_query` | The named provider model generated a plausible fan-out candidate for the analysis | "This provider model generated this candidate in this run." |
| `heuristic_simulation` | The current host model simulated another product or provider without calling it | "This is a lower-confidence platform-style hypothesis." |
| `external_search_signal` | A SERP, PAA item, related search, trend, or current fact informed intent or coverage | "This external signal informed the analysis." |

Never collapse the four types into an unlabeled list.

## What observed means

Observed evidence is local to:

- one provider API;
- one exact model and product surface;
- one request configuration;
- one time;
- one language, locale, persona, and context;
- one stochastic run.

It does not reveal the provider's chain-of-thought. It does not prove that the consumer application would use the same query. It does not prove that the same API will repeat the query later.

Preserve every retained observed string verbatim. If a value is empty, non-text, longer than 2,000 characters, or contains an environment credential or credential-shaped secret, discard the whole value and emit `OBSERVED_QUERY_DROPPED_INVALID` or `OBSERVED_QUERY_DROPPED_SECRET`; carry the code into the final failures or limitations. Do not trim, truncate, translate, or redact such a value and then present the edited text as observed.

Only structured trace fields documented in [provider-capabilities.md](provider-capabilities.md) qualify. Do not promote these to observed queries:

- response prose;
- thought or reasoning summaries;
- citations and source URLs;
- search-result titles or snippets;
- People Also Ask or related questions;
- search-suggestion HTML;
- a query count without query strings;
- user-supplied candidate queries;
- text that merely resembles JSON inside an answer.

## Independent-run protocol

- Use the same seed, context, language, locale, persona, provider surface, model, and tool configuration for comparability.
- Start a fresh request for each run.
- Do not send earlier queries, clusters, or summaries into later runs.
- For host-model heuristic runs, prefer isolated subagents, fresh model calls, or fresh contexts. When the host cannot isolate context, label the outputs repeated prompt variations, not strictly independent runs, and lower the confidence of recurrence claims.
- Preserve all successfully returned observed queries, even when there are fewer than 10 or more than 15.
- Deduplicate exact repeats only within a run before analysis.
- Keep the occurrence of an equivalent query in another run; it is evidence for recurrence.
- Record failures and empty traces as run outcomes. Do not silently rerun until a preferred query list appears.

## API credential policy

Read only these environment variables:

- `OPENAI_API_KEY`
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`
- `ANTHROPIC_API_KEY`
- `PERPLEXITY_API_KEY`

Never:

- accept a key through a command-line flag;
- put a key in a request JSON file;
- print request headers;
- print an exception or raw provider body that may contain a key;
- store raw API responses by default;
- write a `.env` file;
- commit credentials or credential-shaped strings.

If a user pastes a key into chat, do not repeat it. Tell the user to revoke or rotate it and set a replacement in the environment.

## API-first execution policy

Treat invocation of this skill as authorization for its ordinary requested or default API plan. A configured credential activates the documented provider API path when the selected model and operation are supported. Do not replace a usable real provider API with host-model simulation merely because the user did not separately request API execution.

Before network calls, generate and show the sanitized collector plan: provider, requested model, API-route availability, credential availability, run count, planned top-level calls, possible provider-side search or continuation calls, and fallback. Then immediately execute eligible entries with the collector's `--allow-api-calls` flag. That flag is a deliberate local network gate, not a second user-consent step.

The ordinary default plan is at most three runs per provider and 10–15 generated candidates per run. Require additional authorization only when the agent proposes to exceed the user's scope or this default, or to select an unrequested higher-cost model. A larger run count or model explicitly requested by the user is already authorized for that scope; encode this as `expanded_scope_authorized: true`. Without that explicit bit, the collector must stop with `SCOPE_AUTHORIZATION_REQUIRED` before any call.

An explicit simulated-only, offline, no-network, or no-paid-API instruction overrides API-first execution. Map no-network to `network_access: false` and no-paid-API to `allow_paid_api_calls: false`; `simulated_only` queues host-model heuristics and does not call provider APIs even when credentials exist. If the user explicitly requires API-backed or `observed_only` output and a credential is missing, name the environment variable and wait for it to be configured outside chat.

## Fallback ladder

Use this order per provider:

1. exact observed tool queries when the API exposes them;
2. provider-generated synthetic candidates when available and useful;
3. host-model heuristic simulation;
4. a recorded provider failure when no responsible candidate can be produced.

In `observed_only` mode, do not proceed from step 1 to a simulated fallback; record the unsupported, missing-credential, failed, or incomplete observed run instead.

Never change an unavailable model silently. Record the requested model, actual model, status, and fallback reason. Record `actual` only when a response exposes the exact model ID. When a provider or host does not expose it, use `null` plus `not_exposed`; do not copy the requested model as a guess.

For every final report run, record `api_attempted`, total prior HTTP attempts, and `fallback_reason`. Observed and provider-synthetic evidence requires an actual provider API attempt. A heuristic simulation always requires a non-empty reason; set `api_attempted: true` and preserve the attempt count when it follows a failed or empty provider call, and use `false` with zero attempts only when no provider call occurred.

## External research

Use authorized current web research to improve entity resolution, intent, recency, and terminology. Keep those signals in `external_search_signals`, separate from platform traces, so that a shared Google SERP does not make every platform simulation look falsely identical. Record the signal type, text, source URL and title when available, retrieval time, language, and locale.

If networking is unavailable, continue with heuristic simulations and add `NETWORK_UNAVAILABLE` plus an explicit low-confidence limitation. If the locale is missing, add `REGION_UNSPECIFIED`; do not name an assumed country.

## Prohibited interpretations

- A 3/3 cluster is not a 100% real-world query probability.
- Cross-model coverage is not market share or platform agreement outside this run.
- Search-query counts are not search volume.
- A recurring synthetic query is not an observed provider query.
- A cited source is not proof of the search query used to find it.
- Grounding and fan-out are related but not synonymous.
- Ranking for a fan-out query does not guarantee inclusion or citation.
