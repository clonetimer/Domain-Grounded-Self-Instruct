"""SYNTHETIC_TEST_ONLY: scored ten-dimension reviews bound to a C2 cohort."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_blind_review_manifest import (
    L1BlindReviewManifestError, build_l1_blind_review_manifest,
)
from dgsi.l1_c2_scored_review import (
    audit_c2_scored_review, audit_c2_scored_review_batch,
)
from dgsi.l1_coverage_review import REVIEW_DIMENSIONS

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
CARDS = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


def _submission(entry):
    """Fictional review tokens and scores, NEVER a real expert claim."""
    return {
        "schema_version": "dgsi-c2-scored-blind-review-submission.v1",
        "task_id": entry["task_id"],
        "collection_projection_sha256": entry["collection_projection_sha256"],
        "packet_sha256": entry["packet_sha256"],
        "source_public_sha256": entry["source_public_sha256"],
        "blind_review": {
            "schema_version": "dgsi-l1-blind-review.v1",
            "blinded_packet_ref": "sha256:" + entry["packet_sha256"],
            "assessments": [
                {
                    "reviewer_token": f"SYNTHETIC_TEST_ONLY_{slot}",
                    "scores": {dimension: 5 for dimension in REVIEW_DIMENSIONS},
                    "finding_codes": ["NO_ISSUE"],
                    "decision": "ACCEPT_L1",
                }
                for slot in ("A", "B")
            ],
        },
        "adjudication_status": "PENDING_REVIEWER_AUTHENTICATION",
    }


class CohortBoundScoredReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_l1_blind_review_manifest(
            COLLECTION, source_fact_cards=CARDS
        )
        cls.entry = cls.manifest["review_packets"][0]

    def test_scored_acceptance_is_not_expert_authentication_or_training(self):
        result = audit_c2_scored_review(self.entry, _submission(self.entry))
        self.assertEqual(result["dimension_count"], 10)
        self.assertEqual(result["reviewer_count"], 2)
        self.assertEqual(
            result["adjudication_status"], "PENDING_REVIEWER_AUTHENTICATION"
        )
        self.assertFalse(result["expert_adjudicated"])
        self.assertFalse(result["identity_authenticated"])
        self.assertFalse(result["source_rights_verified"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertEqual(result["sft_records_emitted"], 0)
        self.assertNotIn("reviewer_token", json.dumps(result))

    def test_reject_missing_one_of_ten_dimensions(self):
        submission = _submission(self.entry)
        del submission["blind_review"]["assessments"][0]["scores"]["fault_source"]
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "INCOMPLETE_REVIEW_DIMENSIONS"
        ):
            audit_c2_scored_review(self.entry, submission)

    def test_reject_stale_collection_with_unchanged_packet(self):
        submission = _submission(self.entry)
        submission["collection_projection_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_STALE_COLLECTION"
        ):
            audit_c2_scored_review(self.entry, submission)

    def test_reject_stale_packet_or_source_and_wrong_task(self):
        for field, code in (
            ("packet_sha256", "C2_SCORED_REVIEW_STALE_PACKET"),
            ("source_public_sha256", "C2_SCORED_REVIEW_STALE_SOURCE"),
            ("task_id", "C2_SCORED_REVIEW_TASK_DRIFT"),
        ):
            with self.subTest(field=field):
                submission = _submission(self.entry)
                submission[field] = "0" * 64 if field != "task_id" else "WRONG_TASK"
                with self.assertRaisesRegex(L1BlindReviewManifestError, code):
                    audit_c2_scored_review(self.entry, submission)

    def test_reject_blind_ref_to_other_packet(self):
        submission = _submission(self.entry)
        submission["blind_review"]["blinded_packet_ref"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_BLIND_REFERENCE_MISMATCH"
        ):
            audit_c2_scored_review(self.entry, submission)

    def test_reject_duplicate_reviewer_tokens_and_wrong_pending_state(self):
        submission = _submission(self.entry)
        submission["blind_review"]["assessments"][1]["reviewer_token"] = (
            " " + submission["blind_review"]["assessments"][0]["reviewer_token"] + " "
        )
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "REVIEWER_TOKENS_MUST_BE_DISTINCT"
        ):
            audit_c2_scored_review(self.entry, submission)
        submission = _submission(self.entry)
        submission["adjudication_status"] = "APPROVED"
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_ADJUDICATION_STATE_INVALID"
        ):
            audit_c2_scored_review(self.entry, submission)

    def test_disagreement_requires_secure_adjudication(self):
        submission = _submission(self.entry)
        submission["blind_review"]["assessments"][1]["scores"]["uncertainty"] = 3
        submission["adjudication_status"] = "PENDING_SECURE_ADJUDICATION"
        result = audit_c2_scored_review(self.entry, submission)
        self.assertEqual(result["decision"], "NEEDS_SECURE_ADJUDICATION")
        self.assertEqual(result["disagreement_dimension_count"], 1)
        self.assertFalse(result["training_authorized"])

    def test_substantive_finding_never_turns_into_acceptance(self):
        submission = _submission(self.entry)
        submission["blind_review"]["assessments"][0]["finding_codes"] = [
            "UNJUSTIFIED_CONFIDENCE"
        ]
        submission["adjudication_status"] = "PENDING_SECURE_ADJUDICATION"
        result = audit_c2_scored_review(self.entry, submission)
        self.assertEqual(result["decision"], "NEEDS_SECURE_ADJUDICATION")
        self.assertFalse(result["expert_adjudicated"])

    def test_all_fifteen_scored_test_receipts_still_not_admitted(self):
        submissions = [
            {"task_id": entry["task_id"], "submission": _submission(entry)}
            for entry in self.manifest["review_packets"]
        ]
        audit = audit_c2_scored_review_batch(self.manifest, submissions)
        self.assertEqual(audit["packet_count"], 15)
        self.assertEqual(audit["ten_dimension_rubric_validated_count"], 15)
        self.assertEqual(audit["expert_adjudicated_count"], 0)
        self.assertFalse(audit["training_authorized"])
        self.assertFalse(audit["gold_eligible"])
        self.assertEqual(audit["sft_records_emitted"], 0)
        self.assertNotIn("reviewer_token", json.dumps(audit))

    def test_batch_cannot_drop_or_duplicate_task(self):
        submissions = [
            {"task_id": entry["task_id"], "submission": _submission(entry)}
            for entry in self.manifest["review_packets"]
        ]
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_BATCH_INCOMPLETE"
        ):
            audit_c2_scored_review_batch(self.manifest, submissions[:-1])
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_BATCH_DUPLICATE_SUBMISSION"
        ):
            audit_c2_scored_review_batch(self.manifest, submissions + [submissions[0]])

    def test_batch_rejects_edited_cohort_digest_without_changing_task(self):
        submissions = [
            {"task_id": entry["task_id"], "submission": _submission(entry)}
            for entry in self.manifest["review_packets"]
        ]
        altered = copy.deepcopy(self.manifest)
        altered["collection_projection_sha256"] = "0" * 64
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_BATCH_COHORT_BINDING_INVALID"
        ):
            audit_c2_scored_review_batch(altered, submissions)


if __name__ == "__main__":
    unittest.main()
