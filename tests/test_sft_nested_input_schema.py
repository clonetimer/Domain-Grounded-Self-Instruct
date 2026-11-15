"""SYNTHETIC-only direct-SFT input-schema adversarial regression tests.

These tests do not contain real spacecraft telemetry or reviewed Gold cases.
"""
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


def fixture() -> dict:
    return copy.deepcopy(SFT)


def edit_input(example: dict, mutate) -> None:
    user = example["messages"][1]["content"]
    start = user.index("{")
    packet = json.loads(user[start:])
    mutate(packet["input"])
    example["messages"][1]["content"] = (
        user[:start] + json.dumps(packet, ensure_ascii=False)
    )


class StandaloneSftInputSchemaTests(unittest.TestCase):
    def assert_invalid(self, example: dict, code: str) -> None:
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^" + code + "$"
        ):
            validate_sft_example(example)

    def test_synthetic_baseline_is_structural_only(self):
        example = fixture()
        validate_sft_example(example)
        self.assertFalse(audit_sft_lineage([example])["gold_eligible"])

    def test_missing_machine_diagnosis_rejected(self):
        example = fixture()
        edit_input(example, lambda x: x.pop("machine_diagnosis"))
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_REQUIRED")

    def test_missing_upstream_method_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["machine_diagnosis"]["producer"].pop("method"),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_REQUIRED")

    def test_unsupported_upstream_status_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["machine_diagnosis"].update(status="EXPERT_CONFIRMED"),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_ENUM")

    def test_malformed_log_type_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["diagnostic_logs"][0].update(log_type="GOLD_VERDICT"),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_ENUM")

    def test_missing_spacecraft_configuration_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["spacecraft_context"].pop("configuration"),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_REQUIRED")

    def test_invalid_cutoff_timestamp_rejected(self):
        example = fixture()
        edit_input(example, lambda x: x.update(analysis_cutoff="not-a-date"))
        self.assert_invalid(example, "INVALID_SFT_ANALYSIS_CUTOFF")

    def test_invalid_log_timestamp_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["diagnostic_logs"][0].update(timestamp="not-a-date"),
        )
        self.assert_invalid(example, "INVALID_SFT_LOG_TIMESTAMP")

    def test_naive_analysis_cutoff_rejected(self):
        example = fixture()
        edit_input(
            example, lambda x: x.update(analysis_cutoff="2026-04-12T09:10:00")
        )
        self.assert_invalid(example, "INVALID_SFT_ANALYSIS_CUTOFF")

    def test_naive_log_timestamp_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["diagnostic_logs"][0].update(
                timestamp="2026-04-12T08:15:00"
            ),
        )
        self.assert_invalid(example, "INVALID_SFT_LOG_TIMESTAMP")

    def test_log_after_cutoff_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["diagnostic_logs"][0].update(
                timestamp="2026-04-12T09:11:00Z"
            ),
        )
        self.assert_invalid(example, "SFT_LOG_AFTER_ANALYSIS_CUTOFF")

    def test_unauthorized_nested_machine_field_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["machine_diagnosis"].update(
                expert_verdict="invented confirmation"
            ),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_ADDITIONALPROPERTIES")

    def test_extra_operational_context_field_rejected(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["operational_context"].update(
                synthesized_conclusion="confirmed"
            ),
        )
        self.assert_invalid(example, "JSON_SCHEMA_INPUT_ADDITIONALPROPERTIES")

    def test_explicit_raw_telemetry_flag_required_false(self):
        for value in (True, None):
            with self.subTest(value=value):
                example = fixture()
                edit_input(
                    example,
                    lambda x: x.update(raw_telemetry_included=value),
                )
                self.assert_invalid(
                    example, "SFT_RAW_TELEMETRY_FLAG_REQUIRED_FALSE"
                )

    def test_lineage_audit_uses_nested_input_gate(self):
        example = fixture()
        edit_input(
            example,
            lambda x: x["machine_diagnosis"]["findings"][0].update(
                finding_type="UNREVIEWED_GOLD"
            ),
        )
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^JSON_SCHEMA_INPUT_ENUM$"
        ):
            audit_sft_lineage([example])


if __name__ == "__main__":
    unittest.main()
