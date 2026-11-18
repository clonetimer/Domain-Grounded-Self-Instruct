"""SYNTHETIC_TEST_ONLY: two separate offline receipts never equal scientific admission."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_blind_review_manifest import build_l1_blind_review_manifest
from dgsi.l1_c2_joint_review_preflight import (
    C2JointReviewError, audit_c2_joint_review_against_current_sources,
)
from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_source_rights_queue import build_c2_source_rights_queue
from dgsi.l1_coverage_review import REVIEW_DIMENSIONS

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
SOURCES = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


def _fictional_submission(row):
    return {
        "schema_version": "dgsi-c2-scored-blind-review-submission.v1",
        "task_id": row["task_id"],
        "collection_projection_sha256": row["collection_projection_sha256"],
        "packet_sha256": row["packet_sha256"],
        "source_public_sha256": row["source_public_sha256"],
        "blind_review": {
            "schema_version": "dgsi-l1-blind-review.v1",
            "blinded_packet_ref": "sha256:" + row["packet_sha256"],
            "assessments": [
                {
                    "reviewer_token": "SYNTHETIC_TEST_ONLY_" + slot,
                    "scores": {dim: 5 for dim in REVIEW_DIMENSIONS},
                    "finding_codes": ["NO_ISSUE"],
                    "decision": "ACCEPT_L1",
                }
                for slot in ("A", "B")
            ],
        },
        "adjudication_status": "PENDING_REVIEWER_AUTHENTICATION",
    }


class JointCurrentCohortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dossier = build_c2_scientific_dossier(COLLECTION, source_fact_cards=SOURCES)
        cls.rights_blank = build_c2_source_rights_queue(dossier)
        cls.scored_manifest = build_l1_blind_review_manifest(
            COLLECTION, source_fact_cards=SOURCES
        )
        cls.scored_submissions = [
            {"task_id": row["task_id"], "submission": _fictional_submission(row)}
            for row in cls.scored_manifest["review_packets"]
        ]

    def _audit(self, rights_blank=None, rights_submission=None,
               scored_manifest=None, scored_submissions=None,
               collection=None, sources=None):
        return audit_c2_joint_review_against_current_sources(
            copy.deepcopy(self.rights_blank if rights_blank is None else rights_blank),
            copy.deepcopy(self.rights_blank if rights_submission is None
                          else rights_submission),
            copy.deepcopy(self.scored_manifest if scored_manifest is None
                          else scored_manifest),
            copy.deepcopy(self.scored_submissions if scored_submissions is None
                          else scored_submissions),
            copy.deepcopy(COLLECTION if collection is None else collection),
            copy.deepcopy(SOURCES if sources is None else sources),
        )

    def test_fifteen_tasks_and_seven_sources_still_unapproved(self):
        report = self._audit()
        self.assertEqual(report["science_packet_count"], 15)
        self.assertEqual(report["science_rubric_validated_count"], 15)
        self.assertEqual(report["source_document_count"], 7)
        self.assertTrue(report["current_public_source_snapshot_matched"])
        self.assertFalse(report["source_rights_verified"])
        self.assertFalse(report["scientific_expert_review_complete"])
        self.assertFalse(report["scientific_expert_identity_authenticated"])
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["gold_eligible"])
        self.assertTrue(report["not_for_sft"])
        self.assertEqual(report["sft_records_emitted"], 0)
        self.assertNotIn("SYNTHETIC_TEST_ONLY_A", json.dumps(report))

    def test_rights_blank_cannot_be_edited(self):
        changed = copy.deepcopy(self.rights_blank)
        changed["collection_projection_sha256"] = "a" * 64
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_RIGHTS_PREFLIGHT_REJECTED"
        ):
            self._audit(rights_blank=changed)

    def test_fake_legal_clearance_is_rejected(self):
        changed = copy.deepcopy(self.rights_blank)
        changed["source_documents"][0]["rights_cleared"] = True
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_RIGHTS_PREFLIGHT_REJECTED"
        ):
            self._audit(rights_submission=changed)

    def test_science_receipts_must_cover_full_cohort(self):
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_SCIENCE_PREFLIGHT_REJECTED"
        ):
            self._audit(scored_submissions=self.scored_submissions[:-1])

    def test_forged_science_source_hash_is_rejected(self):
        changed = copy.deepcopy(self.scored_manifest)
        changed["review_packets"][0]["source_public_sha256"] = "b" * 64
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_SCIENCE_PREFLIGHT_REJECTED"
        ):
            self._audit(scored_manifest=changed)

    def test_changed_l0_fact_invalidates_both_paths(self):
        sources = copy.deepcopy(SOURCES)
        sources[0]["phenomenon_analysis"] += " (SYNTHETIC_TEST_ONLY revision)"
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_RIGHTS_PREFLIGHT_REJECTED"
        ):
            self._audit(sources=sources)

    def test_invalid_shapes_have_content_free_error(self):
        with self.assertRaisesRegex(
            C2JointReviewError, "C2_JOINT_INPUT_SHAPE_INVALID"
        ):
            self._audit(scored_submissions={})

    def test_rights_evidence_digest_never_exposed_in_joined_report(self):
        changed = copy.deepcopy(self.rights_blank)
        evidence = "sha256:" + "c" * 64
        changed["source_documents"][0]["rights_review_status"] = (
            "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW"
        )
        changed["source_documents"][0]["license_or_permission_evidence_ref"] = evidence
        report = self._audit(rights_submission=changed)
        self.assertEqual(report["rights_evidence_referenced_document_count"], 1)
        self.assertNotIn(evidence, json.dumps(report))
        self.assertNotIn("reviewer_token", json.dumps(report))


if __name__ == "__main__":
    unittest.main()
