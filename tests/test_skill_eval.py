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
    extract_skill_treatment,
    generation_order,
    map_blind_scores,
    validate_candidate_against_case,
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
            "claims": [{
                "claim_type": "OBSERVATION",
                "text": "公开案例记录了磁强计失效。",
                "source_passage_ids": ["NEOSSAT_MAGNETOMETER_FAILURE"],
            }],
            "term_mentions": [{
                "surface": "磁强计",
                "term_id": "magnetometer",
                "relation": "PREFERRED",
            }],
            "uncertainty": "内部物理失效原因未由该段资料确定。",
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
            generator_calls = [call for call in calls if call["schema_name"] == "spacecraft_fault_seed_candidate"]
            baseline_call = next(call for call in generator_calls if call["system_prompt"] == BASELINE_SYSTEM)
            treatment_call = next(call for call in generator_calls if "Apply only these additional procedural treatment instructions" in call["system_prompt"])
            self.assertNotIn("Do not invent citations", baseline_call["system_prompt"])
            self.assertEqual(baseline_call["user_prompt"], treatment_call["user_prompt"])
            self.assertNotIn("expected_behaviors", baseline_call["user_prompt"])
            self.assertNotIn("Core public sources include", treatment_call["system_prompt"])
            self.assertEqual(result["metadata"]["api_calls_completed"], 3)
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



    def test_candidate_schema_requires_a_source_passage_for_each_claim(self):
        passage_schema = CANDIDATE_SCHEMA["properties"]["claims"]["items"]["properties"]["source_passage_ids"]
        self.assertEqual(passage_schema["minItems"], 1)



    def test_all_public_literature_cases_resolve_domain_terms_and_passages(self):
        from dgsi.skill_eval import _case_context

        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        self.assertEqual(len(cases), 13)
        self.assertEqual(sum(case["domain"] == "adcs" for case in cases), 6)
        self.assertEqual(sum(case["domain"] == "eps" for case in cases), 7)
        for case in cases:
            context = _case_context(root, case)
            self.assertEqual(context["domain"], case["domain"])
            self.assertTrue(context["terms"])
            self.assertTrue(context["source_passages"])
            self.assertTrue(all(passage["claim_boundary"] for passage in context["source_passages"]))



    def test_skill_treatment_extraction_excludes_domain_reference_sections(self):
        root = Path(__file__).resolve().parents[1]
        skill = (root / "skills" / "eps-gold-seed-curation" / "SKILL.md").read_text(encoding="utf-8")
        treatment = extract_skill_treatment(skill)
        self.assertIn("Preserve the source's certainty", treatment)
        self.assertNotIn("NASA IMAGE Failure Review Board", treatment)
        self.assertNotIn("Quick checks", treatment)

    def test_skill_treatment_extraction_rejects_missing_or_duplicate_section(self):
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_skill_treatment("# no treatment section")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            extract_skill_treatment("## Blind-evaluation treatment instructions\nA\n## Blind-evaluation treatment instructions\nB")

    def test_candidate_preflight_rejects_passage_outside_case_bundle(self):
        from dgsi.skill_eval import _case_context
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(item for item in cases if item["case_id"] == "E01_IMAGE_SSPC_INSTANT_TRIP")
        context = _case_context(root, case)
        candidate = {
            "claims": [{
                "claim_type": "OBSERVATION",
                "text": "unsupported passage",
                "source_passage_ids": ["WMAP_NIH2_CELL_VOLTAGE_COLLAPSE"],
            }],
            "term_mentions": [],
        }
        findings = validate_candidate_against_case(candidate, case, context)
        self.assertIn("PASSAGE_OUTSIDE_CASE_BUNDLE", {item["code"] for item in findings})

    def test_candidate_preflight_rejects_claim_scope_mismatch(self):
        from dgsi.skill_eval import _case_context
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(item for item in cases if item["case_id"] == "E06_WMAP_CELL_COLLAPSE")
        context = _case_context(root, case)
        candidate = {
            "claims": [{
                "claim_type": "CAUSAL",
                "text": "the report proves a cause",
                "source_passage_ids": ["WMAP_NIH2_CELL_VOLTAGE_COLLAPSE"],
            }],
            "term_mentions": [],
        }
        findings = validate_candidate_against_case(candidate, case, context)
        self.assertIn("CLAIM_SCOPE_MISMATCH", {item["code"] for item in findings})

    def test_candidate_preflight_checks_term_alias_class(self):
        from dgsi.skill_eval import _case_context
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(item for item in cases if item["case_id"] == "A02_NEOSSAT_TORQUER_MCU")
        context = _case_context(root, case)
        candidate = {
            "claims": [],
            "term_mentions": [{
                "surface": "磁力矩杆",
                "term_id": "magnetorquer",
                "relation": "EXACT_ALIAS",
            }],
        }
        findings = validate_candidate_against_case(candidate, case, context)
        self.assertIn("TERM_RELATION_MISMATCH", {item["code"] for item in findings})
        self.assertIn("MISSING_CLAIMS", {item["code"] for item in findings})

    def test_candidate_preflight_accepts_case_passage_and_preferred_term(self):
        from dgsi.skill_eval import _case_context
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        case = next(item for item in cases if item["case_id"] == "E01_IMAGE_SSPC_INSTANT_TRIP")
        context = _case_context(root, case)
        candidate = {
            "claims": [{
                "claim_type": "OBSERVATION",
                "text": "The report describes an SSPC instant trip.",
                "source_passage_ids": ["IMAGE_SSPC_SEU_INSTANT_TRIP"],
            }],
            "term_mentions": [{
                "surface": "固态功率控制器",
                "term_id": "solid_state_power_controller",
                "relation": "PREFERRED",
            }],
        }
        self.assertEqual(validate_candidate_against_case(candidate, case, context), [])

    def test_candidate_schema_requires_at_least_one_claim(self):
        self.assertEqual(CANDIDATE_SCHEMA["properties"]["claims"]["minItems"], 1)



    def test_live_runner_records_partial_failure_without_marking_run_complete(self):
        from unittest.mock import patch
        from dgsi.skill_eval import run_live_evaluation

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "failed.jsonl"
            with patch("dgsi.skill_eval._api_call_for_json", side_effect=RuntimeError("synthetic API failure")):
                result = run_live_evaluation(
                    root=root,
                    output_path=output,
                    generator_model="gpt-6-astra",
                    judge_model="gpt-6.1-sol",
                    generator_family="gpt-6-astra-family",
                    judge_family="gpt-6.1-sol-family",
                    api_key="test-key",
                    independence_note="Separate declared model family.",
                    limit=1,
                )
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(result["metadata"]["run_status"], "FAILED")
            self.assertIsNone(result["summary"])
            self.assertEqual(records[-1]["record_type"], "run_failure")
            self.assertEqual(records[-1]["completed_case_count"], 0)
            self.assertEqual(records[-1]["error_type"], "RuntimeError")



    def test_generation_order_is_counterbalanced_across_case_suite(self):
        root = Path(__file__).resolve().parents[1]
        cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
        orders = [tuple(generation_order(20261114, case["case_id"], index)) for index, case in enumerate(cases)]
        self.assertEqual(set(orders), {("baseline", "treatment"), ("treatment", "baseline")})
        self.assertGreaterEqual(orders.count(("baseline", "treatment")), 4)
        self.assertGreaterEqual(orders.count(("treatment", "baseline")), 4)



    def test_holdout_suite_resolves_all_unseen_domain_contexts(self):
        from dgsi.skill_eval import _case_context

        root = Path(__file__).resolve().parents[1]
        suite = json.loads((root / "resources" / "skill_holdout_cases.json").read_text(encoding="utf-8"))
        self.assertEqual(suite["split"], "HOLDOUT_UNSEEN_PUBLIC_CASES")
        self.assertEqual(len(suite["cases"]), 8)
        self.assertEqual(sum(case["domain"] == "adcs" for case in suite["cases"]), 4)
        self.assertEqual(sum(case["domain"] == "eps" for case in suite["cases"]), 4)
        for case in suite["cases"]:
            context = _case_context(root, case)
            self.assertEqual(context["domain"], case["domain"])
            self.assertTrue(context["source_passages"])
            self.assertTrue(context["terms"])
            self.assertTrue(all(p["claim_boundary"] and p["evidence_summary"] for p in context["source_passages"]))

    def test_cli_holdout_dry_run_makes_no_network_calls(self):
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env.pop("OPENAI_API_KEY", None)
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "run_skill_blind_eval.py"), "--suite", "skill_holdout_cases.json"],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["mode"], "DRY_RUN")
        self.assertEqual(payload["suite"], "skill_holdout_cases.json")
        self.assertEqual(payload["cases_available"], 8)
        self.assertEqual(payload["network_calls"], 0)

    def test_live_runner_freezes_holdout_suite_and_hides_judge_only_behaviors(self):
        from unittest.mock import patch
        from dgsi.skill_eval import run_live_evaluation

        root = Path(__file__).resolve().parents[1]
        suite = json.loads((root / "resources" / "skill_holdout_cases.json").read_text(encoding="utf-8"))
        case = suite["cases"][0]
        candidate = {
            "instruction": "SOHO姿态控制异常诊断",
            "input": "公开调查报告描述陀螺配置和地面操作异常。",
            "answer": "不能据此判定陀螺硬件故障，应检查陀螺旋转状态、命令序列和故障检测配置。",
            "diagnostic_status": "DIAGNOSED",
            "fault_source_component": "地面操作命令序列与陀螺配置",
            "claims": [{
                "claim_type": "OBSERVATION",
                "text": "SOHO调查委员会将事故直接原因归于地面操作错误和自主故障检测被禁用。",
                "source_passage_ids": ["SOHO_GYRO_B_FALSE_DIAGNOSIS"],
            }],
            "term_mentions": [{
                "surface": "陀螺仪",
                "term_id": "gyro",
                "relation": "PREFERRED",
            }],
            "uncertainty": "报告没有确认陀螺硬件本体发生故障。",
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
            "rationale": "仅用于验证holdout执行契约。",
        }
        calls = []

        def fake_api_call(**kwargs):
            calls.append(kwargs)
            return judge if kwargs["schema_name"] == "blind_candidate_scores" else candidate

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "holdout.jsonl"
            with patch("dgsi.skill_eval._api_call_for_json", side_effect=fake_api_call):
                result = run_live_evaluation(
                    root=root,
                    output_path=output,
                    generator_model="generator-model",
                    judge_model="judge-model",
                    generator_family="generator-family",
                    judge_family="independent-judge-family",
                    api_key="test-key",
                    independence_note="Mocked API contract test only; not a live evaluation.",
                    limit=1,
                    suite_file="skill_holdout_cases.json",
                )
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(result["metadata"]["suite_split"], "HOLDOUT_UNSEEN_PUBLIC_CASES")
            self.assertEqual(result["metadata"]["suite_file"], "skill_holdout_cases.json")
            self.assertEqual(result["metadata"]["case_ids"], [case["case_id"]])
            self.assertEqual(result["metadata"]["api_calls_completed"], 3)
            generator_calls = [call for call in calls if call["schema_name"] == "spacecraft_fault_seed_candidate"]
            self.assertEqual(len(generator_calls), 2)
            self.assertTrue(all("expected_behaviors" not in call["user_prompt"] for call in generator_calls))
            self.assertTrue(all(case["expected_behaviors"][0] not in call["user_prompt"] for call in generator_calls))
            self.assertEqual(records[-1]["record_type"], "run_summary")

    def test_live_runner_rejects_suite_path_traversal(self):
        from dgsi.skill_eval import run_live_evaluation

        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "JSON filename"):
                run_live_evaluation(
                    root=root,
                    output_path=Path(tmp) / "unsafe.jsonl",
                    generator_model="generator-model",
                    judge_model="judge-model",
                    generator_family="generator-family",
                    judge_family="independent-judge-family",
                    api_key="test-key",
                    independence_note="Path validation test only.",
                    limit=1,
                    suite_file="../skill_holdout_cases.json",
                )




if __name__ == "__main__":
    unittest.main()
