import json
import unittest
from pathlib import Path


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
        self.assertIn("hypothetical", case["provenance"]["generation_method"])

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


if __name__ == "__main__":
    unittest.main()
