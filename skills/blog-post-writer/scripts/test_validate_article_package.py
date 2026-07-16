#!/usr/bin/env python3
"""Unit tests for validate_article_package.py."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_article_package import VERSION, Validator


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="blog-package-test-"))
        self.created: list[Path] = []
        self.write_package()

    def tearDown(self) -> None:
        for path in reversed(self.created):
            if path.is_file():
                path.unlink()
        if self.root.is_dir():
            self.root.rmdir()

    def write(self, name: str, value) -> None:
        path = self.root / name
        if isinstance(value, (dict, list)):
            path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            path.write_text(value, encoding="utf-8")
        self.created.append(path)

    def write_package(self) -> None:
        region = {"value": None, "status": "unspecified"}
        self.write(
            "brief.json",
            {
                "schema_version": "1.0",
                "primary_keyword": "example keyword",
                "language": "en",
                "region": region,
                "audience": None,
                "page_context": None,
                "optional_inputs": {},
                "assumptions": [],
                "open_risks": [],
                "output_mode": "files",
            },
        )
        results = [
            {
                "rank": rank,
                "title": f"Result {rank}",
                "url": f"https://example{rank}.com/article",
                "snippet": "Observed result summary.",
                "observed_at": "2026-07-14T10:00:00Z",
            }
            for rank in range(1, 6)
        ]
        self.write(
            "serp-research.json",
            {
                "schema_version": "1.0",
                "query": "example keyword",
                "searched_at": "2026-07-14T10:00:00Z",
                "language": "en",
                "region": region,
                "queries": [{"text": "example keyword", "language": "en", "purpose": "primary SERP"}],
                "search_environment": "Host search environment; region unavailable",
                "search_method": "direct_search",
                "result_count": len(results),
                "results": results,
                "paa": [],
                "related_searches": [],
                "communities": [],
                "search_intent": {"primary": "informational"},
                "format_recommendation": "explainer",
                "reference_word_count": {"min": 1200, "max": 1800, "rationale": "Comparable coverage."},
                "limitations": ["Region unspecified."],
            },
        )
        self.write(
            "sources.json",
            {
                "sources": [
                    {
                        "id": "s1",
                        "title": "Primary source",
                        "url": "https://example1.com/article",
                        "publisher": "Example",
                        "source_type": "primary",
                        "language": "en",
                        "published_at": None,
                        "retrieved_at": "2026-07-14T10:05:00Z",
                        "supports": ["section-1"],
                        "notes": "Supports the definition.",
                    }
                ]
            },
        )
        self.write(
            "outline.json",
            {
                "primary_keyword": "example keyword",
                "language": "en",
                "region": region,
                "working_title": "Example Keyword Guide",
                "slug": "example-keyword",
                "meta_description": "Learn the example with sourced guidance.",
                "article_type": "explainer",
                "search_intent": "informational",
                "approval": {"status": "approved", "approved_at": "2026-07-14T10:10:00Z"},
                "sections": [
                    {
                        "heading": "What it means",
                        "level": 2,
                        "purpose": "Explain the concept with evidence.",
                        "evidence_required": True,
                        "sources": ["s1"],
                    }
                ],
                "information_gain_plan": ["Decision framework"],
                "internal_link_plan": [],
                "faq_plan": None,
            },
        )
        article = (
            "# Example Keyword Guide\n\n"
            "An example keyword can be explained with [primary evidence](https://example1.com/article).\n\n"
            "## What it means\n\nA concise, useful explanation.\n\n"
            "## Sources\n\n- [Example](https://example1.com/article)\n"
        )
        self.write("draft.md", article)
        self.write("article.md", article)
        self.write(
            "meta.json",
            {
                "seo_title": "Example Keyword Guide",
                "meta_description": "Learn the example with sourced guidance.",
                "slug": "example-keyword",
                "summary": "A concise explanation.",
                "language": "en",
                "region": region,
            },
        )
        self.write(
            "media-plan.md",
            "# Media Plan\n\n"
            "| Asset ID | Placement | Purpose and what to show | Capture or annotation notes | Filename or real URL | Source or creation method | Alt text | Status |\n"
            "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
            "| m1 | After definition | Explain the concept with a diagram | Label the two stages | example-diagram.svg | Original editorial diagram | Diagram explaining the example | pending |\n",
        )
        self.write(
            "quality-report.json",
            {
                "status": "ready_for_final_approval",
                "checked_at": "2026-07-14T10:20:00Z",
                "factual_claims_checked": True,
                "source_links_checked": True,
                "search_intent_satisfied": True,
                "originality_reviewed": True,
                "information_gain_summary": "Adds a decision framework.",
                "structured_data_decision": "Use a minimal verified BlogPosting node.",
                "limitations": ["Region unspecified."],
                "remaining_risks": [],
                "validator": {"status": "passed", "version": VERSION, "errors": 0, "warnings": ["SERP_PARTIAL"]},
                "approval": {"status": "pending", "approved_at": None},
            },
        )
        self.write(
            "structured-data.json",
            {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": "Example Keyword Guide",
            },
        )

    def validate(self):
        return Validator(self.root).run()

    def test_valid_package_passes_with_partial_serp_warning(self) -> None:
        report = self.validate()
        self.assertEqual("passed", report["status"])
        self.assertIn("SERP_PARTIAL", {item["code"] for item in report["warnings"]})

    def test_missing_required_file_fails(self) -> None:
        path = self.root / "meta.json"
        path.unlink()
        self.created.remove(path)
        report = self.validate()
        self.assertEqual("failed", report["status"])
        self.assertIn("MISSING_REQUIRED_FILE", {item["code"] for item in report["errors"]})

    def test_unapproved_outline_and_placeholder_fail(self) -> None:
        outline_path = self.root / "outline.json"
        outline = json.loads(outline_path.read_text(encoding="utf-8"))
        outline["approval"]["status"] = "pending"
        outline_path.write_text(json.dumps(outline), encoding="utf-8")
        article_path = self.root / "article.md"
        article_path.write_text(article_path.read_text(encoding="utf-8") + "\n[NEEDS SOURCE]\n", encoding="utf-8")
        report = self.validate()
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("OUTLINE_NOT_APPROVED", codes)
        self.assertIn("UNRESOLVED_PLACEHOLDER", codes)

    def test_defensive_meta_language_fails(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "An example keyword can be explained",
            "This is not a hands-on comparison. We did not run a controlled output test. "
            "An example keyword can be explained",
        )
        article_path.write_text(article, encoding="utf-8")
        report = self.validate()
        self.assertIn("DEFENSIVE_META_LANGUAGE", {item["code"] for item in report["errors"]})

    def test_confident_editorial_authorship_line_passes(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "An example keyword can be explained",
            "Created by the Example editorial team, this guide applies the same practical criteria to every option. "
            "An example keyword can be explained",
        )
        article_path.write_text(article, encoding="utf-8")
        self.assertEqual("passed", self.validate()["status"])

    def test_claim_specific_evidence_limit_passes(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "A concise, useful explanation.",
            "The provider does not document a retention period for this workflow, so check the current policy before uploading.",
        )
        article_path.write_text(article, encoding="utf-8")
        self.assertEqual("passed", self.validate()["status"])

    def test_fenced_and_sources_examples_do_not_trigger_defensive_language(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "## Sources",
            "```text\nThis is not a hands-on comparison.\n```\n\n## Sources",
        )
        article += "\n- Source title: We did not run a controlled output test\n"
        article_path.write_text(article, encoding="utf-8")
        self.assertEqual("passed", self.validate()["status"])

    def test_broader_defensive_language_requests_review(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "A concise, useful explanation.",
            "We found no official basis for claiming a universal outcome, so compare the documented workflows.",
        )
        article_path.write_text(article, encoding="utf-8")
        report = self.validate()
        self.assertEqual("passed", report["status"])
        self.assertIn("DEFENSIVE_META_LANGUAGE_REVIEW", {item["code"] for item in report["warnings"]})

    def test_bold_disclosure_block_requests_review(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "An example keyword can be explained",
            "**Disclosure:** Example publishes this guide and appears in it.\n\nAn example keyword can be explained",
        )
        article_path.write_text(article, encoding="utf-8")
        report = self.validate()
        self.assertEqual("passed", report["status"])
        self.assertIn("DEFENSIVE_META_LANGUAGE_REVIEW", {item["code"] for item in report["warnings"]})

    def test_secret_like_value_fails(self) -> None:
        article_path = self.root / "article.md"
        article_path.write_text(
            article_path.read_text(encoding="utf-8")
            + "\napi_key="
            + "abcdefghijklmnop"
            + "qrstuvwxyz123456\n",
            encoding="utf-8",
        )
        report = self.validate()
        self.assertIn("SECRET_LIKE_VALUE", {item["code"] for item in report["errors"]})

    def test_unlisted_localized_sources_heading_is_not_a_blocker(self) -> None:
        article_path = self.root / "article.md"
        article_path.write_text(
            article_path.read_text(encoding="utf-8").replace("## Sources", "## แหล่งข้อมูล"),
            encoding="utf-8",
        )
        report = self.validate()
        self.assertEqual("passed", report["status"])
        self.assertIn("SOURCES_HEADING_UNRECOGNIZED", {item["code"] for item in report["warnings"]})

    def test_needs_revision_and_non_iso_dates_fail(self) -> None:
        quality_path = self.root / "quality-report.json"
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality["status"] = "needs_revision"
        quality["checked_at"] = "not-a-date"
        quality_path.write_text(json.dumps(quality), encoding="utf-8")
        report = self.validate()
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("QUALITY_NOT_READY", codes)
        self.assertIn("QUALITY_DATE_INVALID", codes)

        serp_path = self.root / "serp-research.json"
        serp = json.loads(serp_path.read_text(encoding="utf-8"))
        serp["searched_at"] = "also-not-a-date"
        serp_path.write_text(json.dumps(serp), encoding="utf-8")
        self.assertIn("SERP_DATE_INVALID", {item["code"] for item in self.validate()["errors"]})

    def test_unmanifested_article_link_fails(self) -> None:
        article_path = self.root / "article.md"
        article_path.write_text(
            article_path.read_text(encoding="utf-8").replace(
                "A concise, useful explanation.",
                "A concise [internal guide](https://mysite.example/guide).",
            ),
            encoding="utf-8",
        )
        report = self.validate()
        self.assertIn("ARTICLE_LINK_NOT_IN_SOURCES", {item["code"] for item in report["errors"]})

    def test_honest_structured_data_omission_passes(self) -> None:
        schema_path = self.root / "structured-data.json"
        schema_path.write_text(
            json.dumps(
                {
                    "status": "omitted",
                    "reason": "No verified deployment target was supplied.",
                    "eligibility_checked_at": "2026-07-14T10:15:00Z",
                }
            ),
            encoding="utf-8",
        )
        quality_path = self.root / "quality-report.json"
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality["structured_data_decision"] = "Omitted with an explicit audit record."
        quality_path.write_text(json.dumps(quality), encoding="utf-8")
        self.assertEqual("passed", self.validate()["status"])

    def test_final_approved_state_passes(self) -> None:
        quality_path = self.root / "quality-report.json"
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality["status"] = "final_approved"
        quality["approval"] = {"status": "approved", "approved_at": "2026-07-14T10:30:00Z"}
        quality_path.write_text(json.dumps(quality), encoding="utf-8")
        self.assertEqual("passed", self.validate()["status"])

    def test_missing_contract_fields_fail(self) -> None:
        brief_path = self.root / "brief.json"
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
        brief.pop("assumptions")
        brief_path.write_text(json.dumps(brief), encoding="utf-8")

        meta_path = self.root / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["title_candidates"] = ["One", "Two"]
        meta_path.write_text(json.dumps(meta), encoding="utf-8")

        report = self.validate()
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("BRIEF_LIST_INVALID", codes)
        self.assertIn("META_ALTERNATIVES_PRESENT", codes)

    def test_json_array_roots_cannot_bypass_validation(self) -> None:
        for name in (
            "brief.json",
            "serp-research.json",
            "outline.json",
            "meta.json",
            "quality-report.json",
        ):
            (self.root / name).write_text("[]", encoding="utf-8")
        report = self.validate()
        self.assertEqual("failed", report["status"])
        self.assertGreaterEqual(
            sum(item["code"] == "JSON_ROOT_INVALID" for item in report["errors"]),
            5,
        )

    def test_reference_style_and_html_links_must_be_manifested(self) -> None:
        article_path = self.root / "article.md"
        article = article_path.read_text(encoding="utf-8")
        article = article.replace(
            "A concise, useful explanation.",
            "A [reference-style source][extra] and <a href=\"https://raw-html.example/page\">HTML source</a>.\n\n[extra]: https://reference-style.example/page",
        )
        article_path.write_text(article, encoding="utf-8")
        report = self.validate()
        self.assertIn("ARTICLE_LINK_NOT_IN_SOURCES", {item["code"] for item in report["errors"]})

    def test_incomplete_media_meta_and_validator_records_fail(self) -> None:
        meta_path = self.root / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["seo_titles"] = ["Alternative A", "Alternative B"]
        meta_path.write_text(json.dumps(meta), encoding="utf-8")

        (self.root / "media-plan.md").write_text(
            "Placement: x Purpose and what to show: x Filename: x Alt text: x Status: pending",
            encoding="utf-8",
        )

        quality_path = self.root / "quality-report.json"
        quality = json.loads(quality_path.read_text(encoding="utf-8"))
        quality["validator"] = {}
        quality_path.write_text(json.dumps(quality), encoding="utf-8")

        report = self.validate()
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("META_ALTERNATIVES_PRESENT", codes)
        self.assertIn("MEDIA_TABLE_MISSING", codes)
        self.assertIn("QUALITY_VALIDATOR_INCOMPLETE", codes)

    def test_cross_file_region_and_language_mismatch_fail(self) -> None:
        meta_path = self.root / "meta.json"
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        meta["language"] = "fr"
        meta["region"] = {"value": "FR", "status": "specified"}
        meta_path.write_text(json.dumps(meta), encoding="utf-8")
        report = self.validate()
        codes = {item["code"] for item in report["errors"]}
        self.assertIn("LANGUAGE_MISMATCH", codes)
        self.assertIn("REGION_MISMATCH", codes)

    def test_report_does_not_expose_absolute_package_path(self) -> None:
        report = self.validate()
        self.assertEqual(self.root.name, report["package_dir"])
        self.assertNotIn(str(self.root.parent), json.dumps(report))


if __name__ == "__main__":
    unittest.main()
