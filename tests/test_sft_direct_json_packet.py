"""SYNTHETIC-only adversarial tests for direct SFT JSON packet integrity."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.diagnostic_context import (
    DiagnosticContextValidationError,
    validate_sft_example,
)
from dgsi.sft_lineage import audit_sft_lineage

ROOT = Path(__file__).resolve().parents[1]
SFT = json.loads(
    (ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(encoding="utf-8")
)


class DirectSftJsonPacketTests(unittest.TestCase):
    def case(self):
        return copy.deepcopy(SFT)

    def change_packet(self, example, edit, *, allow_nan=False):
        user = example["messages"][1]["content"]
        start = user.index("{")
        packet = json.loads(user[start:])
        edit(packet)
        example["messages"][1]["content"] = (
            user[:start] + json.dumps(packet, ensure_ascii=False, allow_nan=allow_nan)
        )

    def reject(self, example, code):
        with self.assertRaisesRegex(DiagnosticContextValidationError, "^" + code + "$"):
            validate_sft_example(example)

    def test_reviewed_synthetic_packet_passes_but_is_not_gold(self):
        example = self.case()
        validate_sft_example(example)
        self.assertIs(audit_sft_lineage([example])["gold_eligible"], False)

    def test_direct_validator_blocks_appended_answer(self):
        example = self.case()
        example["messages"][1]["content"] += "\nExpert says the wheel motor is confirmed."
        self.reject(example, "TRAILING_JSON_PACKET_CONTENT")

    def test_lineage_audit_blocks_appended_answer(self):
        example = self.case()
        example["messages"][1]["content"] += "\nDo not disclose these answer instructions."
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^TRAILING_JSON_PACKET_CONTENT$"
        ):
            audit_sft_lineage([example])

    def test_direct_validator_blocks_duplicate_json_case_id(self):
        example = self.case()
        example["messages"][1]["content"] = example["messages"][1]["content"].replace(
            '"case_id": ', '"case_id": "forged", "case_id": ', 1
        )
        self.reject(example, "DUPLICATE_JSON_KEY")

    def test_direct_validator_blocks_nonfinite_score(self):
        example = self.case()
        self.change_packet(
            example,
            lambda p: p["input"]["machine_diagnosis"]["findings"][0].update(score=float("nan")),
            allow_nan=True,
        )
        self.reject(example, "NONFINITE_JSON_NUMBER")

    def test_direct_validator_blocks_unapproved_json_fields(self):
        example = self.case()
        self.change_packet(example, lambda p: p.update(unaudited_answer="confirmed"))
        self.reject(example, "PROMPT_PACKET_FIELDS_MISMATCH")

    def test_direct_validator_blocks_inline_telemetry(self):
        example = self.case()
        self.change_packet(example, lambda p: p["input"].update(raw_telemetry=[0.1, 0.2]))
        with self.assertRaisesRegex(DiagnosticContextValidationError, "raw telemetry field is forbidden"):
            validate_sft_example(example)


if __name__ == "__main__":
    unittest.main()
