"""SYNTHETIC_TEST_ONLY: current-cohort scored receipts cannot inherit stale review."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_blind_review_manifest import (
    L1BlindReviewManifestError,
    build_l1_blind_review_manifest,
)
from dgsi.l1_c2_current_scored_review_preflight import (
    audit_c2_scored_review_against_current_sources,
)
from dgsi.l1_coverage_review import REVIEW_DIMENSIONS

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
SOURCES = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


def _fictional_submission(entry):
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
                    "scores": {key: 5 for key in REVIEW_DIMENSIONS},
                    "finding_codes": ["NO_ISSUE"],
                    "decision": "ACCEPT_L1",
                }
                for slot in ("A", "B")
            ],
        },
        "adjudication_status": "PENDING_REVIEWER_AUTHENTICATION",
    }


class C2CurrentScoredReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_l1_blind_review_manifest(
            COLLECTION, source_fact_cards=SOURCES
        )
        cls.submissions = [
            {"task_id": row["task_id"], "submission": _fictional_submission(row)}
            for row in cls.manifest["review_packets"]
        ]

    def _audit(self, manifest=None, submissions=None, collection=None, sources=None):
        return audit_c2_scored_review_against_current_sources(
            copy.deepcopy(self.manifest if manifest is None else manifest),
            copy.deepcopy(self.submissions if submissions is None else submissions),
            copy.deepcopy(COLLECTION if collection is None else collection),
            copy.deepcopy(SOURCES if sources is None else sources),
        )

    def test_all_fifteen_synthetic_receipts_remain_review_only(self):
        report = self._audit()
        self.assertTrue(report["current_public_source_snapshot_matched"])
        self.assertEqual(report["packet_count"], 15)
        self.assertEqual(report["ten_dimension_rubric_validated_count"], 15)
        self.assertEqual(report["expert_adjudicated_count"], 0)
        for key in ("identity_authenticated", "source_rights_verified",
                    "expert_review_complete", "training_authorized",
                    "gold_eligible", "official_splits_assigned"):
            self.assertIs(report[key], False)
        self.assertEqual(report["sft_records_emitted"], 0)
        self.assertNotIn("SYNTHETIC_TEST_ONLY_A", json.dumps(report))

    def test_old_manifest_rejected_after_l0_fact_revision(self):
        sources = copy.deepcopy(SOURCES)
        sources[0]["phenomenon_analysis"] += " (SYNTHETIC_TEST_ONLY source correction)"
        with self.assertRaisesRegex(
            L1BlindReviewManifestError,
            "C2_SCORED_STALE_OR_TAMPERED_COORDINATOR_MANIFEST",
        ):
            self._audit(sources=sources)

    def test_old_manifest_rejected_after_l1_instruction_revision(self):
        changed = copy.deepcopy(COLLECTION)
        changed["packets"][0]["case"]["instruction"] += " (SYNTHETIC_TEST_ONLY)"
        with self.assertRaisesRegex(
            L1BlindReviewManifestError,
            "C2_SCORED_STALE_OR_TAMPERED_COORDINATOR_MANIFEST",
        ):
            self._audit(collection=changed)

    def test_cohort_binding_tamper_rejected(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["review_packets"][0]["source_fact_bindings"][0][
            "public_fact_sha256"
        ] = "a" * 64
        with self.assertRaisesRegex(
            L1BlindReviewManifestError,
            "C2_SCORED_STALE_OR_TAMPERED_COORDINATOR_MANIFEST",
        ):
            self._audit(manifest=manifest)

    def test_manifest_count_or_decision_flag_tamper_rejected(self):
        for field, new_value in (
            ("packet_count", 14),
            ("training_authorized", True),
            ("decision", "EXPERT_APPROVED"),
        ):
            with self.subTest(field=field):
                manifest = copy.deepcopy(self.manifest)
                manifest[field] = new_value
                with self.assertRaisesRegex(
                    L1BlindReviewManifestError,
                    "C2_SCORED_STALE_OR_TAMPERED_COORDINATOR_MANIFEST",
                ):
                    self._audit(manifest=manifest)

    def test_incomplete_receipts_never_treated_as_reviewed(self):
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_REVIEW_BATCH_INCOMPLETE"
        ):
            self._audit(submissions=self.submissions[:-1])

    def test_bad_current_source_snapshot_is_blocked(self):
        with self.assertRaisesRegex(
            L1BlindReviewManifestError, "C2_SCORED_CURRENT_SOURCE_SNAPSHOT_INVALID"
        ):
            self._audit(sources={"cards": []})


if __name__ == "__main__":
    unittest.main()
