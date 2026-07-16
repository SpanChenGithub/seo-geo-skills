# Provider Capabilities and API Contracts

Last verified: 2026-07-15. Provider APIs, models, fields, pricing, and authentication can change. Recheck the linked official documentation before modifying the collector or making a claim about a newly exposed field.

## Capability matrix

| Platform surface | Credential | Default model | API-first execution | What can be observed |
|---|---|---|---|---|
| OpenAI Responses API with web search | `OPENAI_API_KEY` | `chat-latest` | Call the real API when the route, model, and credential are available. | Structured `web_search_call` search actions may return exact `queries`. |
| Gemini Interactions API with Google Search | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `gemini-3.5-flash` | Call the real API when the route, model, and credential are available. | `google_search_call.arguments.queries` returns executed query strings when search occurs. |
| Google AI Mode | Gemini key only for provider-backed simulation | Gemini default above | There is no corresponding consumer AI Mode API. A Gemini call is an optional provider-backed simulation and is labeled as such. | No public consumer trace is used; output remains simulated and must not be labeled observed. |
| Claude Messages API with web search | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` | Call the real API when the route, model, and credential are available. | `server_tool_use` blocks named `web_search` expose `input.query`. |
| Perplexity Sonar Pro Search | `PERPLEXITY_API_KEY` | `sonar-pro` | Call the real Sonar API with Pro Search streaming when the model and credential are available. | Concise reasoning stream events expose executed `web_search.search_keywords[]`; retain those exact strings as observed queries. |

## API-first capability gate

Apply this gate separately to every requested platform:

1. Confirm separately whether the named product/model has a corresponding official API and whether only a provider-backed simulation route exists.
2. Resolve the requested model from the user override, environment override, or tested default. Check that it belongs to a conservative model family documented for this skill's text-plus-web-search operation; a vendor-shaped ID alone is insufficient.
3. Check only whether the documented credential environment variable is present; never expose its value.
4. Run the sanitized collector plan. Require `official_surface_api_route_available`, a non-incompatible `corresponding_model_api_status`, `api_execution_available`, and `credential_available` before treating a call as the corresponding real product/model API. A simulation route must be labeled `provider_synthetic_api`, never as a corresponding product API.
5. Verify recognized non-default models at call time. If the model family is for embeddings, image/video generation, realtime/audio, moderation, or another unsupported operation, do not call it; return `MODEL_OPERATION_UNSUPPORTED_OR_UNVERIFIED`. If the provider rejects a plausibly compatible model or operation, preserve the failure and use the documented fallback for the selected mode; never silently switch models.

The plan reports initial calls separately from the maximum top-level requests after Claude continuations/provider-synthetic fallback and from maximum HTTP attempts after retries. It does not invent a currency estimate when provider pricing, token use, or provider-side search count is not determinable before execution; show `cost_estimate_status` instead.

For Google AI Mode, `official_surface_api_route_available` is false even when `provider_simulation_api_available` is true. For Perplexity `sonar-pro`, Pro Search concise streaming exposes structured search keywords and therefore supports observed execution; other model/configuration combinations remain provider-synthetic unless their current official schema documents an equivalent trace.

Environment model overrides:

- `OPENAI_FANOUT_MODEL`
- `GEMINI_FANOUT_MODEL`
- `ANTHROPIC_FANOUT_MODEL`
- `PERPLEXITY_FANOUT_MODEL`

Resolve an explicit request model before the environment override, then the tested default. Report this as `model_source`. A model override deliberately configured in the documented environment variable is treated as user-owned execution configuration, but still passes the provider namespace check and is marked `verify_at_call_time` until accepted by the provider. Always report the requested model. Report an actual model ID only when the response exposes it; otherwise use `null` and `not_exposed`. Never silently replace an unavailable model or copy a requested ID into the actual field as a guess.

## OpenAI

- Endpoint: `POST https://api.openai.com/v1/responses`
- Authentication header: `Authorization: Bearer ...`
- Send `store: false`; this is separate from the collector's guarantee that it does not persist raw responses locally.
- Tool: `{"type":"web_search"}`
- Set `max_tool_calls: 10` to bound chargeable built-in tool calls per run.
- Structured trace: `output[].type == "web_search_call"`, then `action.type == "search"`, then `action.queries[]`; accept deprecated `action.query` as a single query.
- Ignore `open_page`, `find_in_page`, citations, sources, and answer text as query evidence.
- If search ran but query strings are absent, use `live_search_unobserved` and do not invent an observed query.

Official documentation: [Web search](https://developers.openai.com/api/docs/guides/tools-web-search), [Chat Latest model](https://developers.openai.com/api/docs/models/chat-latest), [API authentication](https://developers.openai.com/api/reference/overview#authentication), [data controls](https://platform.openai.com/docs/models/default-usage-policies-by-endpoint).

`chat-latest` is an API alias intended to track a current ChatGPT-family model, but an API response still lacks the consumer product's full system orchestration, memory, account context, and interface behavior.

## Gemini

- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/interactions`
- Authentication header: `x-goog-api-key: ...`
- Tool: `{"type":"google_search"}`
- Current structured trace: `steps[].type == "google_search_call"`, then `arguments.queries[]`.
- For compatibility, also accept `outputs[]` with the same call shape, a single `arguments.query`, and legacy Generate Content `candidates[].groundingMetadata.webSearchQueries[]`.
- Ignore thought summaries, search suggestions, grounding chunks, citations, and answer text as query evidence.
- A model may decide not to search. Report `not_searched`; do not relabel generated text as observed.

Official documentation: [Gemini 3.5 Flash](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash), [Grounding with Google Search](https://ai.google.dev/gemini-api/docs/google-search), [legacy Generate Content grounding](https://ai.google.dev/gemini-api/docs/generate-content/google-search), [API keys](https://ai.google.dev/gemini-api/docs/api-key).

## Google AI Mode

Google publicly states that its AI search features may use query fan-out across subtopics and sources, but there is no public consumer API in this skill that exports a user's complete AI Mode trace. Use public principles, current search signals, and a separately identified Gemini model to generate simulations only.

Official background: [Google Search Central: AI features and your website](https://developers.google.com/search/docs/appearance/ai-features).

## Claude

- Endpoint: `POST https://api.anthropic.com/v1/messages`
- Authentication header: `x-api-key: ...`
- Version header: `anthropic-version: 2023-06-01`
- Basic web-search tool: `{"type":"web_search_20250305","name":"web_search","max_uses":10}`
- Structured trace: `content[].type == "server_tool_use"`, `name == "web_search"`, then `input.query`, but only after a `web_search_tool_result.tool_use_id` matches the call's `id`.
- Ignore citations, result titles, result snippets, and response prose as query evidence.
- Inspect `web_search_tool_result` for error objects even when HTTP status is 200.
- If `stop_reason` is `pause_turn`, a continuation must resend the original user message and returned assistant content unchanged. A paused response may end with a server-tool call that has not executed; keep it pending until a later matching result arrives. Bound continuation loops and never promote an unresolved call to observed.

Official documentation: [Claude web search tool](https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool), [model IDs and versioning](https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions), [server tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/server-tools), [authentication](https://platform.claude.com/docs/en/manage-claude/authentication).

These traces represent Claude API tool calls, not claude.ai consumer sessions.

## Perplexity

- Fixed endpoint: `POST https://api.perplexity.ai/v1/sonar`
- Authentication header: `Authorization: Bearer ...`
- Default model: `sonar-pro`
- To observe Pro Search keywords, send `stream: true`, `stream_mode: "concise"`, and `web_search_options.search_type: "pro"` with `sonar-pro`.
- Structured trace: stream event `choices[].delta.reasoning_steps[]` with `type == "web_search"`, then `web_search.search_keywords[]`. Persist the report trace path as `$.events[i].choices[j].delta.reasoning_steps[k].web_search.search_keywords[n]`.
- `usage.num_search_queries` is a count and `search_results[]`, citations, and `related_questions[]` are supporting metadata; none is a substitute for an exact `search_keywords[]` value.
- For another Sonar model or configuration without the documented trace, ask the provider to return plausible candidates and label them `synthetic_provider_query`; do not label them observed.
- When `live_research` is false for a provider-synthetic call, send `web_search_options.disable_search: true`.

Official documentation: [Sonar API](https://docs.perplexity.ai/api-reference/sonar-post), [Pro Search quickstart](https://docs.perplexity.ai/docs/sonar/pro-search/quickstart), [Pro Search stream mode](https://docs.perplexity.ai/docs/sonar/pro-search/stream-mode).

Queries explicitly supplied by this skill to the Perplexity Search API are skill-supplied executed queries, not Sonar's hidden fan-out. Do not label them provider-observed.

## Retry and failure rules

- Retry timeouts, HTTP 408/429, and 5xx failures no more than twice with short exponential backoff and jitter.
- Count `attempts` as total HTTP attempts for the analysis run. Most providers therefore allow at most 3; Claude can reach 9 when an initial call plus two bounded continuations each consume all 3 retry attempts.
- Do not retry missing credentials, 400/401/403 authentication or request-shape errors, or invalid model identifiers without changing the configuration.
- Map provider failures to stable codes; do not emit raw provider bodies or raw exception strings.
- Continue other providers after one failure.
- Preserve `requested`, `actual`, `actual_status`, and `fallback_reason` model fields; do not infer `actual` from `requested`.
- Use fixed official HTTPS endpoints. Do not accept an endpoint override in a credential-bearing script.

Suggested failure codes:

- `API_EXECUTION_FLAG_REQUIRED`
- `SCOPE_AUTHORIZATION_REQUIRED`
- `CREDENTIAL_MISSING`
- `AUTH_FAILED`
- `RATE_LIMITED`
- `PROVIDER_4XX`
- `PROVIDER_5XX`
- `TIMEOUT`
- `INVALID_PROVIDER_JSON`
- `QUERY_TRACE_MISSING`
- `SEARCH_NOT_USED`
- `OBSERVED_MODE_UNSUPPORTED`
- `RETRY_EXHAUSTED`
- `HOST_MODEL_NOT_EXPOSED`
- `REGION_UNSPECIFIED`
- `NETWORK_UNAVAILABLE`

## Collector request document

The bundled collector accepts a UTF-8 JSON object from a file or stdin. Do not include a URL or API key.

```json
{
  "schema_version": "1.0",
  "seed_input": "best project management software",
  "detected_language": "en",
  "target_locale": "unspecified",
  "location": null,
  "persona_or_context": "Operations lead at a 20-person SaaS company",
  "business_context": null,
  "desired_answer_type": "Product comparison",
  "providers": ["openai", "gemini", "google_ai_mode", "claude", "perplexity"],
  "runs_per_provider": 3,
  "queries_per_run": 12,
  "mode": "hybrid",
  "models": {},
  "live_research": true,
  "network_access": true,
  "allow_paid_api_calls": true,
  "expanded_scope_authorized": false
}
```

`location` may contain `city`, `region`, two-letter `country`, and IANA `timezone`. Omit it when unspecified. The script sends it only through supported provider location fields and prompt context; it never defaults to a country.

`network_access` and `allow_paid_api_calls` default to true for normal API-first execution. Set either to false when the user explicitly requests no-network or no-paid-API operation. `expanded_scope_authorized` defaults to false and must be true before executing more than three runs per provider or more than 15 generated candidates per run; an explicit larger user request supplies that authorization. `simulated_only` always queues host-model heuristic simulations and never calls a provider API, even if credentials are configured.
