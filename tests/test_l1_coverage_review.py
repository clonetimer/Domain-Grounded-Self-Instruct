"""SYNTHETIC_TEST_ONLY: L1 coverage and independent blind-review metadata gates."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import L1TaskPacketError, validate_l1_task_packet_collection
from dgsi.l1_coverage_review import (
    L1QualityGateError,
    REVIEW_DIMENSIONS,
    audit_l1_coverage,
    validate_blind_l1_review,
)

ROOT = Path(__file__).resolve().parents[1]


def _pilot():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


def _blind_form():
    return {
        "schema_version": "dgsi-l1-blind-review.v1",
        "blinded_packet_ref": "SYNTHETIC-BLIND-TOKEN-001",
        "assessments": [
            {
                "reviewer_token": token,
                "scores": {dimension: 4 for dimension in REVIEW_DIMENSIONS},
                "finding_codes": ["NO_ISSUE"],
                "decision": "ACCEPT_L1",
            }
            for token in ("SYNTHETIC-REVIEWER-A", "SYNTHETIC-REVIEWER-B")
        ],
    }


class L1CoverageReviewTests(unittest.TestCase):
    def test_pilot_coverage_is_aggregate_and_separate_from_real_gold(self):
        collection, cards = _pilot()
        out = audit_l1_coverage([collection], source_fact_cards=cards)
        self.assertEqual(out["packet_count_by_track"]["LITERATURE_DERIVED_SYNTHETIC"], 15)
        self.assertEqual(out["packet_count_by_track"]["REAL_CASE_CANDIDATE"], 0)
        self.assertEqual(out["event_family_count_by_track"]["LITERATURE_DERIVED_SYNTHETIC"], 9)
        self.assertEqual(out["task_coverage"]["diagnostic_synthesis"], 10)
        self.assertEqual(out["task_coverage"]["conflict_reconciliation"], 1)
        self.assertEqual(out["task_coverage"]["historical_case_reuse"], 1)
        self.assertEqual(out["task_coverage"]["evidence_sufficiency"], 1)
        self.assertEqual(out["task_coverage"]["next_step_recommendation"], 1)
        self.assertEqual(out["task_coverage"]["handover_summary"], 1)
        self.assertEqual(out["history_context_coverage"]["NO_HIT"], 12)
        self.assertEqual(out["history_context_coverage"]["REJECTED_ONLY"], 2)
        self.assertEqual(out["history_context_coverage"]["PARTIALLY_CONFIRMED_ONLY"], 1)
        self.assertEqual(out["real_gold_count"], 0)
        self.assertEqual(out["unreviewed_count_by_track"]["LITERATURE_DERIVED_SYNTHETIC"], 15)
        self.assertEqual(
            out["source_fact_domain_review_status_by_track"]["LITERATURE_DERIVED_SYNTHETIC"]
            ["AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION"],
            12,
        )
        self.assertFalse(out["training_authorized"])
        self.assertNotIn(collection["packets"][0]["task_id"], repr(out))

    def test_unreviewed_packets_cannot_receive_formal_split_assignments(self):
        collection, cards = _pilot()
        collection["split_assignments"] = [
            {"task_id": p["task_id"], "split": "train"} for p in collection["packets"]
        ]
        with self.assertRaisesRegex(L1QualityGateError, "L1_SPLIT_BEFORE_INDEPENDENT_REVIEW"):
            audit_l1_coverage([collection], source_fact_cards=cards)

    def test_canonical_collection_validator_blocks_review_required_split(self):
        collection, cards = _pilot()
        collection["split_assignments"] = [
            {"task_id": p["task_id"], "split": "train"} for p in collection["packets"]
        ]
        with self.assertRaisesRegex(L1TaskPacketError, "L1_SPLIT_BEFORE_INDEPENDENT_REVIEW"):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_cross_collection_duplicate_task_is_blocked(self):
        collection, cards = _pilot()
        other = copy.deepcopy(collection)
        other["collection_id"] = "SYNTHETIC-OTHER-COLLECTION"
        with self.assertRaisesRegex(L1QualityGateError, "L1_TASK_REUSED_ACROSS_COLLECTIONS"):
            audit_l1_coverage([collection, other], source_fact_cards=cards)

    def test_no_collections_fail_closed(self):
        with self.assertRaisesRegex(L1QualityGateError, "L1_COVERAGE_COLLECTIONS_REQUIRED"):
            audit_l1_coverage([], source_fact_cards=[])

    def test_two_blinded_reviewers_are_required(self):
        form = _blind_form()
        form["assessments"].pop()
        with self.assertRaisesRegex(L1QualityGateError, "TWO_INDEPENDENT_ASSESSMENTS_REQUIRED"):
            validate_blind_l1_review(form)

    def test_duplicate_reviewer_token_is_blocked(self):
        form = _blind_form()
        form["assessments"][1]["reviewer_token"] = form["assessments"][0]["reviewer_token"]
        with self.assertRaisesRegex(L1QualityGateError, "REVIEWER_TOKENS_MUST_BE_DISTINCT"):
            validate_blind_l1_review(form)

    def test_valid_review_does_not_approve_gold_or_training(self):
        out = validate_blind_l1_review(_blind_form())
        self.assertEqual(out["reviewer_count"], 2)
        self.assertEqual(out["decision"], "AWAITING_INDEPENDENT_REVIEWER_AUTHENTICATION")
        self.assertFalse(out["gold_eligible"])
        self.assertFalse(out["training_authorized"])

    def test_blinded_review_rejects_missing_dimension(self):
        form = _blind_form()
        del form["assessments"][0]["scores"]["disposal_fidelity"]
        with self.assertRaisesRegex(L1QualityGateError, "INCOMPLETE_REVIEW_DIMENSIONS"):
            validate_blind_l1_review(form)

    def test_invalid_score_and_boolean_score_fail_closed(self):
        for score in (0, 6, True, "5"):
            form = _blind_form()
            form["assessments"][0]["scores"]["fault_source"] = score
            with self.subTest(score=score), self.assertRaisesRegex(L1QualityGateError, "INVALID_REVIEW_SCORE"):
                validate_blind_l1_review(form)

    def test_review_disagreement_requires_adjudication(self):
        form = _blind_form()
        form["assessments"][0]["scores"]["fault_source"] = 1
        form["assessments"][0]["finding_codes"] = ["FAULT_SOURCE_UNSUPPORTED"]
        out = validate_blind_l1_review(form)
        self.assertEqual(out["decision"], "NEEDS_SECURE_ADJUDICATION")
        self.assertEqual(out["disagreement_dimensions"], ["fault_source"])

    def test_review_decision_disagreement_requires_adjudication(self):
        form = _blind_form()
        form["assessments"][1]["decision"] = "REVISE"
        out = validate_blind_l1_review(form)
        self.assertEqual(out["decision"], "NEEDS_SECURE_ADJUDICATION")

    def test_unknown_findings_and_extra_free_text_are_rejected(self):
        form = _blind_form()
        form["assessments"][0]["finding_codes"] = ["SECRET:diagnostic-case-body"]
        with self.assertRaisesRegex(L1QualityGateError, "INVALID_REVIEW_FINDING_CODES"):
            validate_blind_l1_review(form)
        form = _blind_form()
        form["assessments"][0]["private_text"] = "DO NOT COPY TO REPO"
        with self.assertRaisesRegex(L1QualityGateError, "INVALID_REVIEW_ASSESSMENT_STRUCTURE"):
            validate_blind_l1_review(form)


if __name__ == "__main__":
    unittest.main()
