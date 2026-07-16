#!/usr/bin/env python3
"""Unit tests for deterministic content-plan priority scoring."""

from __future__ import annotations

import unittest

from score_content_plan import ScoringError, score_artifact


def sample_artifact() -> dict:
    return {
        "schema_version": "1.0",
        "metadata": {
            "project_name": "示例 AI 工具",
            "site_domain_rating": 20,
        },
        "content_plan": [
            {
                "primary_keyword": "ai music generator",
                "topic": "AI Music",
                "funnel": "BOFU",
                "volume": 100,
                "traffic_potential": 200,
                "kd": 10,
                "commercial_relevance_score": 30,
                "strategic_value_score": 10,
            },
            {
                "primary_keyword": "how to make ai music",
                "topic": "AI Music",
                "funnel": "MOFU",
                "volume": 10,
                "traffic_potential": 20,
                "kd": 30,
                "commercial_relevance_score": 22,
                "strategic_value_score": 5,
            },
            {
                "primary_keyword": "ai music history",
                "topic": "AI Music Education",
                "funnel": "TOFU",
                "volume": 0,
                "traffic_potential": None,
                "kd": None,
                "commercial_relevance_score": 15,
                "strategic_value_score": 2,
            },
        ],
    }


class ScoreContentPlanTests(unittest.TestCase):
    def test_scores_and_sorts_rows(self) -> None:
        result = score_artifact(sample_artifact())
        rows = result["content_plan"]
        self.assertEqual(rows[0]["primary_keyword"], "ai music generator")
        self.assertEqual(rows[0]["priority"], "P1")
        self.assertEqual(rows[1]["priority"], "P2")
        self.assertEqual(rows[2]["priority"], "P3")
        self.assertTrue(rows[2]["score_is_provisional"])
        self.assertLessEqual(rows[2]["priority_score"], 74)

    def test_zero_is_not_missing(self) -> None:
        result = score_artifact(sample_artifact())
        row = next(item for item in result["content_plan"] if item["primary_keyword"] == "ai music history")
        self.assertEqual(row["score_breakdown"]["demand"], 0)

    def test_rejects_invalid_discrete_relevance(self) -> None:
        artifact = sample_artifact()
        artifact["content_plan"][0]["commercial_relevance_score"] = 29
        with self.assertRaises(ScoringError):
            score_artifact(artifact)

    def test_rejects_zero_relevance_planned_page(self) -> None:
        artifact = sample_artifact()
        artifact["content_plan"][0]["commercial_relevance_score"] = 0
        with self.assertRaises(ScoringError):
            score_artifact(artifact)


if __name__ == "__main__":
    unittest.main()
