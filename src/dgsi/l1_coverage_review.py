"""SYNTHETIC_TEST_ONLY-safe L1 coverage and blinded-review metadata gates.

Only aggregate L1 packet metadata, not diagnostic text, IDs or reviewer identities.
This module does not approve Gold, SFT training, model fine-tuning or data splits.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .l1_task_packet import validate_l1_task_packet_collection


TASK_TYPES = (
    "diagnostic_synthesis",
    "historical_case_reuse",
    "conflict_reconciliation",
    "evidence_sufficiency",
    "next_step_recommendation",
    "handover_summary",
)
REVIEW_DIMENSIONS = (
    "fault_source",
    "affected_components",
    "evidence_fidelity",
    "uncertainty",
    "disposal_fidelity",
    "historical_context_transfer",
    "engineering_actionability",
)
TRACKS = ("REAL_CASE_CANDIDATE", "LITERATURE_DERIVED_SYNTHETIC")
DECISIONS = {"ACCEPT_L1", "REVISE", "REJECT"}
FINDING_CODES = {
    "NO_ISSUE",
    "SOURCE_FACT_OVERSTATEMENT",
    "FAULT_SOURCE_UNSUPPORTED",
    "AFFECTED_COMPONENT_MISMATCH",
    "EVIDENCE_REFERENCE_INVALID",
    "UNJUSTIFIED_CONFIDENCE",
    "HISTORICAL_TRANSFER_INVALID",
    "FUTURE_HISTORY_LEAK",
    "DISPOSAL_NOT_SOURCE_SUPPORTED",
    "CURATOR_PROMPT_LEAK",
    "SYNTHETIC_PROVENANCE_GAP",
    "OTHER_REQUIRES_SECURE_ADJUDICATION",
}


class L1QualityGateError(ValueError):
    """A fixed, payload-free audit code; no identifying metadata in errors."""


def _fail(code: str) -> None:
    raise L1QualityGateError(code)


def _history_bucket(packet: dict[str, Any]) -> str:
    context = packet["history_context"]
    if context["retrieval_status"] == "NO_HIT":
        return "NO_HIT"
    statuses = {item["outcome_status"] for item in context["items"]}
    if "CONFIRMED" in statuses and len(statuses) > 1:
        return "MIXED_CONFIRMED_AND_NONCONFIRMED"
    if len(statuses) > 1:
        return "MIXED_NONCONFIRMED"
    return next(iter(statuses)) + "_ONLY"


def audit_l1_coverage(
    collections: list[dict[str, Any]],
    *,
    source_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate collections and report *counts*, never packet/source identifiers.

    No training split is acceptable while independent review has not occurred.
    A review-status string alone cannot authenticate independent reviewers:
    separate blind-review receipts and secure adjudication are still required.
    """
    if not isinstance(collections, list) or not collections:
        _fail("L1_COVERAGE_COLLECTIONS_REQUIRED")
    seen_tasks: set[str] = set()
    tasks = Counter()
    tracks = Counter()
    history = Counter()
    family_sets: dict[str, set[str]] = {track: set() for track in TRACKS}
    not_reviewed = Counter()
    split_counts = Counter()

    for collection in collections:
        validate_l1_task_packet_collection(
            collection, source_fact_cards=source_fact_cards
        )
        track = collection["track"]
        packets = collection["packets"]
        has_unreviewed = (
            collection["data_status"] != "APPROVED_FOR_L1_EXPERIMENT"
            or any(p["review"]["status"] != "APPROVED_FOR_L1_EXPERIMENT" for p in packets)
        )
        if collection.get("split_assignments") and has_unreviewed:
            _fail("L1_SPLIT_BEFORE_INDEPENDENT_REVIEW")
        for packet in packets:
            task_id = packet["task_id"]
            if task_id in seen_tasks:
                _fail("L1_TASK_REUSED_ACROSS_COLLECTIONS")
            seen_tasks.add(task_id)
            task_type = packet["case"]["task_type"]
            if task_type not in TASK_TYPES:
                _fail("UNRECOGNIZED_L1_TASK_TYPE")
            tasks[task_type] += 1
            tracks[track] += 1
            family_sets[track].add(packet["case"]["provenance"]["source_group"])
            history[_history_bucket(packet)] += 1
            if packet["review"]["status"] != "APPROVED_FOR_L1_EXPERIMENT":
                not_reviewed[track] += 1
        split_counts[track] += len(collection.get("split_assignments", []))

    return {
        "schema_version": "dgsi-l1-coverage.v1",
        "decision": "METADATA_COVERAGE_ONLY",
        "collection_count": len(collections),
        "packet_count_by_track": {t: tracks[t] for t in TRACKS},
        "event_family_count_by_track": {t: len(family_sets[t]) for t in TRACKS},
        "unreviewed_count_by_track": {t: not_reviewed[t] for t in TRACKS},
        "split_assignment_count_by_track": {t: split_counts[t] for t in TRACKS},
        "task_coverage": {t: tasks[t] for t in TASK_TYPES},
        "uncovered_task_types": [t for t in TASK_TYPES if tasks[t] == 0],
        "history_context_coverage": dict(sorted(history.items())),
        "real_gold_count": 0,
        "training_authorized": False,
        "warning": "Coverage and review metadata never certify provenance or Gold eligibility.",
    }


def validate_blind_l1_review(
    form: dict[str, Any],
) -> dict[str, Any]:
    """Validate two independently submitted *blinded* scorecards.

    This is an audit of the rubric's completeness, not verification of who
    reviewed it. No packet content or reviewer identity is returned.
    """
    if not isinstance(form, dict) or set(form) != {
        "schema_version", "blinded_packet_ref", "assessments"
    } or form.get("schema_version") != "dgsi-l1-blind-review.v1":
        _fail("INVALID_BLIND_REVIEW_ENVELOPE")
    if not isinstance(form["blinded_packet_ref"], str) or not form["blinded_packet_ref"].strip():
        _fail("BLINDED_PACKET_REFERENCE_REQUIRED")
    assessments = form["assessments"]
    if not isinstance(assessments, list) or len(assessments) != 2:
        _fail("TWO_INDEPENDENT_ASSESSMENTS_REQUIRED")
    reviewer_tokens: set[str] = set()
    decisions: set[str] = set()
    scores_by_dimension: dict[str, list[int]] = {k: [] for k in REVIEW_DIMENSIONS}
    for item in assessments:
        if not isinstance(item, dict) or set(item) != {
            "reviewer_token", "scores", "finding_codes", "decision"
        }:
            _fail("INVALID_REVIEW_ASSESSMENT_STRUCTURE")
        token = item["reviewer_token"]
        if not isinstance(token, str) or not token.strip() or token in reviewer_tokens:
            _fail("REVIEWER_TOKENS_MUST_BE_DISTINCT")
        reviewer_tokens.add(token)
        if item["decision"] not in DECISIONS:
            _fail("INVALID_REVIEW_DECISION")
        decisions.add(item["decision"])
        scores = item["scores"]
        if not isinstance(scores, dict) or set(scores) != set(REVIEW_DIMENSIONS):
            _fail("INCOMPLETE_REVIEW_DIMENSIONS")
        for dimension, score in scores.items():
            if type(score) is not int or not 1 <= score <= 5:
                _fail("INVALID_REVIEW_SCORE")
            scores_by_dimension[dimension].append(score)
        codes = item["finding_codes"]
        if (not isinstance(codes, list) or not codes or
                any(not isinstance(c, str) or c not in FINDING_CODES for c in codes)):
            _fail("INVALID_REVIEW_FINDING_CODES")
        if len(codes) != len(set(codes)):
            _fail("DUPLICATE_REVIEW_FINDING_CODE")
    disagreements = sorted(
        d for d, pair in scores_by_dimension.items() if abs(pair[0] - pair[1]) >= 2
    )
    needs_adjudication = bool(disagreements) or len(decisions) > 1 or decisions != {"ACCEPT_L1"}
    return {
        "schema_version": "dgsi-l1-blind-review-audit.v1",
        "decision": "NEEDS_SECURE_ADJUDICATION" if needs_adjudication else "AWAITING_INDEPENDENT_REVIEWER_AUTHENTICATION",
        "reviewer_count": 2,
        "disagreement_dimension_count": len(disagreements),
        "disagreement_dimensions": disagreements,
        "gold_eligible": False,
        "training_authorized": False,
        "note": "No automatic Gold/L1 approval; verify identities, blinding and decisions outside this form.",
    }
