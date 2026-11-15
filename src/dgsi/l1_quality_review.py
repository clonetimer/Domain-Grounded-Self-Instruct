"""Structured expert review and non-Gold L1 quality scoring."""
from __future__ import annotations

from typing import Any

from .schema_validation import SchemaContractError, validate_payload_schema


class L1QualityReviewError(ValueError):
    """Stable review validation error without source payload details."""


_WEIGHTS = {
    "source_fidelity": 15,
    "phenomenon_analysis": 10,
    "ml_interpretation": 10,
    "localization": 15,
    "evidence": 15,
    "uncertainty": 10,
    "history_context": 10,
    "disposal_fidelity": 10,
    "follow_up_actions": 5,
}


def validate_l1_quality_review(review: dict[str, Any]) -> dict[str, Any]:
    """Validate one review and enforce rubric thresholds.

    This calculates L1 review disposition only. It never grants Gold status,
    authorizes training or certifies source authenticity.
    """
    if not isinstance(review, dict):
        raise L1QualityReviewError("L1_REVIEW_NOT_OBJECT")
    try:
        validate_payload_schema("l1_quality_review", review)
    except SchemaContractError as exc:
        raise L1QualityReviewError(str(exc)) from None

    scores = review["dimension_scores"]
    if set(scores) != set(_WEIGHTS):
        raise L1QualityReviewError("L1_REVIEW_DIMENSION_SET_MISMATCH")
    weighted = sum(_WEIGHTS[key] * scores[key] / 2 for key in _WEIGHTS)
    score = round(weighted, 2)
    if review["failed_gates"]:
        expected = "REJECT"
    elif score >= 90:
        expected = "ACCEPT_FOR_L1_EXPERIMENT"
    elif score >= 75:
        expected = "REVISE"
    else:
        expected = "REJECT"
    if review["review_outcome"] != expected:
        raise L1QualityReviewError("L1_REVIEW_OUTCOME_THRESHOLD_MISMATCH")

    return {
        "schema_version": "dgsi-l1-quality-review-result.v1",
        "task_id": review["task_id"],
        "track": review["track"],
        "weighted_score": score,
        "failed_gate_count": len(review["failed_gates"]),
        "review_outcome": expected,
        "gold_eligible": False,
        "training_authorized": False,
        "note": "L1 quality disposition only; Gold admission and training authorization are separate gates.",
    }
