"""SYNTHETIC_TEST_ONLY: no offline rights form authenticates reuse rights."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_source_rights_queue import build_c2_source_rights_queue
from dgsi.l1_c2_rights_intake_audit import (
    C2SourceRightsIntakeError, audit_c2_source_rights_intake,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
SOURCES = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]
EVIDENCE_REF = "sha256:" + "a" * 64


class C2RightsIntakeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dossier = build_c2_scientific_dossier(COLLECTION, source_fact_cards=SOURCES)
        cls.blank = build_c2_source_rights_queue(dossier)

    def _submission(self):
        return copy.deepcopy(self.blank)

    def test_unfilled_seven_document_queue_stays_blocked(self):
        report = audit_c2_source_rights_intake(self.blank, self._submission())
        self.assertEqual(report["distinct_source_document_count"], 7)
        self.assertEqual(report["referenced_evidence_document_count"], 0)
        self.assertEqual(report["rights_cleared_document_count"], 0)
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["source_rights_verified"])

    def test_evidence_submitted_does_not_grant_permission_or_training(self):
        submitted = self._submission()
        doc = submitted["source_documents"][0]
        doc["rights_review_status"] = "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW"
        doc["license_or_permission_evidence_ref"] = EVIDENCE_REF
        report = audit_c2_source_rights_intake(self.blank, submitted)
        self.assertEqual(report["referenced_evidence_document_count"], 1)
        self.assertEqual(
            report["status_counts"]["EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW"], 1
        )
        self.assertFalse(report["source_rights_verified"])
        self.assertFalse(report["training_authorized"])
        self.assertNotIn(EVIDENCE_REF, json.dumps(report))

    def test_explicit_denial_is_not_a_clearance(self):
        submitted = self._submission()
        doc = submitted["source_documents"][0]
        doc["rights_review_status"] = "REUSE_DENIED"
        doc["rights_decision"] = "DENIED"
        report = audit_c2_source_rights_intake(self.blank, submitted)
        self.assertEqual(report["status_counts"]["REUSE_DENIED"], 1)
        self.assertEqual(report["rights_cleared_document_count"], 0)

    def test_stale_cohort_fingerprint_rejected(self):
        submitted = self._submission()
        submitted["collection_projection_sha256"] = "b" * 64
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_INTAKE_COHORT_OR_FLAGS_DRIFT"):
            audit_c2_source_rights_intake(self.blank, submitted)

    def test_document_binding_or_episode_tamper_rejected(self):
        for field, altered in (
            ("source_title", "FORGED DOCUMENT"),
            ("source_url", "https://example.invalid/forged"),
            ("event_families", ["FORGED-FAMILY"]),
            ("bound_l0_fact_bindings", []),
        ):
            submitted = self._submission()
            submitted["source_documents"][0][field] = altered
            with self.subTest(field=field), self.assertRaisesRegex(
                C2SourceRightsIntakeError, "C2_RIGHTS_INTAKE_DOCUMENT_BINDING_DRIFT"
            ):
                audit_c2_source_rights_intake(self.blank, submitted)

    def test_duplicate_or_missing_source_rejected(self):
        submitted = self._submission()
        submitted["source_documents"].append(
            copy.deepcopy(submitted["source_documents"][0])
        )
        with self.assertRaises(C2SourceRightsIntakeError):
            audit_c2_source_rights_intake(self.blank, submitted)
        submitted = self._submission()
        submitted["source_documents"].pop()
        with self.assertRaisesRegex(
            C2SourceRightsIntakeError, "C2_RIGHTS_INTAKE_DOCUMENT_COUNT_DRIFT"
        ):
            audit_c2_source_rights_intake(self.blank, submitted)

    def test_unverified_claimed_clearance_scope_or_permission_rejected(self):
        for field, altered in (
            ("rights_cleared", True),
            ("permitted_reuse_scope", ["MODEL_TRAINING"]),
            ("rights_decision", "PERMITTED"),
        ):
            submitted = self._submission()
            submitted["source_documents"][0][field] = altered
            with self.subTest(field=field), self.assertRaises(C2SourceRightsIntakeError):
                audit_c2_source_rights_intake(self.blank, submitted)

    def test_missing_or_unverifiable_evidence_ref_rejected(self):
        for value in (None, "https://private.invalid/record", "sha256:bad"):
            submitted = self._submission()
            doc = submitted["source_documents"][0]
            doc["rights_review_status"] = "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW"
            doc["license_or_permission_evidence_ref"] = value
            with self.subTest(value=value), self.assertRaises(C2SourceRightsIntakeError):
                audit_c2_source_rights_intake(self.blank, submitted)

    def test_top_level_training_claim_and_private_metadata_rejected(self):
        submitted = self._submission()
        submitted["training_authorized"] = True
        with self.assertRaises(C2SourceRightsIntakeError):
            audit_c2_source_rights_intake(self.blank, submitted)
        submitted = self._submission()
        submitted["source_documents"][0]["private_reviewer_token"] = "SECRET"
        with self.assertRaises(C2SourceRightsIntakeError):
            audit_c2_source_rights_intake(self.blank, submitted)


if __name__ == "__main__":
    unittest.main()
