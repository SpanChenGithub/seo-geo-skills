#!/usr/bin/env python3
"""Validate a completed tools landing-page package with Python's standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


REQUIRED_SECTIONS = [
    "hero",
    "why-choose",
    "key-features",
    "how-to",
    "comparison",
    "faq",
    "privacy",
    "final-cta",
]

VOID_TAGS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}

SKIP_VISIBLE_TAGS = {"script", "style", "code", "pre", "template"}
INTERACTIVE_TAGS = {"button", "form", "input", "select", "textarea"}
WORD_PATTERN = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z0-9]+)?")
PLACEHOLDER_PATTERN = re.compile(
    r"(?:\bTODO\b|\bTBD\b|\[NEEDS(?:\s+SOURCE|\s+SPEC)?\]|"
    r"\[Brand(?:\s+Name)?\]|\[Target(?:\s+Keyword)?\]|"
    r"\{\{[^{}]+\}\}|example\.com|lorem\s+ipsum)",
    re.IGNORECASE,
)


@dataclass
class Node:
    tag: str
    attrs: dict[str, str | None] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)
    parent: "Node | None" = None


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), dict(attrs), parent=self.stack[-1])
        self.stack[-1].children.append(node)
        if tag.lower() not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag.lower(), dict(attrs), parent=self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag: str) -> None:
        wanted = tag.lower()
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == wanted:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


def walk(node: Node) -> Iterable[Node]:
    yield node
    for child in node.children:
        if isinstance(child, Node):
            yield from walk(child)


def descendants(node: Node) -> Iterable[Node]:
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from descendants(child)


def find_all(
    root: Node,
    *,
    tag: str | None = None,
    attr: str | None = None,
    value: str | None = None,
) -> list[Node]:
    matches: list[Node] = []
    for node in walk(root):
        if tag is not None and node.tag != tag:
            continue
        if attr is not None:
            if attr not in node.attrs:
                continue
            if value is not None and node.attrs.get(attr) != value:
                continue
        matches.append(node)
    return matches


def find_within(
    root: Node,
    *,
    tag: str | None = None,
    attr: str | None = None,
    value: str | None = None,
) -> list[Node]:
    matches: list[Node] = []
    for node in descendants(root):
        if tag is not None and node.tag != tag:
            continue
        if attr is not None:
            if attr not in node.attrs:
                continue
            if value is not None and node.attrs.get(attr) != value:
                continue
        matches.append(node)
    return matches


def text_content(node: Node, *, visible_only: bool = False) -> str:
    parts: list[str] = []

    def collect(current: Node) -> None:
        if visible_only and current.tag in SKIP_VISIBLE_TAGS:
            return
        for child in current.children:
            if isinstance(child, str):
                parts.append(child)
            else:
                collect(child)

    collect(node)
    return normalize_space(" ".join(parts))


def normalize_space(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalized_casefold(value: Any) -> str:
    return normalize_space(value).casefold()


def word_count(value: str) -> int:
    return len(WORD_PATTERN.findall(value))


def json_type_values(value: Any) -> set[str]:
    if isinstance(value, str):
        return {value}
    if isinstance(value, list):
        return {item for item in value if isinstance(item, str)}
    return set()


def strip_html(value: Any) -> str:
    return normalize_space(re.sub(r"<[^>]+>", " ", str(value or "")))


def parse_iso_date(value: str) -> datetime | None:
    candidate = value.strip()
    try:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", candidate):
            return datetime.combine(date.fromisoformat(candidate), datetime.min.time())
        if candidate.endswith("Z"):
            candidate = candidate[:-1] + "+00:00"
        return datetime.fromisoformat(candidate)
    except ValueError:
        return None


def first_json_entity(entities: list[dict[str, Any]], entity_type: str) -> dict[str, Any] | None:
    for entity in entities:
        if entity_type in json_type_values(entity.get("@type")):
            return entity
    return None


def add_issue(report: dict[str, Any], level: str, code: str, message: str) -> None:
    report[level].append({"code": code, "message": message})


def load_json_file(path: Path, report: dict[str, Any], code: str) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        add_issue(report, "errors", code, f"Cannot parse {path.name}: {exc}")
        return None


def require_artifacts(package_dir: Path, report: dict[str, Any]) -> dict[str, Any]:
    exact_files = [
        "index.html",
        "manifest.json",
        "research/intake.md",
        "research/sources.json",
        "research/fact-ledger.json",
        "research/style-report.md",
        "content/landing-page-copy.md",
        "assets/asset-manifest.json",
        "validation/qa-report.md",
    ]
    for relative in exact_files:
        path = package_dir / relative
        if not path.is_file():
            add_issue(report, "errors", "artifact.missing", f"Missing required artifact: {relative}")

    patterns = [
        ("research/keyword-research-*.md", "keyword research report"),
        ("content/seo-elements-*.md", "SEO elements artifact"),
    ]
    for pattern, label in patterns:
        if not any(package_dir.glob(pattern)):
            add_issue(report, "errors", "artifact.missing", f"Missing required {label}: {pattern}")

    parsed_files: dict[str, Any] = {}
    for relative in [
        "manifest.json",
        "research/sources.json",
        "research/fact-ledger.json",
        "assets/asset-manifest.json",
    ]:
        path = package_dir / relative
        if path.is_file():
            parsed_files[relative] = load_json_file(path, report, "artifact.invalid_json")
    return parsed_files


def validate_manifest(
    manifest: Any,
    keyword: str,
    canonical: str,
    title: str,
    report: dict[str, Any],
) -> None:
    if not isinstance(manifest, dict):
        add_issue(report, "errors", "manifest.shape", "manifest.json must contain one JSON object.")
        return

    required = [
        "schemaVersion",
        "keyword",
        "keywordSlug",
        "brandName",
        "productName",
        "canonicalUrl",
        "pageLanguage",
        "visualSourceMode",
        "research",
        "artifacts",
        "validation",
    ]
    missing = [key for key in required if key not in manifest]
    if missing:
        add_issue(report, "errors", "manifest.fields", f"manifest.json is missing fields: {missing}.")

    if manifest.get("schemaVersion") != "1.0":
        add_issue(report, "errors", "manifest.version", "manifest.json schemaVersion must be 1.0.")
    if keyword and normalized_casefold(manifest.get("keyword")) != normalized_casefold(keyword):
        add_issue(report, "errors", "manifest.keyword", "Manifest keyword does not match the validator keyword.")
    if canonical and normalize_space(manifest.get("canonicalUrl")) != canonical:
        add_issue(report, "errors", "manifest.canonical", "Manifest canonicalUrl does not match HTML canonical.")

    allowed_modes = {"user-supplied", "local-project", "site-extracted", "user-approved-neutral-fallback"}
    mode = manifest.get("visualSourceMode")
    if mode not in allowed_modes:
        add_issue(report, "errors", "manifest.visual_mode", f"Unknown visualSourceMode: {mode!r}.")

    research = manifest.get("research")
    if not isinstance(research, dict):
        add_issue(report, "errors", "manifest.research", "Manifest research must be an object.")
    else:
        research_required = [
            "market",
            "language",
            "device",
            "date",
            "organicUsableCount",
            "serpGatePassed",
            "redditStatus",
            "quoraStatus",
        ]
        missing_research = [key for key in research_required if key not in research]
        if missing_research:
            add_issue(report, "errors", "manifest.research_fields", f"Manifest research is missing fields: {missing_research}.")

    brand = normalize_space(manifest.get("brandName"))
    if brand and title:
        brand_pattern = re.compile(rf"(?<![A-Za-z0-9]){re.escape(brand)}(?![A-Za-z0-9])", re.IGNORECASE)
        if brand_pattern.search(title):
            add_issue(report, "errors", "seo.title_brand", "Title must not contain the verified brand name.")


def meta_values(root: Node, key: str, *, property_name: bool = False) -> list[str]:
    attr_name = "property" if property_name else "name"
    values: list[str] = []
    for node in find_all(root, tag="meta"):
        if normalized_casefold(node.attrs.get(attr_name)) == key.casefold():
            values.append(normalize_space(node.attrs.get("content")))
    return values


def validate_identity(
    root: Node,
    entities: list[dict[str, Any]],
    report: dict[str, Any],
) -> tuple[str, str, str]:
    titles = [text_content(node) for node in find_all(root, tag="title")]
    if len(titles) != 1 or not titles[0]:
        add_issue(report, "errors", "seo.title_count", "HTML must contain exactly one non-empty title.")
    title = titles[0] if titles else ""
    report["metrics"]["title_characters"] = len(title)
    if title and not 50 <= len(title) <= 60:
        add_issue(report, "warnings", "seo.title_length", f"Title has {len(title)} characters; target is 50 to 60.")

    descriptions = meta_values(root, "description")
    if len(descriptions) != 1 or not descriptions[0]:
        add_issue(report, "errors", "seo.description_count", "HTML must contain exactly one non-empty Meta Description.")
    description = descriptions[0] if descriptions else ""
    report["metrics"]["meta_description_characters"] = len(description)
    if description and not 150 <= len(description) <= 160:
        add_issue(
            report,
            "warnings",
            "seo.description_length",
            f"Meta Description has {len(description)} characters; target is 150 to 160.",
        )

    canonicals: list[str] = []
    for node in find_all(root, tag="link"):
        rel_tokens = normalized_casefold(node.attrs.get("rel")).split()
        if "canonical" in rel_tokens:
            canonicals.append(normalize_space(node.attrs.get("href")))
    if len(canonicals) != 1 or not canonicals[0]:
        add_issue(report, "errors", "seo.canonical_count", "HTML must contain exactly one non-empty canonical link.")
    canonical = canonicals[0] if canonicals else ""
    parsed = urlparse(canonical)
    if canonical and (parsed.scheme != "https" or not parsed.netloc):
        add_issue(report, "errors", "seo.canonical_url", "Canonical must be an absolute HTTPS URL.")

    required_og = {
        "og:type": "website",
        "og:title": title,
        "og:description": description,
        "og:url": canonical,
    }
    for key, expected in required_og.items():
        values = meta_values(root, key, property_name=True)
        if len(values) != 1 or not values[0]:
            add_issue(report, "errors", "seo.open_graph", f"Missing or duplicate required {key} tag.")
        elif expected and values[0] != expected:
            add_issue(report, "errors", "seo.identity_mismatch", f"{key} does not match its source-of-truth value.")

    required_twitter = {
        "twitter:card": None,
        "twitter:title": title,
        "twitter:description": description,
    }
    for key, expected in required_twitter.items():
        values = meta_values(root, key)
        if len(values) != 1 or not values[0]:
            add_issue(report, "errors", "seo.twitter", f"Missing or duplicate required {key} tag.")
        elif expected and values[0] != expected:
            add_issue(report, "errors", "seo.identity_mismatch", f"{key} does not match its source-of-truth value.")

    webpage = first_json_entity(entities, "WebPage")
    if webpage is not None:
        invariants = {
            "name": title,
            "description": description,
            "url": canonical,
        }
        for key, expected in invariants.items():
            if expected and normalize_space(webpage.get(key)) != expected:
                add_issue(report, "errors", "seo.identity_mismatch", f"WebPage.{key} does not match HTML metadata.")

    return title, description, canonical


def validate_json_ld(root: Node, report: dict[str, Any]) -> list[dict[str, Any]]:
    entities: list[dict[str, Any]] = []
    scripts = [
        node
        for node in find_all(root, tag="script")
        if normalized_casefold(node.attrs.get("type")) == "application/ld+json"
    ]
    if not scripts:
        add_issue(report, "errors", "schema.missing", "No JSON-LD blocks found in the document head.")

    for index, node in enumerate(scripts, start=1):
        raw = text_content(node)
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            add_issue(report, "errors", "schema.invalid_json", f"JSON-LD block {index} is invalid: {exc}")
            continue
        if not isinstance(value, dict):
            add_issue(report, "errors", "schema.array", f"JSON-LD block {index} must contain one object, not an array.")
            continue
        if "@graph" in value:
            add_issue(report, "errors", "schema.graph", f"JSON-LD block {index} combines entities in @graph; use separate blocks.")
            continue
        entities.append(value)

    type_counts: dict[str, int] = {}
    for entity in entities:
        for value in json_type_values(entity.get("@type")):
            type_counts[value] = type_counts.get(value, 0) + 1
    report["metrics"]["json_ld_types"] = type_counts

    if type_counts.get("WebPage", 0) != 1:
        add_issue(report, "errors", "schema.webpage", "Exactly one WebPage JSON-LD object is required.")
    if type_counts.get("SoftwareApplication", 0) != 1:
        add_issue(report, "errors", "schema.application", "Exactly one SoftwareApplication object is required.")
    if type_counts.get("FAQPage", 0) != 1:
        add_issue(report, "errors", "schema.faq", "Exactly one FAQPage object is required for the visible FAQ.")

    webpage = first_json_entity(entities, "WebPage")
    if webpage:
        published = webpage.get("datePublished")
        modified = webpage.get("dateModified")
        if bool(published) != bool(modified):
            add_issue(report, "errors", "schema.date_pair", "WebPage datePublished and dateModified must appear together or both be omitted.")
        if published and modified:
            published_dt = parse_iso_date(str(published))
            modified_dt = parse_iso_date(str(modified))
            if published_dt is None or modified_dt is None:
                add_issue(report, "errors", "schema.date_format", "WebPage dates must use valid ISO 8601 values.")
            elif modified_dt < published_dt:
                add_issue(report, "errors", "schema.date_order", "dateModified must not be earlier than datePublished.")
            else:
                today = datetime.now(timezone.utc).date()
                if published_dt.date() > today or modified_dt.date() > today:
                    add_issue(report, "errors", "schema.future_date", "Publication and modification dates must not be in the future.")

    app = first_json_entity(entities, "SoftwareApplication")
    if app:
        rating = app.get("aggregateRating")
        if rating is not None:
            if not isinstance(rating, dict) or not all(key in rating for key in ("ratingValue", "ratingCount")):
                add_issue(report, "errors", "schema.rating", "aggregateRating must include verified ratingValue and ratingCount.")
            else:
                add_issue(report, "warnings", "schema.rating_evidence", "Manually verify that aggregateRating is current, sourced, and visible on the page.")
        offers = app.get("offers")
        if offers is not None:
            offer_items = offers if isinstance(offers, list) else [offers]
            for offer in offer_items:
                if not isinstance(offer, dict) or "price" not in offer or "priceCurrency" not in offer:
                    add_issue(report, "errors", "schema.offer", "Every emitted offer must include verified price and priceCurrency.")

    return entities


def validate_sections(root: Node, keyword: str, report: dict[str, Any]) -> None:
    sections = find_all(root, attr="data-section")
    section_values = [normalize_space(node.attrs.get("data-section")) for node in sections]
    report["metrics"]["section_order"] = section_values
    if section_values != REQUIRED_SECTIONS:
        add_issue(
            report,
            "errors",
            "structure.section_order",
            f"Required section order is {REQUIRED_SECTIONS}; found {section_values}.",
        )

    section_by_name = {normalize_space(node.attrs.get("data-section")): node for node in sections}
    hero = section_by_name.get("hero")
    if hero:
        hero_h1s = find_within(hero, tag="h1")
        if len(hero_h1s) != 1:
            add_issue(report, "errors", "structure.hero_h1", "HERO must contain exactly one H1.")
        elif keyword and normalized_casefold(keyword) not in normalized_casefold(text_content(hero_h1s[0])):
            add_issue(report, "errors", "copy.h1_keyword", "H1 must contain the exact target keyword naturally.")

        hero_descriptions = find_within(hero, attr="data-hero-description")
        if len(hero_descriptions) != 1:
            add_issue(report, "errors", "structure.hero_description", "HERO must contain one data-hero-description element.")
        else:
            count = word_count(text_content(hero_descriptions[0], visible_only=True))
            report["metrics"]["hero_description_words"] = count
            if not 20 <= count <= 25:
                add_issue(report, "warnings", "copy.hero_description_length", f"HERO description has {count} words; target is 20 to 25.")

        tools = find_within(hero, attr="data-tool-placeholder")
        if len(tools) != 1:
            add_issue(report, "errors", "structure.tool_placeholder", "HERO must contain exactly one tool placeholder.")
        else:
            tool = tools[0]
            if tool.attrs.get("id") != "tool-root":
                add_issue(report, "errors", "structure.tool_id", "Tool placeholder must use id=tool-root.")
            if normalized_casefold(tool.attrs.get("role")) != "region" or not normalize_space(tool.attrs.get("aria-label")):
                add_issue(report, "errors", "a11y.tool_label", "Tool placeholder needs role=region and a non-empty aria-label.")
            interactive = [node for node in descendants(tool) if node.tag in INTERACTIVE_TAGS]
            interactive += [
                node
                for node in descendants(tool)
                if node.tag == "a" and normalize_space(node.attrs.get("href"))
            ]
            if interactive:
                add_issue(report, "errors", "placeholder.interactive", "Tool placeholder must not contain interactive or fake functional controls.")

    count_specs = [
        ("data-how-step", 3, 4, "How to steps"),
        ("data-why-point", 4, 4, "Why Choose points"),
        ("data-feature", 6, 6, "Key Features"),
        ("data-comparison-product", 6, 6, "comparison products"),
        ("data-faq-item", 8, 10, "FAQ items"),
        ("data-privacy-point", 4, 4, "privacy points"),
        ("data-final-cta", 1, 1, "Final CTA blocks"),
    ]
    for hook, minimum, maximum, label in count_specs:
        count = len(find_all(root, attr=hook))
        report["metrics"][hook] = count
        if not minimum <= count <= maximum:
            expected = str(minimum) if minimum == maximum else f"{minimum} to {maximum}"
            add_issue(report, "errors", "structure.item_count", f"Expected {expected} {label}; found {count}.")

    features = find_all(root, attr="data-feature")
    for index, feature in enumerate(features, start=1):
        descriptions = find_within(feature, attr="data-feature-description")
        ctas = find_within(feature, attr="data-feature-cta")
        if len(descriptions) != 1 or len(ctas) != 1:
            add_issue(report, "errors", "structure.feature_children", f"Feature {index} needs one description and one CTA.")
            continue
        count = word_count(text_content(descriptions[0], visible_only=True))
        if not 60 <= count <= 100:
            add_issue(report, "warnings", "copy.feature_length", f"Feature {index} has {count} words; approximately 80 is expected.")

    faqs = find_all(root, attr="data-faq-item")
    visible_faq: list[tuple[str, str]] = []
    for index, faq in enumerate(faqs, start=1):
        questions = find_within(faq, attr="data-faq-question")
        answers = find_within(faq, attr="data-faq-answer")
        if len(questions) != 1 or len(answers) != 1:
            add_issue(report, "errors", "structure.faq_children", f"FAQ item {index} needs one question and one answer.")
            continue
        question = text_content(questions[0], visible_only=True)
        answer = text_content(answers[0], visible_only=True)
        visible_faq.append((question, answer))
        count = word_count(answer)
        if not 20 <= count <= 50:
            add_issue(report, "warnings", "copy.faq_length", f"FAQ answer {index} has {count} words; target is 20 to 50.")

    report["_visible_faq"] = visible_faq


def validate_faq_schema(entities: list[dict[str, Any]], report: dict[str, Any]) -> None:
    faq_entity = first_json_entity(entities, "FAQPage")
    visible_faq = report.pop("_visible_faq", [])
    if faq_entity is None:
        return
    main_entity = faq_entity.get("mainEntity")
    if not isinstance(main_entity, list):
        add_issue(report, "errors", "schema.faq_shape", "FAQPage.mainEntity must be a list of visible questions.")
        return
    schema_faq: list[tuple[str, str]] = []
    for item in main_entity:
        if not isinstance(item, dict):
            continue
        answer = item.get("acceptedAnswer")
        answer_text = answer.get("text") if isinstance(answer, dict) else ""
        schema_faq.append((normalize_space(item.get("name")), strip_html(answer_text)))
    normalized_visible = [(normalized_casefold(q), normalized_casefold(a)) for q, a in visible_faq]
    normalized_schema = [(normalized_casefold(q), normalized_casefold(a)) for q, a in schema_faq]
    if normalized_visible != normalized_schema:
        add_issue(report, "errors", "schema.faq_mismatch", "FAQPage questions and answers must exactly match visible FAQ copy and order.")


def validate_accessibility_and_assets(root: Node, canonical: str, report: dict[str, Any]) -> None:
    html_nodes = find_all(root, tag="html")
    if len(html_nodes) != 1 or not normalize_space(html_nodes[0].attrs.get("lang")):
        add_issue(report, "errors", "a11y.lang", "HTML must contain one html element with a non-empty lang attribute.")

    mains = [node for node in find_all(root, tag="main") if node.attrs.get("id") == "main-content"]
    if len(mains) != 1:
        add_issue(report, "errors", "a11y.main", "HTML must contain exactly one main element with id=main-content.")

    h1s = find_all(root, tag="h1")
    report["metrics"]["h1_count"] = len(h1s)
    if len(h1s) != 1:
        add_issue(report, "errors", "a11y.h1", f"HTML must contain exactly one H1; found {len(h1s)}.")
    elif not 5 <= word_count(text_content(h1s[0], visible_only=True)) <= 10:
        add_issue(report, "warnings", "copy.h1_length", "H1 is outside the 5 to 10 word target; document any justified exception.")

    for index, image in enumerate(find_all(root, tag="img"), start=1):
        if "alt" not in image.attrs:
            add_issue(report, "errors", "a11y.image_alt", f"Image {index} is missing an alt attribute.")
        source = normalize_space(image.attrs.get("src"))
        if source.startswith(("http://", "https://")):
            add_issue(report, "warnings", "asset.remote", f"Image {index} uses a remote URL; verify authorization and that it is not a hotlink.")

    for node in find_all(root, tag="link"):
        rel_tokens = normalized_casefold(node.attrs.get("rel")).split()
        if "stylesheet" in rel_tokens:
            add_issue(report, "errors", "asset.external_css", "External stylesheets are not allowed; keep CSS inline.")
        if "preload" in rel_tokens and normalized_casefold(node.attrs.get("as")) == "font":
            add_issue(report, "errors", "asset.remote_font", "Remote or preloaded fonts are not allowed without an authorized local asset.")

    for node in find_all(root, tag="script"):
        if normalize_space(node.attrs.get("src")):
            add_issue(report, "errors", "asset.external_script", "External scripts are not allowed.")

    for index, link in enumerate(find_all(root, tag="a"), start=1):
        href = normalize_space(link.attrs.get("href"))
        if not href or href.lower().startswith("javascript:"):
            add_issue(report, "errors", "link.invalid", f"Link {index} has a missing or unsafe href.")

    robots = meta_values(root, "robots")
    if any("noindex" in normalized_casefold(value).split(",") for value in robots):
        add_issue(report, "errors", "seo.noindex", "Publishable landing page must not contain an accidental noindex directive.")

    if canonical:
        canonical_host = urlparse(canonical).hostname or ""
        visible = text_content(root, visible_only=True)
        if canonical_host.casefold() != "vidmage.ai" and "vidmage" in visible.casefold():
            add_issue(report, "errors", "content.example_brand", "VidMage text appears on a non-VidMage page.")


def validate_visible_copy(root: Node, raw_html: str, keyword: str, title: str, report: dict[str, Any]) -> None:
    visible = text_content(root, visible_only=True)
    dash_hits: list[str] = []
    if "—" in visible:
        dash_hits.append("em dash")
    if "–" in visible:
        dash_hits.append("en dash")
    if re.search(r"\s-\s", visible):
        dash_hits.append("spaced hyphen")
    if dash_hits:
        add_issue(report, "errors", "copy.dash_punctuation", f"Visible copy contains forbidden punctuation: {', '.join(dash_hits)}.")

    placeholder_hits = sorted({match.group(0) for match in PLACEHOLDER_PATTERN.finditer(raw_html)})
    if placeholder_hits:
        add_issue(report, "errors", "content.placeholder", f"Unresolved placeholder markers found: {placeholder_hits}.")

    if keyword and title and normalized_casefold(keyword) not in normalized_casefold(title):
        add_issue(report, "warnings", "seo.title_keyword", "Title does not contain the exact target keyword; document any justified grammatical variant.")


def validate_package(package_dir: Path, keyword: str = "") -> dict[str, Any]:
    report: dict[str, Any] = {
        "schemaVersion": "1.0",
        "package": str(package_dir.resolve()),
        "keyword": keyword,
        "valid": False,
        "errors": [],
        "warnings": [],
        "metrics": {},
    }

    if not package_dir.is_dir():
        add_issue(report, "errors", "package.missing", f"Package directory does not exist: {package_dir}")
        return report

    parsed_artifacts = require_artifacts(package_dir, report)
    html_path = package_dir / "index.html"
    if not html_path.is_file():
        return report

    try:
        raw_html = html_path.read_text(encoding="utf-8")
    except OSError as exc:
        add_issue(report, "errors", "html.read", f"Cannot read index.html: {exc}")
        return report

    parser = TreeParser()
    try:
        parser.feed(raw_html)
        parser.close()
    except Exception as exc:  # HTMLParser can surface malformed entity edge cases.
        add_issue(report, "errors", "html.parse", f"Cannot parse index.html: {exc}")
        return report

    entities = validate_json_ld(parser.root, report)
    title, _description, canonical = validate_identity(parser.root, entities, report)
    validate_manifest(parsed_artifacts.get("manifest.json"), keyword, canonical, title, report)
    validate_sections(parser.root, keyword, report)
    validate_faq_schema(entities, report)
    validate_accessibility_and_assets(parser.root, canonical, report)
    validate_visible_copy(parser.root, raw_html, keyword, title, report)

    report["valid"] = len(report["errors"]) == 0
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_dir", type=Path, help="Completed output/<keyword-slug> directory")
    parser.add_argument("--keyword", default="", help="Exact primary target keyword")
    parser.add_argument("--output", type=Path, help="Optional JSON report path")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = validate_package(args.package_dir, args.keyword)
    indent = 2 if args.pretty else None
    rendered = json.dumps(report, ensure_ascii=False, indent=indent, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
