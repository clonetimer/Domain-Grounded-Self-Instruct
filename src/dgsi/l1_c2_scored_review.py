"""Bind the *existing* ten-dimension blind review rubric to the C2 cohort.

This is a structural, metadata-only preflight. It does not verify human
independence, source rights or scientific truth and never authorizes training.
Detailed reviews must remain in an access-controlled workspace.
"""
from __future__ import annotations

import re
from typing import Any

from .l1_blind_review_manifest import L1BlindReviewManifestError
from .l1_coverage_review import (
    L1QualityGateError, REVIEW_DIMENSIONS, validate_blind_l1_review,
)

_SHA256 = re.compile(r"^[a-f0-9]{64}$")
_VERSION = "dgsi-c2-scored-blind-review-submission.v1"


def _fail(code: str) -> None:
    raise L1BlindReviewManifestError(code)


def audit_c2_scored_review(
    entry: dict[str, Any], submission: dict[str, Any]
) -> dict[str, Any]:
    """Check a scored pair against the same task, sources and whole cohort.

    The simpler two-recommendation manifest check is not a scientific rubric.
    This explicit bridge calls the *only* selected 10-dimension validator.
    """
    required = {
        "schema_version", "task_id", "collection_projection_sha256",
        "packet_sha256", "source_public_sha256", "blind_review",
        "adjudication_status",
    }
    if not isinstance(entry, dict) or not isinstance(submission, dict):
        _fail("C2_SCORED_REVIEW_SHAPE_INVALID")
    if set(submission) != required or submission.get("schema_version") != _VERSION:
        _fail("C2_SCORED_REVIEW_ENVELOPE_INVALID")
    if not isinstance(entry.get("task_id"), str) or not entry["task_id"]:
        _fail("C2_SCORED_REVIEW_ENTRY_TASK_INVALID")
    if submission["task_id"] != entry["task_id"]:
        _fail("C2_SCORED_REVIEW_TASK_DRIFT")

    for field, code in (
        ("collection_projection_sha256", "C2_SCORED_REVIEW_STALE_COLLECTION"),
        ("packet_sha256", "C2_SCORED_REVIEW_STALE_PACKET"),
        ("source_public_sha256", "C2_SCORED_REVIEW_STALE_SOURCE"),
    ):
        expected = entry.get(field)
        if not isinstance(expected, str) or not _SHA256.fullmatch(expected):
            _fail("C2_SCORED_REVIEW_ENTRY_FINGERPRINT_INVALID")
        if submission[field] != expected:
            _fail(code)

    form = submission["blind_review"]
    if not isinstance(form, dict) or form.get("blinded_packet_ref") != (
        "sha256:" + entry["packet_sha256"]
    ):
        _fail("C2_SCORED_REVIEW_BLIND_REFERENCE_MISMATCH")
    try:
        result = validate_blind_l1_review(form)
    except L1QualityGateError as exc:
        # Only fixed-code validator errors; no scorecard text or reviewer token.
        _fail(str(exc))
    state = (
        "PENDING_SECURE_ADJUDICATION"
        if result["decision"] == "NEEDS_SECURE_ADJUDICATION"
        else "PENDING_REVIEWER_AUTHENTICATION"
    )
    if submission["adjudication_status"] != state:
        _fail("C2_SCORED_REVIEW_ADJUDICATION_STATE_INVALID")
    return {
        "schema_version": "dgsi-c2-scored-blind-review-audit.v1",
        "task_id": entry["task_id"],
        "decision": result["decision"],
        "dimension_count": len(REVIEW_DIMENSIONS),
        "reviewer_count": result["reviewer_count"],
        "disagreement_dimension_count": result["disagreement_dimension_count"],
        "adjudication_status": state,
        "identity_authenticated": False,
        "source_rights_verified": False,
        "expert_adjudicated": False,
        "sft_records_emitted": 0,
        "gold_eligible": False,
        "training_authorized": False,
    }


def audit_c2_scored_review_batch(
    manifest: dict[str, Any], submissions: list[dict[str, Any]]
) -> dict[str, Any]:
    """Require exact 15-or-N cohort coverage; never infer scientific approval.

    Per-task inputs contain blinded reviewer tokens, but batch outputs contain
    only counts. The calling authorized workspace must not publish submissions.
    """
    if (
        not isinstance(manifest, dict)
        or manifest.get("schema_version") !=
        "dgsi-l1-blind-review-fingerprint-manifest.v1"
        or manifest.get("track") != "LITERATURE_DERIVED_SYNTHETIC"
        or manifest.get("training_authorized") is not False
        or manifest.get("gold_eligible") is not False
        or not isinstance(manifest.get("review_packets"), list)
        or not isinstance(submissions, list)
    ):
        _fail("C2_SCORED_REVIEW_BATCH_SHAPE_INVALID")
    rows = manifest["review_packets"]
    index: dict[str, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("task_id"), str):
            _fail("C2_SCORED_REVIEW_BATCH_ENTRY_INVALID")
        if row["task_id"] in index:
            _fail("C2_SCORED_REVIEW_BATCH_DUPLICATE_TASK")
        if row.get("collection_projection_sha256") != manifest.get(
            "collection_projection_sha256"
        ):
            _fail("C2_SCORED_REVIEW_BATCH_COHORT_BINDING_INVALID")
        index[row["task_id"]] = row
    if not index or len(index) != manifest.get("packet_count"):
        _fail("C2_SCORED_REVIEW_BATCH_MANIFEST_COUNT_INVALID")
    seen: set[str] = set()
    counts = {
        "PENDING_SECURE_ADJUDICATION": 0,
        "PENDING_REVIEWER_AUTHENTICATION": 0,
    }
    for item in submissions:
        if not isinstance(item, dict) or set(item) != {"task_id", "submission"}:
            _fail("C2_SCORED_REVIEW_BATCH_ITEM_INVALID")
        task_id = item["task_id"]
        if not isinstance(task_id, str) or task_id not in index:
            _fail("C2_SCORED_REVIEW_BATCH_UNKNOWN_TASK")
        if task_id in seen:
            _fail("C2_SCORED_REVIEW_BATCH_DUPLICATE_SUBMISSION")
        seen.add(task_id)
        outcome = audit_c2_scored_review(index[task_id], item["submission"])
        counts[outcome["adjudication_status"]] += 1
    if seen != set(index):
        _fail("C2_SCORED_REVIEW_BATCH_INCOMPLETE")
    return {
        "schema_version": "dgsi-c2-scored-blind-review-batch-audit.v1",
        "decision": "SCORED_RECEIPTS_STRUCTURALLY_BOUND_EXTERNAL_REVIEW_PENDING",
        "packet_count": len(index),
        "scored_submission_count": len(seen),
        "ten_dimension_rubric_validated_count": len(seen),
        "adjudication_status_counts": counts,
        "expert_adjudicated_count": 0,
        "rights_cleared_count": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
        "gold_eligible": False,
    }
