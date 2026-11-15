"""SYNTHETIC-only regression tests: citations and prompt identity in direct SFT.

This suite never imports real spacecraft records or creates Gold training data.
"""
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
ILLUSTRATIVE = json.loads(
    (ROOT / "examples/diagnostic_context_sft_illustrative.json").read_text(
        encoding="utf-8"
    )
)


def synthetic_example():
    return copy.deepcopy(ILLUSTRATIVE)


def edit_prompt(example, mutate):
    message = example["messages"][1]
    prefix, separator, packet_text = message["content"].partition("{")
    assert separator
    packet = json.loads("{" + packet_text)
    mutate(packet)
    message["content"] = prefix + json.dumps(packet, ensure_ascii=False)


def edit_target(example, mutate):
    message = example["messages"][2]
    target = json.loads(message["content"])
    mutate(target)
    message["content"] = json.dumps(target, ensure_ascii=False)


class StandaloneSftEvidenceTests(unittest.TestCase):
    def reject(self, example, code):
        with self.assertRaisesRegex(
            DiagnosticContextValidationError, "^" + code + "$"
        ):
            validate_sft_example(example)

    def test_valid_synthetic_example_is_structural_only(self):
        example = synthetic_example()
        validate_sft_example(example)
        result = audit_sft_lineage([example])
        self.assertEqual(result["decision"], "PASS_STRUCTURAL_ONLY")
        self.assertFalse(result["gold_eligible"])

    def test_absent_machine_evidence_in_target_is_rejected(self):
        example = synthetic_example()
        edit_target(
            example,
            lambda t: t["evidence_assessment"]["supporting_refs"].append("ML-NOT-SUPPLIED"),
        )
        self.reject(example, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_absent_log_evidence_in_target_is_rejected(self):
        example = synthetic_example()
        edit_target(
            example,
            lambda t: t["evidence_assessment"]["contradicting_refs"].append("LOG-NOT-SUPPLIED"),
        )
        self.reject(example, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_absent_candidate_evidence_in_target_is_rejected(self):
        example = synthetic_example()
        edit_target(
            example,
            lambda t: t["cause_localization"]["candidates"][0]["supporting_refs"].append("FUTURE-REF"),
        )
        self.reject(example, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_unprovided_historical_case_relevance_is_rejected(self):
        example = synthetic_example()
        edit_target(
            example,
            lambda t: t["historical_experience_relevance"][0].update(case_ref="HIST-NOT-SUPPLIED"),
        )
        self.reject(example, "UNRESOLVED_HISTORICAL_EXPERIENCE_REFERENCE")

    def test_machine_evidence_removed_from_input_is_rejected(self):
        example = synthetic_example()
        edit_prompt(
            example,
            lambda p: p["input"]["machine_diagnosis"]["findings"][0][
                "supporting_evidence_ids"
            ].remove("ML-E-02"),
        )
        self.reject(example, "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    def test_ambiguous_cross_namespace_citation_is_rejected(self):
        example = synthetic_example()
        edit_prompt(
            example,
            lambda p: p["input"]["diagnostic_logs"][0].update(log_id="ML-E-01"),
        )
        self.reject(example, "AMBIGUOUS_CROSS_SOURCE_EVIDENCE_ID")

    def test_duplicate_log_ids_rejected(self):
        example = synthetic_example()
        edit_prompt(
            example,
            lambda p: p["input"]["diagnostic_logs"][1].update(log_id="LOG-01"),
        )
        self.reject(example, "DUPLICATE_DIAGNOSTIC_LOG_ID")

    def test_duplicate_findings_rejected(self):
        example = synthetic_example()
        edit_prompt(
            example,
            lambda p: p["input"]["machine_diagnosis"]["findings"][1].update(finding_id="F-01"),
        )
        self.reject(example, "DUPLICATE_MACHINE_FINDING_ID")

    def test_prompt_case_identity_must_match_example(self):
        example = synthetic_example()
        edit_prompt(example, lambda p: p.update(case_id="DIFFERENT-SYNTH-CASE"))
        self.reject(example, "SFT_PROMPT_CASE_REFERENCE_MISMATCH")

    def test_prompt_task_type_must_match_example(self):
        example = synthetic_example()
        edit_prompt(example, lambda p: p.update(task_type="handover_summary"))
        self.reject(example, "SFT_PROMPT_TASK_TYPE_MISMATCH")

    def test_lineage_audit_cannot_bypass_reference_gate(self):
        example = synthetic_example()
        edit_target(
            example,
            lambda t: t["evidence_assessment"]["supporting_refs"].append("FAKE-GOLD-REF"),
        )
        with self.assertRaisesRegex(
            DiagnosticContextValidationError,
            "^UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE$",
        ):
            audit_sft_lineage([example])


if __name__ == "__main__":
    unittest.main()
