#!/usr/bin/env python3
"""Offline tests for query fan-out collection and report validation."""

from __future__ import annotations

import copy
import io
import json
import os
import unittest
import urllib.error
from unittest import mock

import collect_queries
import export_report_csv
import validate_report


FAKE_OPENAI_KEY = "-".join(("sk", "proj", "TESTKEY0000000000000000"))
FAKE_GEMINI_KEY = "test-gemini-key-000000000000"
FAKE_ANTHROPIC_KEY = "-".join(("sk", "ant", "TESTKEY000000000000"))
FAKE_PERPLEXITY_KEY = "-".join(("pplx", "TESTKEY000000000000"))


def request_document(**overrides):
    document = {
        "schema_version": "1.0",
        "seed_input": "best project management software",
        "detected_language": "en",
        "target_locale": "unspecified",
        "providers": ["openai"],
        "runs_per_provider": 3,
        "queries_per_run": 12,
        "mode": "hybrid",
    }
    document.update(overrides)
    return collect_queries.validate_request(document)


def query_record(query_id, text, source_type, cluster_id, trace_path=None):
    return {
        "query_id": query_id,
        "text": text,
        "normalized_text": collect_queries.normalize_exact(text),
        "source_type": source_type,
        "form": "comparison",
        "information_gap": "comparison_criteria",
        "journey_stage": "evaluation",
        "intent": "commercial investigation",
        "language": "en",
        "platform_cluster_id": cluster_id,
        "trace_path": trace_path,
    }


def valid_report_document():
    q1 = query_record(
        "openai-r1-q01",
        "best project management software for small teams",
        "observed_tool_query",
        "openai-c01",
        "$.output[0].action.queries[0]",
    )
    q2 = query_record(
        "openai-r2-q01",
        "top project management tools for a small team",
        "synthetic_provider_query",
        "openai-c01",
    )
    q3 = query_record(
        "openai-r3-q01",
        "project management software pricing comparison",
        "heuristic_simulation",
        "openai-c02",
    )
    fallback_failure = {
        "code": "CREDENTIAL_MISSING",
        "provider": "openai",
        "run_index": 3,
        "message": "The third run used a host-model fallback.",
        "degraded": True,
    }
    return {
        "schema_version": "1.2",
        "status": "partial",
        "input": {
            "seed_input": "best project management software",
            "detected_language": "en",
            "target_locale": "unspecified",
            "persona_or_context": None,
            "business_context": None,
            "desired_answer_type": None,
            "url": None,
            "page_content_provided": False,
        },
        "intent_analysis": {
            "primary_intent": "Compare project management software.",
            "secondary_intents": [],
            "ambiguities": ["Team size is unspecified."],
            "important_attributes": ["pricing", "collaboration"],
            "journey_trust_action_risk_needs": ["independent comparisons"],
        },
        "configuration": {
            "analysis_timestamp": "2026-07-14T00:00:00Z",
            "mode": "hybrid",
            "requested_providers": ["openai"],
            "participating_providers": ["openai"],
            "runs_per_provider": 3,
            "queries_per_synthetic_run": 12,
            "api_execution_policy": "api_first",
            "network_access": True,
            "allow_paid_api_calls": True,
            "expanded_scope_authorized": False,
            "live_research_enabled": True,
            "external_search_signals_used": False,
        },
        "external_search_signals": [],
        "platforms": [
            {
                "platform_id": "openai",
                "provider": "OpenAI",
                "product_surface": "Responses API",
                "model": {
                    "requested": "chat-latest",
                    "actual": "chat-latest",
                    "actual_status": "confirmed",
                    "fallback_reason": None,
                },
                "execution_mode": "mixed",
                "observability_status": "query_strings_exposed",
                "runs": [
                    {
                        "run_index": 1,
                        "status": "success",
                        "attempts": 1,
                        "api_attempted": True,
                        "fallback_reason": None,
                        "queries": [q1],
                        "observed_query_count": 1,
                        "provider_search_query_count": 1,
                        "failure": None,
                    },
                    {
                        "run_index": 2,
                        "status": "success",
                        "attempts": 1,
                        "api_attempted": True,
                        "fallback_reason": "QUERY_TRACE_UNAVAILABLE",
                        "queries": [q2],
                        "observed_query_count": 0,
                        "provider_search_query_count": None,
                        "failure": None,
                    },
                    {
                        "run_index": 3,
                        "status": "degraded",
                        "attempts": 0,
                        "api_attempted": False,
                        "fallback_reason": "CREDENTIAL_MISSING",
                        "queries": [q3],
                        "observed_query_count": 0,
                        "provider_search_query_count": None,
                        "failure": copy.deepcopy(fallback_failure),
                    },
                ],
                "clusters": [
                    {
                        "cluster_id": "openai-c01",
                        "label": "small-team tool comparison",
                        "canonical_query": "best project management software for small teams",
                        "query_ids": ["openai-r1-q01", "openai-r2-q01"],
                        "run_indices": [1, 2],
                        "within_model_stability": {
                            "numerator": 2,
                            "denominator": 3,
                            "score": 0.666667,
                            "label": "medium",
                        },
                    },
                    {
                        "cluster_id": "openai-c02",
                        "label": "pricing comparison",
                        "canonical_query": "project management software pricing comparison",
                        "query_ids": ["openai-r3-q01"],
                        "run_indices": [3],
                        "within_model_stability": {
                            "numerator": 1,
                            "denominator": 3,
                            "score": 0.333333,
                            "label": "low",
                        },
                    },
                ],
            }
        ],
        "cross_platform_clusters": [
            {
                "cross_cluster_id": "cross-c01",
                "label": "small-team tool comparison",
                "canonical_query": "best project management software for small teams",
                "member_platform_clusters": [
                    {"platform_id": "openai", "cluster_id": "openai-c01"}
                ],
                "platform_ids": ["openai"],
                "cross_model_coverage": {
                    "numerator": 1,
                    "denominator": 1,
                    "score": 1.0,
                    "label": "high",
                },
                "interpretation": "The run set repeatedly compares tools for small teams.",
            },
            {
                "cross_cluster_id": "cross-c02",
                "label": "pricing comparison",
                "canonical_query": "project management software pricing comparison",
                "member_platform_clusters": [
                    {"platform_id": "openai", "cluster_id": "openai-c02"}
                ],
                "platform_ids": ["openai"],
                "cross_model_coverage": {
                    "numerator": 1,
                    "denominator": 1,
                    "score": 1.0,
                    "label": "high",
                },
                "interpretation": "Pricing is a decision-stage information need.",
            },
        ],
        "coverage_matrix": [
            {
                "cross_cluster_id": "cross-c01",
                "presence": {
                    "openai": True,
                    "gemini": False,
                    "google_ai_mode": False,
                    "claude": False,
                    "perplexity": False,
                },
            },
            {
                "cross_cluster_id": "cross-c02",
                "presence": {
                    "openai": True,
                    "gemini": False,
                    "google_ai_mode": False,
                    "claude": False,
                    "perplexity": False,
                },
            },
        ],
        "page_coverage": None,
        "recommended_page_topics": {
            "status": "available",
            "basis": "fanout_only",
            "unavailable_reason": None,
            "items": [
                {
                    "rank": 1,
                    "topic_id": "topic-01",
                    "label": "Project management tools for small teams",
                    "priority": "P0",
                    "action": "include_on_page",
                    "supporting_cross_cluster_ids": ["cross-c01"],
                    "supporting_signal_ids": [],
                    "coverage_guidance": "Explain the best-fit criteria for small teams and compare the leading options.",
                    "rationale": "This directly satisfies the primary comparison intent with answerable criteria.",
                    "suggested_format": "Comparison table followed by concise recommendations.",
                },
                {
                    "rank": 2,
                    "topic_id": "topic-02",
                    "label": "Pricing and plan comparison",
                    "priority": "P1",
                    "action": "include_on_page",
                    "supporting_cross_cluster_ids": ["cross-c02"],
                    "supporting_signal_ids": [],
                    "coverage_guidance": "Compare plan prices, limits, and the total cost for a small team.",
                    "rationale": "Pricing closes a decision-stage information gap and supports direct extraction.",
                    "suggested_format": "Dated pricing matrix with plan constraints.",
                },
            ],
        },
        "assumptions": ["The locale was not specified."],
        "limitations": [
            "This run does not reproduce the ChatGPT consumer product's private orchestration."
        ],
        "failures": [fallback_failure],
        "provenance": {
            "raw_api_responses_persisted": False,
            "api_keys_persisted": False,
            "observed_queries_preserved_verbatim": True,
            "consumer_product_equivalence_claimed": False,
        },
    }


class ParserTests(unittest.TestCase):
    def test_openai_extracts_only_search_actions(self):
        document = {
            "output": [
                {
                    "type": "web_search_call",
                    "action": {
                        "type": "search",
                        "queries": ["alpha query", "beta query"],
                    },
                },
                {
                    "type": "web_search_call",
                    "action": {"type": "open_page", "url": "https://example.com"},
                },
                {
                    "type": "message",
                    "content": [{"type": "output_text", "text": '{"queries":["fake"]}'}],
                },
            ]
        }
        values, searched = collect_queries.extract_openai_queries(document)
        self.assertTrue(searched)
        self.assertEqual([item[0] for item in values], ["alpha query", "beta query"])

    def test_openai_legacy_single_query(self):
        document = {
            "output": [
                {
                    "type": "web_search_call",
                    "action": {"type": "search", "query": "legacy query"},
                }
            ]
        }
        values, searched = collect_queries.extract_openai_queries(document)
        self.assertTrue(searched)
        self.assertEqual(values[0][0], "legacy query")

    def test_gemini_supports_current_and_legacy_paths(self):
        document = {
            "steps": [
                {"type": "thought", "summary": [{"text": "fake hidden query"}]},
                {
                    "type": "google_search_call",
                    "arguments": {"queries": ["current query"]},
                },
            ],
            "outputs": [
                {
                    "type": "google_search_call",
                    "arguments": {"query": "old interactions query"},
                }
            ],
            "candidates": [
                {
                    "groundingMetadata": {
                        "webSearchQueries": ["generate content query"]
                    }
                }
            ],
        }
        values, searched = collect_queries.extract_gemini_queries(document)
        self.assertTrue(searched)
        self.assertEqual(
            [item[0] for item in values],
            ["current query", "old interactions query", "generate content query"],
        )

    def test_claude_server_tool_query_is_observed(self):
        document = {
            "content": [
                {"type": "text", "text": "I'll search."},
                {
                    "type": "server_tool_use",
                    "id": "srvtoolu_test_1",
                    "name": "web_search",
                    "input": {"query": "claude observed query"},
                },
                {
                    "type": "web_search_tool_result",
                    "tool_use_id": "srvtoolu_test_1",
                    "content": [],
                },
            ]
        }
        values, searched = collect_queries.extract_claude_queries(document)
        self.assertTrue(searched)
        self.assertEqual(values[0][0], "claude observed query")

    def test_claude_unmatched_server_tool_query_is_not_observed(self):
        document = {
            "stop_reason": "pause_turn",
            "content": [
                {
                    "type": "server_tool_use",
                    "id": "srvtoolu_pending",
                    "name": "web_search",
                    "input": {"query": "not executed yet"},
                }
            ],
        }
        values, searched = collect_queries.extract_claude_queries(document)
        self.assertTrue(searched)
        self.assertEqual(values, [])

    def test_synthetic_json_parser_does_not_require_code_fence(self):
        values = collect_queries.parse_synthetic_queries(
            '{"queries":["one query",{"text":"two query"}]}'
        )
        self.assertEqual([item[0] for item in values], ["one query", "two query"])

    def test_exact_normalization_preserves_punctuation_distinction(self):
        self.assertEqual(
            collect_queries.normalize_exact("  BEST\u3000CRM  "), "best crm"
        )
        self.assertNotEqual(
            collect_queries.normalize_exact("best crm?"),
            collect_queries.normalize_exact("best crm"),
        )


class ProviderCollectionTests(unittest.TestCase):
    def test_api_first_plan_prefers_real_api_when_key_exists(self):
        request = request_document()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            payload = collect_queries.build_plan(
                request, collect_queries.all_environment_secrets()
            )
        entry = payload["plan"]["providers"][0]
        self.assertTrue(entry["api_execution_available"])
        self.assertTrue(entry["credential_available"])
        self.assertTrue(entry["will_call_api"])
        self.assertEqual(entry["execution_preference"], "observed_provider_api")
        self.assertTrue(entry["official_surface_api_route_available"])
        self.assertEqual(entry["corresponding_model_api_status"], "documented_default")
        self.assertEqual(entry["model_compatibility_check"], "documented_default")
        self.assertEqual(payload["plan"]["execution_policy"], "api_first")
        self.assertTrue(payload["plan"]["ordinary_default_plan_auto_authorized"])
        self.assertFalse(payload["plan"]["api_authorization_required"])
        self.assertTrue(payload["plan"]["api_execution_flag_required"])

    def test_api_first_plan_falls_back_when_key_is_missing(self):
        request = request_document()
        with mock.patch.dict(os.environ, {}, clear=True):
            payload = collect_queries.build_plan(request, [])
        entry = payload["plan"]["providers"][0]
        self.assertTrue(entry["api_execution_available"])
        self.assertFalse(entry["credential_available"])
        self.assertFalse(entry["will_call_api"])
        self.assertEqual(entry["execution_preference"], "host_model_fallback")
        self.assertEqual(entry["fallback"], "CREDENTIAL_MISSING")
        self.assertFalse(payload["plan"]["api_execution_flag_required"])

    def test_plan_distinguishes_surface_simulation_and_observed_api(self):
        request = request_document(
            providers=["google_ai_mode", "perplexity"], mode="hybrid"
        )
        with mock.patch.dict(
            os.environ,
            {
                "GEMINI_API_KEY": FAKE_GEMINI_KEY,
                "PERPLEXITY_API_KEY": FAKE_PERPLEXITY_KEY,
            },
            clear=True,
        ):
            payload = collect_queries.build_plan(
                request, collect_queries.all_environment_secrets()
            )
        entries = {item["provider"]: item for item in payload["plan"]["providers"]}
        ai_mode = entries["google_ai_mode"]
        self.assertEqual(ai_mode["call_kind"], "provider_synthetic")
        self.assertFalse(ai_mode["official_surface_api_route_available"])
        self.assertTrue(ai_mode["provider_simulation_api_available"])
        self.assertFalse(ai_mode["observed_query_trace_supported"])
        self.assertEqual(ai_mode["execution_preference"], "provider_synthetic_api")

        perplexity = entries["perplexity"]
        self.assertEqual(perplexity["call_kind"], "observed_api")
        self.assertTrue(perplexity["official_surface_api_route_available"])
        self.assertTrue(perplexity["observed_query_trace_supported"])
        self.assertEqual(perplexity["execution_preference"], "observed_provider_api")

    def test_local_network_gate_requires_flag_even_when_key_exists(self):
        request = request_document()
        fake_collector = mock.Mock()
        with mock.patch.dict(os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=False):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                payload, code = collect_queries.collect_document(request, False)
        self.assertEqual(code, 2)
        self.assertEqual(payload["error"]["code"], "API_EXECUTION_FLAG_REQUIRED")
        fake_collector.assert_not_called()

    def test_perplexity_non_pro_configuration_queries_are_synthetic(self):
        response = {
            "model": "sonar-pro",
            "choices": [
                {
                    "message": {
                        "content": '{"queries":["pricing comparison","user reviews"]}'
                    }
                }
            ],
            "usage": {"num_search_queries": 4},
            "search_results": [{"url": "https://example.com"}],
            "related_questions": ["must not become an observed query"],
        }
        request = request_document(
            providers=["perplexity"], models={"perplexity": "sonar"}
        )
        with mock.patch.object(
            collect_queries, "http_post_json", return_value=(response, 1, "req-1")
        ):
            run = collect_queries.collect_perplexity(
                request, 1, "sonar", FAKE_PERPLEXITY_KEY, []
            )
        self.assertEqual(run["provider_search_query_count"], 4)
        self.assertTrue(run["queries"])
        self.assertEqual(
            {item["source_type"] for item in run["queries"]},
            {"synthetic_provider_query"},
        )
        self.assertIsNone(run["observed_query_count"])
        self.assertNotIn(
            "must not become an observed query",
            [item["text"] for item in run["queries"]],
        )

    def test_perplexity_sonar_pro_stream_queries_are_observed(self):
        events = [
            {
                "object": "chat.reasoning",
                "model": "sonar-pro",
                "choices": [
                    {
                        "delta": {
                            "reasoning_steps": [
                                {
                                    "type": "web_search",
                                    "web_search": {
                                        "search_keywords": [
                                            "best crm for startups",
                                            "crm pricing comparison",
                                        ]
                                    },
                                }
                            ]
                        }
                    }
                ],
            },
            {
                "object": "chat.reasoning.done",
                "model": "sonar-pro",
                "usage": {"num_search_queries": 2},
                "search_results": [{"url": "https://example.com/crm"}],
            },
        ]
        request = request_document(providers=["perplexity"])
        with mock.patch.object(
            collect_queries,
            "http_post_sse_json",
            return_value=(events, 1, "req-p-stream"),
        ) as post:
            run = collect_queries.collect_perplexity(
                request, 1, "sonar-pro", FAKE_PERPLEXITY_KEY, []
            )
        payload = post.call_args.args[2]
        self.assertTrue(payload["stream"])
        self.assertEqual(payload["stream_mode"], "concise")
        self.assertEqual(payload["web_search_options"]["search_type"], "pro")
        self.assertEqual(run["status"], "success")
        self.assertEqual(run["observability_status"], "query_strings_exposed")
        self.assertEqual(run["observed_query_count"], 2)
        self.assertEqual(run["provider_search_query_count"], 2)
        self.assertEqual(
            {item["source_type"] for item in run["queries"]},
            {"observed_tool_query"},
        )
        self.assertIn(
            ".web_search.search_keywords[0]", run["queries"][0]["trace_path"]
        )
        self.assertNotIn(
            "PERPLEXITY_INTERNAL_QUERY_STRINGS_NOT_EXPOSED", run["warnings"]
        )

    def test_perplexity_sse_parser_handles_done_and_multiline_data(self):
        raw = (
            b'data: {"object":"chat.reasoning",\n'
            b'data: "choices":[]}\n\n'
            b'data: [DONE]\n\n'
        )
        self.assertEqual(
            collect_queries.parse_sse_json_events(raw),
            [{"object": "chat.reasoning", "choices": []}],
        )

    def test_claude_collector_marks_structured_query_observed(self):
        response = {
            "model": "claude-sonnet-4-6",
            "stop_reason": "end_turn",
            "content": [
                {
                    "type": "server_tool_use",
                    "id": "srvtoolu_prices",
                    "name": "web_search",
                    "input": {"query": "current project management prices"},
                },
                {
                    "type": "web_search_tool_result",
                    "tool_use_id": "srvtoolu_prices",
                    "content": [{"type": "web_search_result", "url": "https://example.com"}],
                },
            ],
        }
        request = request_document(providers=["claude"])
        with mock.patch.object(
            collect_queries, "http_post_json", return_value=(response, 1, "req-c")
        ):
            run = collect_queries.collect_claude(
                request, 1, "claude-sonnet-4-6", FAKE_ANTHROPIC_KEY, []
            )
        self.assertEqual(run["status"], "success")
        self.assertEqual(run["queries"][0]["source_type"], "observed_tool_query")
        self.assertIn("input.query", run["queries"][0]["trace_path"])

    def test_claude_pause_turn_waits_for_matching_result(self):
        paused = {
            "model": "claude-sonnet-4-6",
            "stop_reason": "pause_turn",
            "content": [
                {
                    "type": "server_tool_use",
                    "id": "srvtoolu_later",
                    "name": "web_search",
                    "input": {"query": "query completed on continuation"},
                }
            ],
        }
        completed = {
            "model": "claude-sonnet-4-6",
            "stop_reason": "end_turn",
            "content": [
                {
                    "type": "web_search_tool_result",
                    "tool_use_id": "srvtoolu_later",
                    "content": [],
                }
            ],
        }
        request = request_document(providers=["claude"])
        with mock.patch.object(
            collect_queries,
            "http_post_json",
            side_effect=[(paused, 1, "req-1"), (completed, 1, "req-2")],
        ):
            run = collect_queries.collect_claude(
                request, 1, "claude-sonnet-4-6", FAKE_ANTHROPIC_KEY, []
            )
        self.assertEqual(run["status"], "success")
        self.assertEqual(
            [item["text"] for item in run["queries"]],
            ["query completed on continuation"],
        )

    def test_claude_continuation_limit_does_not_promote_pending_queries(self):
        responses = []
        for index in range(3):
            responses.append(
                (
                    {
                        "model": "claude-sonnet-4-6",
                        "stop_reason": "pause_turn",
                        "content": [
                            {
                                "type": "server_tool_use",
                                "id": "srvtoolu_pending_%d" % index,
                                "name": "web_search",
                                "input": {"query": "pending query %d" % index},
                            }
                        ],
                    },
                    1,
                    "req-%d" % index,
                )
            )
        request = request_document(providers=["claude"])
        with mock.patch.object(
            collect_queries, "http_post_json", side_effect=responses
        ):
            run = collect_queries.collect_claude(
                request, 1, "claude-sonnet-4-6", FAKE_ANTHROPIC_KEY, []
            )
        self.assertEqual(run["status"], "degraded")
        self.assertEqual(run["queries"], [])
        self.assertIn("CLAUDE_PENDING_SEARCH_NOT_OBSERVED", run["warnings"])

    def test_environment_secret_is_redacted_from_provider_query(self):
        secret = "-".join(("sk", "proj", "REALSECRET00000000000000"))
        queries, changed = collect_queries.ordered_unique_queries(
            [("search for " + secret, "$.trace")], [secret]
        )
        self.assertTrue(changed)
        self.assertNotIn(secret, json.dumps(queries))

    def test_observed_query_is_preserved_verbatim_or_dropped(self):
        secret = "-".join(("sk", "proj", "REALSECRET00000000000000"))
        values, secret_dropped, invalid_dropped = (
            collect_queries.ordered_unique_observed_queries(
                [
                    ("  Exact observed query  ", "$.trace[0]"),
                    ("search for " + secret, "$.trace[1]"),
                ],
                [secret],
            )
        )
        self.assertEqual(values[0]["text"], "  Exact observed query  ")
        self.assertTrue(secret_dropped)
        self.assertFalse(invalid_dropped)

    def test_non_text_observed_trace_value_is_dropped_with_warning(self):
        response = {
            "model": "chat-latest",
            "output": [
                {
                    "type": "web_search_call",
                    "action": {"type": "search", "queries": [42]},
                }
            ],
        }
        request = request_document(providers=["openai"])
        with mock.patch.object(
            collect_queries, "http_post_json", return_value=(response, 1, "req-o")
        ) as post:
            run = collect_queries.collect_openai(
                request, 1, "chat-latest", FAKE_OPENAI_KEY, []
            )
        self.assertFalse(post.call_args.args[2]["store"])
        self.assertEqual(
            post.call_args.args[2]["max_tool_calls"],
            collect_queries.MAX_SEARCH_TOOL_CALLS_PER_RUN,
        )
        self.assertEqual(run["queries"], [])
        self.assertIn("OBSERVED_QUERY_DROPPED_INVALID", run["warnings"])

    def test_perplexity_disables_search_when_live_research_is_false(self):
        response = {
            "choices": [{"message": {"content": '{"queries":["crm pricing"]}'}}]
        }
        request = request_document(
            providers=["perplexity"], live_research=False, mode="hybrid"
        )
        with mock.patch.object(
            collect_queries, "http_post_json", return_value=(response, 1, "req-p")
        ) as post:
            run = collect_queries.collect_perplexity(
                request, 1, "sonar-pro", FAKE_PERPLEXITY_KEY, []
            )
        self.assertTrue(
            post.call_args.args[2]["web_search_options"]["disable_search"]
        )
        self.assertIsNone(run["actual_model"])
        self.assertIn("ACTUAL_MODEL_NOT_EXPOSED", run["warnings"])

    def test_live_research_false_uses_provider_synthetic_mode(self):
        self.assertEqual(
            collect_queries.call_kind("openai", "hybrid", False),
            "provider_synthetic",
        )

    def test_simulated_only_never_calls_provider_with_configured_key(self):
        request = request_document(mode="simulated_only")
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        self.assertEqual(plan["plan"]["planned_top_level_api_calls"], 0)
        self.assertEqual(
            plan["plan"]["providers"][0]["fallback"],
            "SIMULATED_ONLY_REQUESTED",
        )
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["pending_host_simulations"][0]["reason"],
            "SIMULATED_ONLY_REQUESTED",
        )
        fake_collector.assert_not_called()

    def test_no_network_policy_never_calls_provider_with_configured_key(self):
        request = request_document(network_access=False)
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        entry = plan["plan"]["providers"][0]
        self.assertFalse(entry["api_execution_allowed"])
        self.assertFalse(entry["will_call_api"])
        self.assertEqual(entry["fallback"], "API_POLICY_DISABLED")
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["pending_host_simulations"][0]["reason"],
            "NETWORK_ACCESS_DISABLED",
        )
        fake_collector.assert_not_called()

    def test_no_paid_api_policy_never_calls_provider_with_configured_key(self):
        request = request_document(allow_paid_api_calls=False)
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        self.assertFalse(plan["plan"]["providers"][0]["will_call_api"])
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["pending_host_simulations"][0]["reason"],
            "PAID_API_CALLS_DISABLED",
        )
        fake_collector.assert_not_called()

    def test_incompatible_model_id_never_calls_provider(self):
        request = request_document(models={"openai": "claude-not-an-openai-model"})
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        entry = plan["plan"]["providers"][0]
        self.assertEqual(entry["corresponding_model_api_status"], "incompatible_model_id")
        self.assertEqual(entry["fallback"], "MODEL_INCOMPATIBLE")
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["pending_host_simulations"][0]["reason"], "MODEL_INCOMPATIBLE"
        )
        fake_collector.assert_not_called()

    def test_non_search_model_family_never_calls_provider(self):
        self.assertEqual(
            collect_queries.model_api_compatibility(
                "gemini", "gemini-embedding-001"
            ),
            "operation_capability_unverified",
        )
        request = request_document(models={"openai": "gpt-image-2"})
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        entry = plan["plan"]["providers"][0]
        self.assertEqual(
            entry["corresponding_model_api_status"],
            "operation_capability_unverified",
        )
        self.assertEqual(
            entry["fallback"], "MODEL_OPERATION_UNSUPPORTED_OR_UNVERIFIED"
        )
        self.assertEqual(code, 1)
        self.assertEqual(
            payload["pending_host_simulations"][0]["reason"],
            "MODEL_OPERATION_UNSUPPORTED_OR_UNVERIFIED",
        )
        fake_collector.assert_not_called()

    def test_supported_search_model_families_pass_operation_gate(self):
        for provider, model in (
            ("claude", "claude-fable-5"),
            ("claude", "claude-mythos-preview"),
            ("gemini", "gemini-3.1-flash-image-preview"),
        ):
            with self.subTest(provider=provider, model=model):
                self.assertEqual(
                    collect_queries.model_api_compatibility(provider, model),
                    "verify_at_call_time",
                )

    def test_expanded_scope_requires_explicit_authorization(self):
        request = request_document(runs_per_provider=4, queries_per_run=20)
        fake_collector = mock.Mock()
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, False)
        self.assertTrue(plan["plan"]["expanded_scope"])
        self.assertTrue(plan["plan"]["api_authorization_required"])
        self.assertFalse(plan["plan"]["providers"][0]["will_call_api"])
        self.assertEqual(
            plan["plan"]["providers"][0]["execution_preference"],
            "await_scope_authorization",
        )
        self.assertEqual(code, 2)
        self.assertEqual(payload["error"]["code"], "SCOPE_AUTHORIZATION_REQUIRED")
        fake_collector.assert_not_called()

    def test_explicit_larger_user_scope_is_executable(self):
        request = request_document(
            runs_per_provider=4,
            queries_per_run=20,
            expanded_scope_authorized=True,
        )
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            plan = collect_queries.build_plan(request, [])
        self.assertFalse(plan["plan"]["api_authorization_required"])
        self.assertTrue(plan["plan"]["scope_authorized"])
        self.assertTrue(plan["plan"]["providers"][0]["will_call_api"])

    def test_claude_plan_counts_continuations_and_provider_fallback(self):
        request = request_document(providers=["claude"], runs_per_provider=3)
        with mock.patch.dict(
            os.environ, {"ANTHROPIC_API_KEY": FAKE_ANTHROPIC_KEY}, clear=True
        ):
            plan = collect_queries.build_plan(request, [])
        entry = plan["plan"]["providers"][0]
        self.assertEqual(entry["planned_initial_api_calls"], 3)
        self.assertEqual(entry["possible_continuation_calls"], 6)
        self.assertEqual(entry["possible_provider_synthetic_fallback_calls"], 3)
        self.assertEqual(plan["plan"]["maximum_top_level_api_calls"], 12)
        self.assertEqual(plan["plan"]["maximum_http_attempts"], 36)

    def test_empty_observed_trace_uses_same_provider_synthetic_fallback(self):
        request = request_document(runs_per_provider=1)
        observed = collect_queries.base_run("openai", "chat-latest", 1, "observed_api")
        observed.update(
            {
                "status": "degraded",
                "observability_status": "search_not_used",
                "http_attempts": 1,
                "warnings": ["SEARCH_NOT_USED"],
            }
        )
        synthetic = collect_queries.base_run(
            "openai", "chat-latest", 1, "provider_synthetic"
        )
        synthetic.update(
            {
                "status": "success",
                "observability_status": "simulation_only",
                "http_attempts": 1,
                "queries": [
                    {
                        "text": "crm pricing comparison",
                        "normalized_text": "crm pricing comparison",
                        "trace_path": None,
                        "source_type": "synthetic_provider_query",
                    }
                ],
            }
        )
        fake_collector = mock.Mock(side_effect=[observed, synthetic])
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                plan = collect_queries.build_plan(request, [])
                payload, code = collect_queries.collect_document(request, True)
        entry = plan["plan"]["providers"][0]
        self.assertEqual(entry["possible_provider_synthetic_fallback_calls"], 1)
        self.assertEqual(entry["maximum_http_attempts_per_run"], 6)
        self.assertEqual(plan["plan"]["maximum_top_level_api_calls"], 2)
        self.assertEqual(code, 0)
        self.assertEqual(fake_collector.call_count, 2)
        run = payload["runs"][0]
        self.assertEqual(run["call_kind"], "observed_api_then_provider_synthetic")
        self.assertEqual(run["http_attempts"], 2)
        self.assertEqual(run["fallback_reason"], "SEARCH_NOT_USED")
        self.assertEqual(run["queries"][0]["source_type"], "synthetic_provider_query")
        self.assertEqual(payload["pending_host_simulations"], [])

    def test_failed_api_pending_host_fallback_preserves_attempt_history(self):
        request = request_document(runs_per_provider=1)
        fake_collector = mock.Mock(
            side_effect=collect_queries.ProviderFailure(
                "RETRY_EXHAUSTED", retryable=True, attempts=3
            )
        )
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                payload, code = collect_queries.collect_document(request, True)
        self.assertEqual(code, 1)
        pending = payload["pending_host_simulations"][0]
        self.assertTrue(pending["api_attempted"])
        self.assertEqual(pending["prior_api_attempts"], 3)
        self.assertEqual(pending["fallback_reason"], "RETRY_EXHAUSTED")

    def test_observed_only_never_recommends_host_simulation(self):
        cases = (
            ("openai", "CREDENTIAL_MISSING"),
            ("google_ai_mode", "OBSERVED_MODE_UNSUPPORTED"),
        )
        for provider, expected_code in cases:
            with self.subTest(provider=provider):
                request = request_document(
                    providers=[provider], mode="observed_only", live_research=True
                )
                with mock.patch.dict(os.environ, {}, clear=True):
                    payload, code = collect_queries.collect_document(request, True)
                self.assertEqual(code, 2)
                self.assertEqual(payload["status"], "error")
                self.assertEqual(payload["pending_host_simulations"], [])
                self.assertEqual(payload["failures"][0]["code"], expected_code)

    def test_observed_only_empty_trace_does_not_call_synthetic_fallback(self):
        request = request_document(
            providers=["openai"],
            runs_per_provider=1,
            mode="observed_only",
            live_research=True,
        )
        observed = collect_queries.base_run("openai", "chat-latest", 1, "observed_api")
        observed.update(
            {
                "status": "degraded",
                "observability_status": "search_not_used",
                "http_attempts": 1,
                "warnings": ["SEARCH_NOT_USED"],
            }
        )
        fake_collector = mock.Mock(return_value=observed)
        with mock.patch.dict(
            os.environ, {"OPENAI_API_KEY": FAKE_OPENAI_KEY}, clear=True
        ):
            with mock.patch.dict(collect_queries.COLLECTORS, {"openai": fake_collector}):
                payload, code = collect_queries.collect_document(request, True)
        self.assertEqual(code, 2)
        self.assertEqual(fake_collector.call_count, 1)
        self.assertEqual(payload["pending_host_simulations"], [])

    def test_fixed_endpoint_rejects_override(self):
        with mock.patch.object(collect_queries.urllib.request, "urlopen") as urlopen:
            with self.assertRaises(collect_queries.ProviderFailure) as context:
                collect_queries.http_post_json(
                    "https://attacker.invalid/collect", {}, {"seed": "test"}
                )
        self.assertEqual(context.exception.code, "ENDPOINT_NOT_ALLOWED")
        urlopen.assert_not_called()

    def test_retryable_http_errors_retry_twice(self):
        class FakeResponse:
            headers = {"x-request-id": "req-ok"}

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, traceback):
                return False

            def read(self, _limit):
                return b'{"ok":true}'

        failures = [
            urllib.error.HTTPError(
                collect_queries.ENDPOINTS["openai"],
                429,
                "rate limited",
                {},
                io.BytesIO(b"ignored"),
            ),
            urllib.error.HTTPError(
                collect_queries.ENDPOINTS["openai"],
                500,
                "server error",
                {},
                io.BytesIO(b"ignored"),
            ),
            FakeResponse(),
        ]
        with mock.patch.object(
            collect_queries.urllib.request, "urlopen", side_effect=failures
        ) as urlopen:
            with mock.patch.object(collect_queries.time, "sleep") as sleep:
                document, attempts, request_id = collect_queries.http_post_json(
                    collect_queries.ENDPOINTS["openai"], {}, {"seed": "test"}
                )
        self.assertEqual(document, {"ok": True})
        self.assertEqual(attempts, 3)
        self.assertEqual(request_id, "req-ok")
        self.assertEqual(urlopen.call_count, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_non_retryable_failure_records_one_http_attempt(self):
        failure = urllib.error.HTTPError(
            collect_queries.ENDPOINTS["openai"],
            401,
            "unauthorized",
            {},
            io.BytesIO(b"ignored"),
        )
        with mock.patch.object(
            collect_queries.urllib.request, "urlopen", side_effect=failure
        ):
            with self.assertRaises(collect_queries.ProviderFailure) as context:
                collect_queries.http_post_json(
                    collect_queries.ENDPOINTS["openai"], {}, {"seed": "test"}
                )
        self.assertEqual(context.exception.attempts, 1)
        run = collect_queries.provider_failure_run(
            "openai", "chat-latest", 1, "observed_api", context.exception
        )
        self.assertEqual(run["http_attempts"], 1)

    def test_retry_exhaustion_records_three_http_attempts(self):
        failures = [
            urllib.error.HTTPError(
                collect_queries.ENDPOINTS["openai"],
                500,
                "server error",
                {},
                io.BytesIO(b"ignored"),
            )
            for _ in range(3)
        ]
        with mock.patch.object(
            collect_queries.urllib.request, "urlopen", side_effect=failures
        ):
            with mock.patch.object(collect_queries.time, "sleep"):
                with self.assertRaises(collect_queries.ProviderFailure) as context:
                    collect_queries.http_post_json(
                        collect_queries.ENDPOINTS["openai"], {}, {"seed": "test"}
                    )
        self.assertEqual(context.exception.code, "RETRY_EXHAUSTED")
        self.assertEqual(context.exception.attempts, 3)

    def test_claude_failure_accumulates_previous_continuation_attempts(self):
        paused = {
            "model": "claude-sonnet-4-6",
            "stop_reason": "pause_turn",
            "content": [],
        }
        final_failure = collect_queries.ProviderFailure(
            "RETRY_EXHAUSTED", attempts=3
        )
        request = request_document(providers=["claude"])
        with mock.patch.object(
            collect_queries,
            "http_post_json",
            side_effect=[(paused, 2, "req-1"), final_failure],
        ):
            with self.assertRaises(collect_queries.ProviderFailure) as context:
                collect_queries.collect_claude(
                    request,
                    1,
                    "claude-sonnet-4-6",
                    FAKE_ANTHROPIC_KEY,
                    [],
                )
        self.assertEqual(context.exception.attempts, 5)


class CsvExportTests(unittest.TestCase):
    def test_formula_prefix_is_escaped(self):
        for value in ("=SUM(A1:A2)", "+cmd", "-1+2", "@mention", "  =hidden"):
            self.assertTrue(export_report_csv.safe_cell(value).startswith("'"))
        self.assertEqual(export_report_csv.safe_cell("normal query"), "normal query")

    def test_valid_report_exports_query_rows(self):
        output = io.StringIO()
        count = export_report_csv.write_csv(valid_report_document(), output)
        self.assertEqual(count, 3)
        self.assertIn("observed_tool_query", output.getvalue())
        self.assertIn("api_execution_policy", output.getvalue().splitlines()[0])
        self.assertIn("api_first", output.getvalue())

    def test_empty_failed_run_keeps_api_and_failure_provenance(self):
        document = {
            "platforms": [
                {
                    "platform_id": "openai",
                    "provider": "OpenAI",
                    "product_surface": "Responses API",
                    "execution_mode": "failed",
                    "observability_status": "failed",
                    "model": {"requested": "chat-latest", "actual": None},
                    "clusters": [],
                    "runs": [
                        {
                            "run_index": 1,
                            "status": "failed",
                            "attempts": 3,
                            "api_attempted": True,
                            "fallback_reason": "RETRY_EXHAUSTED",
                            "failure": {
                                "code": "RETRY_EXHAUSTED",
                                "message": "Provider call failed.",
                            },
                            "queries": [],
                        }
                    ],
                }
            ],
            "cross_platform_clusters": [],
        }
        rows = list(export_report_csv.report_rows(document))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["record_type"], "run_without_query")
        self.assertTrue(rows[0]["api_attempted"])
        self.assertEqual(rows[0]["failure_code"], "RETRY_EXHAUSTED")


class ReportValidatorTests(unittest.TestCase):
    def test_valid_report_passes(self):
        result = validate_report.validate_report(valid_report_document())
        self.assertEqual(result["status"], "pass", result["issues"])

    def test_expanded_report_scope_requires_authorization_flag(self):
        document = valid_report_document()
        document["configuration"]["queries_per_synthetic_run"] = 20
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_SCOPE_AUTHORIZATION", {item["code"] for item in result["issues"]}
        )
        document["configuration"]["expanded_scope_authorized"] = True
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "pass", result["issues"])

    def test_recommended_topic_requires_valid_cross_cluster_reference(self):
        document = valid_report_document()
        document["recommended_page_topics"]["items"][0][
            "supporting_cross_cluster_ids"
        ] = ["cross-missing"]
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_CLUSTER_REFERENCE",
            {item["code"] for item in result["issues"]},
        )

    def test_recommended_topic_requires_valid_signal_reference(self):
        document = valid_report_document()
        document["recommended_page_topics"]["items"][0][
            "supporting_signal_ids"
        ] = ["signal-missing"]
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_SIGNAL_REFERENCE",
            {item["code"] for item in result["issues"]},
        )

    def test_recommended_topic_ranks_are_contiguous(self):
        document = valid_report_document()
        document["recommended_page_topics"]["items"][1]["rank"] = 3
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_RANK",
            {item["code"] for item in result["issues"]},
        )

    def test_unavailable_recommendations_require_reason_and_no_items(self):
        document = valid_report_document()
        recommendations = document["recommended_page_topics"]
        recommendations["status"] = "not_available"
        result = validate_report.validate_report(document)
        codes = {item["code"] for item in result["issues"]}
        self.assertIn("E_STRING", codes)
        self.assertIn("E_RECOMMENDED_TOPIC_AVAILABILITY", codes)

        recommendations["unavailable_reason"] = "No usable fan-out clusters were produced."
        recommendations["items"] = []
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_AVAILABILITY",
            {item["code"] for item in result["issues"]},
        )

        issues = []
        validate_report.validate_recommended_page_topics(
            recommendations,
            "/recommended_page_topics",
            set(),
            set(),
            None,
            issues,
        )
        self.assertEqual(issues, [])

    def test_p0_recommendation_requires_an_on_page_action(self):
        document = valid_report_document()
        document["recommended_page_topics"]["items"][0][
            "action"
        ] = "separate_page_candidate"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_PRIORITY_ACTION",
            {item["code"] for item in result["issues"]},
        )

    def test_recommended_topic_action_matches_page_coverage(self):
        document = valid_report_document()
        document["input"]["url"] = "https://example.com/project-management"
        document["page_coverage"] = {
            "url": "https://example.com/project-management",
            "items": [
                {
                    "cross_cluster_id": "cross-c01",
                    "status": "missing",
                    "page_evidence": None,
                    "missing_information": "The page lacks a small-team comparison.",
                    "recommendation": "update_existing_page",
                },
                {
                    "cross_cluster_id": "cross-c02",
                    "status": "partial",
                    "page_evidence": "The page names prices without plan limits.",
                    "missing_information": "Plan constraints are absent.",
                    "recommendation": "update_existing_page",
                },
            ],
            "coverage_score": 0.25,
        }
        recommendations = document["recommended_page_topics"]
        recommendations["basis"] = "fanout_and_page_evidence"
        recommendations["items"][0]["action"] = "add_to_page"
        recommendations["items"][1]["action"] = "expand_on_page"
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "pass", result["issues"])

        recommendations["items"][1]["action"] = "retain_on_page"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_RECOMMENDED_TOPIC_PAGE_STATUS",
            {item["code"] for item in result["issues"]},
        )

    def test_malformed_recommended_topic_values_do_not_crash(self):
        document = valid_report_document()
        item = document["recommended_page_topics"]["items"][0]
        item["priority"] = []
        item["action"] = {}
        item["supporting_cross_cluster_ids"] = [{}]
        item["supporting_signal_ids"] = [[]]
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "error")

    def test_pasted_page_content_can_support_page_coverage(self):
        document = valid_report_document()
        document["input"]["page_content_provided"] = True
        document["page_coverage"] = {
            "url": None,
            "items": [
                {
                    "cross_cluster_id": "cross-c01",
                    "status": "missing",
                    "page_evidence": None,
                    "missing_information": "A comparison is missing.",
                    "recommendation": "update_existing_page",
                },
                {
                    "cross_cluster_id": "cross-c02",
                    "status": "partial",
                    "page_evidence": "Pricing is mentioned.",
                    "missing_information": "Plan limits are missing.",
                    "recommendation": "update_existing_page",
                },
            ],
            "coverage_score": 0.25,
        }
        recommendations = document["recommended_page_topics"]
        recommendations["basis"] = "fanout_and_page_evidence"
        recommendations["items"][0]["action"] = "add_to_page"
        recommendations["items"][1]["action"] = "expand_on_page"
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "pass", result["issues"])

    def test_page_coverage_requires_a_supplied_source(self):
        document = valid_report_document()
        document["page_coverage"] = {
            "url": None,
            "items": [],
            "coverage_score": None,
        }
        document["recommended_page_topics"]["basis"] = "fanout_and_page_evidence"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_PAGE_EVIDENCE_SOURCE",
            {item["code"] for item in result["issues"]},
        )

    def test_observed_query_over_two_thousand_characters_fails(self):
        document = valid_report_document()
        query = document["platforms"][0]["runs"][0]["queries"][0]
        query["text"] = "a" * 2001
        query["normalized_text"] = collect_queries.normalize_exact(query["text"])
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_OBSERVED_QUERY_INVALID",
            {item["code"] for item in result["issues"]},
        )

    def test_unhashable_collection_values_do_not_crash(self):
        cases = []

        document = valid_report_document()
        document["configuration"]["requested_providers"] = [{}]
        cases.append(document)

        document = valid_report_document()
        document["platforms"][0]["clusters"][0]["query_ids"] = [{}]
        cases.append(document)

        document = valid_report_document()
        document["cross_platform_clusters"][0]["platform_ids"] = [{}]
        cases.append(document)

        document = valid_report_document()
        document["input"]["page_content_provided"] = True
        document["page_coverage"] = {
            "url": None,
            "items": [
                {
                    "cross_cluster_id": [],
                    "status": [],
                    "page_evidence": None,
                    "missing_information": None,
                    "recommendation": {},
                }
            ],
            "coverage_score": None,
        }
        document["recommended_page_topics"]["basis"] = "fanout_and_page_evidence"
        cases.append(document)

        for malformed in cases:
            with self.subTest(case=len(cases)):
                result = validate_report.validate_report(malformed)
                self.assertEqual(result["status"], "error")

    def test_observed_query_requires_trace(self):
        document = valid_report_document()
        document["platforms"][0]["runs"][0]["queries"][0]["trace_path"] = None
        result = validate_report.validate_report(document)
        self.assertIn("E_OBSERVED_TRACE", {item["code"] for item in result["issues"]})

    def test_observed_query_requires_provider_specific_trace_path(self):
        document = valid_report_document()
        document["platforms"][0]["runs"][0]["queries"][0][
            "trace_path"
        ] = "$.answer.prose"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_OBSERVED_TRACE_PATH", {item["code"] for item in result["issues"]}
        )

    def test_perplexity_observed_trace_pattern_is_supported(self):
        path = "$.events[0].choices[0].delta.reasoning_steps[1].web_search.search_keywords[2]"
        self.assertIsNotNone(validate_report.TRACE_PATTERNS["perplexity"].fullmatch(path))

    def test_heuristic_run_requires_api_fallback_provenance(self):
        document = valid_report_document()
        document["platforms"][0]["runs"][2]["fallback_reason"] = None
        result = validate_report.validate_report(document)
        self.assertIn("E_FALLBACK_REASON", {item["code"] for item in result["issues"]})

    def test_heuristic_run_can_preserve_prior_api_attempt(self):
        document = valid_report_document()
        run = document["platforms"][0]["runs"][2]
        run["api_attempted"] = True
        run["attempts"] = 3
        run["fallback_reason"] = "RETRY_EXHAUSTED"
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "pass", result["issues"])

    def test_provider_synthetic_query_requires_api_attempt(self):
        document = valid_report_document()
        run = document["platforms"][0]["runs"][1]
        run["api_attempted"] = False
        run["attempts"] = 0
        result = validate_report.validate_report(document)
        self.assertIn("E_API_PROVENANCE", {item["code"] for item in result["issues"]})

    def test_synthetic_query_must_not_have_trace(self):
        document = valid_report_document()
        document["platforms"][0]["runs"][1]["queries"][0]["trace_path"] = "$.fake"
        result = validate_report.validate_report(document)
        self.assertIn("E_SYNTHETIC_TRACE", {item["code"] for item in result["issues"]})

    def test_wrong_stability_score_fails(self):
        document = valid_report_document()
        document["platforms"][0]["clusters"][0]["within_model_stability"]["score"] = 0.9
        result = validate_report.validate_report(document)
        self.assertIn("E_STABILITY_SCORE", {item["code"] for item in result["issues"]})

    def test_execution_mode_must_match_query_provenance(self):
        document = valid_report_document()
        document["platforms"][0]["execution_mode"] = "observed_api"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_EXECUTION_MODE_CONSISTENCY",
            {item["code"] for item in result["issues"]},
        )

    def test_unconfirmed_actual_model_must_be_null(self):
        for actual_status in ("not_exposed", "unavailable", "failed"):
            with self.subTest(actual_status=actual_status):
                document = valid_report_document()
                document["platforms"][0]["model"]["actual_status"] = actual_status
                document["platforms"][0]["model"]["actual"] = "chat-latest"
                result = validate_report.validate_report(document)
                self.assertIn(
                    "E_MODEL_EXPOSURE", {item["code"] for item in result["issues"]}
                )

    def test_observed_only_rejects_simulated_queries(self):
        document = valid_report_document()
        document["configuration"]["mode"] = "observed_only"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_MODE_PROVENANCE", {item["code"] for item in result["issues"]}
        )

    def test_simulated_only_rejects_observed_queries(self):
        document = valid_report_document()
        document["configuration"]["mode"] = "simulated_only"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_MODE_PROVENANCE", {item["code"] for item in result["issues"]}
        )

    def test_external_signal_flag_must_match_signal_records(self):
        document = valid_report_document()
        document["external_search_signals"] = [
            {
                "signal_id": "signal-1",
                "signal_type": "serp_result",
                "text": "A current result supports pricing intent.",
                "source_url": "https://example.com/crm",
                "source_title": "CRM comparison",
                "retrieved_at": "2026-07-14T00:00:00Z",
                "language": "en",
                "locale": "unspecified",
            }
        ]
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_EXTERNAL_SIGNAL_FLAG", {item["code"] for item in result["issues"]}
        )

    def test_nested_failure_cannot_be_hidden_from_top_level(self):
        document = valid_report_document()
        document["failures"] = []
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_MISSING_TOP_FAILURE", {item["code"] for item in result["issues"]}
        )

    def test_top_level_provider_failure_requires_matching_run(self):
        document = valid_report_document()
        document["failures"].append(
            {
                "code": "AUTH_FAILED",
                "provider": "openai",
                "run_index": 2,
                "message": "Orphan failure.",
                "degraded": False,
            }
        )
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_ORPHAN_TOP_FAILURE", {item["code"] for item in result["issues"]}
        )

    def test_any_failure_requires_partial_report_status(self):
        document = valid_report_document()
        document["status"] = "complete"
        result = validate_report.validate_report(document)
        self.assertIn(
            "E_STATUS_FAILURE_MISMATCH",
            {item["code"] for item in result["issues"]},
        )

    def test_exact_duplicate_in_one_run_fails(self):
        document = valid_report_document()
        duplicate = copy.deepcopy(document["platforms"][0]["runs"][0]["queries"][0])
        duplicate["query_id"] = "openai-r1-q02"
        document["platforms"][0]["runs"][0]["queries"].append(duplicate)
        document["platforms"][0]["runs"][0]["observed_query_count"] = 2
        document["platforms"][0]["clusters"][0]["query_ids"].append("openai-r1-q02")
        result = validate_report.validate_report(document)
        self.assertIn("E_EXACT_DUPLICATE_IN_RUN", {item["code"] for item in result["issues"]})

    def test_credential_shape_fails_without_echoing_secret(self):
        document = valid_report_document()
        secret = "-".join(("sk", "proj", "LEAKEDKEY000000000000000"))
        document["assumptions"].append(secret)
        result = validate_report.validate_report(document)
        self.assertIn("E_SECRET_PATTERN", {item["code"] for item in result["issues"]})
        self.assertNotIn(secret, json.dumps(result))

    def test_malformed_runs_do_not_crash_validator(self):
        document = valid_report_document()
        document["platforms"][0]["runs"] = None
        result = validate_report.validate_report(document)
        self.assertEqual(result["status"], "error")


if __name__ == "__main__":
    unittest.main()
