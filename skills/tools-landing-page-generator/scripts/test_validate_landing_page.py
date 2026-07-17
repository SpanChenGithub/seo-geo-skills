#!/usr/bin/env python3
"""Unit tests for validate_landing_page.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from validate_landing_page import validate_package


KEYWORD = "storyboard maker"
CANONICAL = "https://cutto.ai/storyboard-maker/"
TITLE = "Storyboard Maker: Plan Clear Video Scenes Online"
DESCRIPTION = (
    "Use this storyboard maker to organize video ideas into clear scenes, review the planned flow, and prepare a practical shot sequence before production begins."
)

FAQS = [
    ("What is a storyboard maker?", "A storyboard maker is a planning tool that organizes a video idea into scenes so you can review the visual order before production begins."),
    ("How do I plan a storyboard?", "Describe the idea, review the proposed scenes, adjust the order and details, then keep the approved plan ready for your production workflow."),
    ("Who can use this planning page?", "Video creators, educators, marketers, and small teams can use the page to understand how structured scene planning may support an upcoming project."),
    ("Can I change the scene order?", "The final connected product workflow must confirm whether scene reordering is available. This sample page does not claim that the reserved tool area works."),
    ("Does this page create finished videos?", "No. This static demonstration explains a storyboard planning workflow and reserves space for a future product integration without simulating a working generator."),
    ("What should each scene include?", "A useful scene plan may include its purpose, subject, action, framing, dialogue, and transition when those details fit the intended video."),
    ("Can teams review the same storyboard?", "Collaboration support depends on the connected product. Confirm the real sharing and review features before publishing any collaboration claim on this page."),
    ("How is project data handled?", "Data handling depends on verified product policy. Publish storage, deletion, sharing, registration, and security details only after the responsible team confirms them."),
]


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_html(*, invalid: bool = False, old_order: bool = False) -> str:
    canonical = "https://example.com/TODO" if invalid else CANONICAL
    h1 = "Plan an Unverified Page" if invalid else "Storyboard Maker for Clear Video Planning"

    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": TITLE,
        "url": canonical,
        "description": DESCRIPTION,
        "inLanguage": "en-US",
    }
    app = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Cutto Storyboard Maker",
        "url": canonical,
        "description": DESCRIPTION,
        "applicationCategory": "MultimediaApplication",
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
            for question, answer in FAQS
        ],
    }

    how_steps = "".join(
        f'<li data-how-step><h3>{title}</h3><p>{text}</p></li>'
        for title, text in [
            ("Describe Your Idea", "Share the main subject, audience, and goal so the future integration has a clear starting point for scene planning."),
            ("Review the Scenes", "Read the proposed sequence and check whether each scene supports the message, pace, and intended viewing experience."),
            ("Prepare the Plan", "Keep the approved scene order and production notes ready for the people who will create the final video."),
        ]
    )
    why_points = "".join(
        f'<article data-why-point><h3>{title}</h3><p>{text}</p></article>'
        for title, text in [
            ("Clear Scene Order", "See how a structured sequence can make the production plan easier to review."),
            ("Practical Preparation", "Turn an early idea into a plan that can guide later production decisions."),
            ("Audience Focus", "Keep the intended viewer and message visible while you review each planned scene."),
            ("Honest Workflow", "Understand the proposed planning steps without mistaking this static page for a working tool."),
        ]
    )
    features = "".join(
        f'<article data-feature><h3>Planning Feature {index}</h3>'
        f'<p data-feature-description>This feature area explains one verified planning capability for a specific user, situation, task, problem, and practical benefit. The final page must replace this test wording with evidence based product copy before publication.</p>'
        f'<a data-feature-cta href="#tool-root">Review the Tool Area</a></article>'
        for index in range(1, 7)
    )
    comparisons = "".join(
        f'<tr data-comparison-product><th scope="row">{name}</th><td>Verified details belong here</td></tr>'
        for name in ["Cutto", "Competitor One", "Competitor Two", "Competitor Three", "Competitor Four", "Competitor Five"]
    )
    faq_items = "".join(
        f'<details data-faq-item><summary data-faq-question>{question}</summary><p data-faq-answer>{answer}</p></details>'
        for question, answer in FAQS
    )
    privacy = "".join(
        f'<article data-privacy-point><h3>{title}</h3><p>{text}</p></article>'
        for title, text in [
            ("Policy Evidence", "Publish only facts supported by the current official policy."),
            ("Storage Details", "Confirm storage behavior before making a public promise."),
            ("Deletion Details", "Confirm deletion timing before stating it on the page."),
            ("Sharing Details", "Confirm third party sharing terms with an authoritative source."),
        ]
    )

    section_parts = [
        f'''<section data-section="hero"><h1>{h1}</h1><p data-hero-description>Plan a clear video sequence, review each scene, and prepare practical production notes with an honest space reserved for the connected tool.</p><div id="tool-root" data-tool-placeholder role="region" aria-label="Reserved storyboard maker integration area"><!-- Replace this boundary with the verified product integration. --><p>This area is reserved for the verified Cutto tool interface.</p></div></section>''',
        f'''<section data-section="why-choose"><h2>Why Use Cutto for Storyboard Maker Planning</h2>{why_points}</section>''',
        f'''<section data-section="key-features"><h2>Storyboard Planning Features</h2><p>Connect verified product capabilities with practical planning needs.</p>{features}</section>''',
        f'''<section data-section="how-to"><h2>How to Plan a Storyboard</h2><p>Follow three clear planning steps after reviewing the key product features.</p><ol>{how_steps}</ol></section>''',
        f'''<section data-section="comparison"><h2>How Cutto Compares for Storyboard Maker Planning</h2><p>Review the same verified planning details for each relevant product.</p><table><thead><tr><th>Product</th><th>Planning detail</th></tr></thead><tbody>{comparisons}</tbody></table></section>''',
        f'''<section data-section="faq"><h2>Storyboard Maker Questions</h2>{faq_items}</section>''',
        f'''<section data-section="privacy"><h2>Privacy and Data Security</h2><p>Use verified policy details only.</p>{privacy}</section>''',
        '''<section data-section="final-cta"><div data-final-cta><h2>Prepare Your Storyboard Plan</h2><p>Review the planning approach, then connect the verified product when its implementation is ready.</p><a href="#tool-root">Review the Reserved Area</a></div></section>''',
    ]
    if invalid:
        section_parts = [part for part in section_parts if 'data-section="privacy"' not in part]
    if old_order:
        section_parts = [section_parts[0], section_parts[3], section_parts[1], section_parts[2], *section_parts[4:]]

    return f'''<!doctype html>
<html lang="en-US">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{TITLE}</title>
  <meta name="description" content="{DESCRIPTION}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{TITLE}">
  <meta property="og:description" content="{DESCRIPTION}">
  <meta property="og:url" content="{canonical}">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{TITLE}">
  <meta name="twitter:description" content="{DESCRIPTION}">
  <script type="application/ld+json">{json.dumps(webpage)}</script>
  <script type="application/ld+json">{json.dumps(app)}</script>
  <script type="application/ld+json">{json.dumps(faq)}</script>
  <style>:root {{ color-scheme: light; }} a:focus-visible {{ outline: 3px solid currentColor; }}</style>
</head>
<body>
  <header><a href="#main-content">Skip to content</a></header>
  <main id="main-content">{''.join(section_parts)}</main>
  <footer><p>Cutto</p></footer>
</body>
</html>'''


def make_package(root: Path, *, invalid: bool = False, old_order: bool = False) -> Path:
    package_name = "bad-package" if invalid else "old-order-package" if old_order else "storyboard-maker"
    package = root / package_name
    required_text = [
        "research/intake.md",
        "research/keyword-research-storyboard-maker.md",
        "research/style-report.md",
        "content/landing-page-copy.md",
        "content/seo-elements-storyboard-maker.md",
        "validation/qa-report.md",
    ]
    for relative in required_text:
        path = package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Test artifact\n", encoding="utf-8")

    write_json(
        package / "manifest.json",
        {
            "schemaVersion": "1.0",
            "keyword": KEYWORD,
            "keywordSlug": "storyboard-maker",
            "brandName": "Cutto",
            "productName": "Cutto Storyboard Maker",
            "canonicalUrl": CANONICAL if not invalid else "https://example.com/TODO",
            "pageLanguage": "en-US",
            "visualSourceMode": "site-extracted",
            "research": {
                "market": "United States",
                "language": "English",
                "device": "desktop",
                "date": "2026-07-17",
                "organicUsableCount": 15,
                "serpGatePassed": True,
                "redditStatus": "accessible",
                "quoraStatus": "accessible",
            },
            "artifacts": {},
            "validation": {"status": "pending"},
        },
    )
    write_json(package / "research/sources.json", [])
    write_json(package / "research/fact-ledger.json", [])
    write_json(package / "assets/asset-manifest.json", {"assets": []})
    (package / "index.html").write_text(build_html(invalid=invalid, old_order=old_order), encoding="utf-8")
    return package


class LandingPageValidatorTests(unittest.TestCase):
    def test_complete_package_has_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = make_package(Path(temp_dir))
            report = validate_package(package, KEYWORD)
            self.assertTrue(report["valid"], report["errors"])
            self.assertEqual([], report["errors"])

    def test_invalid_package_reports_core_failures(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = make_package(Path(temp_dir), invalid=True)
            report = validate_package(package, KEYWORD)
            codes = {issue["code"] for issue in report["errors"]}
            self.assertFalse(report["valid"])
            self.assertIn("structure.section_order", codes)
            self.assertIn("copy.h1_keyword", codes)
            self.assertIn("content.placeholder", codes)

    def test_previous_how_to_position_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            package = make_package(Path(temp_dir), old_order=True)
            report = validate_package(package, KEYWORD)
            codes = {issue["code"] for issue in report["errors"]}
            self.assertFalse(report["valid"])
            self.assertIn("structure.section_order", codes)


if __name__ == "__main__":
    unittest.main()
