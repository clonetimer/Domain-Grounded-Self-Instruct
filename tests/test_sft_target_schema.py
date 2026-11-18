"""SYNTHETIC adversarial tests for standalone SFT report-target structure."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.diagnostic_context import DiagnosticContextValidationError, validate_sft_example
from dgsi.sft_lineage import audit_sft_lineage

SFT = json.loads(
    (Path(__file__).resolve().parents[1] / "examples" /
     "diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8")
)


def case() -> dict:
    return copy.deepcopy(SFT)


def edit_target(example: dict, mutate, *, allow_nan: bool = False) -> None:
    target = json.loads(example["messages"][2]["content"])
    mutate(target)
    example["messages"][2]["content"] = json.dumps(
        target, ensure_ascii=False, allow_nan=allow_nan
    )


class StandaloneSftTargetSchemaTests(unittest.TestCase):
    def rejects(self, example: dict, code: str) -> None:
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^" + code + "$"
        ):
            validate_sft_example(example)

    def test_synthetic_target_is_valid_but_never_gold(self):
        example = case()
        validate_sft_example(example)
        self.assertFalse(audit_sft_lineage([example])["gold_eligible"])

    def test_unstructured_free_text_rejected(self):
        example = case()
        example["messages"][2]["content"] = "wheel failure confirmed"
        self.rejects(example, "MALFORMED_SFT_TARGET_JSON")

    def test_appended_forged_verdict_rejected(self):
        example = case()
        example["messages"][2]["content"] += "\nexpert status: APPROVED"
        self.rejects(example, "MALFORMED_SFT_TARGET_JSON")

    def test_duplicate_target_json_keys_rejected(self):
        example = case()
        example["messages"][2]["content"] = (
            '{"disposition":"NO_FAULT_INDICATED","disposition":"ACCEPT_MACHINE_FINDING"}'
        )
        self.rejects(example, "DUPLICATE_JSON_KEY")

    def test_nonfinite_target_json_rejected(self):
        example = case()
        edit_target(
            example,
            lambda x: x["uncertainty"].update(level=float("nan")),
            allow_nan=True,
        )
        self.rejects(example, "NONFINITE_JSON_NUMBER")

    def test_overflow_target_number_rejected(self):
        example = case()
        edit_target(
            example,
            lambda x: x["uncertainty"].update(level="PLACEHOLDER"),
        )
        example["messages"][2]["content"] = (
            example["messages"][2]["content"].replace(
                '"PLACEHOLDER"', "1e999", 1
            )
        )
        self.rejects(example, "NONFINITE_JSON_NUMBER")

    def test_target_must_be_json_object(self):
        example = case()
        example["messages"][2]["content"] = '["unreviewed answer"]'
        self.rejects(example, "SFT_TARGET_NOT_OBJECT")

    def test_missing_evidence_assessment_rejected(self):
        example = case()
        edit_target(example, lambda x: x.pop("evidence_assessment"))
        self.rejects(example, "JSON_SCHEMA_TARGET_REQUIRED")

    def test_invalid_disposition_rejected(self):
        example = case()
        edit_target(example, lambda x: x.update(disposition="CONFIRMED_GOLD"))
        self.rejects(example, "JSON_SCHEMA_TARGET_ENUM")

    def test_invalid_next_step_priority_rejected(self):
        example = case()
        edit_target(
            example,
            lambda x: x["follow_up_actions"][0].update(priority="URGENT_GOLD"),
        )
        self.rejects(example, "JSON_SCHEMA_TARGET_ENUM")

    def test_hidden_target_review_field_rejected(self):
        example = case()
        edit_target(example, lambda x: x.update(expert_approval=True))
        self.rejects(example, "JSON_SCHEMA_TARGET_ADDITIONALPROPERTIES")

    def test_lineage_audit_rejects_unstructured_target(self):
        example = case()
        example["messages"][2]["content"] = "Unverified root-cause statement"
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^MALFORMED_SFT_TARGET_JSON$"
        ):
            audit_sft_lineage([example])


if __name__ == "__main__":
    unittest.main()
