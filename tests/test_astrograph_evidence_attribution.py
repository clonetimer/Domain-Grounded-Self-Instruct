"""SYNTHETIC-only adversarial checks: do not invent AstroGraph ML evidence links.

These packets are hand-written contract tests, not field history, expert
judgments, Gold SFT, or a model-level prompt-injection evaluation.
"""
from __future__ import annotations

import copy
import math
import unittest

from dgsi.astrograph_adapter import (
    UpstreamDiagnosisAdapterError,
    normalize_astrograph_diagnosis_result,
)


def synthetic_packet():
    return {
        "schema_version": "astrograph-unified-diagnosis.v1",
        "case_id": "SYNTH-EVIDENCE-CONFLICT",
        "status": "CONFLICTING_EVIDENCE",
        "backend": "SYNTHETIC_TEST",
        "primary_subsystem": "ADCS",
        "primary_component": "rw-2",
        "labels_used": False,
        "truth_used": False,
        "claim_boundary": "SYNTHETIC: only screening candidates, not proven faults",
        "candidates": [
            {
                "effect_id": "SYNTHETIC_FAULT_A",
                "screening_score": 0.81,
                "support_engines": ["engine_1"],
                "contradicting_engines": ["engine_2"],
            },
            {
                "effect_id": "SYNTHETIC_FAULT_B",
                "screening_score": 0.37,
                "support_engines": ["engine_2"],
                "contradicting_engines": ["engine_1"],
            },
        ],
        "diagnostic_evidence": [
            {"evidence_id": "SYNTH-E-A", "field": "derived_residual_1",
             "interpretation": "SYNTHETIC derived feature"},
            {"evidence_id": "SYNTH-E-B", "field": "derived_residual_2",
             "interpretation": "SYNTHETIC derived feature"},
        ],
    }


class AstrographEvidenceAttributionSyntheticTests(unittest.TestCase):
    def assert_rejected(self, packet, code):
        with self.assertRaisesRegex(UpstreamDiagnosisAdapterError, "^" + code + "$"):
            normalize_astrograph_diagnosis_result(packet)

    def test_does_not_attribute_all_evidence_to_every_fault(self):
        normalized = normalize_astrograph_diagnosis_result(synthetic_packet())
        self.assertEqual(normalized["status"], "MULTIPLE_CANDIDATES")
        candidates = [f for f in normalized["findings"] if f["finding_type"] == "FAULT_CLASS"]
        residuals = [f for f in normalized["findings"] if f["finding_type"] == "RESIDUAL"]
        self.assertEqual(len(candidates), 2)
        self.assertEqual([f["supporting_evidence_ids"] for f in candidates], [[], []])
        self.assertEqual([f["supporting_evidence_ids"] for f in residuals],
                         [["SYNTH-E-A"], ["SYNTH-E-B"]])
        for finding in candidates:
            self.assertIn("candidate-specific diagnostic evidence links were not supplied",
                          finding["limitations"])
            self.assertIn("upstream reports contradicting engines; resolution required",
                          finding["limitations"])
            self.assertIn("not a calibrated probability", finding["score_semantics"])
        self.assertEqual([f["score"] for f in candidates], [0.81, 0.37])

    def test_zero_is_not_inferred_if_score_is_omitted(self):
        packet = synthetic_packet()
        del packet["candidates"][0]["screening_score"]
        finding = normalize_astrograph_diagnosis_result(packet)["findings"][0]
        self.assertIsNone(finding["score"])
        self.assertIsNone(finding["score_semantics"])

    def test_normal_without_candidates_does_not_invent_a_fault(self):
        packet = synthetic_packet()
        packet["status"] = "NORMAL"
        packet["candidates"] = []
        packet["diagnostic_evidence"] = []
        self.assertEqual(normalize_astrograph_diagnosis_result(packet)["findings"], [])

    def test_missing_truth_or_label_flag_must_not_default_to_false(self):
        for key in ("truth_used", "labels_used"):
            with self.subTest(key=key):
                packet = synthetic_packet()
                del packet[key]
                self.assert_rejected(packet, "UNVERIFIED_UNIFIED_TRUTH_OR_LABEL_FLAGS")

    def test_non_boolean_or_true_flags_fail_closed(self):
        for key in ("truth_used", "labels_used"):
            for value in (True, 0, "false", None):
                with self.subTest(key=key, value=value):
                    packet = synthetic_packet()
                    packet[key] = value
                    self.assert_rejected(packet, "UPSTREAM_TRUTH_OR_LABEL_PROVENANCE_UNSAFE")

    def test_score_range_or_numeric_type_is_never_reinterpreted(self):
        for value in (-0.1, 1.1, float("nan"), float("inf"), "0.81", True, 10**500):
            with self.subTest(value=repr(value)[:20]):
                packet = synthetic_packet()
                packet["candidates"][0]["screening_score"] = value
                self.assert_rejected(packet, "INVALID_UNIFIED_SCREENING_SCORE")

    def test_duplicate_evidence_id_fails_without_echoing_content(self):
        packet = synthetic_packet()
        packet["diagnostic_evidence"][1]["evidence_id"] = "SYNTH-E-A"
        self.assert_rejected(packet, "DUPLICATE_UNIFIED_EVIDENCE_ID")

    def test_malformed_evidence_id_fails_closed(self):
        for broken in (None, "", 123):
            packet = synthetic_packet()
            packet["diagnostic_evidence"][0]["evidence_id"] = broken
            self.assert_rejected(packet, "UNIFIED_EVIDENCE_ID_MISSING")

    def test_unknown_or_duplicate_candidates_fail_closed(self):
        packet = synthetic_packet()
        packet["candidates"][1]["effect_id"] = "SYNTHETIC_FAULT_A"
        self.assert_rejected(packet, "DUPLICATE_UNIFIED_CANDIDATE_EFFECT_ID")
        packet = synthetic_packet()
        packet["candidates"][0]["effect_id"] = " "
        self.assert_rejected(packet, "INVALID_UNIFIED_CANDIDATE_EFFECT_ID")

    def test_invalid_engine_reference_shape_is_rejected(self):
        packet = synthetic_packet()
        packet["candidates"][0]["contradicting_engines"] = "engine_1"
        self.assert_rejected(packet, "INVALID_UNIFIED_ENGINE_REFERENCES")

    def test_unknown_schema_is_not_silently_treated_as_legacy(self):
        packet = {"schema_version": "unrecognized-diagnosis.v42",
                  "candidate_fault_id": "SYNTHETIC_FAULT"}
        self.assert_rejected(packet, "UNSUPPORTED_UPSTREAM_DIAGNOSIS_SCHEMA")

    def test_unknown_status_error_does_not_echo_source_payload(self):
        packet = synthetic_packet()
        packet["status"] = "SYNTHETIC_PRIVATE_TEXT_SENTINEL"
        with self.assertRaises(UpstreamDiagnosisAdapterError) as context:
            normalize_astrograph_diagnosis_result(packet)
        self.assertEqual(str(context.exception), "UNSUPPORTED_UNIFIED_DIAGNOSIS_STATUS")
        self.assertNotIn("SENTINEL", str(context.exception))


if __name__ == "__main__":
    unittest.main()
