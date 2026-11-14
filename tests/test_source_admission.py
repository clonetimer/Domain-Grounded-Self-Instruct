"""SYNTHETIC-ONLY adversarial checks for metadata admission; no real cases or Gold."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.source_admission import SourceAdmissionError, assess_source_admission

ROOT = Path(__file__).resolve().parents[1]
ILLUSTRATION = json.loads(
    (ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8")
)
CHECKS = (
    "upstream_run_verified", "log_provenance_verified",
    "spacecraft_and_mission_context_verified", "historical_outcomes_verified",
    "evidence_citations_verified", "source_hashes_verified",
    "incident_family_deduplicated", "cross_split_leakage_checked",
    "score_semantics_verified",
)
PERMISSIONS = (
    "access_authorized", "ip_rights_checked", "deidentification_checked",
    "internal_sft_use_authorized",
)


def fixture():
    case = copy.deepcopy(ILLUSTRATION)
    manifest = {
        "schema_version": "dgsi-source-admission.v1",
        "case_ref": case["case_id"],
        "incident_family": case["provenance"]["source_group"],
        "source_class": "PUBLIC_SYNTHETIC_FIXTURE",
        "permissions": {field: True for field in PERMISSIONS},
        "checks": {field: True for field in CHECKS},
        "producer": {
            "method": case["input"]["machine_diagnosis"]["producer"]["method"],
            "version": case["input"]["machine_diagnosis"]["producer"]["version"],
        },
        "run_completed_at": "2026-04-12T09:00:00Z",
        "audit_evidence_sha256": "b" * 64,
    }
    return case, manifest


class SourceAdmissionSyntheticAdversarialTests(unittest.TestCase):
    def test_synthetic_is_blocked_even_when_all_claims_true(self):
        case, manifest = fixture()
        decision = assess_source_admission(case, manifest)
        self.assertEqual(decision["decision"], "BLOCKED")
        self.assertIn("SYNTHETIC_SOURCE_NOT_REAL_CASE", decision["blockers"])
        self.assertIn("SYNTHETIC_PROVENANCE_MARKER", decision["blockers"])
        self.assertFalse(decision["gold_eligible"])
        self.assertFalse(decision["eligible_for_training"])
        self.assertFalse(decision["authorization_verified_by_software"])
        self.assertNotIn("case_ref", decision)

    def test_declaring_synthetic_as_real_does_not_override_source_marker(self):
        case, manifest = fixture()
        manifest["source_class"] = "REAL_ON_ORBIT_RECORD"
        decision = assess_source_admission(case, manifest)
        self.assertIn("SYNTHETIC_PROVENANCE_MARKER", decision["blockers"])

    def test_no_source_hashes_blocks(self):
        case, manifest = fixture()
        decision = assess_source_admission(case, manifest)
        self.assertIn("MISSING_SOURCE_ARTIFACT_HASHES", decision["blockers"])

    def test_permission_is_fail_closed(self):
        case, manifest = fixture()
        manifest["permissions"]["internal_sft_use_authorized"] = False
        decision = assess_source_admission(case, manifest)
        self.assertIn("PERMISSION_INTERNAL_SFT_USE_AUTHORIZED_NOT_VERIFIED", decision["blockers"])

    def test_ip_rights_are_separate_from_data_access(self):
        case, manifest = fixture()
        manifest["permissions"]["ip_rights_checked"] = False
        self.assertIn(
            "PERMISSION_IP_RIGHTS_CHECKED_NOT_VERIFIED",
            assess_source_admission(case, manifest)["blockers"],
        )

    def test_score_semantics_verification_blocks(self):
        case, manifest = fixture()
        manifest["checks"]["score_semantics_verified"] = False
        self.assertIn(
            "CHECK_SCORE_SEMANTICS_VERIFIED_NOT_VERIFIED",
            assess_source_admission(case, manifest)["blockers"],
        )

    def test_incident_family_dedup_separate_from_split_audit(self):
        case, manifest = fixture()
        manifest["checks"]["incident_family_deduplicated"] = False
        self.assertIn(
            "CHECK_INCIDENT_FAMILY_DEDUPLICATED_NOT_VERIFIED",
            assess_source_admission(case, manifest)["blockers"],
        )

    def test_post_cutoff_upstream_result_blocks(self):
        case, manifest = fixture()
        manifest["run_completed_at"] = "2026-04-12T11:15:00+00:00"
        self.assertIn(
            "UPSTREAM_RUN_AFTER_ANALYSIS_CUTOFF",
            assess_source_admission(case, manifest)["blockers"],
        )

    def test_naive_run_time_rejected(self):
        case, manifest = fixture()
        manifest["run_completed_at"] = "2026-04-12T09:00:00"
        with self.assertRaisesRegex(SourceAdmissionError, "^INVALID_SOURCE_RUN_TIME$"):
            assess_source_admission(case, manifest)

    def test_swapped_case_reference_rejected(self):
        case, manifest = fixture()
        manifest["case_ref"] = "foreign-case"
        with self.assertRaisesRegex(SourceAdmissionError, "^CASE_ATTESTATION_BINDING_MISMATCH$"):
            assess_source_admission(case, manifest)

    def test_wrong_incident_family_rejected(self):
        case, manifest = fixture()
        manifest["incident_family"] = "unrelated-episode"
        with self.assertRaisesRegex(SourceAdmissionError, "^CASE_ATTESTATION_BINDING_MISMATCH$"):
            assess_source_admission(case, manifest)

    def test_producer_version_mismatch_rejected(self):
        case, manifest = fixture()
        manifest["producer"]["version"] = "42.0"
        with self.assertRaisesRegex(SourceAdmissionError, "^UPSTREAM_PRODUCER_BINDING_MISMATCH$"):
            assess_source_admission(case, manifest)

    def test_boolean_strings_rejected(self):
        case, manifest = fixture()
        manifest["permissions"]["access_authorized"] = "true"
        with self.assertRaisesRegex(SourceAdmissionError, "^INVALID_ATTESTATION_BOOLEAN$"):
            assess_source_admission(case, manifest)

    def test_extra_sensitive_payload_field_rejected(self):
        case, manifest = fixture()
        manifest["raw_diagnostic_logs"] = [{"secret": "never write to public repo"}]
        with self.assertRaisesRegex(SourceAdmissionError, "^INVALID_ATTESTATION_SHAPE$"):
            assess_source_admission(case, manifest)

    def test_missing_audit_evidence_digest_blocks(self):
        case, manifest = fixture()
        manifest["audit_evidence_sha256"] = None
        self.assertIn(
            "MISSING_AUTHORIZATION_AUDIT_EVIDENCE_DIGEST",
            assess_source_admission(case, manifest)["blockers"],
        )

    def test_bad_audit_evidence_digest_rejected(self):
        case, manifest = fixture()
        manifest["audit_evidence_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(SourceAdmissionError, "^INVALID_ATTESTATION_DIGEST$"):
            assess_source_admission(case, manifest)

    def test_unresolved_history_is_counted_without_promotion(self):
        case, manifest = fixture()
        result = assess_source_admission(case, manifest)
        self.assertEqual(result["unresolved_history_count"], 1)
        self.assertFalse(result["gold_eligible"])

    def test_fake_real_metadata_can_only_trigger_manual_audit(self):
        # A malicious/incorrect attestation could disguise a synthetic case.
        # Structural admission MUST NEVER authenticate source reality or grant Gold.
        case, manifest = fixture()
        case["case_id"] = "FAKE-REAL-FOR-TEST-ONLY"
        case["provenance"]["source_group"] = "FAKE-EPISODE-FOR-TEST-ONLY"
        case["provenance"]["diagnosis_run_refs"] = ["mock://unverified-run"]
        case["provenance"]["source_artifact_hashes"] = ["a" * 64]
        case["provenance"]["generation_method"] = "not-supplied"
        manifest["case_ref"] = case["case_id"]
        manifest["incident_family"] = case["provenance"]["source_group"]
        manifest["source_class"] = "REAL_ENGINEERING_DIAGNOSIS"
        result = assess_source_admission(case, manifest)
        self.assertEqual(result["decision"], "READY_FOR_MANUAL_SOURCE_AUDIT")
        self.assertFalse(result["authorization_verified_by_software"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["eligible_for_training"])


if __name__ == "__main__":
    unittest.main()
