"""SYNTHETIC_TEST_ONLY: no real case payload, report or reviewer identity."""
from __future__ import annotations

import copy
import json
import unittest

from dgsi.real_review_queue_preflight import (
    CHECKS, ReviewQueuePreflightError, audit_review_queue, load_review_queue,
)


def synthetic_queue():
    def check(code):
        return {
            "check_id": code, "review_status": "NOT_VERIFIED", "evidence_ref": None,
            "evidence_sha256": None, "reviewer_token": None, "not_for_sft": True,
        }
    return {
        "schema_version": "dgsi.local-real-candidate-evidence-request.v0.5",
        "classification": "LOCAL_REVIEW_WORKSPACE_ONLY",
        "safety": {
            "internal_review_not_for_sft": True, "raw_telemetry_not_default_llm_input": True,
            "historical_no_hit_acceptable_when_proven": True, "no_automatic_gold": True,
            "no_training_authorized": True, "no_fake_ml_runs_or_logs": True,
        },
        "counts": {
            "candidate_count": 1, "real_gold": 0, "upstream_ml_verified": 0,
            "independent_expert_reviews_completed": 0, "training_authorized": False,
        },
        "cases": [{
            "case_id": "SYNTHETIC_TEST_ONLY-1", "source_case_sha256": "a" * 64,
            "admission_track": "REAL_GOLD_TRACK_CANDIDATE", "event_family_id": None,
            "gold_eligible": False, "training_authorized": False, "not_for_sft": True,
            "source_permission_verified": False, "deidentification_verified": False,
            "l1_packet_sha256": None,
            "reviewer_1": None, "reviewer_2": None, "adjudication_status": "NOT_STARTED",
            "verification_checklist": [check(code) for code in sorted(CHECKS)],
        }],
    }


class QueuePreflightSyntheticTests(unittest.TestCase):
    def test_valid_unverified_queue_is_not_training_ready(self):
        report = audit_review_queue(synthetic_queue())
        self.assertEqual(report["case_count"], 1)
        self.assertEqual(report["unbound_event_family_count"], 1)
        self.assertTrue(all(v == 1 for v in report["unverified_by_dimension"].values()))
        self.assertFalse(report["training_authorized"])
        self.assertEqual(report["real_gold_count"], 0)
        self.assertNotIn("SYNTHETIC_TEST_ONLY-1", json.dumps(report))

    def test_verified_claim_without_receipt_blocked(self):
        q = synthetic_queue()
        q["cases"][0]["verification_checklist"][0]["review_status"] = "VERIFIED"
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_CHECK_REQUIRES_SEPARATE_EVIDENCE_RECEIPT"):
            audit_review_queue(q)

    def test_untrusted_training_claim_blocked(self):
        q = synthetic_queue()
        q["cases"][0]["training_authorized"] = True
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_PREMATURE_PROMOTION"):
            audit_review_queue(q)

    def test_permission_claim_requires_independent_receipt(self):
        q = synthetic_queue()
        q["cases"][0]["source_permission_verified"] = True
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_deidentification_claim_requires_independent_receipt(self):
        q = synthetic_queue()
        q["cases"][0]["deidentification_verified"] = True
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_l1_packet_binding_claim_requires_independent_receipt(self):
        q = synthetic_queue()
        q["cases"][0]["l1_packet_sha256"] = "b" * 64
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_missing_explicit_permission_status_is_blocked(self):
        q = synthetic_queue()
        del q["cases"][0]["source_permission_verified"]
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_missing_explicit_l1_binding_null_is_blocked(self):
        q = synthetic_queue()
        del q["cases"][0]["l1_packet_sha256"]
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_no_faked_review(self):
        q = synthetic_queue()
        q["cases"][0]["reviewer_1"] = {"token": "SYNTHETIC_TEST_ONLY-REVIEWER"}
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_REVIEW_STATUS_REQUIRES_SEPARATE_RECEIPT"):
            audit_review_queue(q)

    def test_duplicate_case_id_rejected_without_echo(self):
        q = synthetic_queue()
        q["cases"].append(copy.deepcopy(q["cases"][0]))
        q["counts"]["candidate_count"] = 2
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_CASE_ID_INVALID_OR_DUPLICATE") as cm:
            audit_review_queue(q)
        self.assertNotIn("SYNTHETIC_TEST_ONLY-1", str(cm.exception))

    def test_missing_check_rejected(self):
        q = synthetic_queue()
        q["cases"][0]["verification_checklist"].pop()
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_CHECKLIST_INCOMPLETE"):
            audit_review_queue(q)

    def test_duplicate_json_key_rejected(self):
        with self.assertRaisesRegex(ReviewQueuePreflightError, "DUPLICATE_QUEUE_JSON_KEY"):
            load_review_queue('{"cases": [], "cases": [1]}')

    def test_nonfinite_json_number_rejected(self):
        with self.assertRaisesRegex(ReviewQueuePreflightError, "NONFINITE_QUEUE_JSON_NUMBER"):
            load_review_queue('{"count":NaN}')

    def test_cohort_count_mismatch_rejected(self):
        q = synthetic_queue()
        q["counts"]["candidate_count"] = 7
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_UNVERIFIED_COUNTS_INCONSISTENT"):
            audit_review_queue(q)

    def test_bool_is_not_numeric_zero_for_verified(self):
        q = synthetic_queue()
        q["counts"]["upstream_ml_verified"] = False
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_UNVERIFIED_COUNTS_INCONSISTENT"):
            audit_review_queue(q)

    def test_hidden_internal_review_leak_never_echoed(self):
        q = synthetic_queue()
        q["cases"][0]["internal_review"] = "PRIVATE_SYNTHETIC_TEST_ONLY_REVIEW"
        self.assertNotIn("PRIVATE_SYNTHETIC_TEST_ONLY_REVIEW", json.dumps(audit_review_queue(q)))

    def test_missing_safety_guard_blocks(self):
        q = synthetic_queue()
        q["safety"]["no_fake_ml_runs_or_logs"] = False
        with self.assertRaisesRegex(ReviewQueuePreflightError, "QUEUE_SAFETY_GUARD_MISSING"):
            audit_review_queue(q)


if __name__ == "__main__":
    unittest.main()
