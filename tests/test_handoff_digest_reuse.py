"""SYNTHETIC ONLY: adversarial cohort digest/split/identity tests."""
from __future__ import annotations

import copy
import json
import unittest

from dgsi.handoff_digest_reuse import (
    HandoffDigestReuseError, audit_handoff_digest_reuse,
)

D1 = "a" * 64
D2 = "b" * 64
D3 = "c" * 64


def synthetic(case_id: str = "SYNTHETIC-CASE-A",
              family: str = "SYNTHETIC-FAMILY-A",
              diagnosis_sha: str = D1,
              log_sha: str = D2) -> dict:
    return {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": case_id,
        "event_family_id": family,
        "source_class": "SYNTHETIC_FIXTURE",
        "permission_status": "AUTHORIZED_FOR_REVIEW",
        "source_owner": "SYNTHETIC-TEST-SOURCE",
        "analysis_cutoff": "2026-11-15T04:20:00Z",
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
            "expert_target.json",
        ],
        "input_file_sha256": {
            "diagnosis_result.json": diagnosis_sha,
            "diagnostic_logs.jsonl": log_sha,
        },
        "outcome_status": "UNKNOWN",
    }


def entry(m: dict, split: str | None = None) -> dict:
    return {"manifest": m, "split": split}


class SyntheticHandoffDigestReuseTests(unittest.TestCase):
    def test_single_synthetic_never_gold(self):
        report = audit_handoff_digest_reuse([entry(synthetic())])
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(report["training_eligible"])
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["source_authenticity_verified"])
        self.assertFalse(report["input_bytes_verified_by_this_audit"])
        self.assertFalse(report["split_assignment_allowed"])

    def test_same_event_family_repeated_digest_is_not_an_alias(self):
        m = synthetic()
        n = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-A")
        report = audit_handoff_digest_reuse([entry(m), entry(n)])
        self.assertEqual(report["repeated_incident_family_count"], 1)
        self.assertEqual(report["cross_family_digest_reuse_signature_count"], 0)
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")

    def test_different_event_families_same_diagnosis_digest_require_review(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D1, D3)
        report = audit_handoff_digest_reuse([entry(a), entry(b)])
        self.assertIn("DECLARED_EVENT_SOURCE_REUSED_ACROSS_FAMILIES", report["manual_review_codes"])
        self.assertEqual(report["cross_family_digest_reuse_signature_count"], 1)
        self.assertEqual(report["cross_split_digest_reuse_signature_count"], 0)

    def test_cross_split_diagnosis_digest_blocked_even_when_family_names_differ(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D1, D3)
        report = audit_handoff_digest_reuse([entry(a, "train"), entry(b, "test")])
        self.assertEqual(report["decision"], "BLOCKED_SOURCE_REUSE")
        self.assertIn("CROSS_SPLIT_DECLARED_EVENT_SOURCE_DIGEST", report["blocker_codes"])
        self.assertEqual(report["cross_split_digest_reuse_signature_count"], 1)

    def test_cross_split_log_digest_also_blocked(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D3, D2)
        report = audit_handoff_digest_reuse([entry(a, "train"), entry(b, "validation")])
        self.assertIn("CROSS_SPLIT_DECLARED_EVENT_SOURCE_DIGEST", report["blocker_codes"])

    def test_same_family_cross_split_rejected_before_digest_check(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-A", D3, D3)
        with self.assertRaisesRegex(HandoffDigestReuseError, "^CROSS_SPLIT_INCIDENT_FAMILY$"):
            audit_handoff_digest_reuse([entry(a, "train"), entry(b, "test")])

    def test_synthetic_real_claim_digest_alias_blocked(self):
        a, b = synthetic(), synthetic("PSEUDONYM-B", "FAMILY-B", D1, D3)
        b["source_class"] = "ENGINEERING_TEST"  # deliberately unverified claim
        report = audit_handoff_digest_reuse([entry(a), entry(b)])
        self.assertEqual(report["decision"], "BLOCKED_SOURCE_REUSE")
        self.assertIn("SYNTHETIC_REAL_DECLARED_SOURCE_ALIAS", report["blocker_codes"])
        self.assertFalse(report["training_eligible"])

    def test_real_claim_no_collision_never_gold(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A")
        a["source_class"] = "REAL_GROUND_TEST"  # synthetic fixture pretending to be real
        report = audit_handoff_digest_reuse([entry(a)])
        self.assertEqual(report["decision"], "PASS_UNTRUSTED_DECLARATIONS_ONLY")
        self.assertFalse(report["source_authenticity_verified"])
        self.assertFalse(report["gold_eligible"])

    def test_missing_diagnosis_digest_is_manual_review(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A")
        a["source_class"] = "ENGINEERING_TEST"
        del a["input_file_sha256"]["diagnosis_result.json"]
        report = audit_handoff_digest_reuse([entry(a)])
        self.assertEqual(report["decision"], "MANUAL_EVENT_FAMILY_REVIEW")
        self.assertIn("EPISODE_SOURCE_DIGEST_DECLARATIONS_INCOMPLETE", report["manual_review_codes"])
        self.assertEqual(report["missing_event_digest_case_count"], 1)

    def test_nonready_manifest_cannot_appear_clean(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A")
        a["source_class"] = "REAL_FLIGHT"  # only a synthetic test claim
        a["permission_status"] = "RESTRICTED_REVIEW_ONLY"
        report = audit_handoff_digest_reuse([entry(a)])
        self.assertEqual(report["decision"], "MANUAL_EVENT_FAMILY_REVIEW")
        self.assertEqual(report["manifest_not_ready_case_count"], 1)

    def test_duplicate_case_id_rejected_even_if_families_differ(self):
        a = synthetic()
        b = synthetic(family="SYNTHETIC-FAMILY-B", diagnosis_sha=D3)
        with self.assertRaisesRegex(HandoffDigestReuseError, "^DUPLICATE_HANDOFF_CASE_ID$"):
            audit_handoff_digest_reuse([entry(a), entry(b)])

    def test_partial_existing_splits_cannot_avoid_check(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D3, D3)
        with self.assertRaisesRegex(HandoffDigestReuseError, "^PARTIALLY_ASSIGNED_SPLIT_COHORT$"):
            audit_handoff_digest_reuse([entry(a, "train"), entry(b)])

    def test_invalid_preassigned_split_rejected(self):
        with self.assertRaisesRegex(HandoffDigestReuseError, "^INVALID_PREEXISTING_SPLIT$"):
            audit_handoff_digest_reuse([entry(synthetic(), "gold")])

    def test_invalid_manifest_rejected_without_values(self):
        a = synthetic()
        a["raw_telemetry"] = [[4, 5, 6]]
        with self.assertRaisesRegex(HandoffDigestReuseError, "^INVALID_HANDOFF_MANIFEST$"):
            audit_handoff_digest_reuse([entry(a)])

    def test_invalid_entry_shape_rejected(self):
        with self.assertRaisesRegex(HandoffDigestReuseError, "^INVALID_DIGEST_REUSE_ENTRY$"):
            audit_handoff_digest_reuse([{"manifest": synthetic(), "split": None, "target": "private"}])

    def test_wrong_batch_type_rejected(self):
        with self.assertRaisesRegex(HandoffDigestReuseError, "^INVALID_DIGEST_REUSE_BATCH$"):
            audit_handoff_digest_reuse({"manifest": synthetic()})

    def test_no_role_confusion_with_generic_context_hash(self):
        a = synthetic()
        a["input_file_sha256"]["spacecraft_context.json"] = D3
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D3, "d"*64)
        report = audit_handoff_digest_reuse([entry(a), entry(b)])
        self.assertEqual(report["cross_family_digest_reuse_signature_count"], 0)

    def test_no_case_ids_paths_or_hash_values_in_output(self):
        a = synthetic("PRIVATE-CASE-NAME", "PRIVATE-FAMILY-NAME")
        b = synthetic("PRIVATE-CASE-OTHER", "PRIVATE-FAMILY-OTHER", D1, D3)
        report = audit_handoff_digest_reuse([entry(a), entry(b)])
        body = json.dumps(report, ensure_ascii=False)
        self.assertNotIn("PRIVATE-", body)
        self.assertNotIn(D1, body)
        self.assertNotIn(D2, body)
        self.assertNotIn("diagnosis_result.json", body)

    def test_counts_do_not_assign_any_split(self):
        a, b = synthetic(), synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B", D3, D3)
        report = audit_handoff_digest_reuse([entry(a, "train"), entry(b, "validation")])
        self.assertTrue(report["split_labels_provided"])
        self.assertEqual(report["existing_split_counts"]["train"], 1)
        self.assertEqual(report["existing_split_counts"]["validation"], 1)
        self.assertFalse(report["split_assignment_allowed"])


if __name__ == "__main__":
    unittest.main()
