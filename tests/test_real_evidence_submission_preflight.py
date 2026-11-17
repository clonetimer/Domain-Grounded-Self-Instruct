"""SYNTHETIC_TEST_ONLY: all refs and case IDs are synthetic and non-sensitive."""
from __future__ import annotations

import copy
import json
import unittest

from dgsi.real_evidence_submission_preflight import (
    RealEvidenceSubmissionError, audit_evidence_submissions,
)
from dgsi.real_review_queue_preflight import CHECKS


def synthetic_queue():
    return {
        "schema_version": "dgsi.local-real-candidate-evidence-request.v0.5",
        "classification": "LOCAL_REVIEW_WORKSPACE_ONLY",
        "safety": {
            "internal_review_not_for_sft": True,
            "raw_telemetry_not_default_llm_input": True,
            "historical_no_hit_acceptable_when_proven": True,
            "no_automatic_gold": True,
            "no_training_authorized": True,
            "no_fake_ml_runs_or_logs": True,
        },
        "counts": {
            "candidate_count": 1, "real_gold": 0,
            "upstream_ml_verified": 0,
            "independent_expert_reviews_completed": 0,
            "training_authorized": False,
        },
        "cases": [{
            "case_id": "SYNTHETIC_TEST_ONLY_CASE_1",
            "source_case_sha256": "a" * 64,
            "admission_track": "REAL_GOLD_TRACK_CANDIDATE",
            "event_family_id": None,
            "gold_eligible": False,
            "training_authorized": False,
            "not_for_sft": True,
            "source_permission_verified": False,
            "deidentification_verified": False,
            "l1_packet_sha256": None,
            "reviewer_1": None, "reviewer_2": None,
            "adjudication_status": "NOT_STARTED",
            "verification_checklist": [
                {"check_id": code, "review_status": "NOT_VERIFIED",
                 "evidence_ref": None, "evidence_sha256": None,
                 "reviewer_token": None, "not_for_sft": True}
                for code in sorted(CHECKS)
            ],
        }],
    }


def synthetic_bundle():
    return {
        "schema_version": "dgsi.local-real-evidence-submissions.v1",
        "classification": "LOCAL_REVIEW_WORKSPACE_ONLY",
        "candidate_count": 1,
        "not_for_sft": True,
        "gold_eligible": False,
        "training_authorized": False,
        "split_assignment_allowed": False,
        "cases": [{
            "case_id": "SYNTHETIC_TEST_ONLY_CASE_1",
            "source_case_sha256": "a" * 64,
            "not_for_sft": True,
            "submissions": [
                {"check_id": code, "status": "NOT_SUBMITTED",
                 "artifacts": [], "not_for_sft": True}
                for code in sorted(CHECKS)
            ],
        }],
    }


def submit(bundle, check_id, ref="SYNTHETIC_TEST_ONLY_REF", sha="b" * 64):
    slot = next(s for s in bundle["cases"][0]["submissions"] if s["check_id"] == check_id)
    slot["status"] = "SUBMITTED_FOR_REVIEW"
    types = {
        "SOURCE_RIGHTS": "SOURCE_PERMISSION_RECORD",
        "DEIDENTIFICATION": "DEIDENTIFICATION_REPORT",
        "EVENT_FAMILY": "EVENT_FAMILY_RECORD",
        "UPSTREAM_ML": "ML_RESULT",
        "LOGS_CUTOFF": "DIAGNOSTIC_LOG",
        "MISSION_CONTEXT": "MISSION_CONTEXT",
        "HISTORY_ASOF": "HISTORY_ASOF_RETRIEVAL",
        "EVIDENCE_DISPOSAL": "EVIDENCE_LINK",
        "BLIND_EXPERT": "BLIND_REVIEW_REQUEST",
    }
    slot["artifacts"] = [{
        "evidence_ref": ref, "evidence_sha256": sha, "evidence_type": types[check_id],
    }]


class EvidenceSubmissionSyntheticTests(unittest.TestCase):
    def test_all_missing_stays_unverified(self):
        result = audit_evidence_submissions(synthetic_queue(), synthetic_bundle())
        self.assertEqual(result["case_count"], 1)
        self.assertEqual(sum(result["not_submitted_by_dimension"].values()), 9)
        self.assertEqual(result["real_gold_count"], 0)
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["split_assignment_allowed"])

    def test_submitted_is_not_verified_and_refs_never_echo(self):
        bundle = synthetic_bundle()
        submit(bundle, "UPSTREAM_ML", ref="PRIVATE_SYNTHETIC_TEST_ONLY_REF")
        report = audit_evidence_submissions(synthetic_queue(), bundle)
        self.assertEqual(report["submitted_for_review_by_dimension"]["UPSTREAM_ML"], 1)
        self.assertEqual(report["evidence_verified_count"], 0)
        self.assertEqual(report["expert_review_ready_count"], 0)
        serialized = json.dumps(report)
        self.assertNotIn("PRIVATE_SYNTHETIC_TEST_ONLY_REF", serialized)
        self.assertNotIn("SYNTHETIC_TEST_ONLY_CASE_1", serialized)

    def test_case_hash_binding_invalid(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["source_case_sha256"] = "c" * 64
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_CASE_BINDING_INVALID"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_queue_itself_must_be_unverified(self):
        queue = synthetic_queue()
        queue["cases"][0]["source_permission_verified"] = True
        with self.assertRaises(ValueError):
            audit_evidence_submissions(queue, synthetic_bundle())

    def test_unexpected_case_id_rejected_without_echo(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["case_id"] = "PRIVATE_SYNTHETIC_TEST_ONLY"
        with self.assertRaises(RealEvidenceSubmissionError) as cm:
            audit_evidence_submissions(synthetic_queue(), bundle)
        self.assertNotIn("PRIVATE_SYNTHETIC_TEST_ONLY", str(cm.exception))

    def test_unsupported_verified_claim_rejected(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["submissions"][0]["status"] = "VERIFIED"
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_UNSUPPORTED_VERIFICATION_CLAIM"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_premature_training_authorization_rejected(self):
        bundle = synthetic_bundle()
        bundle["training_authorized"] = True
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_SCOPE_OR_PROMOTION_INVALID"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_submitted_without_artifact_rejected(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["submissions"][0]["status"] = "SUBMITTED_FOR_REVIEW"
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_SUBMITTED_WITHOUT_ARTIFACTS"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_not_submitted_with_artifacts_rejected(self):
        bundle = synthetic_bundle()
        submit(bundle, "UPSTREAM_ML")
        slot = next(s for s in bundle["cases"][0]["submissions"] if s["check_id"] == "UPSTREAM_ML")
        slot["status"] = "NOT_SUBMITTED"
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_MISSING_WITH_ARTIFACTS"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_artifact_type_mismatch_rejected(self):
        bundle = synthetic_bundle()
        submit(bundle, "SOURCE_RIGHTS")
        slot = next(s for s in bundle["cases"][0]["submissions"] if s["check_id"] == "SOURCE_RIGHTS")
        slot["artifacts"][0]["evidence_type"] = "ML_RESULT"
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_ARTIFACT_METADATA_INVALID"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_ref_with_two_digests_rejected(self):
        bundle = synthetic_bundle()
        submit(bundle, "UPSTREAM_ML", ref="same", sha="b" * 64)
        submit(bundle, "MISSION_CONTEXT", ref="same", sha="c" * 64)
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_EVIDENCE_REF_HASH_CONFLICT"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_internal_review_field_cannot_enter_submission(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["internal_review"] = "SECRET_SYNTHETIC_TEST_ONLY"
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_CASE_FIELDS_INVALID") as cm:
            audit_evidence_submissions(synthetic_queue(), bundle)
        self.assertNotIn("SECRET_SYNTHETIC_TEST_ONLY", str(cm.exception))

    def test_duplicate_dimension_rejected(self):
        bundle = synthetic_bundle()
        bundle["cases"][0]["submissions"][1]["check_id"] = bundle["cases"][0]["submissions"][0]["check_id"]
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_CHECK_INVALID_OR_DUPLICATE"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_full_submissions_still_no_gold(self):
        bundle = synthetic_bundle()
        for code in CHECKS:
            submit(bundle, code, ref="SYNTHETIC_TEST_ONLY_" + code)
        result = audit_evidence_submissions(synthetic_queue(), bundle)
        self.assertEqual(sum(result["submitted_for_review_by_dimension"].values()), 9)
        self.assertEqual(result["real_gold_count"], 0)
        self.assertEqual(result["expert_review_ready_count"], 0)
        self.assertEqual(result["evidence_verified_count"], 0)

    def test_spurious_case_missing_source_record_rejected(self):
        bundle = synthetic_bundle()
        duplicate = copy.deepcopy(bundle["cases"][0])
        duplicate["case_id"] = "SYNTHETIC_TEST_ONLY_UNEXPECTED"
        duplicate["source_case_sha256"] = "c" * 64
        bundle["cases"].append(duplicate)
        bundle["candidate_count"] = 2
        with self.assertRaisesRegex(RealEvidenceSubmissionError, "SUBMISSION_CASE_COUNT_MISMATCH"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def _two_case_bundle(self):
        queue = synthetic_queue()
        bundle = synthetic_bundle()
        case_q = copy.deepcopy(queue["cases"][0])
        case_b = copy.deepcopy(bundle["cases"][0])
        case_q["case_id"] = case_b["case_id"] = "SYNTHETIC_TEST_ONLY_CASE_2"
        case_q["source_case_sha256"] = case_b["source_case_sha256"] = "c" * 64
        queue["cases"].append(case_q)
        bundle["cases"].append(case_b)
        queue["counts"]["candidate_count"] = bundle["candidate_count"] = 2
        return queue, bundle

    def _submit_for_case(self, bundle, case_index, check_id, kind, ref, sha="d" * 64):
        slot = next(s for s in bundle["cases"][case_index]["submissions"]
                    if s["check_id"] == check_id)
        slot["status"] = "SUBMITTED_FOR_REVIEW"
        slot["artifacts"] = [{"evidence_ref": ref,
                              "evidence_sha256": sha, "evidence_type": kind}]

    def test_reused_ml_run_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "UPSTREAM_ML", "ML_RESULT", "SYNTHETIC_SHARED_RUN")
        with self.assertRaisesRegex(RealEvidenceSubmissionError,
                                    "SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_REUSE"):
            audit_evidence_submissions(queue, bundle)

    def test_reused_log_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "LOGS_CUTOFF", "DIAGNOSTIC_LOG", "SYNTHETIC_SHARED_LOG")
        with self.assertRaisesRegex(RealEvidenceSubmissionError,
                                    "SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_REUSE"):
            audit_evidence_submissions(queue, bundle)

    def test_reused_history_asof_receipt_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "HISTORY_ASOF", "HISTORY_ASOF_RETRIEVAL", "SYNTHETIC_SHARED_ASOF")
        with self.assertRaisesRegex(RealEvidenceSubmissionError,
                                    "SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_REUSE"):
            audit_evidence_submissions(queue, bundle)

    def test_reused_blind_review_request_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "BLIND_EXPERT", "BLIND_REVIEW_REQUEST", "SYNTHETIC_SHARED_REVIEW")
        with self.assertRaisesRegex(RealEvidenceSubmissionError,
                                    "SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_REUSE"):
            audit_evidence_submissions(queue, bundle)

    def test_same_ref_cannot_claim_two_evidence_types(self):
        bundle = synthetic_bundle()
        submit(bundle, "UPSTREAM_ML", ref="SYNTHETIC_MULTI_TYPE_REF")
        submit(bundle, "MISSION_CONTEXT", ref="SYNTHETIC_MULTI_TYPE_REF")
        with self.assertRaisesRegex(RealEvidenceSubmissionError,
                                    "SUBMISSION_EVIDENCE_REF_TYPE_CONFLICT"):
            audit_evidence_submissions(synthetic_queue(), bundle)

    def test_distinct_refs_with_identical_ml_digest_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(
                bundle, index, "UPSTREAM_ML", "ML_RESULT",
                "SYNTHETIC_CASE_SPECIFIC_REF_" + str(index), sha="d" * 64,
            )
        with self.assertRaisesRegex(
            RealEvidenceSubmissionError,
            "^SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_DIGEST_REUSE$",
        ):
            audit_evidence_submissions(queue, bundle)

    def test_identical_log_digest_under_distinct_refs_across_cases_rejected(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(
                bundle, index, "LOGS_CUTOFF", "DIAGNOSTIC_LOG",
                "SYNTHETIC_LOG_RECEIPT_" + str(index), sha="e" * 64,
            )
        with self.assertRaisesRegex(
            RealEvidenceSubmissionError,
            "^SUBMISSION_CROSS_CASE_SCOPED_EVIDENCE_DIGEST_REUSE$",
        ):
            audit_evidence_submissions(queue, bundle)

    def test_common_permission_receipt_may_cover_two_cases(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "SOURCE_RIGHTS",
                                  "SOURCE_PERMISSION_RECORD", "SYNTHETIC_SHARED_PERMISSION")
        result = audit_evidence_submissions(queue, bundle)
        self.assertEqual(result["submitted_for_review_by_dimension"]["SOURCE_RIGHTS"], 2)
        self.assertEqual(result["distinct_artifact_ref_count"], 1)
        self.assertEqual(result["evidence_verified_count"], 0)

    def test_distinct_case_specific_ml_receipts_remain_unverified(self):
        queue, bundle = self._two_case_bundle()
        for index in (0, 1):
            self._submit_for_case(bundle, index, "UPSTREAM_ML", "ML_RESULT",
                                  "SYNTHETIC_CASE_SCOPED_ML_" + str(index),
                                  sha=("d" if index == 0 else "e") * 64)
        result = audit_evidence_submissions(queue, bundle)
        self.assertEqual(result["submitted_for_review_by_dimension"]["UPSTREAM_ML"], 2)
        self.assertEqual(result["real_gold_count"], 0)
        self.assertFalse(result["training_authorized"])



if __name__ == "__main__":
    unittest.main()
