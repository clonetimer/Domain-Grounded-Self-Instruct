"""SYNTHETIC_TEST_ONLY: disposal provenance adversarial regression cases.

All tests mutate illustrative fixtures. Nothing here represents real flight
records, executed commands, expert adjudication, or Gold training samples.
"""
import copy
import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import (
    DiagnosticContextValidationError,
    validate_diagnostic_case,
    validate_sft_example,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_case():
    return json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))


def synthetic_sft():
    return json.loads((ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8"))


def change_disposal(report, status, measure_type, refs):
    report["disposal_status"] = status
    report["disposal_measures"] = [{
        "measure": "SYNTHETIC_ONLY source action, not a real action",
        "measure_type": measure_type,
        "evidence_refs": refs,
    }]


def change_sft_target(example, callback):
    target = json.loads(example["messages"][2]["content"])
    callback(target)
    example["messages"][2]["content"] = json.dumps(target, ensure_ascii=False)


class SyntheticDisposalAttributionTests(unittest.TestCase):
    def assert_case_rejects(self, case, code):
        with self.assertRaisesRegex(DiagnosticContextValidationError, code):
            validate_diagnostic_case(case)

    def assert_sft_rejects(self, example, code):
        with self.assertRaisesRegex(DiagnosticContextValidationError, code):
            validate_sft_example(example)

    def test_synthetic_fixture_remains_valid(self):
        validate_diagnostic_case(synthetic_case())
        validate_sft_example(synthetic_sft())

    def test_planned_action_requires_source_citation(self):
        case = synthetic_case()
        change_disposal(case["expected_output"], "RECOMMENDED_ONLY", "PLANNED", [])
        self.assert_case_rejects(case, "SOURCE_DISPOSAL_REQUIRES_EVIDENCE")

    def test_synthetic_machine_finding_cannot_document_disposal(self):
        case = synthetic_case()
        finding_id = case["input"]["machine_diagnosis"]["findings"][0]["finding_id"]
        change_disposal(case["expected_output"], "RECOMMENDED_ONLY", "RECOMMENDED", [finding_id])
        self.assert_case_rejects(case, "DISPOSAL_CITATION_NOT_SOURCE_RECORD")

    def test_executed_action_cannot_be_supported_only_by_literature(self):
        case = synthetic_case()
        passage_id = case["input"]["knowledge_evidence"][0]["evidence_id"]
        change_disposal(case["expected_output"], "RECORDED", "EXECUTED", [passage_id])
        self.assert_case_rejects(case, "EXECUTED_DISPOSAL_REQUIRES_LOG_REFERENCE")

    def test_synthetic_log_reference_is_structurally_allowed(self):
        case = synthetic_case()
        log_id = case["input"]["diagnostic_logs"][0]["log_id"]
        change_disposal(case["expected_output"], "RECORDED", "EXECUTED", [log_id])
        validate_diagnostic_case(case)  # Structural pass is not proof the action occurred.

    def test_source_passage_can_support_recorded_recommendation(self):
        case = synthetic_case()
        evidence_id = case["input"]["knowledge_evidence"][0]["evidence_id"]
        change_disposal(case["expected_output"], "RECOMMENDED_ONLY", "RECOMMENDED", [evidence_id])
        validate_diagnostic_case(case)  # Source wording still needs human verification.

    def test_not_applicable_cannot_have_action(self):
        case = synthetic_case()
        log_id = case["input"]["diagnostic_logs"][0]["log_id"]
        change_disposal(case["expected_output"], "NOT_APPLICABLE", "EXECUTED", [log_id])
        self.assert_case_rejects(case, "NOT_APPLICABLE disposal must have an empty")

    def test_direct_sft_not_recorded_cannot_claim_execution(self):
        example = synthetic_sft()
        def edit(target):
            log_id = synthetic_case()["input"]["diagnostic_logs"][0]["log_id"]
            change_disposal(target, "NOT_RECORDED", "EXECUTED", [log_id])
        change_sft_target(example, edit)
        self.assert_sft_rejects(example, "NOT_RECORDED disposal must have an empty")

    def test_direct_sft_recommended_only_needs_source(self):
        example = synthetic_sft()
        change_sft_target(
            example,
            lambda target: change_disposal(target, "RECOMMENDED_ONLY", "RECOMMENDED", []),
        )
        self.assert_sft_rejects(example, "SOURCE_DISPOSAL_REQUIRES_EVIDENCE")

    def test_direct_sft_executed_needs_log_not_knowledge_alone(self):
        example = synthetic_sft()
        passage_id = synthetic_case()["input"]["knowledge_evidence"][0]["evidence_id"]
        change_sft_target(
            example,
            lambda target: change_disposal(target, "RECORDED", "EXECUTED", [passage_id]),
        )
        self.assert_sft_rejects(example, "EXECUTED_DISPOSAL_REQUIRES_LOG_REFERENCE")

    def test_direct_sft_cannot_use_ml_evidence_for_planned_action(self):
        example = synthetic_sft()
        finding_id = synthetic_case()["input"]["machine_diagnosis"]["findings"][0]["finding_id"]
        change_sft_target(
            example,
            lambda target: change_disposal(target, "RECOMMENDED_ONLY", "PLANNED", [finding_id]),
        )
        self.assert_sft_rejects(example, "DISPOSAL_CITATION_NOT_SOURCE_RECORD")


if __name__ == "__main__":
    unittest.main()
