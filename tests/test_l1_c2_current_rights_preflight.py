"""SYNTHETIC_TEST_ONLY: old self-consistent rights worksheets are not current."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_c2_current_rights_preflight import (
    audit_c2_rights_intake_against_current_sources,
)
from dgsi.l1_c2_rights_intake_audit import C2SourceRightsIntakeError
from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_source_rights_queue import build_c2_source_rights_queue

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
SOURCES = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


class C2CurrentRightsPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dossier = build_c2_scientific_dossier(COLLECTION, source_fact_cards=SOURCES)
        cls.blank = build_c2_source_rights_queue(dossier)

    def _check(self, blank=None, submission=None, collection=None, sources=None):
        return audit_c2_rights_intake_against_current_sources(
            copy.deepcopy(self.blank if blank is None else blank),
            copy.deepcopy(self.blank if submission is None else submission),
            copy.deepcopy(COLLECTION if collection is None else collection),
            copy.deepcopy(SOURCES if sources is None else sources),
        )

    def test_current_unfilled_cohort_remains_review_only(self):
        result = self._check()
        self.assertTrue(result["current_public_source_snapshot_matched"])
        self.assertEqual(result["distinct_source_document_count"], 7)
        self.assertEqual(result["rights_cleared_document_count"], 0)
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["source_rights_verified"])

    def test_old_blank_rejected_when_current_l0_fact_changes(self):
        modified = copy.deepcopy(SOURCES)
        modified[0]["phenomenon_analysis"] += " (new review-only correction)"
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_INTAKE_STALE_OR_TAMPERED_BLANK"):
            self._check(sources=modified)

    def test_changed_cohort_projection_in_blank_rejected(self):
        blank = copy.deepcopy(self.blank)
        blank["collection_projection_sha256"] = "b" * 64
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_INTAKE_STALE_OR_TAMPERED_BLANK"):
            self._check(blank=blank)

    def test_reordered_or_reassigned_source_document_rejected(self):
        blank = copy.deepcopy(self.blank)
        blank["source_documents"][0]["event_families"] = ["FORGED_FAMILY"]
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_INTAKE_STALE_OR_TAMPERED_BLANK"):
            self._check(blank=blank)

    def test_submitted_evidence_still_cannot_approve_rights_or_sft(self):
        submission = copy.deepcopy(self.blank)
        submission["source_documents"][0]["rights_review_status"] = (
            "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW"
        )
        evidence = "sha256:" + "b" * 64
        submission["source_documents"][0]["license_or_permission_evidence_ref"] = evidence
        result = self._check(submission=submission)
        self.assertEqual(result["referenced_evidence_document_count"], 1)
        self.assertFalse(result["source_rights_verified"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn(evidence, json.dumps(result))

    def test_unauthenticated_clearance_still_rejected(self):
        submission = copy.deepcopy(self.blank)
        submission["source_documents"][0]["rights_cleared"] = True
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_INTAKE_FALSE_CLEARANCE"):
            self._check(submission=submission)

    def test_bad_current_source_payload_cannot_pass(self):
        with self.assertRaisesRegex(C2SourceRightsIntakeError,
                                    "C2_RIGHTS_CURRENT_SOURCE_SNAPSHOT_INVALID"):
            self._check(sources={"cards": []})


if __name__ == "__main__":
    unittest.main()
