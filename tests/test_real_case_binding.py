"""SYNTHETIC-only adversarial checks for untrusted manifest-to-Case binding."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.real_case_binding import (
    HandoffCaseBindingError, assess_handoff_case_binding,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "diagnostic_context_case_illustrative.json"


def packet() -> dict:
    case = json.loads(FIXTURE.read_text(encoding="utf-8"))
    case["case_id"] = "SYNTHETIC-TEST-CASE-01"
    case["provenance"]["source_group"] = "SYNTHETIC-TEST-FAMILY-01"
    case["provenance"]["source_artifact_hashes"] = ["0" * 64]  # synthetic placeholder, never verified
    return case


def manifest_for(case: dict) -> dict:
    return {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": case["case_id"],
        "source_class": "SYNTHETIC_FIXTURE",
        "permission_status": "AUTHORIZED_FOR_TRAINING",  # deliberately untrusted
        "source_owner": "SYNTHETIC-TEST-OWNER",
        "event_family_id": case["provenance"]["source_group"],
        "spacecraft_pseudonym": case["input"]["spacecraft_context"]["spacecraft_id"],
        "analysis_cutoff": case["input"]["analysis_cutoff"],
        "timestamp_policy": "ORIGINAL_TIMEZONE_AWARE",
        "redaction": {
            "personal_identifiers_removed": True,
            "sensitive_ids_pseudonymized": True,
            "time_shifted": False,
            "redacted_fields": [],
        },
        "available_files": [
            "diagnosis_result.json", "diagnostic_logs.jsonl",
            "spacecraft_context.json", "operational_context.json",
            "historical_cases.json", "knowledge_refs.json", "expert_target.json",
        ],
        "outcome_status": "CONFIRMED",  # synthetic assertion, not a real expert finding
    }


class HandoffCaseBindingSyntheticTests(unittest.TestCase):
    def setUp(self):
        self.case = packet()
        self.manifest = manifest_for(self.case)

    def assess(self):
        return assess_handoff_case_binding(self.manifest, self.case)

    def test_synthetic_cannot_be_gold_even_with_training_permission_claim(self):
        result = self.assess()
        self.assertEqual(result["decision"], "SYNTHETIC_TEST_ONLY")
        for name in ("training_eligible", "gold_eligible", "source_rights_verified",
                     "case_content_authenticated", "split_assignment_allowed",
                     "independent_expert_review_verified"):
            self.assertFalse(result[name])

    def test_real_source_claim_with_synthetic_case_marker_is_rejected(self):
        self.manifest["source_class"] = "REAL_FLIGHT"
        result = self.assess()
        self.assertEqual(result["decision"], "REJECT")
        self.assertIn("SYNTHETIC_CASE_MISDECLARED_REAL", result["blocker_codes"])

    def test_case_id_mismatch_is_caught(self):
        self.manifest["case_id"] = "SYNTHETIC-ANOTHER-CASE"
        self.assertIn("CASE_ID_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_event_family_mismatch_is_caught(self):
        self.manifest["event_family_id"] = "SYNTHETIC-UNRELATED-FAMILY"
        self.assertIn("EVENT_FAMILY_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_equal_absolute_cutoff_with_different_timezone_is_accepted(self):
        self.manifest["analysis_cutoff"] = "2026-04-12T18:10:00+09:00"
        self.assertNotIn("ANALYSIS_CUTOFF_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_different_cutoff_is_caught(self):
        self.manifest["analysis_cutoff"] = "2026-04-12T09:11:00Z"
        self.assertIn("ANALYSIS_CUTOFF_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_naive_cutoff_is_invalid_without_raw_error(self):
        self.manifest["analysis_cutoff"] = "2026-04-12T09:10:00"
        with self.assertRaisesRegex(HandoffCaseBindingError, "^INVALID_HANDOFF_MANIFEST$"):
            self.assess()

    def test_spacecraft_pseudonym_mismatch_is_caught(self):
        self.manifest["spacecraft_pseudonym"] = "SYNTHETIC-OTHER-SPACECRAFT"
        self.assertIn("SPACECRAFT_PSEUDONYM_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_missing_historical_file_declaration_is_caught(self):
        self.manifest["available_files"].remove("historical_cases.json")
        self.assertIn("OPTIONAL_EVIDENCE_FILE_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_forged_knowledge_file_declaration_is_caught(self):
        self.case["input"]["knowledge_evidence"] = []
        self.manifest["available_files"].append("historical_cases.json") if False else None
        self.assertIn("OPTIONAL_EVIDENCE_FILE_BINDING_MISMATCH", self.assess()["blocker_codes"])

    def test_missing_upstream_run_ref_blocks_binding(self):
        self.case["provenance"]["diagnosis_run_refs"] = []
        self.assertIn("DIAGNOSIS_RUN_REFERENCE_MISSING", self.assess()["blocker_codes"])

    def test_missing_source_hash_blocks_binding(self):
        self.case["provenance"]["source_artifact_hashes"] = []
        self.assertIn("SOURCE_ARTIFACT_HASH_MISSING", self.assess()["blocker_codes"])

    def test_embedded_raw_telemetry_fails_closed(self):
        self.case["input"]["raw_telemetry"] = [[1, 2, 3]]
        with self.assertRaisesRegex(HandoffCaseBindingError, "^INVALID_DIAGNOSTIC_CASE$"):
            self.assess()

    def test_invalid_manifest_fails_closed(self):
        self.manifest["injection_truth"] = "SYNTHETIC-UNTRUSTED"
        with self.assertRaisesRegex(HandoffCaseBindingError, "^INVALID_HANDOFF_MANIFEST$"):
            self.assess()

    def test_no_private_text_or_pseudonym_in_aggregate_report(self):
        self.manifest["case_id"] = "SYNTHETIC-SECRET-CASE"
        result = self.assess()
        serialized = json.dumps(result)
        self.assertNotIn("SYNTHETIC-SECRET-CASE", serialized)
        self.assertNotIn("ILLUSTRATIVE-LEO-01", serialized)
        self.assertNotIn("expected_output", serialized)

    def test_fake_real_claim_passes_alignment_not_source_authentication(self):
        # All fields are still authored SYNTHETIC: removing markers does NOT
        # prove a real episode. This tests the explicitly unverified review state.
        self.manifest["source_class"] = "ENGINEERING_TEST"
        self.case["case_id"] = self.manifest["case_id"] = "TEST-CLAIM-CASE-01"
        self.case["provenance"]["source_group"] = self.manifest["event_family_id"] = "TEST-CLAIM-FAMILY-01"
        self.case["provenance"]["diagnosis_run_refs"] = ["test://claim/01"]
        self.case["provenance"]["generation_method"] = "unverified test claim"
        result = self.assess()
        self.assertEqual(result["decision"], "READY_FOR_MANUAL_SOURCE_AUDIT")
        self.assertFalse(result["source_rights_verified"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_eligible"])

    def test_approved_review_flag_is_not_expert_proof(self):
        self.case["review"]["status"] = "APPROVED"
        self.case["review"]["reviewer_id"] = "SYNTHETIC-REVIEWER"
        self.case["review"]["reviewed_at"] = "2026-04-12T10:00:00Z"
        result = self.assess()
        self.assertIn("CASE_APPROVAL_ASSERTION_NOT_INDEPENDENT_PROOF", result["warning_codes"])
        self.assertFalse(result["independent_expert_review_verified"])
        self.assertFalse(result["gold_eligible"])


if __name__ == "__main__":
    unittest.main()
