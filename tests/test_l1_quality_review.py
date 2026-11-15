"""Synthetic-only tests for the L1 quality review rubric."""
from __future__ import annotations

import copy
import unittest

from dgsi.l1_quality_review import L1QualityReviewError, validate_l1_quality_review


_BASE = {
    "schema_version": "dgsi-l1-quality-review.v1",
    "task_id": "SYNTH-L1-REVIEW-001",
    "packet_sha256": "a" * 64,
    "track": "LITERATURE_DERIVED_SYNTHETIC",
    "reviewer_pseudonym": "SYNTHETIC-REVIEWER-A",
    "reviewer_role": "DOMAIN_EXPERT",
    "reviewed_at": "2026-11-15T14:00:00Z",
    "dimension_scores": {
        "source_fidelity": 2,
        "phenomenon_analysis": 2,
        "ml_interpretation": 2,
        "localization": 2,
        "evidence": 2,
        "uncertainty": 2,
        "history_context": 2,
        "disposal_fidelity": 2,
        "follow_up_actions": 2,
    },
    "dimension_rationales": {
        "source_fidelity": "Synthetic source boundary is explicit.",
        "phenomenon_analysis": "Observed symptoms are separated from cause.",
        "ml_interpretation": "Candidate score is not described as probability.",
        "localization": "Fault source and affected interfaces are separate.",
        "evidence": "Claims resolve to evidence IDs.",
        "uncertainty": "Candidate status is retained.",
        "history_context": "History is qualified and time-safe.",
        "disposal_fidelity": "No unrecorded action is invented.",
        "follow_up_actions": "Checks address missing evidence.",
    },
    "failed_gates": [],
    "review_outcome": "ACCEPT_FOR_L1_EXPERIMENT",
    "gold_eligible": False,
    "adjudication_note": None,
}


class L1QualityReviewTests(unittest.TestCase):
    def test_high_quality_review_is_accepted_for_l1_experiment_only(self):
        result = validate_l1_quality_review(copy.deepcopy(_BASE))
        self.assertEqual(result["weighted_score"], 100.0)
        self.assertEqual(result["review_outcome"], "ACCEPT_FOR_L1_EXPERIMENT")
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])

    def test_automatic_rejection_gate_overrides_high_numeric_score(self):
        review = copy.deepcopy(_BASE)
        review["failed_gates"] = ["SYNTHETIC_AS_REAL"]
        review["review_outcome"] = "REJECT"
        result = validate_l1_quality_review(review)
        self.assertEqual(result["weighted_score"], 100.0)
        self.assertEqual(result["review_outcome"], "REJECT")

    def test_mid_score_requires_revision(self):
        review = copy.deepcopy(_BASE)
        review["dimension_scores"]["source_fidelity"] = 1
        review["dimension_scores"]["evidence"] = 1
        review["review_outcome"] = "REVISE"
        result = validate_l1_quality_review(review)
        self.assertGreaterEqual(result["weighted_score"], 75)
        self.assertLess(result["weighted_score"], 90)
        self.assertEqual(result["review_outcome"], "REVISE")

    def test_low_score_requires_rejection(self):
        review = copy.deepcopy(_BASE)
        review["dimension_scores"] = {key: 0 for key in review["dimension_scores"]}
        review["review_outcome"] = "REJECT"
        result = validate_l1_quality_review(review)
        self.assertEqual(result["weighted_score"], 0.0)
        self.assertEqual(result["review_outcome"], "REJECT")

    def test_outcome_cannot_disagree_with_threshold(self):
        review = copy.deepcopy(_BASE)
        review["review_outcome"] = "REVISE"
        with self.assertRaisesRegex(L1QualityReviewError, "L1_REVIEW_OUTCOME_THRESHOLD_MISMATCH"):
            validate_l1_quality_review(review)

    def test_review_cannot_claim_gold_eligibility(self):
        review = copy.deepcopy(_BASE)
        review["gold_eligible"] = True
        with self.assertRaises(L1QualityReviewError):
            validate_l1_quality_review(review)

    def test_missing_dimension_rationale_is_rejected(self):
        review = copy.deepcopy(_BASE)
        del review["dimension_rationales"]["evidence"]
        with self.assertRaises(L1QualityReviewError):
            validate_l1_quality_review(review)

    def test_bad_packet_hash_is_rejected(self):
        review = copy.deepcopy(_BASE)
        review["packet_sha256"] = "not-a-hash"
        with self.assertRaises(L1QualityReviewError):
            validate_l1_quality_review(review)


if __name__ == "__main__":
    unittest.main()
