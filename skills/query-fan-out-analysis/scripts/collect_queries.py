#!/usr/bin/env python3
"""Collect observed or provider-synthetic query fan-out candidates.

The script uses only the Python standard library. It never accepts credentials
as command-line arguments, never persists raw provider responses, and keeps a
deliberate local network gate: collect requires --allow-api-calls whenever its
sanitized plan selects real provider API execution. The API-first skill workflow
supplies that flag automatically after planning.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import socket
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


SCHEMA_VERSION = "1.0"
MAX_INPUT_BYTES = 1024 * 1024
MAX_RESPONSE_BYTES = 5 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 60
MAX_RETRIES = 2
MAX_CLAUDE_CONTINUATIONS = 2
MAX_SEARCH_TOOL_CALLS_PER_RUN = 10

PROVIDERS = ("openai", "gemini", "google_ai_mode", "claude", "perplexity")
OBSERVED_QUERY_TRACE_PROVIDERS = frozenset(("openai", "gemini", "claude"))
DEFAULT_PROVIDERS = list(PROVIDERS)
DEFAULT_MODELS = {
    "openai": "chat-latest",
    "gemini": "gemini-3.5-flash",
    "google_ai_mode": "gemini-3.5-flash",
    "claude": "claude-sonnet-4-6",
    "perplexity": "sonar-pro",
}
MODEL_NAMESPACE_PATTERNS = {
    "openai": re.compile(r"^(?:chat-latest$|gpt-|o[1-9](?:-|$))"),
    "gemini": re.compile(r"^gemini-"),
    "google_ai_mode": re.compile(r"^gemini-"),
    "claude": re.compile(r"^claude-"),
    "perplexity": re.compile(r"^(?:sonar(?:-|$)|r1-1776$)"),
}
WEB_SEARCH_MODEL_PATTERNS = {
    "openai": re.compile(
        r"^(?:chat-latest|gpt-(?:5(?:\.\d+)?(?:-(?:mini|nano|pro|sol|terra|luna))?"
        r"|4\.1(?:-(?:mini|nano))?|4o(?:-mini)?)(?:-\d{4}-\d{2}-\d{2})?"
        r"|o(?:3(?:-pro)?|4-mini)(?:-\d{4}-\d{2}-\d{2})?)$"
    ),
    "gemini": re.compile(
        r"^gemini-(?:[1-9]\d*(?:\.\d+)?-(?:flash|pro)(?:-lite)?"
        r"(?:-(?:image-)?preview(?:-[0-9-]+)?)?|(?:flash|pro)-latest)$"
    ),
    "google_ai_mode": re.compile(
        r"^gemini-(?:[1-9]\d*(?:\.\d+)?-(?:flash|pro)(?:-lite)?"
        r"(?:-(?:image-)?preview(?:-[0-9-]+)?)?|(?:flash|pro)-latest)$"
    ),
    "claude": re.compile(
        r"^claude-(?:(?:opus|sonnet|haiku|fable)-\d+(?:-\d+)*(?:-\d{8})?"
        r"|mythos-(?:\d+|preview))$"
    ),
    "perplexity": re.compile(
        r"^(?:sonar|sonar-pro|sonar-reasoning|sonar-reasoning-pro|sonar-deep-research|r1-1776)$"
    ),
}
MODEL_ENV = {
    "openai": "OPENAI_FANOUT_MODEL",
    "gemini": "GEMINI_FANOUT_MODEL",
    "google_ai_mode": "GEMINI_FANOUT_MODEL",
    "claude": "ANTHROPIC_FANOUT_MODEL",
    "perplexity": "PERPLEXITY_FANOUT_MODEL",
}
KEY_ENV = {
    "openai": ("OPENAI_API_KEY",),
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "google_ai_mode": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
    "claude": ("ANTHROPIC_API_KEY",),
    "perplexity": ("PERPLEXITY_API_KEY",),
}
ENDPOINTS = {
    "openai": "https://api.openai.com/v1/responses",
    "gemini": "https://generativelanguage.googleapis.com/v1beta/interactions",
    "google_ai_mode": "https://generativelanguage.googleapis.com/v1beta/interactions",
    "claude": "https://api.anthropic.com/v1/messages",
    "perplexity": "https://api.perplexity.ai/v1/sonar",
}

ALLOWED_REQUEST_FIELDS = {
    "schema_version",
    "seed_input",
    "detected_language",
    "target_locale",
    "location",
    "persona_or_context",
    "business_context",
    "desired_answer_type",
    "providers",
    "runs_per_provider",
    "queries_per_run",
    "mode",
    "models",
    "live_research",
    "network_access",
    "allow_paid_api_calls",
    "expanded_scope_authorized",
}

SECRET_PATTERNS = (
    re.compile(r"sk-ant-[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"pplx-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]{12,}"),
)


class ConfigError(Exception):
    """Invalid local request configuration."""


class DuplicateJsonKeyError(ValueError):
    """JSON object contains a duplicate key."""


class ProviderFailure(Exception):
    """Sanitized provider failure suitable for stable error mapping."""

    def __init__(
        self,
        code: str,
        retryable: bool = False,
        status: Optional[int] = None,
        attempts: int = 0,
    ):
        super().__init__(code)
        self.code = code
        self.retryable = retryable
        self.status = status
        self.attempts = attempts


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def duplicate_key_hook(pairs: Sequence[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(_: str) -> None:
    raise ValueError("invalid JSON constant")


def load_json_bytes(raw: bytes) -> Any:
    return json.loads(
        raw.decode("utf-8", errors="strict"),
        object_pairs_hook=duplicate_key_hook,
        parse_constant=reject_constant,
    )


def read_document(path: str) -> Any:
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ConfigError("INPUT_TOO_LARGE")
    try:
        return load_json_bytes(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError, ValueError):
        raise ConfigError("INVALID_INPUT_JSON")


def redact_text(value: str, secrets: Iterable[str]) -> str:
    redacted = value
    for secret in secrets:
        if secret:
            redacted = redacted.replace(secret, "[REDACTED]")
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def redact_value(value: Any, secrets: Iterable[str]) -> Any:
    if isinstance(value, str):
        return redact_text(value, secrets)
    if isinstance(value, list):
        return [redact_value(item, secrets) for item in value]
    if isinstance(value, dict):
        return {key: redact_value(item, secrets) for key, item in value.items()}
    return value


def all_environment_secrets() -> List[str]:
    values: List[str] = []
    for names in KEY_ENV.values():
        for name in names:
            value = os.environ.get(name)
            if value and value not in values:
                values.append(value)
    return values


def credential_for(provider: str) -> Tuple[Optional[str], Optional[str]]:
    for name in KEY_ENV[provider]:
        value = os.environ.get(name)
        if value:
            return value, name
    return None, None


def normalize_exact(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    normalized = " ".join(normalized.strip().split())
    return normalized.casefold()


def ordered_unique_queries(
    values: Iterable[Tuple[str, Optional[str]]], secrets: Iterable[str]
) -> Tuple[List[Dict[str, Any]], bool]:
    seen = set()
    result: List[Dict[str, Any]] = []
    redacted_any = False
    for raw_text, trace_path in values:
        if not isinstance(raw_text, str):
            continue
        stripped = raw_text.strip()
        if not stripped:
            continue
        safe = redact_text(stripped[:2000], secrets)
        if safe != stripped[:2000]:
            redacted_any = True
        key = normalize_exact(safe)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "text": safe,
                "normalized_text": key,
                "trace_path": trace_path,
            }
        )
    return result, redacted_any


def ordered_unique_observed_queries(
    values: Iterable[Tuple[Any, Optional[str]]], secrets: Iterable[str]
) -> Tuple[List[Dict[str, Any]], bool, bool]:
    """Keep safe observed query strings byte-for-byte equivalent as Python text.

    Unsafe or unreasonably large values are dropped instead of rewritten so an
    edited value can never be presented as an exact observed trace.
    """
    seen = set()
    result: List[Dict[str, Any]] = []
    secret_dropped = False
    invalid_dropped = False
    for raw_text, trace_path in values:
        if not isinstance(raw_text, str) or not raw_text.strip() or len(raw_text) > 2000:
            invalid_dropped = True
            continue
        if redact_text(raw_text, secrets) != raw_text:
            secret_dropped = True
            continue
        key = normalize_exact(raw_text)
        if not key or key in seen:
            continue
        seen.add(key)
        result.append(
            {
                "text": raw_text,
                "normalized_text": key,
                "trace_path": trace_path,
            }
        )
    return result, secret_dropped, invalid_dropped


def clean_optional_string(value: Any, field: str, max_length: int = 20000) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ConfigError("INVALID_" + field.upper())
    value = value.strip()
    if len(value) > max_length:
        raise ConfigError(field.upper() + "_TOO_LONG")
    return value or None


def validate_location(value: Any) -> Optional[Dict[str, str]]:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ConfigError("INVALID_LOCATION")
    allowed = {"city", "region", "country", "timezone"}
    if set(value) - allowed:
        raise ConfigError("UNKNOWN_LOCATION_FIELD")
    result: Dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(item, str) or not item.strip() or len(item) > 200:
            raise ConfigError("INVALID_LOCATION_VALUE")
        result[key] = item.strip()
    if not result:
        return None
    if "country" in result and len(result["country"]) != 2:
        raise ConfigError("COUNTRY_MUST_BE_ISO_ALPHA2")
    return result


def validate_request(document: Any) -> Dict[str, Any]:
    if not isinstance(document, dict):
        raise ConfigError("INPUT_ROOT_MUST_BE_OBJECT")
    unknown = set(document) - ALLOWED_REQUEST_FIELDS
    if unknown:
        raise ConfigError("UNKNOWN_INPUT_FIELD")
    if document.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError("UNSUPPORTED_SCHEMA_VERSION")

    seed = document.get("seed_input")
    if not isinstance(seed, str) or not seed.strip():
        raise ConfigError("SEED_INPUT_REQUIRED")
    seed = seed.strip()
    if len(seed) > 20000:
        raise ConfigError("SEED_INPUT_TOO_LONG")

    providers = document.get("providers", DEFAULT_PROVIDERS)
    if not isinstance(providers, list) or not providers:
        raise ConfigError("PROVIDERS_REQUIRED")
    if any(not isinstance(item, str) or item not in PROVIDERS for item in providers):
        raise ConfigError("INVALID_PROVIDER")
    if len(set(providers)) != len(providers):
        raise ConfigError("DUPLICATE_PROVIDER")

    runs = document.get("runs_per_provider", 3)
    query_count = document.get("queries_per_run", 12)
    if not isinstance(runs, int) or isinstance(runs, bool) or not 1 <= runs <= 10:
        raise ConfigError("INVALID_RUN_COUNT")
    if (
        not isinstance(query_count, int)
        or isinstance(query_count, bool)
        or not 1 <= query_count <= 50
    ):
        raise ConfigError("INVALID_QUERY_COUNT")

    mode = document.get("mode", "hybrid")
    if mode not in {"hybrid", "observed_only", "simulated_only"}:
        raise ConfigError("INVALID_MODE")

    models = document.get("models", {})
    if not isinstance(models, dict) or set(models) - set(PROVIDERS):
        raise ConfigError("INVALID_MODELS")
    for provider, model in models.items():
        if not isinstance(model, str) or not model.strip() or len(model) > 200:
            raise ConfigError("INVALID_MODEL")

    live_research = document.get("live_research", True)
    if not isinstance(live_research, bool):
        raise ConfigError("INVALID_LIVE_RESEARCH")
    if mode == "observed_only" and not live_research:
        raise ConfigError("OBSERVED_MODE_REQUIRES_LIVE_RESEARCH")

    network_access = document.get("network_access", True)
    if not isinstance(network_access, bool):
        raise ConfigError("INVALID_NETWORK_ACCESS")
    allow_paid_api_calls = document.get("allow_paid_api_calls", True)
    if not isinstance(allow_paid_api_calls, bool):
        raise ConfigError("INVALID_ALLOW_PAID_API_CALLS")
    expanded_scope_authorized = document.get("expanded_scope_authorized", False)
    if not isinstance(expanded_scope_authorized, bool):
        raise ConfigError("INVALID_EXPANDED_SCOPE_AUTHORIZATION")
    if mode == "observed_only" and (
        not network_access or not allow_paid_api_calls
    ):
        raise ConfigError("OBSERVED_MODE_REQUIRES_API_ACCESS")

    target_locale = document.get("target_locale", "unspecified")
    if not isinstance(target_locale, str) or not target_locale.strip():
        raise ConfigError("INVALID_TARGET_LOCALE")

    request = {
        "schema_version": SCHEMA_VERSION,
        "seed_input": seed,
        "detected_language": clean_optional_string(
            document.get("detected_language"), "detected_language", 100
        )
        or "undetermined",
        "target_locale": target_locale.strip(),
        "location": validate_location(document.get("location")),
        "persona_or_context": clean_optional_string(
            document.get("persona_or_context"), "persona_or_context"
        ),
        "business_context": clean_optional_string(
            document.get("business_context"), "business_context"
        ),
        "desired_answer_type": clean_optional_string(
            document.get("desired_answer_type"), "desired_answer_type", 1000
        ),
        "providers": list(providers),
        "runs_per_provider": runs,
        "queries_per_run": query_count,
        "mode": mode,
        "models": {key: value.strip() for key, value in models.items()},
        "live_research": live_research,
        "network_access": network_access,
        "allow_paid_api_calls": allow_paid_api_calls,
        "expanded_scope_authorized": expanded_scope_authorized,
    }
    return request


def resolve_model_with_source(
    provider: str, request: Dict[str, Any]
) -> Tuple[str, str]:
    explicit = request["models"].get(provider)
    if explicit:
        return explicit, "request_override"
    environment = os.environ.get(MODEL_ENV[provider])
    if environment and environment.strip():
        return environment.strip(), "environment_override"
    return DEFAULT_MODELS[provider], "tested_default"


def resolve_model(provider: str, request: Dict[str, Any]) -> str:
    return resolve_model_with_source(provider, request)[0]


def perplexity_observed_trace_supported(model: str) -> bool:
    return model == "sonar-pro"


def official_surface_api_route_available(provider: str) -> bool:
    """Return whether the named product surface has a corresponding API route."""
    return provider != "google_ai_mode"


def provider_simulation_api_available(provider: str) -> bool:
    return provider in PROVIDERS


def model_api_compatibility(provider: str, model: str) -> str:
    """Conservatively classify compatibility with this skill's search operation."""
    if model == DEFAULT_MODELS[provider]:
        return "documented_default"
    if WEB_SEARCH_MODEL_PATTERNS[provider].fullmatch(model):
        return "verify_at_call_time"
    if MODEL_NAMESPACE_PATTERNS[provider].match(model):
        return "operation_capability_unverified"
    return "incompatible_model_id"


def call_kind(
    provider: str,
    mode: str,
    live_research: bool = True,
    model: Optional[str] = None,
) -> str:
    selected_model = model or DEFAULT_MODELS[provider]
    if mode == "simulated_only":
        return "heuristic_simulation"
    if not live_research:
        return "provider_synthetic"
    if mode == "observed_only":
        if provider in OBSERVED_QUERY_TRACE_PROVIDERS:
            return "observed_api"
        if provider == "perplexity" and perplexity_observed_trace_supported(
            selected_model
        ):
            return "observed_api"
        return "unsupported"
    if provider in OBSERVED_QUERY_TRACE_PROVIDERS:
        return "observed_api"
    if provider == "perplexity" and perplexity_observed_trace_supported(selected_model):
        return "observed_api"
    return "provider_synthetic"


def build_plan(request: Dict[str, Any], secrets: Iterable[str]) -> Dict[str, Any]:
    entries: List[Dict[str, Any]] = []
    planned_calls = 0
    maximum_top_level_api_calls = 0
    maximum_http_attempts = 0
    expanded_scope = bool(
        request["runs_per_provider"] > 3 or request["queries_per_run"] > 15
    )
    scope_authorized = bool(
        not expanded_scope or request["expanded_scope_authorized"]
    )
    for provider in request["providers"]:
        key, key_name = credential_for(provider)
        model, model_source = resolve_model_with_source(provider, request)
        kind = call_kind(
            provider, request["mode"], request["live_research"], model
        )
        corresponding_route = official_surface_api_route_available(provider)
        simulation_api = provider_simulation_api_available(provider)
        model_status = model_api_compatibility(provider, model)
        api_policy_allows = bool(
            request["network_access"]
            and request["allow_paid_api_calls"]
            and scope_authorized
        )
        api_path_available = kind in {"observed_api", "provider_synthetic"}
        supported = kind != "unsupported"
        api_execution_available = bool(
            api_path_available
            and api_policy_allows
            and model_status
            not in {"incompatible_model_id", "operation_capability_unverified"}
        )
        will_call = bool(key and api_execution_available)
        initial_attempt_cap = (
            9 if provider == "claude" and kind == "observed_api" else 3
        )
        continuation_call_cap = (
            MAX_CLAUDE_CONTINUATIONS
            if provider == "claude" and kind == "observed_api"
            else 0
        )
        fallback_call_cap = 1 if kind == "observed_api" else 0
        max_attempts_per_run = initial_attempt_cap + (3 * fallback_call_cap)
        if will_call:
            planned_calls += request["runs_per_provider"]
            maximum_top_level_api_calls += request["runs_per_provider"] * (
                1 + continuation_call_cap + fallback_call_cap
            )
            maximum_http_attempts += request["runs_per_provider"] * max_attempts_per_run
        entries.append(
            {
                "provider": provider,
                "requested_model": model,
                "model_source": model_source,
                "call_kind": kind,
                "official_surface_api_route_available": corresponding_route,
                "corresponding_model_api_status": (
                    model_status if corresponding_route else "surface_api_unavailable"
                ),
                "provider_simulation_api_available": simulation_api,
                "simulation_model_api_status": model_status,
                "api_execution_allowed": api_policy_allows,
                "api_execution_available": api_execution_available,
                "observed_query_trace_supported": bool(
                    kind == "observed_api"
                    and model_status
                    not in {
                        "incompatible_model_id",
                        "operation_capability_unverified",
                    }
                ),
                "model_compatibility_check": (
                    model_status if api_path_available else "not_applicable"
                ),
                "credential_environment": key_name or KEY_ENV[provider][0],
                "credential_available": bool(key),
                "will_call_api": will_call,
                "planned_initial_api_calls": (
                    request["runs_per_provider"] if will_call else 0
                ),
                "possible_provider_synthetic_fallback_calls": (
                    request["runs_per_provider"] * fallback_call_cap
                    if will_call
                    else 0
                ),
                "possible_continuation_calls": (
                    request["runs_per_provider"] * continuation_call_cap
                    if will_call
                    else 0
                ),
                "maximum_http_attempts_per_run": max_attempts_per_run,
                "maximum_http_attempts": (
                    request["runs_per_provider"] * max_attempts_per_run
                    if will_call
                    else 0
                ),
                "provider_search_call_cap_per_run": (
                    MAX_SEARCH_TOOL_CALLS_PER_RUN
                    if provider in {"openai", "claude"}
                    and kind == "observed_api"
                    else None
                ),
                "execution_preference": (
                    (
                        "observed_provider_api"
                        if kind == "observed_api"
                        else "provider_synthetic_api"
                    )
                    if will_call
                    else (
                        "await_scope_authorization"
                        if not scope_authorized
                        else (
                            "hard_failure"
                            if request["mode"] == "observed_only"
                            else "host_model_fallback"
                        )
                    )
                ),
                "fallback": (
                    None
                    if will_call
                    else (
                        "OBSERVED_MODE_UNSUPPORTED"
                        if not supported
                        else (
                            "SCOPE_AUTHORIZATION_REQUIRED"
                            if not scope_authorized
                            else (
                                "SIMULATED_ONLY_REQUESTED"
                                if kind == "heuristic_simulation"
                                else (
                                    "MODEL_OPERATION_UNSUPPORTED_OR_UNVERIFIED"
                                    if model_status == "operation_capability_unverified"
                                    else (
                                        "MODEL_INCOMPATIBLE"
                                        if model_status == "incompatible_model_id"
                                        else (
                                            "API_POLICY_DISABLED"
                                            if not api_policy_allows
                                            else "CREDENTIAL_MISSING"
                                        )
                                    )
                                )
                            )
                        )
                    )
                ),
            }
        )
    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": "plan",
        "plan": {
            "seed_input": request["seed_input"],
            "detected_language": request["detected_language"],
            "target_locale": request["target_locale"],
            "mode": request["mode"],
            "runs_per_provider": request["runs_per_provider"],
            "queries_per_synthetic_run": request["queries_per_run"],
            "providers": entries,
            "planned_top_level_api_calls": planned_calls,
            "maximum_top_level_api_calls": maximum_top_level_api_calls,
            "maximum_http_attempts": maximum_http_attempts,
            "cost_estimate": None,
            "cost_estimate_status": "not_calculated_usage_and_pricing_variable",
            "possible_claude_continuations_per_observed_run": MAX_CLAUDE_CONTINUATIONS,
            "provider_side_search_calls_may_exceed_top_level_calls": True,
            "execution_policy": "api_first",
            "expanded_scope": expanded_scope,
            "expanded_scope_authorized": request["expanded_scope_authorized"],
            "scope_authorized": scope_authorized,
            "network_access": request["network_access"],
            "allow_paid_api_calls": request["allow_paid_api_calls"],
            "ordinary_default_plan_auto_authorized": not expanded_scope,
            "api_authorization_required": bool(
                expanded_scope and not scope_authorized
            ),
            "api_execution_flag_required": planned_calls > 0,
            "raw_api_responses_persisted": False,
            "api_keys_persisted": False,
        },
    }
    return redact_value(payload, secrets)


def context_lines(request: Dict[str, Any]) -> str:
    lines = [
        "Seed input: " + request["seed_input"],
        "Output language: " + request["detected_language"],
        "Target locale: " + request["target_locale"],
    ]
    if request["location"]:
        location = ", ".join(
            "%s=%s" % (key, value) for key, value in request["location"].items()
        )
        lines.append("Approximate location: " + location)
    for label, key in (
        ("Persona or context", "persona_or_context"),
        ("Business context", "business_context"),
        ("Desired answer type", "desired_answer_type"),
    ):
        if request[key]:
            lines.append(label + ": " + request[key])
    return "\n".join(lines)


def observed_prompt(request: Dict[str, Any]) -> str:
    return (
        "Act as a search-backed answer engine. Research and answer the user's input "
        "comprehensively. Use web search independently where it improves ambiguity "
        "resolution, related-topic coverage, comparisons, recency, context, trust, "
        "risk, or next steps. Do not list hypothetical searches or reveal private "
        "reasoning. If the input is a bare keyword, treat it as a request for a useful "
        "research answer about that topic.\n\n" + context_lines(request)
    )


def provider_location(request: Dict[str, Any]) -> Optional[Dict[str, str]]:
    location = request.get("location")
    if not isinstance(location, dict) or not location:
        return None
    result = {"type": "approximate"}
    result.update(location)
    return result


def synthetic_prompt(request: Dict[str, Any], surface: str) -> str:
    count = request["queries_per_run"]
    return (
        "Generate plausible query fan-out candidates for one independent analysis run. "
        "This is a transparent simulation for %s, not a request for hidden reasoning "
        "or a claim about a consumer product's actual searches. Produce %d natural "
        "retrieval queries that materially help answer the seed. Include only relevant "
        "reformulations, related topics, implicit questions, comparisons, recency, "
        "contextual variations, and next steps. Do not force a category. Remove "
        "duplicates and off-topic queries. Return only JSON with this shape: "
        '{"queries":["query one","query two"]}.\n\n%s'
        % (surface, count, context_lines(request))
    )


def safe_request_id(headers: Any) -> Optional[str]:
    if headers is None:
        return None
    for name in ("x-request-id", "request-id", "x-goog-request-id"):
        try:
            value = headers.get(name)
        except Exception:
            value = None
        if value and isinstance(value, str) and len(value) <= 200:
            return value
    return None


def http_post_json(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Tuple[Dict[str, Any], int, Optional[str]]:
    if url not in ENDPOINTS.values():
        raise ProviderFailure("ENDPOINT_NOT_ALLOWED")
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ProviderFailure("PROVIDER_REQUEST_TOO_LARGE")

    for attempt in range(MAX_RETRIES + 1):
        request = urllib.request.Request(
            url,
            data=encoded,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ProviderFailure(
                        "PROVIDER_RESPONSE_TOO_LARGE", attempts=attempt + 1
                    )
                try:
                    document = load_json_bytes(raw)
                except (
                    UnicodeDecodeError,
                    json.JSONDecodeError,
                    DuplicateJsonKeyError,
                    ValueError,
                ):
                    raise ProviderFailure("INVALID_PROVIDER_JSON", attempts=attempt + 1)
                if not isinstance(document, dict):
                    raise ProviderFailure("INVALID_PROVIDER_JSON", attempts=attempt + 1)
                return document, attempt + 1, safe_request_id(response.headers)
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            try:
                exc.read(4096)
            except Exception:
                pass
            if status in {401, 403}:
                failure = ProviderFailure(
                    "AUTH_FAILED", status=status, attempts=attempt + 1
                )
            elif status == 429:
                failure = ProviderFailure(
                    "RATE_LIMITED",
                    retryable=True,
                    status=status,
                    attempts=attempt + 1,
                )
            elif status == 408 or status >= 500:
                failure = ProviderFailure(
                    "PROVIDER_5XX" if status >= 500 else "TIMEOUT",
                    retryable=True,
                    status=status,
                    attempts=attempt + 1,
                )
            else:
                failure = ProviderFailure(
                    "PROVIDER_4XX", status=status, attempts=attempt + 1
                )
        except (urllib.error.URLError, socket.timeout, TimeoutError):
            failure = ProviderFailure(
                "TIMEOUT", retryable=True, attempts=attempt + 1
            )

        if not failure.retryable or attempt >= MAX_RETRIES:
            if failure.retryable and attempt >= MAX_RETRIES:
                raise ProviderFailure(
                    "RETRY_EXHAUSTED",
                    status=failure.status,
                    attempts=attempt + 1,
                )
            raise failure
        time.sleep((2**attempt) + random.random() * 0.25)

    raise ProviderFailure("RETRY_EXHAUSTED", attempts=MAX_RETRIES + 1)


def parse_sse_json_events(raw: bytes) -> List[Dict[str, Any]]:
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        raise ProviderFailure("INVALID_PROVIDER_JSON")

    events: List[Dict[str, Any]] = []
    data_lines: List[str] = []

    def flush() -> None:
        if not data_lines:
            return
        data = "\n".join(data_lines)
        data_lines.clear()
        if data == "[DONE]":
            return
        try:
            event = load_json_bytes(data.encode("utf-8"))
        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            DuplicateJsonKeyError,
            ValueError,
        ):
            raise ProviderFailure("INVALID_PROVIDER_JSON")
        if not isinstance(event, dict):
            raise ProviderFailure("INVALID_PROVIDER_JSON")
        events.append(event)

    for line in text.splitlines():
        if not line:
            flush()
        elif line.startswith("data:"):
            data_lines.append(line[5:].lstrip())
    flush()
    if not events:
        raise ProviderFailure("INVALID_PROVIDER_JSON")
    return events


def http_post_sse_json(
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
) -> Tuple[List[Dict[str, Any]], int, Optional[str]]:
    if url not in ENDPOINTS.values():
        raise ProviderFailure("ENDPOINT_NOT_ALLOWED")
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ProviderFailure("PROVIDER_REQUEST_TOO_LARGE")

    for attempt in range(MAX_RETRIES + 1):
        request = urllib.request.Request(
            url,
            data=encoded,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise ProviderFailure(
                        "PROVIDER_RESPONSE_TOO_LARGE", attempts=attempt + 1
                    )
                try:
                    events = parse_sse_json_events(raw)
                except ProviderFailure as exc:
                    raise ProviderFailure(exc.code, attempts=attempt + 1)
                return events, attempt + 1, safe_request_id(response.headers)
        except urllib.error.HTTPError as exc:
            status = int(exc.code)
            try:
                exc.read(4096)
            except Exception:
                pass
            if status in {401, 403}:
                failure = ProviderFailure(
                    "AUTH_FAILED", status=status, attempts=attempt + 1
                )
            elif status == 429:
                failure = ProviderFailure(
                    "RATE_LIMITED",
                    retryable=True,
                    status=status,
                    attempts=attempt + 1,
                )
            elif status == 408 or status >= 500:
                failure = ProviderFailure(
                    "PROVIDER_5XX" if status >= 500 else "TIMEOUT",
                    retryable=True,
                    status=status,
                    attempts=attempt + 1,
                )
            else:
                failure = ProviderFailure(
                    "PROVIDER_4XX", status=status, attempts=attempt + 1
                )
        except (urllib.error.URLError, socket.timeout, TimeoutError):
            failure = ProviderFailure(
                "TIMEOUT", retryable=True, attempts=attempt + 1
            )

        if not failure.retryable or attempt >= MAX_RETRIES:
            if failure.retryable and attempt >= MAX_RETRIES:
                raise ProviderFailure(
                    "RETRY_EXHAUSTED",
                    status=failure.status,
                    attempts=attempt + 1,
                )
            raise failure
        time.sleep((2**attempt) + random.random() * 0.25)

    raise ProviderFailure("RETRY_EXHAUSTED", attempts=MAX_RETRIES + 1)


def extract_openai_queries(document: Dict[str, Any]) -> Tuple[List[Tuple[Any, str]], bool]:
    found: List[Tuple[Any, str]] = []
    search_call_seen = False
    output = document.get("output")
    if not isinstance(output, list):
        return found, search_call_seen
    for index, item in enumerate(output):
        if not isinstance(item, dict) or item.get("type") != "web_search_call":
            continue
        action = item.get("action")
        if not isinstance(action, dict) or action.get("type") != "search":
            continue
        search_call_seen = True
        queries = action.get("queries")
        if isinstance(queries, list):
            for query_index, query in enumerate(queries):
                found.append(
                    (query, "$.output[%d].action.queries[%d]" % (index, query_index))
                )
        if "query" in action:
            found.append((action.get("query"), "$.output[%d].action.query" % index))
    return found, search_call_seen


def extract_openai_sources(document: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    for item in document.get("output", []) if isinstance(document.get("output"), list) else []:
        if not isinstance(item, dict) or item.get("type") != "web_search_call":
            continue
        action = item.get("action")
        if not isinstance(action, dict):
            continue
        for source in action.get("sources", []) if isinstance(action.get("sources"), list) else []:
            if isinstance(source, dict) and isinstance(source.get("url"), str):
                urls.append(source["url"])
    return list(dict.fromkeys(urls))[:100]


def extract_gemini_queries(document: Dict[str, Any]) -> Tuple[List[Tuple[Any, str]], bool]:
    found: List[Tuple[Any, str]] = []
    search_call_seen = False
    for container_name in ("steps", "outputs"):
        container = document.get(container_name)
        if not isinstance(container, list):
            continue
        for index, item in enumerate(container):
            if not isinstance(item, dict) or item.get("type") != "google_search_call":
                continue
            search_call_seen = True
            arguments = item.get("arguments")
            if not isinstance(arguments, dict):
                continue
            queries = arguments.get("queries")
            if isinstance(queries, list):
                for query_index, query in enumerate(queries):
                    found.append(
                        (
                            query,
                            "$.%s[%d].arguments.queries[%d]"
                            % (container_name, index, query_index),
                        )
                    )
            if "query" in arguments:
                found.append(
                    (
                        arguments.get("query"),
                        "$.%s[%d].arguments.query" % (container_name, index),
                    )
                )

    candidates = document.get("candidates")
    if isinstance(candidates, list):
        for candidate_index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                continue
            metadata_key = "groundingMetadata"
            metadata = candidate.get(metadata_key)
            if not isinstance(metadata, dict):
                metadata_key = "grounding_metadata"
                metadata = candidate.get(metadata_key)
            if not isinstance(metadata, dict):
                continue
            queries_key = "webSearchQueries"
            queries = metadata.get(queries_key)
            if not isinstance(queries, list):
                queries_key = "web_search_queries"
                queries = metadata.get(queries_key)
            if isinstance(queries, list):
                search_call_seen = True
                for query_index, query in enumerate(queries):
                    found.append(
                        (
                            query,
                            "$.candidates[%d].%s.%s[%d]"
                            % (
                                candidate_index,
                                metadata_key,
                                queries_key,
                                query_index,
                            ),
                        )
                    )
    return found, search_call_seen


def extract_claude_search_events(
    document: Dict[str, Any]
) -> Tuple[List[Tuple[str, Any, str]], Set[str], bool]:
    calls: List[Tuple[str, Any, str]] = []
    result_ids: Set[str] = set()
    search_call_seen = False
    content = document.get("content")
    if not isinstance(content, list):
        return calls, result_ids, search_call_seen
    for index, item in enumerate(content):
        if not isinstance(item, dict):
            continue
        if item.get("type") == "server_tool_use" and item.get("name") == "web_search":
            search_call_seen = True
            tool_id = item.get("id")
            tool_input = item.get("input")
            if (
                isinstance(tool_id, str)
                and tool_id
                and isinstance(tool_input, dict)
                and "query" in tool_input
            ):
                calls.append(
                    (tool_id, tool_input["query"], "$.content[%d].input.query" % index)
                )
        elif item.get("type") == "web_search_tool_result":
            tool_use_id = item.get("tool_use_id")
            if isinstance(tool_use_id, str) and tool_use_id:
                result_ids.add(tool_use_id)
    return calls, result_ids, search_call_seen


def extract_claude_queries(document: Dict[str, Any]) -> Tuple[List[Tuple[Any, str]], bool]:
    calls, result_ids, search_call_seen = extract_claude_search_events(document)
    found = [(query, path) for tool_id, query, path in calls if tool_id in result_ids]
    return found, search_call_seen


def extract_claude_tool_errors(document: Dict[str, Any]) -> List[str]:
    codes: List[str] = []
    content = document.get("content")
    if not isinstance(content, list):
        return codes
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "web_search_tool_result":
            continue
        result = item.get("content")
        if isinstance(result, dict) and result.get("type") == "web_search_tool_result_error":
            code = result.get("error_code")
            if isinstance(code, str):
                codes.append(code)
    return codes


def extract_claude_sources(document: Dict[str, Any]) -> List[str]:
    urls: List[str] = []
    content = document.get("content")
    if not isinstance(content, list):
        return urls
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "web_search_tool_result":
            continue
        result = item.get("content")
        if not isinstance(result, list):
            continue
        for entry in result:
            if isinstance(entry, dict) and isinstance(entry.get("url"), str):
                urls.append(entry["url"])
    return list(dict.fromkeys(urls))[:100]


def collect_all_urls(document: Any) -> List[str]:
    urls: List[str] = []

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "url" and isinstance(item, str) and item.startswith(("http://", "https://")):
                    urls.append(item)
                else:
                    visit(item)
        elif isinstance(value, list):
            for item in value:
                visit(item)

    visit(document)
    return list(dict.fromkeys(urls))[:100]


def output_text_openai(document: Dict[str, Any]) -> str:
    if isinstance(document.get("output_text"), str):
        return document["output_text"]
    chunks: List[str] = []
    output = document.get("output")
    if isinstance(output, list):
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
    return "\n".join(chunks)


def output_text_gemini(document: Dict[str, Any]) -> str:
    if isinstance(document.get("output_text"), str):
        return document["output_text"]
    chunks: List[str] = []
    for container_name in ("steps", "outputs"):
        container = document.get(container_name)
        if not isinstance(container, list):
            continue
        for item in container:
            if not isinstance(item, dict) or item.get("type") != "model_output":
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
    candidates = document.get("candidates")
    if isinstance(candidates, list):
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            content = candidate.get("content")
            if not isinstance(content, dict):
                continue
            for part in content.get("parts", []) if isinstance(content.get("parts"), list) else []:
                if isinstance(part, dict) and isinstance(part.get("text"), str):
                    chunks.append(part["text"])
    return "\n".join(chunks)


def output_text_claude(document: Dict[str, Any]) -> str:
    chunks: List[str] = []
    content = document.get("content")
    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text" and isinstance(item.get("text"), str):
                chunks.append(item["text"])
    return "\n".join(chunks)


def output_text_perplexity(document: Dict[str, Any]) -> str:
    choices = document.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    first = choices[0]
    if not isinstance(first, dict):
        return ""
    message = first.get("message")
    if isinstance(message, dict) and isinstance(message.get("content"), str):
        return message["content"]
    return ""


def extract_perplexity_stream_queries(
    events: Sequence[Dict[str, Any]],
) -> Tuple[List[Tuple[Any, str]], bool]:
    """Extract Sonar Pro search keywords from concise reasoning SSE events."""
    found: List[Tuple[Any, str]] = []
    search_call_seen = False
    for event_index, event in enumerate(events):
        choices = event.get("choices")
        if not isinstance(choices, list):
            continue
        for choice_index, choice in enumerate(choices):
            if not isinstance(choice, dict):
                continue
            delta = choice.get("delta")
            if not isinstance(delta, dict):
                continue
            steps = delta.get("reasoning_steps")
            if not isinstance(steps, list):
                continue
            for step_index, step in enumerate(steps):
                if not isinstance(step, dict) or step.get("type") != "web_search":
                    continue
                search_call_seen = True
                web_search = step.get("web_search")
                if not isinstance(web_search, dict):
                    continue
                keywords = web_search.get("search_keywords")
                if not isinstance(keywords, list):
                    continue
                for keyword_index, keyword in enumerate(keywords):
                    found.append(
                        (
                            keyword,
                            "$.events[%d].choices[%d].delta.reasoning_steps[%d].web_search.search_keywords[%d]"
                            % (
                                event_index,
                                choice_index,
                                step_index,
                                keyword_index,
                            ),
                        )
                    )
    return found, search_call_seen


def extract_perplexity_stream_metadata(
    events: Sequence[Dict[str, Any]],
) -> Tuple[Optional[str], Optional[int], List[str]]:
    actual_model: Optional[str] = None
    provider_search_count: Optional[int] = None
    urls: List[str] = []
    for event in events:
        model = exposed_model(event)
        if model:
            actual_model = model
        usage = event.get("usage")
        if isinstance(usage, dict) and isinstance(
            usage.get("num_search_queries"), int
        ):
            provider_search_count = usage["num_search_queries"]
        search_results = event.get("search_results")
        if isinstance(search_results, list):
            for item in search_results:
                if isinstance(item, dict) and isinstance(item.get("url"), str):
                    urls.append(item["url"])
    return actual_model, provider_search_count, list(dict.fromkeys(urls))[:100]


def parse_synthetic_queries(text: str) -> List[Tuple[str, Optional[str]]]:
    if not isinstance(text, str) or not text.strip():
        return []
    candidates = [text.strip()]
    for match in re.finditer(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE):
        candidates.append(match.group(1).strip())

    decoder = json.JSONDecoder()
    for raw in list(candidates):
        for marker in ("{", "["):
            offset = 0
            while True:
                position = raw.find(marker, offset)
                if position < 0:
                    break
                try:
                    value, _ = decoder.raw_decode(raw[position:])
                    candidates.append(value)  # type: ignore[arg-type]
                    break
                except json.JSONDecodeError:
                    offset = position + 1

    for candidate in candidates:
        value: Any = candidate
        if isinstance(candidate, str):
            try:
                value = json.loads(candidate)
            except json.JSONDecodeError:
                continue
        if isinstance(value, dict):
            value = value.get("queries")
        if not isinstance(value, list):
            continue
        result: List[Tuple[str, Optional[str]]] = []
        for item in value:
            if isinstance(item, str):
                result.append((item, None))
            elif isinstance(item, dict):
                query = item.get("query") if isinstance(item.get("query"), str) else item.get("text")
                if isinstance(query, str):
                    result.append((query, None))
        if result:
            return result
    return []


def exposed_model(document: Dict[str, Any]) -> Optional[str]:
    for key in ("model", "modelVersion", "model_version"):
        value = document.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return None


def base_run(provider: str, model: str, run_index: int, kind: str) -> Dict[str, Any]:
    return {
        "provider": provider,
        "product_surface": {
            "openai": "OpenAI Responses API",
            "gemini": "Gemini Interactions API",
            "google_ai_mode": "Google AI Mode simulation via Gemini API",
            "claude": "Claude Messages API",
            "perplexity": "Perplexity Sonar API",
        }[provider],
        "requested_model": model,
        "actual_model": None,
        "run_index": run_index,
        "call_kind": kind,
        "api_attempted": True,
        "fallback_reason": None,
        "status": "failed",
        "observability_status": "failed",
        "queries": [],
        "observed_query_count": None,
        "provider_search_query_count": None,
        "sources": [],
        "http_attempts": 0,
        "request_id": None,
        "warnings": [],
        "failure": None,
        "raw_api_response_persisted": False,
    }


def attach_queries(
    run: Dict[str, Any],
    values: Iterable[Tuple[Any, Optional[str]]],
    source_type: str,
    secrets: Iterable[str],
) -> None:
    if source_type == "observed_tool_query":
        queries, secret_dropped, invalid_dropped = ordered_unique_observed_queries(
            values, secrets
        )
        redacted = False
        if secret_dropped:
            run["warnings"].append("OBSERVED_QUERY_DROPPED_SECRET")
        if invalid_dropped:
            run["warnings"].append("OBSERVED_QUERY_DROPPED_INVALID")
    else:
        queries, redacted = ordered_unique_queries(values, secrets)
    for query in queries:
        query["source_type"] = source_type
    run["queries"] = queries
    if redacted:
        run["warnings"].append("SECRET_REDACTED_FROM_QUERY")


def provider_failure_run(
    provider: str,
    model: str,
    run_index: int,
    kind: str,
    failure: ProviderFailure,
) -> Dict[str, Any]:
    run = base_run(provider, model, run_index, kind)
    run["http_attempts"] = failure.attempts
    run["fallback_reason"] = failure.code
    run["failure"] = {
        "code": failure.code,
        "message": "Provider call failed; raw provider details were not retained.",
        "retryable": bool(failure.retryable),
        "http_status": failure.status,
    }
    return run


def collect_openai(
    request: Dict[str, Any], run_index: int, model: str, key: str, secrets: Iterable[str]
) -> Dict[str, Any]:
    kind = call_kind("openai", request["mode"], request["live_research"])
    run = base_run("openai", model, run_index, kind)
    if kind == "observed_api":
        web_search_tool: Dict[str, Any] = {"type": "web_search"}
        location = provider_location(request)
        if location:
            web_search_tool["user_location"] = location
        payload = {
            "model": model,
            "input": observed_prompt(request),
            "store": False,
            "tools": [web_search_tool],
            "tool_choice": "required",
            "max_tool_calls": MAX_SEARCH_TOOL_CALLS_PER_RUN,
            "include": ["web_search_call.action.sources"],
        }
    else:
        payload = {
            "model": model,
            "input": synthetic_prompt(request, "OpenAI API"),
            "store": False,
        }
    document, attempts, request_id = http_post_json(
        ENDPOINTS["openai"],
        {"Authorization": "Bearer " + key, "Content-Type": "application/json"},
        payload,
    )
    run["http_attempts"] = attempts
    run["request_id"] = request_id
    run["actual_model"] = exposed_model(document)
    if run["actual_model"] is None:
        run["warnings"].append("ACTUAL_MODEL_NOT_EXPOSED")

    if kind == "observed_api":
        values, searched = extract_openai_queries(document)
        attach_queries(run, values, "observed_tool_query", secrets)
        run["sources"] = redact_value(extract_openai_sources(document), secrets)
        run["observed_query_count"] = len(run["queries"])
        if run["queries"]:
            run["status"] = "success"
            run["observability_status"] = "query_strings_exposed"
        elif searched:
            run["status"] = "degraded"
            run["observability_status"] = "search_used_query_strings_hidden"
            run["warnings"].append("QUERY_TRACE_MISSING")
        else:
            run["status"] = "degraded"
            run["observability_status"] = "search_not_used"
            run["warnings"].append("SEARCH_NOT_USED")
    else:
        run["fallback_reason"] = "LIVE_RESEARCH_DISABLED"
        values = parse_synthetic_queries(output_text_openai(document))
        attach_queries(run, values, "synthetic_provider_query", secrets)
        if run["queries"]:
            run["status"] = "success"
            run["observability_status"] = "simulation_only"
        else:
            run["status"] = "degraded"
            run["observability_status"] = "simulation_only"
            run["warnings"].append("INVALID_PROVIDER_JSON")
    return run


def collect_gemini_like(
    provider: str,
    request: Dict[str, Any],
    run_index: int,
    model: str,
    key: str,
    secrets: Iterable[str],
) -> Dict[str, Any]:
    kind = call_kind(provider, request["mode"], request["live_research"])
    run = base_run(provider, model, run_index, kind)
    if kind == "observed_api":
        payload = {
            "model": model,
            "input": observed_prompt(request),
            "tools": [{"type": "google_search"}],
        }
    else:
        surface = "Google AI Mode" if provider == "google_ai_mode" else "Gemini API"
        payload = {"model": model, "input": synthetic_prompt(request, surface)}
    document, attempts, request_id = http_post_json(
        ENDPOINTS[provider],
        {"x-goog-api-key": key, "Content-Type": "application/json"},
        payload,
    )
    run["http_attempts"] = attempts
    run["request_id"] = request_id
    run["actual_model"] = exposed_model(document)
    if run["actual_model"] is None:
        run["warnings"].append("ACTUAL_MODEL_NOT_EXPOSED")
    run["sources"] = redact_value(collect_all_urls(document), secrets)

    if kind == "observed_api":
        values, searched = extract_gemini_queries(document)
        attach_queries(run, values, "observed_tool_query", secrets)
        run["observed_query_count"] = len(run["queries"])
        if run["queries"]:
            run["status"] = "success"
            run["observability_status"] = "query_strings_exposed"
        elif searched:
            run["status"] = "degraded"
            run["observability_status"] = "search_used_query_strings_hidden"
            run["warnings"].append("QUERY_TRACE_MISSING")
        else:
            run["status"] = "degraded"
            run["observability_status"] = "search_not_used"
            run["warnings"].append("SEARCH_NOT_USED")
    else:
        run["fallback_reason"] = (
            "SURFACE_API_UNAVAILABLE"
            if provider == "google_ai_mode"
            else "LIVE_RESEARCH_DISABLED"
        )
        values = parse_synthetic_queries(output_text_gemini(document))
        attach_queries(run, values, "synthetic_provider_query", secrets)
        if run["queries"]:
            run["status"] = "success"
            run["observability_status"] = "simulation_only"
        else:
            run["status"] = "degraded"
            run["observability_status"] = "simulation_only"
            run["warnings"].append("INVALID_PROVIDER_JSON")
    return run


def collect_claude(
    request: Dict[str, Any], run_index: int, model: str, key: str, secrets: Iterable[str]
) -> Dict[str, Any]:
    kind = call_kind("claude", request["mode"], request["live_research"])
    run = base_run("claude", model, run_index, kind)
    messages: List[Dict[str, Any]] = [
        {
            "role": "user",
            "content": observed_prompt(request)
            if kind == "observed_api"
            else synthetic_prompt(request, "Claude API"),
        }
    ]
    tools = None
    if kind == "observed_api":
        search_tool: Dict[str, Any] = {
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": MAX_SEARCH_TOOL_CALLS_PER_RUN,
        }
        location = provider_location(request)
        if location:
            search_tool["user_location"] = location
        tools = [search_tool]
    observed_values: List[Tuple[Any, Optional[str]]] = []
    pending_observed: Dict[str, Tuple[Any, Optional[str]]] = {}
    completed_tool_ids: Set[str] = set()
    search_call_seen = False
    sources: List[str] = []
    tool_errors: List[str] = []
    total_attempts = 0
    request_id: Optional[str] = None
    final_document: Dict[str, Any] = {}
    actual_model: Optional[str] = None

    for continuation in range(MAX_CLAUDE_CONTINUATIONS + 1):
        payload: Dict[str, Any] = {
            "model": model,
            "max_tokens": 2048,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools
        try:
            document, attempts, call_request_id = http_post_json(
                ENDPOINTS["claude"],
                {
                    "x-api-key": key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json",
                },
                payload,
            )
        except ProviderFailure as failure:
            failure.attempts += total_attempts
            raise
        total_attempts += attempts
        request_id = request_id or call_request_id
        final_document = document
        actual_model = exposed_model(document) or actual_model
        calls, result_ids, saw_search_call = extract_claude_search_events(document)
        search_call_seen = search_call_seen or saw_search_call
        for tool_id, query, path in calls:
            continuation_path = (
                "$continuations[%d]%s" % (continuation, path[1:]) if path else None
            )
            if tool_id not in completed_tool_ids:
                pending_observed.setdefault(tool_id, (query, continuation_path))
        for tool_id in result_ids:
            if tool_id in pending_observed and tool_id not in completed_tool_ids:
                observed_values.append(pending_observed.pop(tool_id))
                completed_tool_ids.add(tool_id)
        sources.extend(extract_claude_sources(document))
        tool_errors.extend(extract_claude_tool_errors(document))
        if kind != "observed_api":
            break
        if document.get("stop_reason") != "pause_turn":
            break
        if continuation >= MAX_CLAUDE_CONTINUATIONS:
            run["warnings"].append("CLAUDE_CONTINUATION_LIMIT_REACHED")
            break
        content = document.get("content")
        if not isinstance(content, list):
            run["warnings"].append("INVALID_PROVIDER_JSON")
            break
        messages.append({"role": "assistant", "content": content})

    run["http_attempts"] = total_attempts
    run["request_id"] = request_id
    run["actual_model"] = actual_model
    if run["actual_model"] is None:
        run["warnings"].append("ACTUAL_MODEL_NOT_EXPOSED")
    run["sources"] = redact_value(list(dict.fromkeys(sources))[:100], secrets)
    for code in tool_errors:
        run["warnings"].append("CLAUDE_TOOL_ERROR_" + code.upper())
    if pending_observed:
        run["warnings"].append("CLAUDE_PENDING_SEARCH_NOT_OBSERVED")

    if kind == "observed_api":
        attach_queries(run, observed_values, "observed_tool_query", secrets)
        run["observed_query_count"] = len(run["queries"])
        if run["queries"]:
            run["status"] = (
                "success" if not tool_errors and not pending_observed else "degraded"
            )
            run["observability_status"] = "query_strings_exposed"
        else:
            run["status"] = "degraded"
            run["observability_status"] = (
                "search_not_used"
                if pending_observed or not search_call_seen
                else "search_used_query_strings_hidden"
            )
            run["warnings"].append(
                "QUERY_TRACE_INCOMPLETE"
                if pending_observed
                else ("QUERY_TRACE_MISSING" if search_call_seen else "SEARCH_NOT_USED")
            )
    else:
        run["fallback_reason"] = "LIVE_RESEARCH_DISABLED"
        values = parse_synthetic_queries(output_text_claude(final_document))
        attach_queries(run, values, "synthetic_provider_query", secrets)
        run["observability_status"] = "simulation_only"
        if run["queries"]:
            run["status"] = "success"
        else:
            run["status"] = "degraded"
            run["warnings"].append("INVALID_PROVIDER_JSON")
    return run


def collect_perplexity(
    request: Dict[str, Any], run_index: int, model: str, key: str, secrets: Iterable[str]
) -> Dict[str, Any]:
    kind = call_kind(
        "perplexity", request["mode"], request["live_research"], model
    )
    run = base_run("perplexity", model, run_index, kind)
    headers = {
        "Authorization": "Bearer " + key,
        "Content-Type": "application/json",
    }

    if kind == "observed_api":
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": observed_prompt(request)}],
            "stream": True,
            "stream_mode": "concise",
            "web_search_options": {"search_type": "pro"},
        }
        events, attempts, request_id = http_post_sse_json(
            ENDPOINTS["perplexity"], headers, payload
        )
        run["http_attempts"] = attempts
        run["request_id"] = request_id
        values, searched = extract_perplexity_stream_queries(events)
        attach_queries(run, values, "observed_tool_query", secrets)
        actual_model, search_count, sources = extract_perplexity_stream_metadata(
            events
        )
        run["actual_model"] = actual_model
        run["provider_search_query_count"] = search_count
        run["sources"] = redact_value(sources, secrets)
        run["observed_query_count"] = len(run["queries"])
        if run["actual_model"] is None:
            run["warnings"].append("ACTUAL_MODEL_NOT_EXPOSED")
        if run["queries"]:
            run["status"] = "success"
            run["observability_status"] = "query_strings_exposed"
        elif searched:
            run["status"] = "degraded"
            run["observability_status"] = "search_used_query_strings_hidden"
            run["warnings"].append("QUERY_TRACE_MISSING")
        else:
            run["status"] = "degraded"
            run["observability_status"] = "search_not_used"
            run["warnings"].append("SEARCH_NOT_USED")
        return run

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": synthetic_prompt(request, "Perplexity Sonar API"),
            }
        ],
    }
    run["fallback_reason"] = (
        "LIVE_RESEARCH_DISABLED"
        if not request["live_research"]
        else "OBSERVED_TRACE_UNAVAILABLE_FOR_MODEL"
    )
    if not request["live_research"]:
        payload["web_search_options"] = {"disable_search": True}
    document, attempts, request_id = http_post_json(
        ENDPOINTS["perplexity"], headers, payload
    )
    run["http_attempts"] = attempts
    run["request_id"] = request_id
    run["actual_model"] = exposed_model(document)
    if run["actual_model"] is None:
        run["warnings"].append("ACTUAL_MODEL_NOT_EXPOSED")
    values = parse_synthetic_queries(output_text_perplexity(document))
    attach_queries(run, values, "synthetic_provider_query", secrets)

    usage = document.get("usage")
    if isinstance(usage, dict) and isinstance(usage.get("num_search_queries"), int):
        run["provider_search_query_count"] = usage["num_search_queries"]
    search_results = document.get("search_results")
    if isinstance(search_results, list):
        urls = [
            item["url"]
            for item in search_results
            if isinstance(item, dict) and isinstance(item.get("url"), str)
        ]
        run["sources"] = redact_value(list(dict.fromkeys(urls))[:100], secrets)
    run["observability_status"] = "simulation_only"
    if request["live_research"]:
        run["warnings"].append(
            "PERPLEXITY_QUERY_TRACE_NOT_AVAILABLE_FOR_CONFIGURATION"
        )
    if run["queries"]:
        run["status"] = "success"
    else:
        run["status"] = "degraded"
        run["warnings"].append("INVALID_PROVIDER_JSON")
    return run


COLLECTORS: Dict[str, Callable[..., Dict[str, Any]]] = {
    "openai": collect_openai,
    "gemini": lambda request, run_index, model, key, secrets: collect_gemini_like(
        "gemini", request, run_index, model, key, secrets
    ),
    "google_ai_mode": lambda request, run_index, model, key, secrets: collect_gemini_like(
        "google_ai_mode", request, run_index, model, key, secrets
    ),
    "claude": collect_claude,
    "perplexity": collect_perplexity,
}


def provider_synthetic_fallback_request(request: Dict[str, Any]) -> Dict[str, Any]:
    fallback_request = dict(request)
    fallback_request["mode"] = "hybrid"
    fallback_request["live_research"] = False
    return fallback_request


def observed_fallback_reason(run: Dict[str, Any]) -> str:
    warnings = run.get("warnings")
    if isinstance(warnings, list):
        if "QUERY_TRACE_MISSING" in warnings or "QUERY_TRACE_INCOMPLETE" in warnings:
            return "QUERY_TRACE_MISSING"
        if "SEARCH_NOT_USED" in warnings:
            return "SEARCH_NOT_USED"
    return "OBSERVED_QUERY_TRACE_UNAVAILABLE"


def merge_provider_synthetic_fallback(
    observed_run: Dict[str, Any], synthetic_run: Dict[str, Any]
) -> Dict[str, Any]:
    """Preserve the observed attempt while using same-provider synthetic evidence."""
    reason = observed_fallback_reason(observed_run)
    observed_attempts = observed_run.get("http_attempts", 0)
    synthetic_attempts = synthetic_run.get("http_attempts", 0)
    observed_run["call_kind"] = "observed_api_then_provider_synthetic"
    observed_run["fallback_reason"] = reason
    observed_run["fallback_http_attempts"] = synthetic_attempts
    observed_run["fallback_request_id"] = synthetic_run.get("request_id")
    observed_run["http_attempts"] = (
        observed_attempts if isinstance(observed_attempts, int) else 0
    ) + (synthetic_attempts if isinstance(synthetic_attempts, int) else 0)
    if observed_run.get("actual_model") is None:
        observed_run["actual_model"] = synthetic_run.get("actual_model")
    observed_sources = observed_run.get("sources")
    synthetic_sources = synthetic_run.get("sources")
    sources: List[str] = []
    for collection in (observed_sources, synthetic_sources):
        if isinstance(collection, list):
            sources.extend(item for item in collection if isinstance(item, str))
    observed_run["sources"] = list(dict.fromkeys(sources))[:100]
    observed_run["queries"] = synthetic_run.get("queries", [])
    observed_run["observed_query_count"] = 0
    observed_run["status"] = synthetic_run.get("status", "degraded")
    observed_run["failure"] = synthetic_run.get("failure")
    existing_warnings = observed_run.get("warnings")
    fallback_warnings = synthetic_run.get("warnings")
    warnings = existing_warnings if isinstance(existing_warnings, list) else []
    if isinstance(fallback_warnings, list):
        warnings.extend(fallback_warnings)
    warnings.append(
        "PROVIDER_SYNTHETIC_FALLBACK_USED"
        if observed_run["queries"]
        else "PROVIDER_SYNTHETIC_FALLBACK_FAILED"
    )
    observed_run["warnings"] = list(dict.fromkeys(warnings))
    return observed_run


def pending_item(
    request: Dict[str, Any],
    provider: str,
    model: str,
    run_index: int,
    reason: str,
    api_attempted: bool = False,
    prior_api_attempts: int = 0,
) -> Dict[str, Any]:
    return {
        "provider": provider,
        "requested_model": model,
        "run_index": run_index,
        "reason": reason,
        "api_attempted": api_attempted,
        "prior_api_attempts": prior_api_attempts,
        "fallback_reason": reason,
        "recommended_source_type": "heuristic_simulation",
        "simulation_prompt": synthetic_prompt(request, provider.replace("_", " ")),
    }


def collect_document(request: Dict[str, Any], allow_api_calls: bool) -> Tuple[Dict[str, Any], int]:
    secrets = all_environment_secrets()
    plan = build_plan(request, secrets)
    if plan["plan"]["api_authorization_required"]:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "error": {
                "code": "SCOPE_AUTHORIZATION_REQUIRED",
                "message": "The requested plan exceeds the ordinary automatic scope. Confirm the larger run/query scope, then set expanded_scope_authorized to true.",
            },
            "plan": plan["plan"],
        }
        return redact_value(payload, secrets), 2
    planned_calls = plan["plan"]["planned_top_level_api_calls"]
    if planned_calls and not allow_api_calls:
        payload = {
            "schema_version": SCHEMA_VERSION,
            "status": "error",
            "error": {
                "code": "API_EXECUTION_FLAG_REQUIRED",
                "message": "The API-first plan selected real provider APIs; rerun deliberately with --allow-api-calls. The normal skill workflow supplies this flag automatically after planning.",
            },
            "plan": plan["plan"],
        }
        return redact_value(payload, secrets), 2

    runs: List[Dict[str, Any]] = []
    pending: List[Dict[str, Any]] = []
    failures: List[Dict[str, Any]] = []

    for provider in request["providers"]:
        model = resolve_model(provider, request)
        key, _ = credential_for(provider)
        kind = call_kind(
            provider, request["mode"], request["live_research"], model
        )
        for run_index in range(1, request["runs_per_provider"] + 1):
            if kind == "heuristic_simulation":
                pending.append(
                    pending_item(
                        request,
                        provider,
                        model,
                        run_index,
                        "SIMULATED_ONLY_REQUESTED",
                    )
                )
                continue
            if kind == "unsupported":
                failures.append(
                    {
                        "provider": provider,
                        "run_index": run_index,
                        "code": "OBSERVED_MODE_UNSUPPORTED",
                        "degraded": False,
                    }
                )
                continue
            if not request["network_access"] or not request["allow_paid_api_calls"]:
                reason = (
                    "NETWORK_ACCESS_DISABLED"
                    if not request["network_access"]
                    else "PAID_API_CALLS_DISABLED"
                )
                pending.append(
                    pending_item(request, provider, model, run_index, reason)
                )
                failures.append(
                    {
                        "provider": provider,
                        "run_index": run_index,
                        "code": reason,
                        "degraded": True,
                    }
                )
                continue
            model_status = model_api_compatibility(provider, model)
            if model_status in {
                "incompatible_model_id",
                "operation_capability_unverified",
            }:
                reason = (
                    "MODEL_OPERATION_UNSUPPORTED_OR_UNVERIFIED"
                    if model_status == "operation_capability_unverified"
                    else "MODEL_INCOMPATIBLE"
                )
                if request["mode"] != "observed_only":
                    pending.append(
                        pending_item(
                            request,
                            provider,
                            model,
                            run_index,
                            reason,
                        )
                    )
                failures.append(
                    {
                        "provider": provider,
                        "run_index": run_index,
                        "code": reason,
                        "degraded": True,
                    }
                )
                continue
            if not key:
                if request["mode"] != "observed_only":
                    pending.append(
                        pending_item(
                            request, provider, model, run_index, "CREDENTIAL_MISSING"
                        )
                    )
                failures.append(
                    {
                        "provider": provider,
                        "run_index": run_index,
                        "code": "CREDENTIAL_MISSING",
                        "degraded": True,
                    }
                )
                continue
            try:
                run = COLLECTORS[provider](request, run_index, model, key, secrets)
            except ProviderFailure as exc:
                run = provider_failure_run(provider, model, run_index, kind, exc)
            if (
                kind == "observed_api"
                and request["mode"] != "observed_only"
                and not run.get("queries")
                and run.get("failure") is None
            ):
                fallback_request = provider_synthetic_fallback_request(request)
                try:
                    synthetic_run = COLLECTORS[provider](
                        fallback_request, run_index, model, key, secrets
                    )
                except ProviderFailure as exc:
                    synthetic_run = provider_failure_run(
                        provider, model, run_index, "provider_synthetic", exc
                    )
                run = merge_provider_synthetic_fallback(run, synthetic_run)
            if not run.get("queries"):
                reason = (
                    run.get("failure", {}).get("code")
                    if isinstance(run.get("failure"), dict)
                    else "QUERY_TRACE_MISSING"
                )
                run["fallback_reason"] = reason
                if request["mode"] != "observed_only":
                    attempts = run.get("http_attempts")
                    pending.append(
                        pending_item(
                            request,
                            provider,
                            model,
                            run_index,
                            reason,
                            api_attempted=True,
                            prior_api_attempts=(
                                attempts if isinstance(attempts, int) else 0
                            ),
                        )
                    )
                failures.append(
                    {
                        "provider": provider,
                        "run_index": run_index,
                        "code": reason,
                        "degraded": True,
                    }
                )
            runs.append(redact_value(run, secrets))

    expected_runs = len(request["providers"]) * request["runs_per_provider"]
    successful_runs = sum(bool(run.get("queries")) for run in runs)
    if successful_runs == expected_runs:
        status = "complete"
        exit_code = 0
    elif successful_runs or pending:
        status = "partial"
        exit_code = 1
    else:
        status = "error"
        exit_code = 2

    payload = {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "collection": {
            "seed_input": request["seed_input"],
            "detected_language": request["detected_language"],
            "target_locale": request["target_locale"],
            "mode": request["mode"],
            "execution_policy": "api_first",
            "network_access": request["network_access"],
            "allow_paid_api_calls": request["allow_paid_api_calls"],
            "expanded_scope_authorized": request["expanded_scope_authorized"],
            "api_first_plan_executed": bool(allow_api_calls or planned_calls == 0),
            "providers": request["providers"],
            "runs_per_provider": request["runs_per_provider"],
            "queries_per_synthetic_run": request["queries_per_run"],
            "analysis_timestamp": utc_now(),
            "raw_api_responses_persisted": False,
            "api_keys_persisted": False,
        },
        "runs": runs,
        "api_plan": plan["plan"]["providers"],
        "pending_host_simulations": pending,
        "failures": failures,
        "warnings": (
            ["REGION_UNSPECIFIED"] if request["target_locale"] == "unspecified" else []
        ),
    }
    return redact_value(payload, secrets), exit_code


def emit(payload: Dict[str, Any], pretty: bool) -> None:
    json.dump(
        payload,
        sys.stdout,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )
    sys.stdout.write("\n")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan or collect query fan-out candidates without persisting raw API responses."
    )
    parser.add_argument("command", choices=("plan", "collect"))
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 JSON file or - for stdin")
    parser.add_argument(
        "--allow-api-calls",
        action="store_true",
        help="Open the deliberate local network gate after reviewing the sanitized API-first plan.",
    )
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    secrets = all_environment_secrets()
    try:
        request = validate_request(read_document(args.input))
    except (ConfigError, OSError) as exc:
        code = exc.args[0] if isinstance(exc, ConfigError) and exc.args else "INPUT_READ_FAILED"
        emit(
            {
                "schema_version": SCHEMA_VERSION,
                "status": "error",
                "error": {
                    "code": code,
                    "message": "The local request document could not be accepted.",
                },
            },
            args.pretty,
        )
        return 2

    if args.command == "plan":
        emit(build_plan(request, secrets), args.pretty)
        return 0
    payload, exit_code = collect_document(request, args.allow_api_calls)
    emit(payload, args.pretty)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
