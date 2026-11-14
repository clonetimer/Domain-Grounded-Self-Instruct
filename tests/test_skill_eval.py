"""Offline tests for the opt-in, stateless blind-evaluation runner."""
import json
import unittest

from dgsi.skill_eval import (
    build_response_request,
    blind_pair,
    extract_output_text,
    map_blind_scores,
    validate_live_config,
)


SCHEMA = {
    "type": "object",
    "properties": {"candidate": {"type": "string"}},
    "required": ["candidate"],
    "additionalProperties": False,
}


class SkillEvalTest(unittest.TestCase):
    def test_live_config_requires_distinct_generator_and_judge(self):
        with self.assertRaisesRegex(ValueError, "must be different"):
            validate_live_config("gpt-6-astra", "gpt-6-astra", "key")

    def test_live_config_requires_api_key(self):
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            validate_live_config("gpt-6-astra", "gpt-6.1-sol", "")

    def test_responses_request_is_stateless_and_uses_strict_schema(self):
        request = build_response_request(
            model="gpt-6-astra",
            system_prompt="system",
            user_prompt="user",
            api_key="secret",
            schema_name="candidate",
            schema=SCHEMA,
        )
        payload = json.loads(request.data)
        self.assertEqual(request.full_url, "https://api.openai.com/v1/responses")
        self.assertEqual(request.get_header("Authorization"), "Bearer secret")
        self.assertFalse(payload["store"])
        self.assertEqual(payload["text"]["format"]["type"], "json_schema")
        self.assertTrue(payload["text"]["format"]["strict"])
        self.assertEqual(payload["text"]["format"]["schema"], SCHEMA)

    def test_blind_order_is_reproducible_and_does_not_include_condition_labels(self):
        first = blind_pair(20261114, "T01", "baseline output", "skill output")
        second = blind_pair(20261114, "T01", "baseline output", "skill output")
        self.assertEqual(first, second)
        self.assertEqual(set(first["order"]), {"baseline", "treatment"})
        self.assertEqual(set(first["candidates"]), {"A", "B"})

    def test_judge_scores_are_mapped_back_to_hidden_conditions(self):
        pair = {"order": ["treatment", "baseline"]}
        judged = {
            "candidate_a": {"score": 10, "critical_failures": []},
            "candidate_b": {"score": 4, "critical_failures": ["unsupported_cause"]},
        }
        mapped = map_blind_scores(judged, pair)
        self.assertEqual(mapped["treatment"]["score"], 10)
        self.assertEqual(mapped["baseline"]["score"], 4)
        self.assertEqual(mapped["baseline"]["critical_failures"], ["unsupported_cause"])

    def test_response_parser_extracts_only_output_text(self):
        response = {
            "status": "completed",
            "output": [
                {"type": "reasoning", "id": "rs_1"},
                {"type": "message", "content": [
                    {"type": "output_text", "text": "{\"candidate\":\"ok\"}"}
                ]},
            ],
        }
        self.assertEqual(extract_output_text(response), '{"candidate":"ok"}')

    def test_response_parser_rejects_incomplete_response(self):
        with self.assertRaisesRegex(ValueError, "incomplete"):
            extract_output_text({"status": "incomplete", "output": []})


if __name__ == "__main__":
    unittest.main()
