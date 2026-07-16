#!/usr/bin/env python3
"""Validate a blog-post-writer article package with Python's standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


VERSION = "1.1.0"
JSON_FILES = (
    "brief.json",
    "serp-research.json",
    "sources.json",
    "outline.json",
    "meta.json",
    "quality-report.json",
    "structured-data.json",
)
TEXT_FILES = ("article.md", "media-plan.md")
OPTIONAL_FILES = ("draft.md",)

PLACEHOLDER_RE = re.compile(
    r"\[\s*needs?\s+source\s*\]|\bTODO\b|\bTBD\b|\bFIXME\b|"
    r"\{\{[^}\n]+\}\}|<\s*(?:insert|placeholder)[^>]*>",
    re.IGNORECASE,
)
DEFENSIVE_META_PATTERNS = (
    re.compile(r"\bnot (?:a )?hands[- ]on (?:comparison|review|test)\b", re.IGNORECASE),
    re.compile(
        r"\bwe (?:did not|didn't) (?:run|conduct|perform|complete) "
        r"(?:a |an )?(?:controlled )?(?:output )?(?:comparison|test|benchmark)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\bwe do not present\b.{0,160}\b(?:universal|objective)\b.{0,40}\b(?:winner|best)\b",
        re.IGNORECASE | re.DOTALL,
    ),
)
DEFENSIVE_META_WARNING_PATTERNS = (
    re.compile(r"(?m)^\s*\*\*Disclosure:\*\*", re.IGNORECASE),
    re.compile(
        r"\bwe (?:did not|didn't|have not|haven't) (?:independently )?"
        r"(?:test|benchmark|verify|confirm|evaluate)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bwe found no official basis for (?:claiming|saying)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:a |an )?(?:controlled|independent)\b.{0,60}\b"
        r"(?:comparison|benchmark|test) would require\b",
        re.IGNORECASE | re.DOTALL,
    ),
    re.compile(r"\b(?:those|these) inputs were not available\b", re.IGNORECASE),
    re.compile(r"\b(?:it|this guide) does not rank (?:measured )?\w+", re.IGNORECASE),
    re.compile(r"\bappears first because\b", re.IGNORECASE),
    re.compile(r"\bnot because (?:an )?independent benchmark\b", re.IGNORECASE),
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\((https?://[^)\s]+)\)")
REFERENCE_LINK_RE = re.compile(r"\[[^\]]+\]\[([^\]]+)\]")
REFERENCE_DEFINITION_RE = re.compile(
    r"(?m)^\s*\[([^\]]+)\]:\s*<?(https?://[^>\s]+)>?"
)
URL_RE = re.compile(r"https?://[^\s<>\"']+")
SECRET_PATTERNS = (
    re.compile(r"sk-(?:proj-|ant-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(
        r"(?i)(?:api[_ -]?key|access[_ -]?token|client[_ -]?secret|"
        r"bearer|password)\s*[=:]\s*[\"']?[A-Za-z0-9_./+\-=]{20,}"
    ),
)
SOURCE_HEADING_RE = re.compile(
    r"^#{1,6}\s+(?:sources?|references?|来源|参考资料|參考資料|資料來源|"
    r"出典|quellen|fuentes|fontes|bronnen)\s*$",
    re.IGNORECASE | re.MULTILINE,
)


class DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


def _is_http_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _normal_url(value: str) -> str:
    return value.rstrip("/.,;# )]}")


def _without_fenced_code(value: str) -> str:
    lines: list[str] = []
    in_fence = False
    fence_marker: str | None = None
    for line in value.splitlines():
        stripped = line.lstrip()
        marker = "```" if stripped.startswith("```") else "~~~" if stripped.startswith("~~~") else None
        if marker:
            if not in_fence:
                in_fence = True
                fence_marker = marker
            elif marker == fence_marker:
                in_fence = False
                fence_marker = None
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def _has_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_iso8601(value: Any) -> bool:
    if not _has_text(value):
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _region_is_valid(value: Any) -> bool:
    if not isinstance(value, dict):
        return False
    status = value.get("status")
    region_value = value.get("value")
    if status == "specified":
        return _has_text(region_value)
    if status == "unspecified":
        return region_value is None or region_value == ""
    return False


def _iter_types(value: Any):
    if isinstance(value, dict):
        item_type = value.get("@type")
        if isinstance(item_type, str):
            yield item_type
        elif isinstance(item_type, list):
            yield from (item for item in item_type if isinstance(item, str))
        for child in value.values():
            yield from _iter_types(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_types(child)


def _nodes_with_type(value: Any, wanted: str) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    if isinstance(value, dict):
        item_type = value.get("@type")
        types = [item_type] if isinstance(item_type, str) else item_type if isinstance(item_type, list) else []
        if wanted in types:
            nodes.append(value)
        for child in value.values():
            nodes.extend(_nodes_with_type(child, wanted))
    elif isinstance(value, list):
        for child in value:
            nodes.extend(_nodes_with_type(child, wanted))
    return nodes


class Validator:
    def __init__(self, package_dir: Path) -> None:
        self.package_dir = package_dir
        self.errors: list[dict[str, str]] = []
        self.warnings: list[dict[str, str]] = []
        self.data: dict[str, Any] = {}
        self.text: dict[str, str] = {}

    def issue(self, level: str, code: str, file: str, message: str) -> None:
        getattr(self, f"{level}s").append(
            {"code": code, "file": file, "message": message}
        )

    def error(self, code: str, file: str, message: str) -> None:
        self.issue("error", code, file, message)

    def warning(self, code: str, file: str, message: str) -> None:
        self.issue("warning", code, file, message)

    def load(self) -> None:
        if not self.package_dir.is_dir():
            self.error("PACKAGE_NOT_DIRECTORY", ".", "Package path is not a directory.")
            return

        for filename in JSON_FILES + TEXT_FILES:
            path = self.package_dir / filename
            if not path.is_file():
                self.error("MISSING_REQUIRED_FILE", filename, "Required file is missing.")
                continue
            try:
                raw = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                self.error("FILE_READ_ERROR", filename, "File could not be read as UTF-8.")
                continue
            self.text[filename] = raw
            if filename.endswith(".json"):
                try:
                    parsed = json.loads(raw, object_pairs_hook=_unique_object)
                    self.data[filename] = parsed
                    if not isinstance(parsed, dict):
                        self.error("JSON_ROOT_INVALID", filename, "The top-level JSON value must be an object.")
                except (json.JSONDecodeError, DuplicateKeyError) as exc:
                    self.error("INVALID_JSON", filename, str(exc))

        for filename in OPTIONAL_FILES:
            path = self.package_dir / filename
            if path.is_file():
                try:
                    self.text[filename] = path.read_text(encoding="utf-8")
                except (OSError, UnicodeError):
                    self.warning("OPTIONAL_FILE_READ_ERROR", filename, "Optional file could not be read as UTF-8.")
            else:
                self.warning(
                    "OPTIONAL_DRAFT_MISSING",
                    filename,
                    "The default audit package includes a draft; omission should be intentional.",
                )

    def scan_secrets(self) -> None:
        for filename, raw in self.text.items():
            for pattern in SECRET_PATTERNS:
                if pattern.search(raw):
                    self.error(
                        "SECRET_LIKE_VALUE",
                        filename,
                        "Credential-shaped content found; remove it before delivery.",
                    )
                    break

    def validate_brief(self) -> None:
        filename = "brief.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return
        for key in ("schema_version", "primary_keyword", "language", "output_mode"):
            if not _has_text(value.get(key)):
                self.error("BRIEF_FIELD_MISSING", filename, f"{key} must be a non-empty string.")

        if not _region_is_valid(value.get("region")):
            self.error(
                "REGION_INVALID",
                filename,
                "region must contain a valid specified or unspecified status and matching value.",
            )

        if value.get("output_mode") not in {"files", "chat_only"}:
            self.error("OUTPUT_MODE_INVALID", filename, "output_mode must be files or chat_only.")
        if not isinstance(value.get("optional_inputs"), dict):
            self.error("BRIEF_OPTIONAL_INPUTS_INVALID", filename, "optional_inputs must be an object.")
        for key in ("assumptions", "open_risks"):
            if not isinstance(value.get(key), list):
                self.error("BRIEF_LIST_INVALID", filename, f"{key} must be an array.")
        for key in ("audience", "page_context"):
            if key not in value or (value[key] is not None and not isinstance(value[key], (str, dict))):
                self.error("BRIEF_CONTEXT_INVALID", filename, f"{key} must exist and be null, a string, or an object.")

    def validate_serp(self) -> None:
        filename = "serp-research.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return
        for key in ("schema_version", "query", "searched_at", "language"):
            if not _has_text(value.get(key)):
                self.error("SERP_FIELD_MISSING", filename, f"{key} must be a non-empty string.")
        if not _is_iso8601(value.get("searched_at")):
            self.error("SERP_DATE_INVALID", filename, "searched_at must be a parseable ISO 8601 timestamp.")
        if not _region_is_valid(value.get("region")):
            self.error("SERP_REGION_INVALID", filename, "region must follow the package region contract.")
        if not _has_text(value.get("search_environment")):
            self.error("SEARCH_ENVIRONMENT_MISSING", filename, "search_environment must describe the actual search context used.")
        queries = value.get("queries")
        if not isinstance(queries, list) or not queries:
            self.error("SERP_QUERIES_MISSING", filename, "queries must contain at least the primary SERP query.")
        else:
            for index, query in enumerate(queries):
                if not isinstance(query, dict) or not all(_has_text(query.get(key)) for key in ("text", "language", "purpose")):
                    self.error("SERP_QUERY_INVALID", filename, f"queries[{index}] needs text, language, and purpose.")
        if value.get("search_method") not in {"direct_search", "user_supplied"}:
            self.error(
                "SERP_METHOD_INVALID",
                filename,
                "search_method must be direct_search or user_supplied.",
            )

        results = value.get("results")
        if not isinstance(results, list):
            self.error("SERP_RESULTS_INVALID", filename, "results must be an array.")
            return
        if len(results) < 3:
            self.error(
                "SERP_EVIDENCE_INSUFFICIENT",
                filename,
                "At least three observed organic results are required for a formal package.",
            )
        elif len(results) < 5:
            self.warning(
                "SERP_EVIDENCE_THIN",
                filename,
                "Fewer than five results were recorded; document why the partial SERP is adequate.",
            )
        elif len(results) < 10:
            self.warning(
                "SERP_PARTIAL",
                filename,
                "Fewer than ten results were recorded; keep missing ranks in limitations.",
            )

        ranks: set[int] = set()
        urls: set[str] = set()
        for index, result in enumerate(results):
            label = f"results[{index}]"
            if not isinstance(result, dict):
                self.error("SERP_RESULT_INVALID", filename, f"{label} must be an object.")
                continue
            rank = result.get("rank")
            if not isinstance(rank, int) or rank < 1:
                self.error("SERP_RANK_INVALID", filename, f"{label}.rank must be a positive integer.")
            elif rank in ranks:
                self.error("SERP_RANK_DUPLICATE", filename, f"Duplicate observed rank {rank}.")
            else:
                ranks.add(rank)
            if not _has_text(result.get("title")):
                self.error("SERP_TITLE_MISSING", filename, f"{label}.title is required.")
            if not _has_text(result.get("snippet")):
                self.error("SERP_SNIPPET_MISSING", filename, f"{label}.snippet is required, even if it records that none was shown.")
            if not _is_iso8601(result.get("observed_at")):
                self.error("SERP_OBSERVED_AT_INVALID", filename, f"{label}.observed_at must be ISO 8601.")
            url = result.get("url")
            if not _is_http_url(url):
                self.error("SERP_URL_INVALID", filename, f"{label}.url must be absolute HTTP(S).")
            else:
                normal = _normal_url(url)
                if normal in urls:
                    self.warning("SERP_URL_DUPLICATE", filename, f"Duplicate result URL: {url}")
                urls.add(normal)

        missing_top_ranks = {1, 2, 3} - ranks
        if missing_top_ranks:
            self.error(
                "SERP_TOP_RANKS_MISSING",
                filename,
                "Formal research must include observed ranks 1, 2, and 3; missing: "
                + ", ".join(str(rank) for rank in sorted(missing_top_ranks)),
            )

        result_count = value.get("result_count")
        if not isinstance(result_count, int) or result_count < 0:
            self.error("SERP_COUNT_INVALID", filename, "result_count must be a non-negative integer.")
        elif result_count != len(results):
            self.warning(
                "SERP_COUNT_MISMATCH",
                filename,
                "result_count does not equal the number of stored results.",
            )
        for key in ("paa", "related_searches", "communities", "limitations"):
            if not isinstance(value.get(key), list):
                self.error("SERP_LIST_INVALID", filename, f"{key} must be an array.")
        if not isinstance(value.get("search_intent"), (str, dict, list)):
            self.error("SERP_INTENT_MISSING", filename, "search_intent must be recorded.")
        if not _has_text(value.get("format_recommendation")):
            self.error("SERP_FORMAT_MISSING", filename, "format_recommendation is required.")
        word_count = value.get("reference_word_count")
        if not isinstance(word_count, dict) or not all(key in word_count for key in ("min", "max", "rationale")) or not _has_text(word_count.get("rationale")):
            self.error("SERP_WORD_RANGE_INVALID", filename, "reference_word_count needs min, max, and rationale.")
        elif not isinstance(word_count.get("min"), int) or not isinstance(word_count.get("max"), int) or word_count["min"] < 0 or word_count["max"] < word_count["min"]:
            self.error("SERP_WORD_RANGE_INVALID", filename, "reference_word_count min and max must be a valid increasing integer range.")

    def validate_sources(self) -> tuple[set[str], set[str]]:
        filename = "sources.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return set(), set()
        sources = value.get("sources")
        if not isinstance(sources, list) or not sources:
            self.error("SOURCES_INVALID", filename, "sources must be a non-empty array.")
            return set(), set()

        ids: set[str] = set()
        urls: set[str] = set()
        for index, source in enumerate(sources):
            label = f"sources[{index}]"
            if not isinstance(source, dict):
                self.error("SOURCE_INVALID", filename, f"{label} must be an object.")
                continue
            source_id = source.get("id")
            if not _has_text(source_id):
                self.error("SOURCE_ID_MISSING", filename, f"{label}.id is required.")
            elif source_id in ids:
                self.error("SOURCE_ID_DUPLICATE", filename, f"Duplicate source id: {source_id}")
            else:
                ids.add(source_id)
            for key in ("title", "publisher", "source_type"):
                if not _has_text(source.get(key)):
                    self.error("SOURCE_FIELD_MISSING", filename, f"{label}.{key} is required.")
            if not _has_text(source.get("language")):
                self.error("SOURCE_LANGUAGE_MISSING", filename, f"{label}.language is required.")
            if not _has_text(source.get("notes")):
                self.error("SOURCE_NOTES_MISSING", filename, f"{label}.notes must contain a concise evidence note.")
            url = source.get("url")
            if not _is_http_url(url):
                self.error("SOURCE_URL_INVALID", filename, f"{label}.url must be absolute HTTP(S).")
            else:
                urls.add(_normal_url(url))
            if not _is_iso8601(source.get("retrieved_at")):
                self.error("SOURCE_RETRIEVED_AT_INVALID", filename, f"{label}.retrieved_at must be ISO 8601.")
            published_at = source.get("published_at")
            if published_at is not None and not _is_iso8601(published_at):
                self.error("SOURCE_PUBLISHED_AT_INVALID", filename, f"{label}.published_at must be null or ISO 8601.")
            if not isinstance(source.get("supports"), list) or not source.get("supports"):
                self.error("SOURCE_SUPPORTS_MISSING", filename, f"{label}.supports must name supported claims or sections.")
            elif not all(_has_text(item) for item in source["supports"]):
                self.error("SOURCE_SUPPORTS_INVALID", filename, f"{label}.supports entries must be non-empty strings.")
        return ids, urls

    def validate_outline(self, source_ids: set[str]) -> None:
        filename = "outline.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return
        for key in (
            "primary_keyword",
            "language",
            "working_title",
            "slug",
            "meta_description",
            "article_type",
        ):
            if not _has_text(value.get(key)):
                self.error("OUTLINE_FIELD_MISSING", filename, f"{key} must be a non-empty string.")
        if not _region_is_valid(value.get("region")):
            self.error("OUTLINE_REGION_INVALID", filename, "region must follow the package region contract.")
        if not isinstance(value.get("search_intent"), (str, dict, list)):
            self.error("OUTLINE_INTENT_INVALID", filename, "search_intent must be recorded.")
        if not isinstance(value.get("information_gain_plan"), list) or not value.get("information_gain_plan"):
            self.error("OUTLINE_INFORMATION_GAIN_INVALID", filename, "information_gain_plan must be a non-empty array.")
        if not isinstance(value.get("internal_link_plan"), list):
            self.error("OUTLINE_INTERNAL_LINKS_INVALID", filename, "internal_link_plan must be an array.")
        if "faq_plan" not in value or value.get("faq_plan") is not None and not isinstance(value.get("faq_plan"), (list, dict)):
            self.error("OUTLINE_FAQ_PLAN_INVALID", filename, "faq_plan must be null, an array, or an object.")

        approval = value.get("approval")
        if not isinstance(approval, dict) or approval.get("status") != "approved":
            self.error("OUTLINE_NOT_APPROVED", filename, "Explicit outline approval is required.")
        elif not _is_iso8601(approval.get("approved_at")):
            self.error("OUTLINE_APPROVAL_DATE_INVALID", filename, "approval.approved_at must be ISO 8601.")

        sections = value.get("sections")
        if not isinstance(sections, list) or not sections:
            self.error("OUTLINE_SECTIONS_MISSING", filename, "sections must be a non-empty array.")
        else:
            for index, section in enumerate(sections):
                if not isinstance(section, dict):
                    self.error("OUTLINE_SECTION_INVALID", filename, f"sections[{index}] must be an object.")
                    continue
                if not _has_text(section.get("heading")):
                    self.error("OUTLINE_HEADING_MISSING", filename, f"sections[{index}].heading is required.")
                if not isinstance(section.get("level"), int) or not 1 <= section["level"] <= 6:
                    self.error("OUTLINE_LEVEL_INVALID", filename, f"sections[{index}].level must be 1 through 6.")
                if not _has_text(section.get("purpose")):
                    self.error("OUTLINE_PURPOSE_MISSING", filename, f"sections[{index}].purpose is required.")
                if not isinstance(section.get("evidence_required"), bool):
                    self.error("OUTLINE_EVIDENCE_FLAG_MISSING", filename, f"sections[{index}].evidence_required must be boolean.")
                refs = section.get("sources", section.get("source_ids", []))
                if not isinstance(refs, list):
                    self.error("OUTLINE_SOURCES_INVALID", filename, f"sections[{index}].sources must be an array.")
                else:
                    if not all(_has_text(item) for item in refs):
                        self.error("OUTLINE_SOURCE_ID_INVALID", filename, f"sections[{index}].sources entries must be non-empty strings.")
                    unknown = sorted({item for item in refs if isinstance(item, str)} - source_ids)
                    if unknown:
                        self.error("OUTLINE_UNKNOWN_SOURCE", filename, f"sections[{index}] references unknown source IDs: {', '.join(unknown)}")
                    if section.get("evidence_required") is True and not refs:
                        self.error("OUTLINE_EVIDENCE_UNMAPPED", filename, f"sections[{index}] requires evidence but has no source IDs.")

    def validate_article(self, source_urls: set[str]) -> None:
        filename = "article.md"
        raw = self.text.get(filename)
        if raw is None:
            return
        if PLACEHOLDER_RE.search(raw):
            self.error("UNRESOLVED_PLACEHOLDER", filename, "Unresolved source or drafting placeholder found.")

        headings: list[int] = []
        in_fence = False
        h1_count = 0
        for line in raw.splitlines():
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            match = re.match(r"^(#{1,6})\s+\S", line)
            if match:
                level = len(match.group(1))
                headings.append(level)
                if level == 1:
                    h1_count += 1
        if h1_count != 1:
            self.error("H1_COUNT_INVALID", filename, f"Expected exactly one H1, found {h1_count}.")
        for previous, current in zip(headings, headings[1:]):
            if current > previous + 1:
                self.warning("HEADING_LEVEL_SKIPPED", filename, f"Heading level jumps from H{previous} to H{current}.")
                break

        article_urls = {_normal_url(url) for url in URL_RE.findall(raw)}
        if not article_urls:
            self.error("INLINE_SOURCES_MISSING", filename, "No publishable source URLs were found.")
        unmatched = sorted(article_urls - source_urls)
        if unmatched:
            self.error(
                "ARTICLE_LINK_NOT_IN_SOURCES",
                filename,
                "Every publishable URL, including internal links, must be manifested in sources.json: " + ", ".join(unmatched[:5]),
            )

        source_heading = SOURCE_HEADING_RE.search(raw)
        if source_heading:
            if re.search(r"(?m)^#{1,6}\s+\S", raw[source_heading.end() :]):
                self.error("SOURCES_SECTION_NOT_FINAL", filename, "The Sources or References section must be the final headed section.")
            body_before_sources = raw[: source_heading.start()]
        else:
            heading_matches = list(re.finditer(r"(?m)^#{1,6}\s+\S.*$", raw))
            final_section_urls: set[str] = set()
            if heading_matches:
                final_section = raw[heading_matches[-1].start() :]
                final_section_urls = {_normal_url(url) for url in URL_RE.findall(final_section)}
            if final_section_urls.intersection(source_urls):
                self.warning(
                    "SOURCES_HEADING_UNRECOGNIZED",
                    filename,
                    "The final linked source section appears localized; confirm its heading is clear in the article language.",
                )
            else:
                self.error("SOURCES_SECTION_MISSING", filename, "A final linked Sources or References section is required.")
            body_before_sources = raw[: heading_matches[-1].start()] if heading_matches else raw

        style_body = _without_fenced_code(body_before_sources)
        if any(pattern.search(style_body) for pattern in DEFENSIVE_META_PATTERNS):
            self.error(
                "DEFENSIVE_META_LANGUAGE",
                filename,
                "Rewrite boilerplate non-testing or audit narration as a confident, decision-relevant qualification; keep routine evidence boundaries in methodology or QA artifacts.",
            )
        elif any(pattern.search(style_body) for pattern in DEFENSIVE_META_WARNING_PATTERNS):
            self.warning(
                "DEFENSIVE_META_LANGUAGE_REVIEW",
                filename,
                "Review first-person evidence-limit wording and keep it only when it materially changes the reader's decision.",
            )

        reference_definitions = {
            reference_id.strip().casefold(): _normal_url(url)
            for reference_id, url in REFERENCE_DEFINITION_RE.findall(raw)
        }
        reference_uses = {
            reference_id.strip().casefold()
            for reference_id in REFERENCE_LINK_RE.findall(body_before_sources)
        }
        has_reference_link = bool(reference_uses.intersection(reference_definitions))
        if not MARKDOWN_LINK_RE.search(body_before_sources) and not has_reference_link:
            self.error("INLINE_SOURCE_LINKS_MISSING", filename, "At least one claim-level Markdown link is required before the final source list.")

        brief = self.data.get("brief.json")
        allow_em_dash = False
        if isinstance(brief, dict):
            optional = brief.get("optional_inputs")
            if isinstance(optional, dict):
                allow_em_dash = optional.get("em_dash") == "allow"
        if "—" in raw and not allow_em_dash:
            self.warning("EM_DASH_DEFAULT_VIOLATION", filename, "Em dashes are present while the default policy disallows them.")

    def validate_meta(self) -> None:
        filename = "meta.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return
        for key in ("seo_title", "meta_description", "slug", "summary", "language"):
            if not _has_text(value.get(key)):
                self.error("META_FIELD_INVALID", filename, f"{key} must be one non-empty string.")
        if not _region_is_valid(value.get("region")):
            self.error("META_REGION_INVALID", filename, "region must follow the package region contract.")
        allowed_keys = {"seo_title", "meta_description", "slug", "summary", "language", "region"}
        for key in value:
            if key not in allowed_keys:
                if re.search(r"(?i)(?:title|description|alternative|option|variant|candidate)", key):
                    self.error("META_ALTERNATIVES_PRESENT", filename, f"{key} violates the one-final-metadata rule.")
                else:
                    self.error("META_UNEXPECTED_FIELD", filename, f"Unexpected metadata field: {key}")
        slug = value.get("slug")
        if isinstance(slug, str) and (urlparse(slug).scheme or re.search(r"\s", slug)):
            self.error("SLUG_INVALID", filename, "slug must be a relative, whitespace-free slug, not a URL.")

    def validate_media_plan(self) -> None:
        filename = "media-plan.md"
        raw = self.text.get(filename)
        if raw is None:
            return
        lines = raw.splitlines()
        required_columns = {
            "asset_id": lambda cell: "asset" in cell and "id" in cell,
            "placement": lambda cell: "placement" in cell,
            "purpose": lambda cell: "purpose" in cell and "show" in cell,
            "capture_notes": lambda cell: "capture" in cell and ("annotation" in cell or "notes" in cell),
            "filename": lambda cell: "filename" in cell or ("file" in cell and "url" in cell),
            "source_method": lambda cell: "source" in cell and ("creation" in cell or "method" in cell),
            "alt_text": lambda cell: "alt" in cell and "text" in cell,
            "status": lambda cell: "status" in cell,
        }

        table = None
        for index, line in enumerate(lines[:-2]):
            if "|" not in line:
                continue
            headers = [
                re.sub(r"[^a-z0-9]+", " ", cell.casefold()).strip()
                for cell in line.strip().strip("|").split("|")
            ]
            mapping: dict[str, int] = {}
            for field, predicate in required_columns.items():
                for column_index, header in enumerate(headers):
                    if predicate(header):
                        mapping[field] = column_index
                        break
            if len(mapping) != len(required_columns):
                continue
            separators = [
                cell.strip()
                for cell in lines[index + 1].strip().strip("|").split("|")
            ]
            if len(separators) != len(headers) or not all(
                re.fullmatch(r":?-{3,}:?", cell) for cell in separators
            ):
                continue
            rows = []
            for candidate in lines[index + 2 :]:
                if "|" not in candidate or not candidate.strip():
                    break
                cells = [
                    cell.strip() for cell in candidate.strip().strip("|").split("|")
                ]
                if len(cells) == len(headers):
                    rows.append(cells)
            table = (mapping, rows)
            break

        if table is None:
            self.error("MEDIA_TABLE_MISSING", filename, "Media plan must use the exact contract table columns.")
            return
        mapping, rows = table
        if not rows:
            self.error("MEDIA_ROWS_MISSING", filename, "Media plan needs at least one substantive row.")
            return
        allowed_statuses = {"real", "generated", "pending", "omitted", "complete as text"}
        for row_index, row in enumerate(rows):
            for field, column_index in mapping.items():
                if not row[column_index].strip():
                    self.error("MEDIA_CELL_EMPTY", filename, f"Media row {row_index + 1} has an empty {field} cell.")
            status = re.sub(r"\s+", " ", row[mapping["status"]].casefold()).strip()
            if status not in allowed_statuses:
                self.error("MEDIA_STATUS_INVALID", filename, f"Media row {row_index + 1} uses an unsupported status: {status}")

    def validate_quality(self) -> None:
        filename = "quality-report.json"
        value = self.data.get(filename)
        if not isinstance(value, dict):
            return
        status = value.get("status")
        if status not in {"ready_for_final_approval", "final_approved", "needs_revision"}:
            self.error("QUALITY_STATUS_INVALID", filename, "status must use a documented workflow state.")
        elif status == "needs_revision":
            self.error("QUALITY_NOT_READY", filename, "A needs_revision package cannot pass validation.")
        for key in (
            "factual_claims_checked",
            "source_links_checked",
            "search_intent_satisfied",
            "originality_reviewed",
        ):
            if value.get(key) is not True:
                self.error("QUALITY_CHECK_INCOMPLETE", filename, f"{key} must be true for delivery.")
        if not _is_iso8601(value.get("checked_at")):
            self.error("QUALITY_DATE_INVALID", filename, "checked_at must be ISO 8601.")
        if not _has_text(value.get("information_gain_summary")):
            self.error("INFORMATION_GAIN_MISSING", filename, "information_gain_summary is required.")
        risks = value.get("remaining_risks")
        if not isinstance(value.get("limitations"), list):
            self.error("QUALITY_LIMITATIONS_INVALID", filename, "limitations must be an array.")
        if not isinstance(risks, list):
            self.error("QUALITY_RISKS_INVALID", filename, "remaining_risks must be an array.")
        elif risks:
            self.warning("REMAINING_RISKS", filename, f"{len(risks)} remaining risk(s) must be disclosed to the user.")
        validator_record = value.get("validator")
        if not isinstance(validator_record, dict):
            self.error("QUALITY_VALIDATOR_INVALID", filename, "validator must be an object.")
        elif (
            validator_record.get("status") != "passed"
            or validator_record.get("version") != VERSION
            or validator_record.get("errors") != 0
            or not isinstance(validator_record.get("warnings"), list)
        ):
            self.error("QUALITY_VALIDATOR_INCOMPLETE", filename, "validator must record the current passing version, zero errors, and warning codes.")
        if not _has_text(value.get("structured_data_decision")):
            self.error("STRUCTURED_DATA_DECISION_MISSING", filename, "structured_data_decision is required.")

        approval = value.get("approval")
        if not isinstance(approval, dict) or approval.get("status") not in {"pending", "approved"}:
            self.error("FINAL_APPROVAL_INVALID", filename, "approval must record pending or approved status.")
        elif status == "ready_for_final_approval":
            if approval.get("status") != "pending" or approval.get("approved_at") is not None:
                self.error("FINAL_APPROVAL_STATE_CONFLICT", filename, "ready_for_final_approval requires pending approval and null approved_at.")
        elif status == "final_approved":
            if approval.get("status") != "approved" or not _is_iso8601(approval.get("approved_at")):
                self.error("FINAL_APPROVAL_STATE_CONFLICT", filename, "final_approved requires approved status and an ISO 8601 approved_at.")

    def validate_structured_data(self) -> None:
        filename = "structured-data.json"
        value = self.data.get(filename)
        if value is None:
            return
        if isinstance(value, dict) and value.get("status") == "omitted":
            if not _has_text(value.get("reason")):
                self.error("SCHEMA_OMISSION_REASON_MISSING", filename, "An omitted schema record needs a reason.")
            if not _is_iso8601(value.get("eligibility_checked_at")):
                self.error("SCHEMA_OMISSION_DATE_INVALID", filename, "eligibility_checked_at must be ISO 8601.")
            return
        if not isinstance(value, dict) or value.get("@context") != "https://schema.org":
            self.error("SCHEMA_CONTEXT_INVALID", filename, "JSON-LD must use https://schema.org as @context.")
        types = set(_iter_types(value))
        if not types.intersection({"Article", "BlogPosting", "NewsArticle"}):
            self.error("ARTICLE_SCHEMA_MISSING", filename, "An Article, BlogPosting, or NewsArticle node is required.")
        else:
            article_nodes = []
            for type_name in ("Article", "BlogPosting", "NewsArticle"):
                article_nodes.extend(_nodes_with_type(value, type_name))
            if not any(_has_text(node.get("headline")) for node in article_nodes):
                self.error("ARTICLE_SCHEMA_HEADLINE_MISSING", filename, "The article node needs a verified headline.")

        article = self.text.get("article.md", "")
        for node in _nodes_with_type(value, "FAQPage"):
            main_entity = node.get("mainEntity")
            if not isinstance(main_entity, list) or not main_entity:
                self.error("FAQ_SCHEMA_EMPTY", filename, "FAQPage needs visible, non-empty mainEntity questions.")
            else:
                question_names = [
                    item.get("name", "").strip()
                    for item in main_entity
                    if isinstance(item, dict) and _has_text(item.get("name"))
                ]
                if not question_names or not any(name.casefold() in article.casefold() for name in question_names):
                    self.error("FAQ_SCHEMA_NOT_VISIBLE", filename, "FAQPage questions were not found in the visible article text.")

        for node in _nodes_with_type(value, "HowTo"):
            steps = node.get("step")
            if not isinstance(steps, list) or not steps:
                self.error("HOWTO_SCHEMA_EMPTY", filename, "HowTo needs visible, non-empty steps.")
            if not re.search(r"(?m)^\s*1[.)]\s+", article):
                self.error("HOWTO_SCHEMA_NOT_VISIBLE", filename, "HowTo is present but no visible ordered process was detected.")

    def validate_cross_file_consistency(self) -> None:
        brief = self.data.get("brief.json")
        serp = self.data.get("serp-research.json")
        outline = self.data.get("outline.json")
        meta = self.data.get("meta.json")
        if not all(isinstance(item, dict) for item in (brief, serp, outline, meta)):
            return

        primary = brief.get("primary_keyword")
        for filename, value, key in (
            ("serp-research.json", serp, "query"),
            ("outline.json", outline, "primary_keyword"),
        ):
            other = value.get(key)
            if _has_text(primary) and _has_text(other) and primary.strip().casefold() != other.strip().casefold():
                self.error("PRIMARY_KEYWORD_MISMATCH", filename, f"{key} must match brief.json primary_keyword.")

        language = brief.get("language")
        for filename, value in (("serp-research.json", serp), ("outline.json", outline), ("meta.json", meta)):
            other = value.get("language")
            if _has_text(language) and _has_text(other) and language.strip().casefold() != other.strip().casefold():
                self.error("LANGUAGE_MISMATCH", filename, "language must match brief.json.")

        region = brief.get("region")
        for filename, value in (("serp-research.json", serp), ("outline.json", outline), ("meta.json", meta)):
            if isinstance(region, dict) and isinstance(value.get("region"), dict) and value["region"] != region:
                self.error("REGION_MISMATCH", filename, "region must match brief.json.")

    def run(self) -> dict[str, Any]:
        self.load()
        if self.errors and not self.data and not self.text:
            return self.report()
        self.scan_secrets()
        self.validate_brief()
        self.validate_serp()
        source_ids, source_urls = self.validate_sources()
        self.validate_outline(source_ids)
        self.validate_article(source_urls)
        self.validate_meta()
        self.validate_media_plan()
        self.validate_quality()
        self.validate_structured_data()
        self.validate_cross_file_consistency()
        return self.report()

    def report(self) -> dict[str, Any]:
        return {
            "validator_version": VERSION,
            "package_dir": self.package_dir.name or ".",
            "status": "failed" if self.errors else "passed",
            "summary": {"errors": len(self.errors), "warnings": len(self.warnings)},
            "errors": self.errors,
            "warnings": self.warnings,
        }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path, help="Directory containing the article package")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--version", action="version", version=VERSION)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    report = Validator(args.package_dir).run()
    print(json.dumps(report, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
