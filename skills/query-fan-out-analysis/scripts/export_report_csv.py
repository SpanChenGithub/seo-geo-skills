#!/usr/bin/env python3
"""Export a validated query fan-out report to formula-safe CSV."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, TextIO

from validate_report import DuplicateJsonKeyError, load_json_bytes, validate_report


MAX_INPUT_BYTES = 2 * 1024 * 1024
FIELDS = [
    "record_type",
    "api_execution_policy",
    "network_access",
    "allow_paid_api_calls",
    "expanded_scope_authorized",
    "platform_id",
    "provider",
    "product_surface",
    "requested_model",
    "actual_model",
    "platform_execution_mode",
    "observability_status",
    "run_index",
    "run_status",
    "attempts",
    "api_attempted",
    "fallback_reason",
    "failure_code",
    "failure_message",
    "query_id",
    "query",
    "normalized_query",
    "source_type",
    "form",
    "information_gap",
    "journey_stage",
    "intent",
    "language",
    "translation",
    "platform_cluster_id",
    "within_model_stability",
    "cross_cluster_id",
    "cross_model_coverage",
    "trace_path",
]


def safe_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        text = "true" if value else "false"
    else:
        text = str(value)
    if text.lstrip().startswith(("=", "+", "-", "@")):
        return "'" + text
    return text


def read_document(path: str) -> Dict[str, Any]:
    if path == "-":
        raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("input too large")
    document = load_json_bytes(raw)
    if not isinstance(document, dict):
        raise ValueError("root must be an object")
    return document


def report_rows(document: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    configuration = (
        document.get("configuration")
        if isinstance(document.get("configuration"), dict)
        else {}
    )
    platform_cluster_scores: Dict[str, str] = {}
    cross_by_platform_cluster: Dict[str, Dict[str, str]] = {}
    for platform in document.get("platforms", []):
        if not isinstance(platform, dict):
            continue
        for cluster in platform.get("clusters", []):
            if not isinstance(cluster, dict):
                continue
            stability = cluster.get("within_model_stability")
            if isinstance(stability, dict):
                platform_cluster_scores[cluster.get("cluster_id")] = "%s/%s (%s)" % (
                    stability.get("numerator"),
                    stability.get("denominator"),
                    stability.get("label"),
                )
    for cross_cluster in document.get("cross_platform_clusters", []):
        if not isinstance(cross_cluster, dict):
            continue
        coverage = cross_cluster.get("cross_model_coverage")
        coverage_text = ""
        if isinstance(coverage, dict):
            coverage_text = "%s/%s (%s)" % (
                coverage.get("numerator"),
                coverage.get("denominator"),
                coverage.get("label"),
            )
        for ref in cross_cluster.get("member_platform_clusters", []):
            if isinstance(ref, dict) and isinstance(ref.get("cluster_id"), str):
                cross_by_platform_cluster[ref["cluster_id"]] = {
                    "cross_cluster_id": cross_cluster.get("cross_cluster_id", ""),
                    "cross_model_coverage": coverage_text,
                }

    for platform in document.get("platforms", []):
        if not isinstance(platform, dict):
            continue
        model = platform.get("model") if isinstance(platform.get("model"), dict) else {}
        for run in platform.get("runs", []):
            if not isinstance(run, dict):
                continue
            failure = run.get("failure") if isinstance(run.get("failure"), dict) else {}
            base_row = {
                "record_type": "query",
                "api_execution_policy": configuration.get("api_execution_policy"),
                "network_access": configuration.get("network_access"),
                "allow_paid_api_calls": configuration.get("allow_paid_api_calls"),
                "expanded_scope_authorized": configuration.get(
                    "expanded_scope_authorized"
                ),
                "platform_id": platform.get("platform_id"),
                "provider": platform.get("provider"),
                "product_surface": platform.get("product_surface"),
                "requested_model": model.get("requested"),
                "actual_model": model.get("actual"),
                "platform_execution_mode": platform.get("execution_mode"),
                "observability_status": platform.get("observability_status"),
                "run_index": run.get("run_index"),
                "run_status": run.get("status"),
                "attempts": run.get("attempts"),
                "api_attempted": run.get("api_attempted"),
                "fallback_reason": run.get("fallback_reason"),
                "failure_code": failure.get("code"),
                "failure_message": failure.get("message"),
            }
            queries = [
                query
                for query in run.get("queries", [])
                if isinstance(query, dict)
            ]
            if not queries:
                run_row = dict(base_row)
                run_row["record_type"] = "run_without_query"
                yield run_row
                continue
            for query in queries:
                if not isinstance(query, dict):
                    continue
                platform_cluster_id = query.get("platform_cluster_id")
                cross = cross_by_platform_cluster.get(platform_cluster_id, {})
                row = dict(base_row)
                row.update({
                    "query_id": query.get("query_id"),
                    "query": query.get("text"),
                    "normalized_query": query.get("normalized_text"),
                    "source_type": query.get("source_type"),
                    "form": query.get("form"),
                    "information_gap": query.get("information_gap"),
                    "journey_stage": query.get("journey_stage"),
                    "intent": query.get("intent"),
                    "language": query.get("language"),
                    "translation": query.get("translation"),
                    "platform_cluster_id": platform_cluster_id,
                    "within_model_stability": platform_cluster_scores.get(
                        platform_cluster_id, ""
                    ),
                    "cross_cluster_id": cross.get("cross_cluster_id", ""),
                    "cross_model_coverage": cross.get("cross_model_coverage", ""),
                    "trace_path": query.get("trace_path"),
                })
                yield row


def write_csv(document: Dict[str, Any], handle: TextIO) -> int:
    writer = csv.DictWriter(handle, fieldnames=FIELDS, extrasaction="ignore")
    writer.writeheader()
    count = 0
    for row in report_rows(document):
        writer.writerow({field: safe_cell(row.get(field)) for field in FIELDS})
        count += 1
    return count


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export a validated query fan-out report to CSV.")
    parser.add_argument("input", nargs="?", default="-", help="UTF-8 report JSON or - for stdin")
    parser.add_argument("--output", default="-", help="CSV path or - for stdout")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        document = read_document(args.input)
    except (OSError, ValueError, UnicodeDecodeError, json.JSONDecodeError, DuplicateJsonKeyError):
        sys.stderr.write("Report input is not valid UTF-8 JSON.\n")
        return 2
    validation = validate_report(document)
    if validation["summary"]["error_count"]:
        sys.stderr.write("Report validation failed; CSV was not written.\n")
        return 2
    if args.output == "-":
        write_csv(document, sys.stdout)
    else:
        with open(args.output, "w", encoding="utf-8", newline="") as handle:
            write_csv(document, handle)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
