"""Synthetic-only negative tests for the actual published JSON Schemas."""
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
CASE = json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))
SFT = json.loads((ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8"))


class RuntimeJsonSchemaTests(unittest.TestCase):
    def test_published_illustrative_fixtures_pass(self):
        validate_diagnostic_case(copy.deepcopy(CASE))
        validate_sft_example(copy.deepcopy(SFT))

    def test_unknown_nested_machine_key_is_rejected(self):
        case = copy.deepcopy(CASE)
        case["input"]["machine_diagnosis"]["findings"][0]["source_truth"] = "SYNTHETIC"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ADDITIONALPROPERTIES"):
            validate_diagnostic_case(case)

    def test_unknown_nested_target_key_is_rejected(self):
        case = copy.deepcopy(CASE)
        case["expected_output"]["cause_localization"]["candidates"][0]["expert_secret"] = "SYNTHETIC"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ADDITIONALPROPERTIES"):
            validate_diagnostic_case(case)

    def test_unknown_log_type_is_rejected(self):
        case = copy.deepcopy(CASE)
        case["input"]["diagnostic_logs"][0]["log_type"] = "NOT_A_LOG_TYPE"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ENUM"):
            validate_diagnostic_case(case)

    def test_invalid_historical_outcome_is_rejected(self):
        case = copy.deepcopy(CASE)
        case["input"]["historical_cases"][0]["outcome_status"] = "UNVERIFIED_AS_CONFIRMED"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ENUM"):
            validate_diagnostic_case(case)

    def test_invalid_next_step_priority_is_rejected(self):
        case = copy.deepcopy(CASE)
        case["expected_output"]["follow_up_actions"][0]["priority"] = "IMMEDIATE"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ENUM"):
            validate_diagnostic_case(case)

    def test_missing_required_review_field_is_rejected(self):
        case = copy.deepcopy(CASE)
        del case["expected_output"]["cause_localization"]["candidates"][0]["fault_mode"]
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_REQUIRED"):
            validate_diagnostic_case(case)

    def test_unmodeled_system_message_property_is_rejected(self):
        sft = copy.deepcopy(SFT)
        sft["messages"][0]["hidden_answer"] = "SYNTHETIC"
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ADDITIONALPROPERTIES"):
            validate_sft_example(sft)

    def test_unmodeled_sft_review_property_is_rejected(self):
        sft = copy.deepcopy(SFT)
        sft["review"]["is_gold"] = True
        with self.assertRaisesRegex(DiagnosticContextValidationError, "JSON_SCHEMA_ADDITIONALPROPERTIES"):
            validate_sft_example(sft)

    def test_schema_error_does_not_echo_sensitive_value(self):
        case = copy.deepcopy(CASE)
        case["input"]["diagnostic_logs"][0]["log_type"] = "SYNTHETIC_PRIVATE_SENTINEL"
        with self.assertRaises(DiagnosticContextValidationError) as exc:
            validate_diagnostic_case(case)
        self.assertNotIn("SYNTHETIC_PRIVATE_SENTINEL", str(exc.exception))


if __name__ == "__main__":
    unittest.main()
