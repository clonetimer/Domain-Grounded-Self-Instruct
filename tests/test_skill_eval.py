"""Offline tests for the opt-in, stateless blind-evaluation runner."""
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile

from dgsi.skill_eval import (
    CANDIDATE_SCHEMA,
    build_response_request,
    blind_pair,
    extract_output_text,
    map_blind_scores,
    validate_live_config,
    validate_output_path,
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
            validate_live_config("gpt-6-astra", "gpt-6-astra", "family-a", "family-a", "key", "independent setup")

    def test_live_config_requires_api_key(self):
        with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
            validate_live_config("gpt-6-astra", "gpt-6.1-sol", "family-a", "family-b", "", "independent setup")

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


    def test_live_config_requires_explicit_independence_note(self):
        with self.assertRaisesRegex(ValueError, "INDEPENDENCE_NOTE"):
            validate_live_config("gpt-6-astra", "gpt-6.1-sol", "family-a", "family-b", "key", "")

    def test_cli_defaults_to_no_network_dry_run(self):
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        env.pop("DGSI_GENERATOR_MODEL", None)
        env.pop("DGSI_JUDGE_MODEL", None)
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "run_skill_blind_eval.py")],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "DRY_RUN")
        self.assertEqual(payload["network_calls"], 0)



    def test_live_output_cannot_be_written_into_public_source_tree(self):
        root = Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError, "outside the repository or under reports/skill_blind_eval"):
            validate_output_path(root, root / "resources" / "leaked-candidate.jsonl")

    def test_live_output_is_allowed_in_git_ignored_eval_directory(self):
        root = Path(__file__).resolve().parents[1]
        output = validate_output_path(root, root / "reports" / "skill_blind_eval" / "pilot.jsonl")
        self.assertEqual(output, root / "reports" / "skill_blind_eval" / "pilot.jsonl")



    def test_live_config_rejects_same_model_family_even_when_model_ids_differ(self):
        with self.assertRaisesRegex(ValueError, "model families must be different"):
            validate_live_config(
                "gpt-6-astra",
                "gpt-6.1-sol",
                "gpt-6",
                "gpt-6",
                "key",
                "separate judge family",
            )

    def test_candidate_schema_allows_no_fault_source_when_abstaining(self):
        self.assertEqual(
            CANDIDATE_SCHEMA["properties"]["fault_source_component"]["type"],
            ["string", "null"],
        )

    def test_live_runner_uses_neutral_baseline_and_writes_completion_record(self):
        from unittest.mock import patch
        from dgsi.skill_eval import BASELINE_SYSTEM, run_live_evaluation

        root = Path(__file__).resolve().parents[1]
        candidate = {
            "instruction": "诊断任务",
            "input": "假设观测",
            "answer": "证据不足",
            "diagnostic_status": "INSUFFICIENT_EVIDENCE",
            "fault_source_component": None,
            "claims": [],
            "term_mentions": [],
            "uncertainty": "缺少独立证据",
        }
        score = {
            "terminology": 2,
            "evidence_traceability": 2,
            "causal_calibration": 2,
            "self_attestation_control": 2,
            "truth_leakage_control": 2,
            "abstention": 2,
            "critical_failures": [],
        }
        judge = {
            "candidate_a": score,
            "candidate_b": score,
            "preferred_candidate": "TIE",
            "rationale": "两者表现相同",
        }
        calls = []

        def fake_api_call(**kwargs):
            calls.append(kwargs)
            return judge if kwargs["schema_name"] == "blind_candidate_scores" else candidate

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "blind.jsonl"
            with patch("dgsi.skill_eval._api_call_for_json", side_effect=fake_api_call):
                result = run_live_evaluation(
                    root=root,
                    output_path=output,
                    generator_model="gpt-6-astra",
                    judge_model="gpt-6.1-sol",
                    generator_family="gpt-6-astra-family",
                    judge_family="gpt-6.1-sol-family",
                    api_key="test-key",
                    independence_note="A separate model family is used as judge.",
                    limit=1,
                )
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(calls), 3)
            self.assertEqual(calls[0]["system_prompt"], BASELINE_SYSTEM)
            self.assertNotIn("Do not invent citations", calls[0]["system_prompt"])
            self.assertIn("Apply this additional domain-grounding Skill", calls[1]["system_prompt"])
            self.assertEqual(records[-1]["record_type"], "run_summary")
            self.assertEqual(records[-1]["run_status"], "COMPLETED")
            self.assertEqual(result["metadata"]["generator_family"], "gpt-6-astra-family")
            self.assertEqual(result["metadata"]["judge_family"], "gpt-6.1-sol-family")
            self.assertEqual(result["summary"]["paired_mean_delta"]["terminology"], 0.0)


    def test_eps_pressure_case_loads_eps_glossary_and_evidence_context(self):
        from dgsi.skill_eval import _case_context

        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(item for item in cases if item["case_id"] == "E01_IMAGE_SSPC_INSTANT_TRIP")
        context = _case_context(root, case)
        self.assertEqual(context["domain"], "eps")
        self.assertIn("solid_state_power_controller", {term["term_id"] for term in context["terms"]})
        self.assertIn("IMAGE_SSPC_STATUS_TELEMETRY_MISMATCH", {p["passage_id"] for p in context["source_passages"]})
        self.assertTrue(all(p["claim_boundary"] for p in context["source_passages"]))

    def test_epc_domain_is_not_admitted_by_blind_runner(self):
        from dgsi.skill_eval import _case_context

        root = Path(__file__).resolve().parents[1]
        with self.assertRaisesRegex(ValueError, "unsupported domain"):
            _case_context(root, {"case_id": "LEGACY_EPC", "domain": "epc", "source_passage_ids": [], "term_ids": []})




if __name__ == "__main__":
    unittest.main()
