"""SYNTHETIC-only adversarial checks for standalone SFT provenance.

These tests do not authenticate evidence, grant IP rights or create Gold cases.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from dgsi.diagnostic_context import (
    DiagnosticContextValidationError,
    validate_sft_example,
)
from dgsi.sft_lineage import audit_sft_lineage

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = json.loads(
    (ROOT / "examples/diagnostic_context_sft_illustrative.json")
    .read_text(encoding="utf-8")
)


def example():
    return copy.deepcopy(SYNTHETIC)


def edit_input(item, change):
    user = item["messages"][1]["content"]
    start = user.index("{")
    packet = json.loads(user[start:])
    change(packet["input"])
    item["messages"][1]["content"] = (
        user[:start] + json.dumps(packet, ensure_ascii=False)
    )


class SftStandaloneProvenanceTests(unittest.TestCase):
    def reject(self, item, code):
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^" + code + "$"
        ) as caught:
            validate_sft_example(item)
        self.assertNotIn("ILLUSTRATIVE-LEO-01", str(caught.exception))
        self.assertNotIn("HIST-ADCS-017", str(caught.exception))

    def test_synthetic_fixture_passes_structural_only(self):
        item = example()
        validate_sft_example(item)
        self.assertFalse(audit_sft_lineage([item])["gold_eligible"])

    def test_missing_log_provenance(self):
        item = example()
        item["provenance"]["diagnostic_log_refs"].pop()
        self.reject(item, "SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH")

    def test_duplicate_log_provenance(self):
        item = example()
        item["provenance"]["diagnostic_log_refs"].append("LOG-01")
        self.reject(item, "SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH")

    def test_fabricated_log_provenance(self):
        item = example()
        item["provenance"]["diagnostic_log_refs"][0] = "SYNTH-NO-SOURCE"
        self.reject(item, "SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH")

    def test_input_log_id_changed_without_metadata(self):
        item = example()
        edit_input(item, lambda x: x["diagnostic_logs"][2].update(log_id="SYNTH-NEW-LOG"))
        self.reject(item, "SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH")

    def test_missing_knowledge_passage_provenance(self):
        item = example()
        item["provenance"]["knowledge_passage_ids"] = []
        self.reject(item, "SFT_KNOWLEDGE_PASSAGE_PROVENANCE_MISMATCH")

    def test_fabricated_knowledge_passage_provenance(self):
        item = example()
        item["provenance"]["knowledge_passage_ids"] = ["SYNTH-FORGED-PASSAGE"]
        self.reject(item, "SFT_KNOWLEDGE_PASSAGE_PROVENANCE_MISMATCH")

    def test_duplicate_knowledge_passage_provenance(self):
        item = example()
        item["provenance"]["knowledge_passage_ids"].append("NASA_REACTION_WHEEL_FUNCTION")
        self.reject(item, "SFT_KNOWLEDGE_PASSAGE_PROVENANCE_MISMATCH")

    def test_missing_spacecraft_anchor(self):
        item = example()
        item["provenance"]["context_refs"] = ["mission:synthetic-slew"]
        self.reject(item, "SFT_SPACECRAFT_CONTEXT_PROVENANCE_MISSING")

    def test_spacecraft_identity_changed_without_provenance(self):
        item = example()
        edit_input(
            item, lambda x: x["spacecraft_context"].update(
                spacecraft_id="SYNTH-REPLACED-SPACECRAFT"
            )
        )
        self.reject(item, "SFT_SPACECRAFT_CONTEXT_PROVENANCE_MISSING")

    def test_reference_order_does_not_change_lineage(self):
        item = example()
        item["provenance"]["diagnostic_log_refs"].reverse()
        validate_sft_example(item)

    def test_lineage_batch_cannot_bypass_provenance_checks(self):
        item = example()
        item["provenance"]["diagnostic_log_refs"] = ["SYNTH-FORGED-LOG"]
        with self.assertRaisesRegex(
            DiagnosticContextValidationError,
            "^SFT_DIAGNOSTIC_LOG_PROVENANCE_MISMATCH$"
        ):
            audit_sft_lineage([item])


if __name__ == "__main__":
    unittest.main()
