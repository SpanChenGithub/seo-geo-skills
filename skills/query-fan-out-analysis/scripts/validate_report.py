#!/usr/bin/env python3
"""Validate query fan-out report structure, provenance, scores, and safety."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

from collect_queries import (
    DuplicateJsonKeyError,
    MAX_INPUT_BYTES,
    PROVIDERS,
    all_environment_secrets,
    load_json_bytes,
    normalize_exact,
)


VALIDATOR_VERSION = "1.2"
REPORT_SCHEMA_VERSION = "1.2"
TOP_LEVEL_FIELDS = {
    "schema_version",
    "status",
    "input",
    "intent_analysis",
    "configuration",
    "external_search_signals",
    "platforms",
    "cross_platform_clusters",
    "coverage_matrix",
    "page_coverage",
    "recommended_page_topics",
    "assumptions",
    "limitations",
    "failures",
    "provenance",
}
SOURCE_TYPES = {
    "observed_tool_query",
    "synthetic_provider_query",
    "heuristic_simulation",
}
FORMS = {
    "related_topic",
    "implicit_question",
    "comparison",
    "recency",
    "reformulation",
    "contextual_variation",
    "next_step",
}
INFORMATION_GAPS = {
    "disambiguation",
    "entity_attribute",
    "journey_stage",
    "trust_signal",
    "comparison_criteria",
    "action_and_risk",
}
JOURNEY_STAGES = {
    None,
    "awareness",
    "education",
    "evaluation",
    "decision",
    "implementation",
    "troubleshooting",
}
COVERAGE_STATUSES = {
    "covered",
    "partial",
    "missing",
    "separate_page_candidate",
    "off_page_signal",
    "not_assessable",
}
RECOMMENDATIONS = {
    "update_existing_page",
    "create_new_page",
    "off_page_action",
    "no_action",
    "manual_review",
}
RECOMMENDED_TOPIC_PRIORITIES = {"P0", "P1", "P2"}
RECOMMENDED_TOPIC_ACTIONS = {
    "include_on_page",
    "add_to_page",
    "expand_on_page",
    "retain_on_page",
    "separate_page_candidate",
    "off_page_evidence",
}
ON_PAGE_TOPIC_ACTIONS = {
    "include_on_page",
    "add_to_page",
    "expand_on_page",
    "retain_on_page",
}
EXTERNAL_SIGNAL_TYPES = {
    "serp_result",
    "people_also_ask",
    "related_search",
    "trend",
    "current_fact",
    "other",
}
TRACE_PATTERNS = {
    "openai": re.compile(
        r"^\$\.output\[\d+\]\.action\.(?:queries\[\d+\]|query)$"
    ),
    "gemini": re.compile(
        r"^(?:\$\.(?:steps|outputs)\[\d+\]\.arguments\."
        r"(?:queries\[\d+\]|query)|\$\.candidates\[\d+\]\."
        r"(?:groundingMetadata|grounding_metadata)\."
        r"(?:webSearchQueries|web_search_queries)\[\d+\])$"
    ),
    "claude": re.compile(
        r"^\$(?:continuations\[\d+\])?\.content\[\d+\]\.input\.query$"
    ),
    "perplexity": re.compile(
        r"^\$\.events\[\d+\]\.choices\[\d+\]\.delta\.reasoning_steps"
        r"\[\d+\]\.web_search\.search_keywords\[\d+\]$"
    ),
}
SECRET_PATTERNS = (
    re.compile(r"sk-ant-[A-Za-z0-9_-]{12,}"),
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
    re.compile(r"pplx-[A-Za-z0-9_-]{12,}"),
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]{12,}"),
)


def issue(code: str, path: str, message: str, severity: str = "error") -> Dict[str, str]:
    return {"severity": severity, "code": code, "path": path, "message": message}


def is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_number(value: Any) -> bool:
    return (isinstance(value, int) and not isinstance(value, bool)) or isinstance(value, float)


def label_for_score(score: float) -> str:
    if score >= 0.8:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def check_fields(
    value: Any,
    path: str,
    required: Set[str],
    allowed: Set[str],
    issues: List[Dict[str, str]],
) -> bool:
    if not isinstance(value, dict):
        issues.append(issue("E_TYPE", path, "Expected an object."))
        return False
    for key in sorted(required - set(value)):
        issues.append(issue("E_MISSING_FIELD", path + "/" + key, "Missing required field."))
    for key in sorted(set(value) - allowed):
        issues.append(issue("E_UNKNOWN_FIELD", path + "/" + key, "Unknown field."))
    return True


def require_string(
    value: Any, path: str, issues: List[Dict[str, str]], nullable: bool = False
) -> bool:
    if value is None and nullable:
        return True
    if not isinstance(value, str) or not value.strip():
        issues.append(issue("E_STRING", path, "Expected a non-empty string."))
        return False
    return True


def validate_stability(
    value: Any,
    path: str,
    expected_numerator: int,
    expected_denominator: int,
    issues: List[Dict[str, str]],
) -> None:
    fields = {"numerator", "denominator", "score", "label"}
    if not check_fields(value, path, fields, fields, issues):
        return
    numerator = value.get("numerator")
    denominator = value.get("denominator")
    score = value.get("score")
    label = value.get("label")
    if not is_int(numerator) or numerator < 0:
        issues.append(issue("E_STABILITY_NUMERATOR", path + "/numerator", "Invalid numerator."))
    if not is_int(denominator) or denominator < 1:
        issues.append(issue("E_STABILITY_DENOMINATOR", path + "/denominator", "Invalid denominator."))
    if numerator != expected_numerator:
        issues.append(issue("E_STABILITY_NUMERATOR", path + "/numerator", "Numerator does not match unique occurrences."))
    if denominator != expected_denominator:
        issues.append(issue("E_STABILITY_DENOMINATOR", path + "/denominator", "Denominator does not match valid runs or participating platforms."))
    if expected_denominator > 0:
        expected_score = round(expected_numerator / expected_denominator, 6)
        if not is_number(score) or abs(float(score) - expected_score) > 0.000001:
            issues.append(issue("E_STABILITY_SCORE", path + "/score", "Score does not match numerator / denominator."))
        expected_label = label_for_score(expected_score)
        if label != expected_label:
            issues.append(issue("E_STABILITY_LABEL", path + "/label", "Label does not match score thresholds."))


def iter_strings(value: Any, path: str = "") -> Iterable[Tuple[str, str]]:
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for key, item in value.items():
            child = path + "/" + str(key)
            for result in iter_strings(item, child):
                yield result
    elif isinstance(value, list):
        for index, item in enumerate(value):
            child = path + "/" + str(index)
            for result in iter_strings(item, child):
                yield result


def validate_secret_safety(document: Any, issues: List[Dict[str, str]]) -> None:
    environment_secrets = [item for item in all_environment_secrets() if len(item) >= 8]
    for path, value in iter_strings(document):
        if any(secret in value for secret in environment_secrets):
            issues.append(issue("E_SECRET_VALUE", path, "An environment credential appears in the report."))
            continue
        if any(pattern.search(value) for pattern in SECRET_PATTERNS):
            issues.append(issue("E_SECRET_PATTERN", path, "A credential-shaped value appears in the report."))


def validate_input(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    fields = {
        "seed_input",
        "detected_language",
        "target_locale",
        "persona_or_context",
        "business_context",
        "desired_answer_type",
        "url",
        "page_content_provided",
    }
    if not check_fields(value, path, fields, fields, issues):
        return
    for field in ("seed_input", "detected_language", "target_locale"):
        require_string(value.get(field), path + "/" + field, issues)
    for field in ("persona_or_context", "business_context", "desired_answer_type", "url"):
        require_string(value.get(field), path + "/" + field, issues, nullable=True)
    if not isinstance(value.get("page_content_provided"), bool):
        issues.append(issue("E_BOOLEAN", path + "/page_content_provided", "Expected a boolean."))


def validate_string_list(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    if not isinstance(value, list):
        issues.append(issue("E_STRING_LIST", path, "Expected a string array."))
    elif any(not isinstance(item, str) or not item.strip() for item in value):
        issues.append(issue("E_STRING_LIST", path, "All items must be non-empty strings."))


def validate_intent_analysis(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    fields = {
        "primary_intent",
        "secondary_intents",
        "ambiguities",
        "important_attributes",
        "journey_trust_action_risk_needs",
    }
    if not check_fields(value, path, fields, fields, issues):
        return
    require_string(value.get("primary_intent"), path + "/primary_intent", issues)
    for field in fields - {"primary_intent"}:
        validate_string_list(value.get(field), path + "/" + field, issues)


def validate_external_signals(
    value: Any, path: str, issues: List[Dict[str, str]]
) -> int:
    if not isinstance(value, list):
        issues.append(issue("E_EXTERNAL_SIGNALS", path, "Expected an external-search-signal array."))
        return 0
    fields = {
        "signal_id",
        "signal_type",
        "text",
        "source_url",
        "source_title",
        "retrieved_at",
        "language",
        "locale",
    }
    seen: Set[str] = set()
    for index, signal in enumerate(value):
        signal_path = path + "/" + str(index)
        if not check_fields(signal, signal_path, fields, fields, issues):
            continue
        signal_id = signal.get("signal_id")
        if require_string(signal_id, signal_path + "/signal_id", issues):
            if signal_id in seen:
                issues.append(
                    issue(
                        "E_DUPLICATE_SIGNAL_ID",
                        signal_path + "/signal_id",
                        "External signal IDs must be unique.",
                    )
                )
            seen.add(signal_id)
        if signal.get("signal_type") not in EXTERNAL_SIGNAL_TYPES:
            issues.append(
                issue(
                    "E_EXTERNAL_SIGNAL_TYPE",
                    signal_path + "/signal_type",
                    "Invalid external signal type.",
                )
            )
        for field in ("text", "language", "locale"):
            require_string(signal.get(field), signal_path + "/" + field, issues)
        for field in ("source_url", "source_title", "retrieved_at"):
            require_string(
                signal.get(field), signal_path + "/" + field, issues, nullable=True
            )
        source_url = signal.get("source_url")
        if isinstance(source_url, str) and not source_url.startswith(("https://", "http://")):
            issues.append(
                issue(
                    "E_EXTERNAL_SIGNAL_URL",
                    signal_path + "/source_url",
                    "External signal URL must use HTTP or HTTPS.",
                )
            )
    return len(value)


def validate_configuration(
    value: Any, path: str, issues: List[Dict[str, str]]
) -> Tuple[List[str], List[str], int]:
    fields = {
        "analysis_timestamp",
        "mode",
        "requested_providers",
        "participating_providers",
        "runs_per_provider",
        "queries_per_synthetic_run",
        "api_execution_policy",
        "network_access",
        "allow_paid_api_calls",
        "expanded_scope_authorized",
        "live_research_enabled",
        "external_search_signals_used",
    }
    if not check_fields(value, path, fields, fields, issues):
        return [], [], 0
    require_string(value.get("analysis_timestamp"), path + "/analysis_timestamp", issues)
    if not isinstance(value.get("mode"), str) or value.get("mode") not in {"hybrid", "observed_only", "simulated_only"}:
        issues.append(issue("E_MODE", path + "/mode", "Invalid analysis mode."))

    def provider_list(field_name: str) -> List[str]:
        raw_items = value.get(field_name)
        if not isinstance(raw_items, list) or not raw_items:
            issues.append(issue("E_PROVIDER_LIST", path + "/" + field_name, "Expected a non-empty array."))
            return []
        valid_items: List[str] = []
        seen_items: Set[str] = set()
        for item in raw_items:
            if not isinstance(item, str) or item not in PROVIDERS:
                issues.append(issue("E_PROVIDER", path + "/" + field_name, "Unknown provider."))
                continue
            if item in seen_items:
                issues.append(issue("E_DUPLICATE_PROVIDER", path + "/" + field_name, "Provider IDs must be unique."))
                continue
            seen_items.add(item)
            valid_items.append(item)
        return valid_items

    requested_list = provider_list("requested_providers")
    participating_list = provider_list("participating_providers")
    if not set(participating_list).issubset(set(requested_list)):
        issues.append(issue("E_PARTICIPATING_PROVIDER", path + "/participating_providers", "Participating providers must be requested."))

    runs = value.get("runs_per_provider")
    if not is_int(runs) or not 1 <= runs <= 10:
        issues.append(issue("E_RUN_COUNT", path + "/runs_per_provider", "Run count must be 1–10."))
        runs = 0
    query_count = value.get("queries_per_synthetic_run")
    if not is_int(query_count) or not 1 <= query_count <= 50:
        issues.append(issue("E_QUERY_COUNT", path + "/queries_per_synthetic_run", "Synthetic query target must be 1–50."))
    if (
        (is_int(runs) and runs > 3)
        or (is_int(query_count) and query_count > 15)
    ) and value.get("expanded_scope_authorized") is not True:
        issues.append(issue("E_SCOPE_AUTHORIZATION", path + "/expanded_scope_authorized", "Expanded run/query scope requires explicit authorization."))
    if value.get("api_execution_policy") != "api_first":
        issues.append(issue("E_API_POLICY", path + "/api_execution_policy", "API execution policy must be api_first."))
    for field in (
        "network_access",
        "allow_paid_api_calls",
        "expanded_scope_authorized",
        "live_research_enabled",
        "external_search_signals_used",
    ):
        if not isinstance(value.get(field), bool):
            issues.append(issue("E_BOOLEAN", path + "/" + field, "Expected a boolean."))
    return requested_list, participating_list, runs


def validate_model(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    fields = {"requested", "actual", "actual_status", "fallback_reason"}
    if not check_fields(value, path, fields, fields, issues):
        return
    require_string(value.get("requested"), path + "/requested", issues, nullable=True)
    require_string(value.get("actual"), path + "/actual", issues, nullable=True)
    if not isinstance(value.get("actual_status"), str) or value.get("actual_status") not in {"confirmed", "not_exposed", "unavailable", "failed"}:
        issues.append(issue("E_MODEL_STATUS", path + "/actual_status", "Invalid model status."))
    require_string(value.get("fallback_reason"), path + "/fallback_reason", issues, nullable=True)
    actual_status = value.get("actual_status")
    if actual_status == "confirmed" and value.get("actual") is None:
        issues.append(
            issue(
                "E_MODEL_EXPOSURE",
                path + "/actual",
                "A confirmed actual model requires an exposed model ID.",
            )
        )
    if isinstance(actual_status, str) and actual_status in {"not_exposed", "unavailable", "failed"} and value.get(
        "actual"
    ) is not None:
        issues.append(
            issue(
                "E_MODEL_EXPOSURE",
                path + "/actual",
                "Actual model must be null unless its status is confirmed.",
            )
        )


def validate_failure(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    fields = {"code", "provider", "run_index", "message", "degraded"}
    if not check_fields(value, path, fields, fields, issues):
        return
    require_string(value.get("code"), path + "/code", issues)
    require_string(value.get("message"), path + "/message", issues)
    provider = value.get("provider")
    if provider is not None and (
        not isinstance(provider, str) or provider not in PROVIDERS
    ):
        issues.append(issue("E_PROVIDER", path + "/provider", "Unknown provider."))
    run_index = value.get("run_index")
    if run_index is not None and (not is_int(run_index) or run_index < 1):
        issues.append(issue("E_RUN_INDEX", path + "/run_index", "Invalid run index."))
    if not isinstance(value.get("degraded"), bool):
        issues.append(issue("E_BOOLEAN", path + "/degraded", "Expected a boolean."))


def validate_query(
    value: Any,
    path: str,
    platform_id: str,
    issues: List[Dict[str, str]],
    query_ids: Set[str],
) -> Optional[str]:
    fields = {
        "query_id",
        "text",
        "normalized_text",
        "source_type",
        "form",
        "information_gap",
        "journey_stage",
        "intent",
        "language",
        "translation",
        "platform_cluster_id",
        "trace_path",
    }
    required = fields - {"translation"}
    if not check_fields(value, path, required, fields, issues):
        return None
    query_id = value.get("query_id")
    if not require_string(query_id, path + "/query_id", issues):
        query_id = None
    elif query_id in query_ids:
        issues.append(issue("E_DUPLICATE_QUERY_ID", path + "/query_id", "Query ID must be globally unique."))
    else:
        query_ids.add(query_id)
    text = value.get("text")
    if require_string(text, path + "/text", issues):
        normalized = value.get("normalized_text")
        expected = normalize_exact(text)
        if normalized != expected:
            issues.append(issue("E_NORMALIZATION", path + "/normalized_text", "Normalized text does not match NFKC/whitespace/casefold rules."))
    else:
        require_string(value.get("normalized_text"), path + "/normalized_text", issues)
    source_type = value.get("source_type")
    if not isinstance(source_type, str) or source_type not in SOURCE_TYPES:
        issues.append(issue("E_SOURCE_TYPE", path + "/source_type", "Invalid query provenance."))
    trace_path = value.get("trace_path")
    if source_type == "observed_tool_query":
        if isinstance(text, str) and len(text) > 2000:
            issues.append(issue("E_OBSERVED_QUERY_INVALID", path + "/text", "Observed query text must not exceed 2,000 characters."))
        if not isinstance(trace_path, str) or not trace_path.strip():
            issues.append(issue("E_OBSERVED_TRACE", path + "/trace_path", "Observed queries require a structured trace path."))
        else:
            pattern = TRACE_PATTERNS.get(platform_id)
            if pattern is None or pattern.fullmatch(trace_path) is None:
                issues.append(
                    issue(
                        "E_OBSERVED_TRACE_PATH",
                        path + "/trace_path",
                        "Observed trace path is not valid for this provider.",
                    )
                )
    elif trace_path is not None:
        issues.append(issue("E_SYNTHETIC_TRACE", path + "/trace_path", "Synthetic or heuristic queries must not have a trace path."))
    form = value.get("form")
    if not isinstance(form, str) or form not in FORMS:
        issues.append(issue("E_FORM", path + "/form", "Invalid construction form."))
    information_gap = value.get("information_gap")
    if not isinstance(information_gap, str) or information_gap not in INFORMATION_GAPS:
        issues.append(issue("E_INFORMATION_GAP", path + "/information_gap", "Invalid information-gap function."))
    journey_stage = value.get("journey_stage")
    if journey_stage is not None and (
        not isinstance(journey_stage, str) or journey_stage not in JOURNEY_STAGES
    ):
        issues.append(issue("E_JOURNEY_STAGE", path + "/journey_stage", "Invalid journey stage."))
    for field in ("intent", "language", "platform_cluster_id"):
        require_string(value.get(field), path + "/" + field, issues)
    if "translation" in value:
        require_string(value.get("translation"), path + "/translation", issues, nullable=True)
    return query_id


def validate_platforms(
    platforms: Any,
    path: str,
    participating: List[str],
    runs_target: int,
    analysis_mode: Any,
    issues: List[Dict[str, str]],
) -> Tuple[
    Dict[str, Dict[str, Dict[str, Any]]],
    Dict[str, str],
    Set[str],
    Dict[Tuple[str, int, str], Dict[str, Any]],
]:
    cluster_index: Dict[str, Dict[str, Dict[str, Any]]] = {}
    cluster_owner: Dict[str, str] = {}
    all_query_ids: Set[str] = set()
    nested_failures: Dict[Tuple[str, int, str], Dict[str, Any]] = {}
    actual_participating: Set[str] = set()
    if not isinstance(platforms, list) or not platforms:
        issues.append(issue("E_PLATFORMS", path, "Expected a non-empty platform array."))
        return cluster_index, cluster_owner, all_query_ids, nested_failures

    seen_platforms: Set[str] = set()
    for platform_index, platform in enumerate(platforms):
        platform_path = path + "/" + str(platform_index)
        fields = {
            "platform_id",
            "provider",
            "product_surface",
            "model",
            "execution_mode",
            "observability_status",
            "runs",
            "clusters",
        }
        if not check_fields(platform, platform_path, fields, fields, issues):
            continue
        platform_id = platform.get("platform_id")
        if not isinstance(platform_id, str) or platform_id not in PROVIDERS:
            issues.append(issue("E_PROVIDER", platform_path + "/platform_id", "Unknown platform ID."))
            continue
        if platform_id in seen_platforms:
            issues.append(issue("E_DUPLICATE_PLATFORM", platform_path + "/platform_id", "Platform IDs must be unique."))
        seen_platforms.add(platform_id)
        for field in ("provider", "product_surface"):
            require_string(platform.get(field), platform_path + "/" + field, issues)
        validate_model(platform.get("model"), platform_path + "/model", issues)
        if not isinstance(platform.get("execution_mode"), str) or platform.get("execution_mode") not in {
            "observed_api",
            "provider_synthetic",
            "heuristic_simulation",
            "mixed",
            "failed",
        }:
            issues.append(issue("E_EXECUTION_MODE", platform_path + "/execution_mode", "Invalid execution mode."))
        if not isinstance(platform.get("observability_status"), str) or platform.get("observability_status") not in {
            "query_strings_exposed",
            "search_used_query_strings_hidden",
            "search_not_used",
            "simulation_only",
            "failed",
        }:
            issues.append(issue("E_OBSERVABILITY", platform_path + "/observability_status", "Invalid observability status."))

        runs = platform.get("runs")
        if not isinstance(runs, list):
            issues.append(issue("E_RUNS", platform_path + "/runs", "Expected a run array."))
            runs = []
        if runs_target and len(runs) != runs_target:
            issues.append(issue("E_RUN_COUNT", platform_path + "/runs", "Platform run count does not match configuration."))
        run_indices: Set[int] = set()
        query_to_run: Dict[str, int] = {}
        query_to_cluster: Dict[str, str] = {}
        valid_runs: Set[int] = set()
        platform_source_types: Set[str] = set()
        for run_offset, run in enumerate(runs):
            run_path = platform_path + "/runs/" + str(run_offset)
            run_fields = {
                "run_index",
                "status",
                "attempts",
                "api_attempted",
                "fallback_reason",
                "queries",
                "observed_query_count",
                "provider_search_query_count",
                "failure",
            }
            if not check_fields(run, run_path, run_fields, run_fields, issues):
                continue
            run_index = run.get("run_index")
            if not is_int(run_index) or run_index < 1 or (runs_target and run_index > runs_target):
                issues.append(issue("E_RUN_INDEX", run_path + "/run_index", "Invalid run index."))
                continue
            if run_index in run_indices:
                issues.append(issue("E_DUPLICATE_RUN", run_path + "/run_index", "Run indices must be unique per platform."))
            run_indices.add(run_index)
            if not isinstance(run.get("status"), str) or run.get("status") not in {"success", "degraded", "failed"}:
                issues.append(issue("E_RUN_STATUS", run_path + "/status", "Invalid run status."))
            attempts = run.get("attempts")
            max_attempts = 12 if platform_id == "claude" else 6
            if not is_int(attempts) or not 0 <= attempts <= max_attempts:
                issues.append(
                    issue(
                        "E_ATTEMPTS",
                        run_path + "/attempts",
                        "Attempts must be 0–%d for this provider." % max_attempts,
                    )
                )
            api_attempted = run.get("api_attempted")
            if not isinstance(api_attempted, bool):
                issues.append(issue("E_API_ATTEMPTED", run_path + "/api_attempted", "api_attempted must be a boolean."))
            fallback_reason = run.get("fallback_reason")
            if fallback_reason is not None and (
                not isinstance(fallback_reason, str) or not fallback_reason.strip()
            ):
                issues.append(issue("E_FALLBACK_REASON", run_path + "/fallback_reason", "fallback_reason must be null or a non-empty string."))
            if api_attempted is True and is_int(attempts) and attempts < 1:
                issues.append(issue("E_API_ATTEMPT_CONSISTENCY", run_path + "/attempts", "An attempted API call requires at least one HTTP attempt."))
            if api_attempted is False and attempts != 0:
                issues.append(issue("E_API_ATTEMPT_CONSISTENCY", run_path + "/attempts", "A run without an API call must have zero HTTP attempts."))
            if api_attempted is False and fallback_reason is None:
                issues.append(issue("E_FALLBACK_REASON", run_path + "/fallback_reason", "A run without an API attempt must record why fallback was used."))
            for field in ("observed_query_count", "provider_search_query_count"):
                count = run.get(field)
                if count is not None and (not is_int(count) or count < 0):
                    issues.append(issue("E_QUERY_COUNT", run_path + "/" + field, "Expected null or a non-negative integer."))
            failure = run.get("failure")
            if failure is not None:
                validate_failure(failure, run_path + "/failure", issues)
                if isinstance(failure, dict):
                    if failure.get("provider") != platform_id:
                        issues.append(
                            issue(
                                "E_RUN_FAILURE_OWNER",
                                run_path + "/failure/provider",
                                "Nested failure provider must match its platform.",
                            )
                        )
                    if failure.get("run_index") != run_index:
                        issues.append(
                            issue(
                                "E_RUN_FAILURE_OWNER",
                                run_path + "/failure/run_index",
                                "Nested failure run_index must match its run.",
                            )
                        )
                    code = failure.get("code")
                    if isinstance(code, str):
                        failure_key = (platform_id, run_index, code)
                        if failure_key in nested_failures:
                            issues.append(
                                issue(
                                    "E_DUPLICATE_NESTED_FAILURE",
                                    run_path + "/failure",
                                    "Nested failure identities must be unique.",
                                )
                            )
                        nested_failures[failure_key] = failure
            queries = run.get("queries")
            if not isinstance(queries, list):
                issues.append(issue("E_QUERIES", run_path + "/queries", "Expected a query array."))
                queries = []
            run_status = run.get("status")
            if run_status == "success" and (not queries or failure is not None):
                issues.append(
                    issue(
                        "E_RUN_STATUS_CONSISTENCY",
                        run_path + "/status",
                        "A successful run requires queries and no failure.",
                    )
                )
            if run_status == "failed" and (queries or failure is None):
                issues.append(
                    issue(
                        "E_RUN_STATUS_CONSISTENCY",
                        run_path + "/status",
                        "A failed run requires no queries and a failure record.",
                    )
                )
            if run_status == "degraded" and failure is None:
                issues.append(
                    issue(
                        "E_RUN_STATUS_CONSISTENCY",
                        run_path + "/status",
                        "A degraded run requires a failure record.",
                    )
                )
            if isinstance(failure, dict) and isinstance(
                failure.get("degraded"), bool
            ):
                expected_degraded = run_status == "degraded"
                if failure["degraded"] is not expected_degraded:
                    issues.append(
                        issue(
                            "E_RUN_FAILURE_DEGRADED",
                            run_path + "/failure/degraded",
                            "Failure degraded flag must match the run status.",
                        )
                    )
            if queries:
                valid_runs.add(run_index)
            exact_keys: Set[str] = set()
            observed_count = 0
            non_observed_query_seen = False
            for query_offset, query in enumerate(queries):
                query_path = run_path + "/queries/" + str(query_offset)
                query_id = validate_query(
                    query, query_path, platform_id, issues, all_query_ids
                )
                if query_id:
                    query_to_run[query_id] = run_index
                    if isinstance(query.get("platform_cluster_id"), str):
                        query_to_cluster[query_id] = query["platform_cluster_id"]
                normalized = query.get("normalized_text") if isinstance(query, dict) else None
                if isinstance(normalized, str):
                    if normalized in exact_keys:
                        issues.append(issue("E_EXACT_DUPLICATE_IN_RUN", query_path + "/normalized_text", "Exact duplicate query within one run."))
                    exact_keys.add(normalized)
                if isinstance(query, dict) and query.get("source_type") == "observed_tool_query":
                    observed_count += 1
                    if api_attempted is not True:
                        issues.append(issue("E_API_PROVENANCE", query_path + "/source_type", "Observed tool queries require an attempted provider API call."))
                elif isinstance(query, dict) and query.get("source_type") in {
                    "synthetic_provider_query",
                    "heuristic_simulation",
                }:
                    non_observed_query_seen = True
                    if query.get("source_type") == "synthetic_provider_query" and api_attempted is not True:
                        issues.append(issue("E_API_PROVENANCE", query_path + "/source_type", "Provider-synthetic queries require an attempted provider API call."))
                if (
                    isinstance(query, dict)
                    and isinstance(query.get("source_type"), str)
                    and query.get("source_type") in SOURCE_TYPES
                ):
                    platform_source_types.add(query["source_type"])
            if is_int(run.get("observed_query_count")) and run["observed_query_count"] != observed_count:
                issues.append(issue("E_OBSERVED_COUNT", run_path + "/observed_query_count", "Observed query count does not match records."))
            if observed_count and run.get("observed_query_count") is None:
                issues.append(
                    issue(
                        "E_OBSERVED_COUNT",
                        run_path + "/observed_query_count",
                        "Observed query count must be present when a run has observed queries.",
                    )
                )
            if non_observed_query_seen and fallback_reason is None:
                issues.append(issue("E_FALLBACK_REASON", run_path + "/fallback_reason", "Synthetic queries require a recorded reason that observed API evidence was not used."))

        execution_mode = platform.get("execution_mode")
        expected_execution_mode = None
        if len(platform_source_types) > 1:
            expected_execution_mode = "mixed"
        elif platform_source_types:
            expected_execution_mode = {
                "observed_tool_query": "observed_api",
                "synthetic_provider_query": "provider_synthetic",
                "heuristic_simulation": "heuristic_simulation",
            }[next(iter(platform_source_types))]
        else:
            expected_execution_mode = "failed"
        if execution_mode != expected_execution_mode:
            issues.append(
                issue(
                    "E_EXECUTION_MODE_CONSISTENCY",
                    platform_path + "/execution_mode",
                    "Execution mode does not match the query provenance present.",
                )
            )
        if analysis_mode == "observed_only" and any(
            source_type != "observed_tool_query"
            for source_type in platform_source_types
        ):
            issues.append(
                issue(
                    "E_MODE_PROVENANCE",
                    platform_path + "/execution_mode",
                    "observed_only reports cannot contain simulated queries.",
                )
            )
        if (
            analysis_mode == "simulated_only"
            and "observed_tool_query" in platform_source_types
        ):
            issues.append(
                issue(
                    "E_MODE_PROVENANCE",
                    platform_path + "/execution_mode",
                    "simulated_only reports cannot contain observed queries.",
                )
            )

        observability_status = platform.get("observability_status")
        has_observed = "observed_tool_query" in platform_source_types
        if has_observed and observability_status != "query_strings_exposed":
            issues.append(
                issue(
                    "E_OBSERVABILITY_CONSISTENCY",
                    platform_path + "/observability_status",
                    "Observed queries require query_strings_exposed status.",
                )
            )
        if not has_observed and observability_status == "query_strings_exposed":
            issues.append(
                issue(
                    "E_OBSERVABILITY_CONSISTENCY",
                    platform_path + "/observability_status",
                    "query_strings_exposed requires at least one observed query.",
                )
            )
        if platform_source_types and observability_status == "failed":
            issues.append(
                issue(
                    "E_OBSERVABILITY_CONSISTENCY",
                    platform_path + "/observability_status",
                    "A platform with query output cannot have failed observability.",
                )
            )
        clusters = platform.get("clusters")
        if not isinstance(clusters, list):
            issues.append(issue("E_CLUSTERS", platform_path + "/clusters", "Expected a cluster array."))
            clusters = []
        platform_cluster_map: Dict[str, Dict[str, Any]] = {}
        referenced_queries: Set[str] = set()
        for cluster_offset, cluster in enumerate(clusters):
            cluster_path = platform_path + "/clusters/" + str(cluster_offset)
            cluster_fields = {
                "cluster_id",
                "label",
                "canonical_query",
                "query_ids",
                "run_indices",
                "within_model_stability",
            }
            if not check_fields(cluster, cluster_path, cluster_fields, cluster_fields, issues):
                continue
            cluster_id = cluster.get("cluster_id")
            if not require_string(cluster_id, cluster_path + "/cluster_id", issues):
                continue
            if cluster_id in cluster_owner:
                issues.append(issue("E_DUPLICATE_CLUSTER_ID", cluster_path + "/cluster_id", "Platform cluster IDs must be globally unique."))
            cluster_owner[cluster_id] = platform_id
            platform_cluster_map[cluster_id] = cluster
            for field in ("label", "canonical_query"):
                require_string(cluster.get(field), cluster_path + "/" + field, issues)
            query_ids = cluster.get("query_ids")
            if not isinstance(query_ids, list) or not query_ids:
                issues.append(issue("E_CLUSTER_QUERY_IDS", cluster_path + "/query_ids", "Cluster requires query IDs."))
                query_ids = []
            valid_query_ids: List[str] = []
            seen_query_ids: Set[str] = set()
            for query_id in query_ids:
                if not isinstance(query_id, str) or not query_id.strip():
                    issues.append(issue("E_CLUSTER_QUERY_IDS", cluster_path + "/query_ids", "Cluster query IDs must be non-empty strings."))
                    continue
                if query_id in seen_query_ids:
                    issues.append(issue("E_DUPLICATE_CLUSTER_QUERY", cluster_path + "/query_ids", "Cluster query IDs must be unique."))
                    continue
                seen_query_ids.add(query_id)
                valid_query_ids.append(query_id)
            for query_id in valid_query_ids:
                if query_id not in query_to_run:
                    issues.append(issue("E_CLUSTER_QUERY_REFERENCE", cluster_path + "/query_ids", "Cluster references a missing platform query."))
                    continue
                referenced_queries.add(query_id)
                if query_to_cluster.get(query_id) != cluster_id:
                    issues.append(issue("E_CLUSTER_BACK_REFERENCE", cluster_path + "/query_ids", "Query platform_cluster_id does not match cluster."))
            expected_runs = sorted({query_to_run[item] for item in valid_query_ids if item in query_to_run})
            cluster_runs = cluster.get("run_indices")
            if cluster_runs != expected_runs:
                issues.append(issue("E_CLUSTER_RUNS", cluster_path + "/run_indices", "Cluster run indices do not match query occurrences."))
            validate_stability(
                cluster.get("within_model_stability"),
                cluster_path + "/within_model_stability",
                len(expected_runs),
                len(valid_runs) if valid_runs else 1,
                issues,
            )
        for query_id in sorted(set(query_to_run) - referenced_queries):
            issues.append(issue("E_UNCLUSTERED_QUERY", platform_path + "/clusters", "Query is not referenced by a platform cluster: " + query_id))
        cluster_index[platform_id] = platform_cluster_map
        if valid_runs:
            actual_participating.add(platform_id)

    if set(participating) != actual_participating:
        issues.append(issue("E_PARTICIPATING_PROVIDER", "/configuration/participating_providers", "Participating providers do not match platforms with query output."))
    return cluster_index, cluster_owner, all_query_ids, nested_failures


def validate_cross_clusters(
    value: Any,
    path: str,
    cluster_index: Dict[str, Dict[str, Dict[str, Any]]],
    participating: List[str],
    issues: List[Dict[str, str]],
) -> Tuple[Set[str], Dict[str, Set[str]]]:
    cross_ids: Set[str] = set()
    platform_presence: Dict[str, Set[str]] = {}
    used_platform_clusters: Set[Tuple[str, str]] = set()
    if not isinstance(value, list):
        issues.append(issue("E_CROSS_CLUSTERS", path, "Expected a cross-platform cluster array."))
        return cross_ids, platform_presence
    for index, cluster in enumerate(value):
        cluster_path = path + "/" + str(index)
        fields = {
            "cross_cluster_id",
            "label",
            "canonical_query",
            "member_platform_clusters",
            "platform_ids",
            "cross_model_coverage",
            "interpretation",
        }
        if not check_fields(cluster, cluster_path, fields, fields, issues):
            continue
        cross_id = cluster.get("cross_cluster_id")
        if not require_string(cross_id, cluster_path + "/cross_cluster_id", issues):
            continue
        if cross_id in cross_ids:
            issues.append(issue("E_DUPLICATE_CROSS_CLUSTER", cluster_path + "/cross_cluster_id", "Cross-cluster IDs must be unique."))
        cross_ids.add(cross_id)
        for field in ("label", "canonical_query", "interpretation"):
            require_string(cluster.get(field), cluster_path + "/" + field, issues)
        refs = cluster.get("member_platform_clusters")
        if not isinstance(refs, list) or not refs:
            issues.append(issue("E_CROSS_CLUSTER_MEMBERS", cluster_path + "/member_platform_clusters", "Cross cluster requires members."))
            refs = []
        ref_platforms: Set[str] = set()
        for ref_index, ref in enumerate(refs):
            ref_path = cluster_path + "/member_platform_clusters/" + str(ref_index)
            if not check_fields(ref, ref_path, {"platform_id", "cluster_id"}, {"platform_id", "cluster_id"}, issues):
                continue
            provider = ref.get("platform_id")
            cluster_id = ref.get("cluster_id")
            if not isinstance(provider, str) or provider not in PROVIDERS or not isinstance(cluster_id, str):
                issues.append(issue("E_CROSS_CLUSTER_REFERENCE", ref_path, "Invalid platform-cluster reference."))
                continue
            if cluster_id not in cluster_index.get(provider, {}):
                issues.append(issue("E_CROSS_CLUSTER_REFERENCE", ref_path, "Referenced platform cluster does not exist."))
                continue
            key = (provider, cluster_id)
            if key in used_platform_clusters:
                issues.append(issue("E_REUSED_PLATFORM_CLUSTER", ref_path, "Platform cluster belongs to more than one cross cluster."))
            used_platform_clusters.add(key)
            ref_platforms.add(provider)
        platform_ids = cluster.get("platform_ids")
        if not isinstance(platform_ids, list):
            issues.append(issue("E_CROSS_PLATFORM_IDS", cluster_path + "/platform_ids", "Platform IDs must be a unique array."))
            platform_ids = []
        valid_platform_ids: List[str] = []
        seen_platform_ids: Set[str] = set()
        for provider in platform_ids:
            if not isinstance(provider, str) or provider not in PROVIDERS:
                issues.append(issue("E_CROSS_PLATFORM_IDS", cluster_path + "/platform_ids", "Platform IDs must contain known provider strings."))
                continue
            if provider in seen_platform_ids:
                issues.append(issue("E_CROSS_PLATFORM_IDS", cluster_path + "/platform_ids", "Platform IDs must be unique."))
                continue
            seen_platform_ids.add(provider)
            valid_platform_ids.append(provider)
        if set(valid_platform_ids) != ref_platforms:
            issues.append(issue("E_CROSS_PLATFORM_IDS", cluster_path + "/platform_ids", "Platform IDs do not match member references."))
        platform_presence[cross_id] = ref_platforms
        validate_stability(
            cluster.get("cross_model_coverage"),
            cluster_path + "/cross_model_coverage",
            len(ref_platforms),
            len(participating) if participating else 1,
            issues,
        )
    expected_refs = {
        (provider, cluster_id)
        for provider, clusters in cluster_index.items()
        for cluster_id in clusters
    }
    for provider, cluster_id in sorted(expected_refs - used_platform_clusters):
        issues.append(issue("E_UNMAPPED_PLATFORM_CLUSTER", path, "Platform cluster is not mapped cross-platform: %s/%s" % (provider, cluster_id)))
    return cross_ids, platform_presence


def validate_coverage_matrix(
    value: Any,
    path: str,
    cross_ids: Set[str],
    platform_presence: Dict[str, Set[str]],
    issues: List[Dict[str, str]],
) -> None:
    if not isinstance(value, list):
        issues.append(issue("E_COVERAGE_MATRIX", path, "Expected a coverage matrix array."))
        return
    row_ids: Set[str] = set()
    provider_set = set(PROVIDERS)
    for index, row in enumerate(value):
        row_path = path + "/" + str(index)
        if not check_fields(row, row_path, {"cross_cluster_id", "presence"}, {"cross_cluster_id", "presence"}, issues):
            continue
        cross_id = row.get("cross_cluster_id")
        if not isinstance(cross_id, str) or cross_id not in cross_ids:
            issues.append(issue("E_COVERAGE_REFERENCE", row_path + "/cross_cluster_id", "Coverage row references a missing cross cluster."))
            continue
        if cross_id in row_ids:
            issues.append(issue("E_DUPLICATE_COVERAGE_ROW", row_path + "/cross_cluster_id", "Coverage rows must be unique."))
        row_ids.add(cross_id)
        presence = row.get("presence")
        if not isinstance(presence, dict) or set(presence) != provider_set:
            issues.append(issue("E_COVERAGE_COLUMNS", row_path + "/presence", "Coverage row must contain all five provider columns."))
            continue
        expected = platform_presence.get(cross_id, set())
        for provider in PROVIDERS:
            if not isinstance(presence.get(provider), bool):
                issues.append(issue("E_BOOLEAN", row_path + "/presence/" + provider, "Expected a boolean."))
            elif presence[provider] != (provider in expected):
                issues.append(issue("E_COVERAGE_VALUE", row_path + "/presence/" + provider, "Coverage value does not match cross-cluster membership."))
    if row_ids != cross_ids:
        issues.append(issue("E_COVERAGE_ROWS", path, "Coverage matrix must contain exactly one row per cross cluster."))


def validate_page_coverage(
    value: Any,
    path: str,
    cross_ids: Set[str],
    input_url: Any,
    page_content_provided: Any,
    issues: List[Dict[str, str]],
) -> None:
    if value is None:
        if input_url is not None or page_content_provided is True:
            issues.append(issue("W_PAGE_COVERAGE_MISSING", path, "Page evidence was supplied but page coverage is null.", "warning"))
        return
    fields = {"url", "items", "coverage_score"}
    if not check_fields(value, path, fields, fields, issues):
        return
    if input_url is None and page_content_provided is not True:
        issues.append(issue("E_PAGE_EVIDENCE_SOURCE", path, "Page coverage requires an input URL or supplied page content."))
    page_url = value.get("url")
    if input_url is not None:
        require_string(page_url, path + "/url", issues)
        if page_url != input_url:
            issues.append(issue("E_PAGE_URL", path + "/url", "Page coverage URL does not match input URL."))
    elif page_url is not None:
        issues.append(issue("E_PAGE_URL", path + "/url", "Page coverage URL must be null when no input URL was supplied."))
    items = value.get("items")
    if not isinstance(items, list):
        issues.append(issue("E_PAGE_ITEMS", path + "/items", "Expected a page coverage item array."))
        return
    seen: Set[str] = set()
    score_values: List[float] = []
    for index, item in enumerate(items):
        item_path = path + "/items/" + str(index)
        item_fields = {
            "cross_cluster_id",
            "status",
            "page_evidence",
            "missing_information",
            "recommendation",
        }
        if not check_fields(item, item_path, item_fields, item_fields, issues):
            continue
        cross_id = item.get("cross_cluster_id")
        if not isinstance(cross_id, str) or cross_id not in cross_ids:
            issues.append(issue("E_PAGE_CLUSTER_REFERENCE", item_path + "/cross_cluster_id", "Missing cross-cluster reference."))
        if isinstance(cross_id, str) and cross_id in seen:
            issues.append(issue("E_DUPLICATE_PAGE_CLUSTER", item_path + "/cross_cluster_id", "Page coverage cluster IDs must be unique."))
        if isinstance(cross_id, str):
            seen.add(cross_id)
        status = item.get("status")
        if not isinstance(status, str) or status not in COVERAGE_STATUSES:
            issues.append(issue("E_PAGE_STATUS", item_path + "/status", "Invalid page coverage status."))
        for field in ("page_evidence", "missing_information"):
            require_string(item.get(field), item_path + "/" + field, issues, nullable=True)
        recommendation = item.get("recommendation")
        if not isinstance(recommendation, str) or recommendation not in RECOMMENDATIONS:
            issues.append(issue("E_PAGE_RECOMMENDATION", item_path + "/recommendation", "Invalid recommendation."))
        if isinstance(status, str) and status in {"covered", "partial", "missing"}:
            score_values.append({"covered": 1.0, "partial": 0.5, "missing": 0.0}[status])
    coverage_score = value.get("coverage_score")
    if coverage_score is not None:
        if not is_number(coverage_score) or not 0 <= float(coverage_score) <= 1:
            issues.append(issue("E_PAGE_SCORE", path + "/coverage_score", "Coverage score must be null or 0–1."))
        elif not score_values:
            issues.append(
                issue(
                    "E_PAGE_SCORE",
                    path + "/coverage_score",
                    "Coverage score must be null when no item is assessable.",
                )
            )
        elif score_values:
            expected = round(sum(score_values) / len(score_values), 6)
            if abs(float(coverage_score) - expected) > 0.000001:
                issues.append(issue("E_PAGE_SCORE", path + "/coverage_score", "Unweighted coverage score does not match assessable items."))


def validate_recommended_page_topics(
    value: Any,
    path: str,
    cross_ids: Set[str],
    external_signal_ids: Set[str],
    page_coverage: Any,
    issues: List[Dict[str, str]],
) -> None:
    fields = {"status", "basis", "unavailable_reason", "items"}
    if not check_fields(value, path, fields, fields, issues):
        return

    status = value.get("status")
    basis = value.get("basis")
    reason = value.get("unavailable_reason")
    items = value.get("items")
    if not isinstance(status, str) or status not in {"available", "not_available"}:
        issues.append(issue("E_RECOMMENDED_TOPIC_STATUS", path + "/status", "Invalid recommendation status."))
    if not isinstance(basis, str) or basis not in {"fanout_only", "fanout_and_page_evidence"}:
        issues.append(issue("E_RECOMMENDED_TOPIC_BASIS", path + "/basis", "Invalid recommendation basis."))

    page_evidence_available = isinstance(page_coverage, dict)
    expected_basis = (
        "fanout_and_page_evidence" if page_evidence_available else "fanout_only"
    )
    if isinstance(basis, str) and basis in {"fanout_only", "fanout_and_page_evidence"} and basis != expected_basis:
        issues.append(
            issue(
                "E_RECOMMENDED_TOPIC_BASIS",
                path + "/basis",
                "Recommendation basis does not match the available page evidence.",
            )
        )

    if not isinstance(items, list):
        issues.append(issue("E_RECOMMENDED_TOPICS", path + "/items", "Expected a topic recommendation array."))
        return
    if len(items) > 10:
        issues.append(issue("E_RECOMMENDED_TOPIC_COUNT", path + "/items", "At most ten topic recommendations are allowed."))

    if status == "not_available":
        require_string(reason, path + "/unavailable_reason", issues)
        if items:
            issues.append(issue("E_RECOMMENDED_TOPIC_AVAILABILITY", path + "/items", "Unavailable recommendations must have an empty item array."))
        if cross_ids:
            issues.append(issue("E_RECOMMENDED_TOPIC_AVAILABILITY", path + "/status", "Recommendations cannot be unavailable while usable cross-platform clusters exist."))
        return
    if status == "available":
        if reason is not None:
            issues.append(issue("E_RECOMMENDED_TOPIC_AVAILABILITY", path + "/unavailable_reason", "Available recommendations require a null unavailable_reason."))
        if not items:
            issues.append(issue("E_RECOMMENDED_TOPIC_AVAILABILITY", path + "/items", "Available recommendations require at least one item."))

    page_status_by_cluster: Dict[str, str] = {}
    if isinstance(page_coverage, dict):
        page_items = page_coverage.get("items")
        if isinstance(page_items, list):
            for page_item in page_items:
                if isinstance(page_item, dict) and isinstance(page_item.get("cross_cluster_id"), str) and isinstance(page_item.get("status"), str):
                    page_status_by_cluster[page_item["cross_cluster_id"]] = page_item["status"]

    item_fields = {
        "rank",
        "topic_id",
        "label",
        "priority",
        "action",
        "supporting_cross_cluster_ids",
        "supporting_signal_ids",
        "coverage_guidance",
        "rationale",
        "suggested_format",
    }
    seen_topic_ids: Set[str] = set()
    seen_labels: Set[str] = set()
    used_cross_ids: Set[str] = set()
    ranks: List[int] = []
    ranked_priorities: List[Tuple[int, str]] = []
    has_on_page_action = False
    action_status = {
        "add_to_page": "missing",
        "expand_on_page": "partial",
        "retain_on_page": "covered",
        "separate_page_candidate": "separate_page_candidate",
        "off_page_evidence": "off_page_signal",
    }

    for index, item in enumerate(items):
        item_path = path + "/items/" + str(index)
        if not check_fields(item, item_path, item_fields, item_fields, issues):
            continue
        rank = item.get("rank")
        if not is_int(rank) or rank < 1 or rank > 10:
            issues.append(issue("E_RECOMMENDED_TOPIC_RANK", item_path + "/rank", "Rank must be an integer from 1 to 10."))
        else:
            ranks.append(rank)

        topic_id = item.get("topic_id")
        if require_string(topic_id, item_path + "/topic_id", issues):
            if topic_id in seen_topic_ids:
                issues.append(issue("E_DUPLICATE_RECOMMENDED_TOPIC_ID", item_path + "/topic_id", "Topic IDs must be unique."))
            seen_topic_ids.add(topic_id)

        label = item.get("label")
        if require_string(label, item_path + "/label", issues):
            label_key = normalize_exact(label)
            if label_key in seen_labels:
                issues.append(issue("E_DUPLICATE_RECOMMENDED_TOPIC_LABEL", item_path + "/label", "Topic labels must be unique after normalization."))
            seen_labels.add(label_key)

        priority = item.get("priority")
        if not isinstance(priority, str) or priority not in RECOMMENDED_TOPIC_PRIORITIES:
            issues.append(issue("E_RECOMMENDED_TOPIC_PRIORITY", item_path + "/priority", "Invalid topic priority."))
        elif is_int(rank):
            ranked_priorities.append((rank, priority))

        action = item.get("action")
        if not isinstance(action, str) or action not in RECOMMENDED_TOPIC_ACTIONS:
            issues.append(issue("E_RECOMMENDED_TOPIC_ACTION", item_path + "/action", "Invalid topic action."))
        else:
            has_on_page_action = has_on_page_action or action in ON_PAGE_TOPIC_ACTIONS
            if priority == "P0" and action not in ON_PAGE_TOPIC_ACTIONS:
                issues.append(issue("E_RECOMMENDED_TOPIC_PRIORITY_ACTION", item_path + "/action", "P0 topics require an on-page action."))
            if basis == "fanout_only" and action in {"add_to_page", "expand_on_page", "retain_on_page"}:
                issues.append(issue("E_RECOMMENDED_TOPIC_ACTION_BASIS", item_path + "/action", "Gap-specific actions require page evidence."))
            if basis == "fanout_and_page_evidence" and action == "include_on_page":
                issues.append(issue("E_RECOMMENDED_TOPIC_ACTION_BASIS", item_path + "/action", "Use add, expand, or retain when page evidence is available."))

        for field in ("coverage_guidance", "rationale", "suggested_format"):
            require_string(item.get(field), item_path + "/" + field, issues)

        cluster_refs = item.get("supporting_cross_cluster_ids")
        if not isinstance(cluster_refs, list) or not cluster_refs:
            issues.append(issue("E_RECOMMENDED_TOPIC_CLUSTERS", item_path + "/supporting_cross_cluster_ids", "A recommendation requires at least one cross-cluster ID."))
            cluster_refs = []
        valid_refs: List[str] = []
        local_cluster_ids: Set[str] = set()
        for cluster_id in cluster_refs:
            if not isinstance(cluster_id, str) or not cluster_id.strip():
                issues.append(issue("E_RECOMMENDED_TOPIC_CLUSTERS", item_path + "/supporting_cross_cluster_ids", "Cross-cluster IDs must be non-empty strings."))
                continue
            if cluster_id in local_cluster_ids:
                issues.append(issue("E_DUPLICATE_RECOMMENDED_TOPIC_CLUSTER", item_path + "/supporting_cross_cluster_ids", "Cross-cluster IDs must be unique within a recommendation."))
                continue
            local_cluster_ids.add(cluster_id)
            if cluster_id not in cross_ids:
                issues.append(issue("E_RECOMMENDED_TOPIC_CLUSTER_REFERENCE", item_path + "/supporting_cross_cluster_ids", "Recommendation references a missing cross-platform cluster."))
                continue
            valid_refs.append(cluster_id)
            if cluster_id in used_cross_ids:
                issues.append(issue("E_REUSED_RECOMMENDED_TOPIC_CLUSTER", item_path + "/supporting_cross_cluster_ids", "A cross-platform cluster may support only one recommended topic."))
            used_cross_ids.add(cluster_id)

        signal_refs = item.get("supporting_signal_ids")
        if not isinstance(signal_refs, list):
            issues.append(issue("E_RECOMMENDED_TOPIC_SIGNALS", item_path + "/supporting_signal_ids", "Expected an external-signal ID array."))
        else:
            local_signal_ids: Set[str] = set()
            for signal_id in signal_refs:
                if not isinstance(signal_id, str) or not signal_id.strip():
                    issues.append(issue("E_RECOMMENDED_TOPIC_SIGNALS", item_path + "/supporting_signal_ids", "External-signal IDs must be non-empty strings."))
                    continue
                if signal_id in local_signal_ids:
                    issues.append(issue("E_DUPLICATE_RECOMMENDED_TOPIC_SIGNAL", item_path + "/supporting_signal_ids", "External-signal IDs must be unique within a recommendation."))
                    continue
                local_signal_ids.add(signal_id)
                if signal_id not in external_signal_ids:
                    issues.append(issue("E_RECOMMENDED_TOPIC_SIGNAL_REFERENCE", item_path + "/supporting_signal_ids", "Recommendation references a missing external signal."))

        expected_page_status = action_status.get(action) if isinstance(action, str) else None
        if basis == "fanout_and_page_evidence" and expected_page_status is not None:
            linked_statuses = {page_status_by_cluster.get(cluster_id) for cluster_id in valid_refs}
            if expected_page_status not in linked_statuses:
                issues.append(issue("E_RECOMMENDED_TOPIC_PAGE_STATUS", item_path + "/action", "Topic action does not match the linked page-coverage status."))

    if ranks and sorted(ranks) != list(range(1, len(items) + 1)):
        issues.append(issue("E_RECOMMENDED_TOPIC_RANK", path + "/items", "Topic ranks must be unique and contiguous from 1."))
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    ordered_priorities = [
        priority_order[priority]
        for _, priority in sorted(ranked_priorities)
        if priority in priority_order
    ]
    if any(current > following for current, following in zip(ordered_priorities, ordered_priorities[1:])):
        issues.append(issue("E_RECOMMENDED_TOPIC_PRIORITY_ORDER", path + "/items", "Topic priorities must not increase after a lower-priority rank."))
    if status == "available" and not has_on_page_action:
        issues.append(issue("E_RECOMMENDED_TOPIC_ON_PAGE", path + "/items", "Available recommendations require at least one on-page topic."))


def validate_provenance(value: Any, path: str, issues: List[Dict[str, str]]) -> None:
    fields = {
        "raw_api_responses_persisted",
        "api_keys_persisted",
        "observed_queries_preserved_verbatim",
        "consumer_product_equivalence_claimed",
    }
    if not check_fields(value, path, fields, fields, issues):
        return
    expected = {
        "raw_api_responses_persisted": False,
        "api_keys_persisted": False,
        "observed_queries_preserved_verbatim": True,
        "consumer_product_equivalence_claimed": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) is not expected_value:
            issues.append(issue("E_PROVENANCE_SAFETY", path + "/" + field, "Unsafe or unsupported provenance declaration."))


def validate_report(document: Any) -> Dict[str, Any]:
    issues: List[Dict[str, str]] = []
    if not check_fields(document, "", TOP_LEVEL_FIELDS, TOP_LEVEL_FIELDS, issues):
        document = {}
    if document.get("schema_version") != REPORT_SCHEMA_VERSION:
        issues.append(issue("E_SCHEMA_VERSION", "/schema_version", "schema_version must equal '1.2'."))
    if not isinstance(document.get("status"), str) or document.get("status") not in {"complete", "partial"}:
        issues.append(issue("E_STATUS", "/status", "Invalid report status."))
    validate_input(document.get("input"), "/input", issues)
    validate_intent_analysis(
        document.get("intent_analysis"), "/intent_analysis", issues
    )
    requested, participating, runs_target = validate_configuration(
        document.get("configuration"), "/configuration", issues
    )
    external_signal_count = validate_external_signals(
        document.get("external_search_signals"),
        "/external_search_signals",
        issues,
    )
    external_signal_ids = {
        item.get("signal_id")
        for item in document.get("external_search_signals", [])
        if isinstance(item, dict) and isinstance(item.get("signal_id"), str)
    }
    configuration = (
        document.get("configuration")
        if isinstance(document.get("configuration"), dict)
        else {}
    )
    if configuration.get("external_search_signals_used") is not bool(
        external_signal_count
    ):
        issues.append(
            issue(
                "E_EXTERNAL_SIGNAL_FLAG",
                "/configuration/external_search_signals_used",
                "External-search flag must match whether signal records are present.",
            )
        )
    cluster_index, _, _, nested_failures = validate_platforms(
        document.get("platforms"),
        "/platforms",
        participating,
        runs_target,
        configuration.get("mode"),
        issues,
    )
    platform_ids = {
        item.get("platform_id")
        for item in document.get("platforms", [])
        if isinstance(item, dict) and isinstance(item.get("platform_id"), str)
    }
    if set(requested) != platform_ids:
        issues.append(issue("E_REQUESTED_PLATFORM", "/platforms", "Platform objects must match requested providers, including failed providers."))
    cross_ids, platform_presence = validate_cross_clusters(
        document.get("cross_platform_clusters"),
        "/cross_platform_clusters",
        cluster_index,
        participating,
        issues,
    )
    validate_coverage_matrix(
        document.get("coverage_matrix"),
        "/coverage_matrix",
        cross_ids,
        platform_presence,
        issues,
    )
    input_value = document.get("input") if isinstance(document.get("input"), dict) else {}
    page_coverage = document.get("page_coverage")
    validate_page_coverage(
        page_coverage,
        "/page_coverage",
        cross_ids,
        input_value.get("url"),
        input_value.get("page_content_provided"),
        issues,
    )
    validate_recommended_page_topics(
        document.get("recommended_page_topics"),
        "/recommended_page_topics",
        cross_ids,
        external_signal_ids,
        page_coverage,
        issues,
    )
    for field in ("assumptions", "limitations"):
        values = document.get(field)
        if not isinstance(values, list) or (field == "limitations" and not values):
            issues.append(issue("E_STRING_LIST", "/" + field, "Expected a string array; limitations must not be empty."))
        elif any(not isinstance(item, str) or not item.strip() for item in values):
            issues.append(issue("E_STRING_LIST", "/" + field, "All items must be non-empty strings."))
    failures = document.get("failures")
    if not isinstance(failures, list):
        issues.append(issue("E_FAILURES", "/failures", "Expected a failure array."))
    else:
        top_failure_keys: Set[Tuple[str, int, str]] = set()
        for index, failure in enumerate(failures):
            validate_failure(failure, "/failures/" + str(index), issues)
            if not isinstance(failure, dict):
                continue
            provider = failure.get("provider")
            run_index = failure.get("run_index")
            code = failure.get("code")
            if (provider is None) != (run_index is None):
                issues.append(
                    issue(
                        "E_TOP_FAILURE_OWNER",
                        "/failures/" + str(index),
                        "Top-level failure provider and run_index must both be set or both be null.",
                    )
                )
            if (
                isinstance(provider, str)
                and provider in PROVIDERS
                and is_int(run_index)
                and isinstance(code, str)
            ):
                key = (provider, run_index, code)
                if key in top_failure_keys:
                    issues.append(
                        issue(
                            "E_DUPLICATE_TOP_FAILURE",
                            "/failures/" + str(index),
                            "Top-level failure identities must be unique.",
                        )
                    )
                top_failure_keys.add(key)
        for provider, run_index, code in sorted(
            set(nested_failures) - top_failure_keys
        ):
            issues.append(
                issue(
                    "E_MISSING_TOP_FAILURE",
                    "/failures",
                    "Nested failure is missing from the top-level list: %s/%d/%s"
                    % (provider, run_index, code),
                )
            )
        for provider, run_index, code in sorted(
            top_failure_keys - set(nested_failures)
        ):
            issues.append(
                issue(
                    "E_ORPHAN_TOP_FAILURE",
                    "/failures",
                    "Top-level provider failure has no matching run failure: %s/%d/%s"
                    % (provider, run_index, code),
                )
            )
        if (failures or nested_failures) and document.get("status") == "complete":
            issues.append(issue("E_STATUS_FAILURE_MISMATCH", "/status", "A report with failures must be partial."))
    validate_provenance(document.get("provenance"), "/provenance", issues)
    validate_secret_safety(document, issues)

    error_count = sum(item["severity"] == "error" for item in issues)
    warning_count = sum(item["severity"] == "warning" for item in issues)
    if error_count:
        status = "error"
        exit_code = 2
    elif warning_count:
        status = "advisory"
        exit_code = 1
    else:
        status = "pass"
        exit_code = 0
    return {
        "validator_version": VALIDATOR_VERSION,
        "status": status,
        "exit_code": exit_code,
        "summary": {
            "error_count": error_count,
            "warning_count": warning_count,
            "platform_count": len(document.get("platforms", []))
            if isinstance(document.get("platforms"), list)
            else 0,
            "cross_cluster_count": len(document.get("cross_platform_clusters", []))
            if isinstance(document.get("cross_platform_clusters"), list)
            else 0,
            "recommended_topic_count": len(
                document.get("recommended_page_topics", {}).get("items", [])
            )
            if isinstance(document.get("recommended_page_topics"), dict)
            and isinstance(document.get("recommended_page_topics", {}).get("items"), list)
            else 0,
        },
        "issues": issues,
    }


def read_document(path: str) -> Any:
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise OSError("input too large")
    return load_json_bytes(raw)


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
    parser = argparse.ArgumentParser(description="Validate a query fan-out analysis report.")
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 JSON file or - for stdin")
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        document = read_document(args.input)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError, ValueError):
        payload = {
            "validator_version": VALIDATOR_VERSION,
            "status": "error",
            "exit_code": 2,
            "summary": {"error_count": 1, "warning_count": 0},
            "issues": [issue("E_INPUT", "", "Unable to read a valid UTF-8 JSON document.")],
        }
        emit(payload, args.pretty)
        return 2
    payload = validate_report(document)
    emit(payload, args.pretty)
    return int(payload["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
