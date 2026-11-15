import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import (
    DiagnosticContextValidationError,
    audit_split_groups,
    evaluate_case_readiness,
    validate_diagnostic_case,
    validate_sft_example,
)


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class DiagnosticContextSftContractTests(unittest.TestCase):
    def test_case_schema_is_json_schema_2020_12(self):
        schema = load_json("resources/diagnostic_case.schema.json")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "dgsi-diagnostic-case.v1")
        self.assertIn("machine_diagnosis", schema["properties"]["input"]["required"])
        self.assertIn("diagnostic_logs", schema["properties"]["input"]["required"])
        self.assertIn("operational_context", schema["properties"]["input"]["required"])
        self.assertIn("analysis_cutoff", schema["properties"]["input"]["required"])

    def test_case_example_obeys_required_context_boundary(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        self.assertEqual(case["schema_version"], "dgsi-diagnostic-case.v1")
        self.assertFalse(case["input"]["raw_telemetry_included"])
        self.assertTrue(case["input"]["machine_diagnosis"]["findings"])
        self.assertTrue(case["input"]["diagnostic_logs"])
        self.assertTrue(case["input"]["historical_cases"])
        self.assertTrue(case["input"]["knowledge_evidence"])
        self.assertIn("fault_source_assessment", case["expected_output"])
        self.assertIn("affected_components", case["expected_output"]["fault_source_assessment"])
        self.assertIn("uncertainty", case["expected_output"])
        self.assertEqual(case["review"]["status"], "DRAFT")
        self.assertIn("hypothetical", case["provenance"]["generation_method"])
        self.assertIn("NOT_GOLD_REVIEWED", validate_diagnostic_case(case))

    def test_chat_sft_example_has_three_roles_and_review_gate(self):
        schema = load_json("resources/diagnostic_sft.schema.json")
        example = load_json("examples/diagnostic_context_sft_illustrative.json")
        self.assertEqual(schema["properties"]["schema_version"]["const"], "dgsi-diagnostic-sft.v1")
        self.assertEqual(example["schema_version"], "dgsi-diagnostic-sft.v1")
        self.assertEqual([m["role"] for m in example["messages"]], ["system", "user", "assistant"])
        self.assertEqual(example["review"]["status"], "REVIEW_REQUIRED")
        self.assertEqual(example["split"], "train")
        self.assertTrue(example["provenance"]["diagnosis_result_refs"])
        self.assertTrue(example["provenance"]["diagnostic_log_refs"])
        self.assertTrue(example["provenance"]["knowledge_passage_ids"])
        self.assertIn("原始遥测", example["messages"][1]["content"])
        self.assertIn("不提供原始遥测", example["messages"][1]["content"])
        validate_sft_example(example)

    def test_machine_scores_are_not_promoted_to_probabilities(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        finding = case["input"]["machine_diagnosis"]["findings"][0]
        self.assertEqual(finding["score_semantics"], "uncalibrated ranking score; not a probability")
        self.assertEqual(case["expected_output"]["cause_localization"]["status"], "CANDIDATE_ONLY")

    def test_historical_unresolved_case_remains_unresolved(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        history = case["input"]["historical_cases"][0]
        self.assertEqual(history["outcome_status"], "UNRESOLVED")
        self.assertTrue(history["applicability_limitations"])

    def test_case_validator_rejects_inline_raw_telemetry(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["input"]["raw_telemetry"] = [{"time_s": 0.0, "gyro": 0.01}]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "raw telemetry field"):
            validate_diagnostic_case(case)

    def test_case_validator_requires_score_semantics(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["input"]["machine_diagnosis"]["findings"][0]["score_semantics"] = None
        with self.assertRaisesRegex(DiagnosticContextValidationError, "score_semantics"):
            validate_diagnostic_case(case)

    def test_sft_validator_requires_explicit_roles_and_review_state(self):
        example = load_json("examples/diagnostic_context_sft_illustrative.json")
        example["messages"][1]["role"] = "assistant"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "roles must be"):
            validate_sft_example(example)

    def test_split_audit_rejects_same_incident_across_splits(self):
        examples = [
            {"source_group": "incident-01", "case_ref": "case-01", "split": "train"},
            {"source_group": "incident-01", "case_ref": "case-01-variant", "split": "test"},
        ]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "source_group leakage"):
            audit_split_groups(examples)

    def test_split_audit_accepts_disjoint_case_groups(self):
        examples = [
            {"source_group": "incident-01", "case_ref": "case-01", "split": "train"},
            {"source_group": "incident-02", "case_ref": "case-02", "split": "validation"},
            {"source_group": "incident-03", "case_ref": "case-03", "split": "test"},
        ]
        result = audit_split_groups(examples)
        self.assertEqual(result["example_count"], 3)
        self.assertEqual(result["source_group_count"], 3)

    def test_hypothetical_case_is_not_gold_eligible(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        result = evaluate_case_readiness(case)
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertFalse(result["gold_eligible"])
        self.assertIn("EXPERT_APPROVAL_REQUIRED", result["blockers"])
        self.assertIn("MISSING_SOURCE_ARTIFACT_HASH", result["blockers"])

    def test_approved_case_requires_reviewer_identity_and_timestamp(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["review"]["status"] = "APPROVED"
        result = evaluate_case_readiness(case)
        self.assertIn("APPROVED_WITHOUT_REVIEWER_ID", result["blockers"])
        self.assertIn("APPROVED_WITHOUT_REVIEW_TIMESTAMP", result["blockers"])

    def test_case_validator_rejects_hidden_truth_fields(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["input"]["machine_diagnosis"]["ground_truth"] = {"fault_id": "secret"}
        with self.assertRaisesRegex(DiagnosticContextValidationError, "raw telemetry field"):
            validate_diagnostic_case(case)

    def test_case_validator_rejects_post_cutoff_log_leakage(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["input"]["diagnostic_logs"].append({
            "log_id": "POST-DECISION",
            "timestamp": "2026-04-12T09:11:00Z",
            "log_type": "REVIEW",
            "content": "Post-decision expert confirmation.",
            "author_role": "reviewer",
            "source_ref": "synthetic://post-decision",
        })
        with self.assertRaisesRegex(DiagnosticContextValidationError, "post-decision information leakage"):
            validate_diagnostic_case(case)

    def test_case_validator_rejects_timezone_naive_cutoff(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["input"]["analysis_cutoff"] = "2026-04-12T09:10:00"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "must include a timezone"):
            validate_diagnostic_case(case)

    def test_internal_review_prompts_are_not_serialized_into_sft(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        example = load_json("examples/diagnostic_context_sft_illustrative.json")
        prompt = example["messages"][1]["content"]
        target = example["messages"][2]["content"]
        for note in case["internal_review"]["curator_prompts"] + case["internal_review"]["reviewer_questions"]:
            self.assertNotIn(note, prompt)
            self.assertNotIn(note, target)
        self.assertNotIn("internal_review", prompt)
        self.assertNotIn("internal_review", target)

    def test_report_contains_only_conclusion_fields_and_distinguishes_disposal(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        target = case["expected_output"]
        self.assertIn("phenomenon_analysis", target)
        self.assertIn("cause_localization", target)
        self.assertIn("disposal_status", target)
        self.assertIn("disposal_measures", target)
        self.assertNotIn("curator_prompts", target)
        self.assertNotIn("reviewer_questions", target)
        self.assertNotIn("alternative_hypotheses_to_check", target)

    def test_not_recorded_disposal_cannot_contain_invented_measures(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["expected_output"]["disposal_measures"] = [{
            "measure": "切换备份飞轮",
            "measure_type": "EXECUTED",
            "evidence_refs": ["LOG-01"],
        }]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "NOT_RECORDED disposal"):
            validate_diagnostic_case(case)

    def test_recommended_follow_up_is_not_historical_disposal(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["expected_output"]["disposal_status"] = "NOT_RECORDED"
        case["expected_output"]["disposal_measures"] = []
        case["expected_output"]["follow_up_actions"] = [{
            "action": "检查飞轮独立状态",
            "rationale": "补充执行机构证据",
            "priority": "HIGH",
        }]
        self.assertNotIn("NOT_GOLD_REVIEWED", [])
        validate_diagnostic_case(case)

    def test_executed_disposal_requires_a_source_reference(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["expected_output"]["disposal_status"] = "RECORDED"
        case["expected_output"]["disposal_measures"] = [{
            "measure": "已执行反作用轮构型切换",
            "measure_type": "EXECUTED",
            "evidence_refs": [],
        }]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "EXECUTED_DISPOSAL_REQUIRES_SOURCE_EVIDENCE"):
            validate_diagnostic_case(case)

    def test_disposal_measure_cannot_cite_unprovided_log(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        case["expected_output"]["disposal_status"] = "RECORDED"
        case["expected_output"]["disposal_measures"] = [{
            "measure": "已执行反作用轮构型切换",
            "measure_type": "EXECUTED",
            "evidence_refs": ["LOG-POST-EVENT-NOT-SUPPLIED"],
        }]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE"):
            validate_diagnostic_case(case)


if __name__ == "__main__":
    unittest.main()
