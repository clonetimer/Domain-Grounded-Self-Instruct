import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import (
    DiagnosticContextValidationError,
    audit_split_groups,
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
        self.assertIn("hypothetical", case["provenance"]["generation_method"])\n        self.assertIn("NOT_GOLD_REVIEWED", validate_diagnostic_case(case))

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
        self.assertIn("不提供原始遥测", example["messages"][1]["content"])\n        validate_sft_example(example)

    def test_machine_scores_are_not_promoted_to_probabilities(self):
        case = load_json("examples/diagnostic_context_case_illustrative.json")
        finding = case["input"]["machine_diagnosis"]["findings"][0]
        self.assertEqual(finding["score_semantics"], "uncalibrated ranking score; not a probability")
        self.assertEqual(case["expected_output"]["fault_source_assessment"]["status"], "CANDIDATE_ONLY")

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


if __name__ == "__main__":
    unittest.main()
