#!/usr/bin/env python3
"""Validate SEO metadata structure and editorial length targets.

Read JSON from a file or stdin and write JSON to stdout. This script does not
perform SERP research or judge factual accuracy, intent fit, or copy quality.
It has no third-party dependencies and does not create or modify files.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path
from typing import Any


VALIDATOR_VERSION = "1.0"
SCHEMA_VERSION = "1.0"
MAX_INPUT_BYTES = 2 * 1024 * 1024
TITLE_TARGET = (50, 60)
DESCRIPTION_TARGET = (120, 158)


class CliUsageError(Exception):
    """Raised for invalid CLI usage."""


class DuplicateJsonKeyError(ValueError):
    """Raised when an object contains the same JSON key more than once."""


class InvalidJsonConstantError(ValueError):
    """Raised for NaN and Infinity, which are not valid JSON constants."""


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise CliUsageError(message)


def issue(severity: str, code: str, path: str, message: str) -> dict[str, str]:
    return {
        "severity": severity,
        "code": code,
        "path": path,
        "message": message,
    }


def length_policy() -> dict[str, Any]:
    return {
        "name": "editorial_display_width_target",
        "is_google_limit": False,
        "note": (
            "These display-width ranges are editorial drafting targets, "
            "not Google-enforced limits."
        ),
        "title_display_units": {
            "target_min": TITLE_TARGET[0],
            "target_max": TITLE_TARGET[1],
        },
        "meta_description_display_units": {
            "target_min": DESCRIPTION_TARGET[0],
            "target_max": DESCRIPTION_TARGET[1],
        },
    }


def error_payload(exit_code: int, code: str, message: str) -> dict[str, Any]:
    return {
        "validator_version": VALIDATOR_VERSION,
        "status": "error",
        "exit_code": exit_code,
        "length_policy": length_policy(),
        "summary": {
            "pages_received": 0,
            "pages_validated": 0,
            "candidates_validated": 0,
            "error_count": 1,
            "warning_count": 0,
        },
        "pages": [],
        "issues": [issue("error", code, "", message)],
    }


def emit(payload: dict[str, Any], pretty: bool) -> None:
    json.dump(
        payload,
        sys.stdout,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )
    sys.stdout.write("\n")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = JsonArgumentParser(
        description=(
            "Validate five SEO metadata candidates per page against "
            "editorial display-width targets."
        )
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="-",
        help="UTF-8 JSON file, or - for stdin (default: -)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON result",
    )
    return parser.parse_args(argv)


def read_input(source: str) -> bytes:
    if source == "-":
        data = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    else:
        data = Path(source).read_bytes()
    if len(data) > MAX_INPUT_BYTES:
        raise OSError(f"Input exceeds the {MAX_INPUT_BYTES}-byte size limit.")
    return data


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise InvalidJsonConstantError(f"Invalid JSON constant: {value}")


def load_json(data: bytes) -> Any:
    text = data.decode("utf-8", errors="strict")
    return json.loads(
        text,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )


def display_units(text: str) -> int:
    return sum(
        2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1
        for char in text
    )


def has_surrogate(text: str) -> bool:
    return any(0xD800 <= ord(char) <= 0xDFFF for char in text)


def has_control_character(text: str) -> bool:
    return any(unicodedata.category(char) == "Cc" for char in text)


def target_status(units: int, target: tuple[int, int]) -> str:
    if units < target[0]:
        return "below"
    if units > target[1]:
        return "above"
    return "within"


def validate_text(
    value: Any,
    path: str,
    field_label: str,
    target: tuple[int, int],
    issues: list[dict[str, str]],
) -> dict[str, Any] | None:
    if not isinstance(value, str):
        issues.append(
            issue("error", "E_FIELD_TYPE", path, f"{field_label} must be a string.")
        )
        return None

    if not value.strip():
        issues.append(
            issue("error", "E_TEXT_EMPTY", path, f"{field_label} must not be empty.")
        )
        return None

    invalid = False
    if has_surrogate(value):
        issues.append(
            issue(
                "error",
                "E_INVALID_UNICODE_SCALAR",
                path,
                f"{field_label} contains an invalid Unicode surrogate.",
            )
        )
        invalid = True

    if has_control_character(value):
        issues.append(
            issue(
                "error",
                "E_CONTROL_CHARACTER",
                path,
                f"{field_label} contains a control character.",
            )
        )
        invalid = True

    if value != value.strip():
        issues.append(
            issue(
                "warning",
                "W_EDGE_WHITESPACE",
                path,
                f"{field_label} has leading or trailing whitespace.",
            )
        )

    if unicodedata.normalize("NFC", value) != value:
        issues.append(
            issue(
                "warning",
                "W_NON_NFC",
                path,
                f"{field_label} is not Unicode NFC-normalized.",
            )
        )

    if invalid:
        return None

    units = display_units(value)
    status = target_status(units, target)
    if status != "within":
        direction = "below" if status == "below" else "above"
        code_field = "TITLE" if field_label == "Title" else "DESCRIPTION"
        issues.append(
            issue(
                "warning",
                f"W_{code_field}_{direction.upper()}_TARGET",
                path,
                (
                    f"{field_label} is {direction} the editorial "
                    f"target of {target[0]}–{target[1]} display units."
                ),
            )
        )

    return {
        "code_points": len(value),
        "display_units": units,
        "target_status": status,
    }


def add_unknown_field_issues(
    obj: dict[str, Any],
    allowed: set[str],
    path: str,
    issues: list[dict[str, str]],
) -> None:
    for key in sorted(set(obj) - allowed):
        issues.append(
            issue(
                "error",
                "E_UNKNOWN_FIELD",
                f"{path}/{key}",
                f"Unknown field: {key}",
            )
        )


def validate_document(document: Any) -> tuple[dict[str, Any], int]:
    issues: list[dict[str, str]] = []
    page_results: list[dict[str, Any]] = []
    candidates_validated = 0

    if not isinstance(document, dict):
        issues.append(
            issue("error", "E_FIELD_TYPE", "", "The JSON root must be an object.")
        )
        pages: list[Any] = []
    else:
        add_unknown_field_issues(document, {"schema_version", "pages"}, "", issues)

        if "schema_version" not in document:
            issues.append(
                issue(
                    "error",
                    "E_MISSING_FIELD",
                    "/schema_version",
                    "Missing required field: schema_version",
                )
            )
        elif document["schema_version"] != SCHEMA_VERSION:
            issues.append(
                issue(
                    "error",
                    "E_FIELD_TYPE",
                    "/schema_version",
                    f"schema_version must equal {SCHEMA_VERSION!r}.",
                )
            )

        raw_pages = document.get("pages")
        if not isinstance(raw_pages, list):
            issues.append(
                issue("error", "E_FIELD_TYPE", "/pages", "pages must be an array.")
            )
            pages = []
        else:
            pages = raw_pages
            if not 1 <= len(pages) <= 10:
                issues.append(
                    issue(
                        "error",
                        "E_PAGE_COUNT",
                        "/pages",
                        "pages must contain between 1 and 10 items.",
                    )
                )

    seen_page_ids: set[str] = set()

    for page_index, page in enumerate(pages):
        page_path = f"/pages/{page_index}"
        page_issue_start = len(issues)
        page_result: dict[str, Any] = {
            "page_id": None,
            "status": "error",
            "candidates": [],
        }

        if not isinstance(page, dict):
            issues.append(
                issue("error", "E_FIELD_TYPE", page_path, "Page item must be an object.")
            )
            page_results.append(page_result)
            continue

        add_unknown_field_issues(page, {"page_id", "candidates"}, page_path, issues)

        page_id = page.get("page_id")
        if not isinstance(page_id, str):
            issues.append(
                issue(
                    "error",
                    "E_FIELD_TYPE",
                    f"{page_path}/page_id",
                    "page_id must be a string.",
                )
            )
        elif not page_id.strip():
            issues.append(
                issue(
                    "error",
                    "E_TEXT_EMPTY",
                    f"{page_path}/page_id",
                    "page_id must not be empty.",
                )
            )
        else:
            page_result["page_id"] = page_id
            if page_id in seen_page_ids:
                issues.append(
                    issue(
                        "error",
                        "E_DUPLICATE_PAGE_ID",
                        f"{page_path}/page_id",
                        f"Duplicate page_id: {page_id}",
                    )
                )
            seen_page_ids.add(page_id)

        raw_candidates = page.get("candidates")
        if not isinstance(raw_candidates, list):
            issues.append(
                issue(
                    "error",
                    "E_FIELD_TYPE",
                    f"{page_path}/candidates",
                    "candidates must be an array.",
                )
            )
            candidates: list[Any] = []
        else:
            candidates = raw_candidates
            if len(candidates) != 5:
                issues.append(
                    issue(
                        "error",
                        "E_CANDIDATE_COUNT",
                        f"{page_path}/candidates",
                        "Each page must contain exactly 5 candidates.",
                    )
                )

        seen_pairs: set[tuple[str, str]] = set()
        seen_titles: set[str] = set()
        seen_descriptions: set[str] = set()

        for candidate_index, candidate in enumerate(candidates):
            candidate_path = f"{page_path}/candidates/{candidate_index}"
            candidate_result: dict[str, Any] = {"rank": candidate_index + 1}

            if not isinstance(candidate, dict):
                issues.append(
                    issue(
                        "error",
                        "E_FIELD_TYPE",
                        candidate_path,
                        "Candidate must be an object.",
                    )
                )
                page_result["candidates"].append(candidate_result)
                continue

            add_unknown_field_issues(
                candidate,
                {"title", "meta_description"},
                candidate_path,
                issues,
            )

            for required_field in ("title", "meta_description"):
                if required_field not in candidate:
                    issues.append(
                        issue(
                            "error",
                            "E_MISSING_FIELD",
                            f"{candidate_path}/{required_field}",
                            f"Missing required field: {required_field}",
                        )
                    )

            title = candidate.get("title")
            description = candidate.get("meta_description")
            candidate_result["title"] = title
            candidate_result["meta_description"] = description

            title_metrics = validate_text(
                title,
                f"{candidate_path}/title",
                "Title",
                TITLE_TARGET,
                issues,
            )
            description_metrics = validate_text(
                description,
                f"{candidate_path}/meta_description",
                "Meta Description",
                DESCRIPTION_TARGET,
                issues,
            )

            candidate_result["metrics"] = {
                "title": title_metrics,
                "meta_description": description_metrics,
            }

            if title_metrics is not None and description_metrics is not None:
                candidates_validated += 1
                pair = (title, description)
                if pair in seen_pairs:
                    issues.append(
                        issue(
                            "error",
                            "E_DUPLICATE_CANDIDATE",
                            candidate_path,
                            "Title and Meta Description duplicate an earlier candidate.",
                        )
                    )
                seen_pairs.add(pair)

                if title in seen_titles:
                    issues.append(
                        issue(
                            "warning",
                            "W_DUPLICATE_TITLE",
                            f"{candidate_path}/title",
                            "Title duplicates an earlier candidate on this page.",
                        )
                    )
                seen_titles.add(title)

                if description in seen_descriptions:
                    issues.append(
                        issue(
                            "warning",
                            "W_DUPLICATE_DESCRIPTION",
                            f"{candidate_path}/meta_description",
                            "Meta Description duplicates an earlier candidate on this page.",
                        )
                    )
                seen_descriptions.add(description)

            page_result["candidates"].append(candidate_result)

        page_issues = issues[page_issue_start:]
        if any(item["severity"] == "error" for item in page_issues):
            page_result["status"] = "error"
        elif page_issues:
            page_result["status"] = "advisory"
        else:
            page_result["status"] = "pass"
        page_results.append(page_result)

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

    payload = {
        "validator_version": VALIDATOR_VERSION,
        "status": status,
        "exit_code": exit_code,
        "length_policy": length_policy(),
        "summary": {
            "pages_received": len(pages),
            "pages_validated": len(page_results),
            "candidates_validated": candidates_validated,
            "error_count": error_count,
            "warning_count": warning_count,
        },
        "pages": page_results,
        "issues": issues,
    }
    return payload, exit_code


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    pretty = "--pretty" in args_list

    try:
        args = parse_args(args_list)
    except CliUsageError as exc:
        emit(error_payload(64, "E_CLI_USAGE", str(exc)), pretty)
        return 64

    try:
        raw = read_input(args.input)
    except (OSError, IOError) as exc:
        emit(error_payload(3, "E_INPUT_READ", str(exc)), args.pretty)
        return 3

    try:
        document = load_json(raw)
    except UnicodeDecodeError as exc:
        emit(error_payload(3, "E_INPUT_ENCODING", str(exc)), args.pretty)
        return 3
    except DuplicateJsonKeyError as exc:
        emit(error_payload(4, "E_JSON_DUPLICATE_KEY", str(exc)), args.pretty)
        return 4
    except (json.JSONDecodeError, InvalidJsonConstantError) as exc:
        emit(error_payload(4, "E_JSON_PARSE", str(exc)), args.pretty)
        return 4

    try:
        payload, exit_code = validate_document(document)
    except Exception as exc:  # Defensive JSON response for unexpected failures.
        emit(error_payload(70, "E_INTERNAL", str(exc)), args.pretty)
        return 70

    emit(payload, args.pretty)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
