"""Validate local human text-region review receipts without authenticating reviewers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
REVIEW_SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/diagram_text_review.schema.json"
CANDIDATE_SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/diagram_text_regions.schema.json"


class DiagramTextReviewError(ValueError):
    """Stable, payload-free review receipt validation error."""


def _canonical_sha256(value: Any) -> str:
    try:
        payload = json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError):
        raise DiagramTextReviewError("DIAGRAM_REVIEW_CANONICALIZATION_FAILED") from None
    return hashlib.sha256(payload).hexdigest()


def _load_schema(path: Path, code: str) -> dict[str, Any]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        return schema
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        raise DiagramTextReviewError(code) from None


def validate_diagram_text_review(
    candidate_record: dict[str, Any],
    review_receipt: dict[str, Any],
) -> dict[str, Any]:
    """Bind local decisions to an exact candidate record and exact evidence locators.

    This validator does not authenticate reviewer identity, verify that the
    reviewer actually inspected the image, or promote candidates to Gold/SFT.
    """
    candidate_schema = _load_schema(CANDIDATE_SCHEMA, "DIAGRAM_TEXT_CANDIDATE_SCHEMA_UNAVAILABLE")
    review_schema = _load_schema(REVIEW_SCHEMA, "DIAGRAM_TEXT_REVIEW_SCHEMA_UNAVAILABLE")
    if list(Draft202012Validator(candidate_schema).iter_errors(candidate_record)):
        raise DiagramTextReviewError("DIAGRAM_TEXT_CANDIDATE_RECORD_INVALID")
    if list(Draft202012Validator(review_schema, format_checker=FormatChecker()).iter_errors(review_receipt)):
        raise DiagramTextReviewError("DIAGRAM_TEXT_REVIEW_RECEIPT_INVALID")

    if review_receipt["source_sha256"] != candidate_record["source_sha256"]:
        raise DiagramTextReviewError("DIAGRAM_REVIEW_SOURCE_HASH_MISMATCH")
    if review_receipt["asset_id"] != candidate_record["asset_id"]:
        raise DiagramTextReviewError("DIAGRAM_REVIEW_ASSET_ID_MISMATCH")
    if review_receipt["asset_sha256"] != candidate_record["asset_sha256"]:
        raise DiagramTextReviewError("DIAGRAM_REVIEW_ASSET_HASH_MISMATCH")
    if review_receipt["candidate_record_sha256"] != _canonical_sha256(candidate_record):
        raise DiagramTextReviewError("DIAGRAM_REVIEW_CANDIDATE_RECORD_HASH_MISMATCH")

    candidates = {item["candidate_id"]: item for item in candidate_record["candidates"]}
    if len(candidates) != len(candidate_record["candidates"]):
        raise DiagramTextReviewError("DIAGRAM_TEXT_CANDIDATE_ID_DUPLICATE")

    seen: set[str] = set()
    counts = {"ACCEPT_AS_LABEL": 0, "REJECT_LABEL": 0, "UNRESOLVED": 0}
    for decision in review_receipt["decisions"]:
        candidate_id = decision["candidate_id"]
        if candidate_id in seen:
            raise DiagramTextReviewError("DIAGRAM_REVIEW_DECISION_DUPLICATE")
        seen.add(candidate_id)
        candidate = candidates.get(candidate_id)
        if candidate is None:
            raise DiagramTextReviewError("DIAGRAM_REVIEW_CANDIDATE_UNKNOWN")
        if decision["evidence_locator"] not in candidate["evidence_locators"]:
            raise DiagramTextReviewError("DIAGRAM_REVIEW_EVIDENCE_LOCATOR_MISMATCH")
        counts[decision["decision"]] += 1

    return {
        "decision": "REVIEW_RECEIPT_BOUND_NOT_AUTHENTICATED",
        "candidate_count": len(candidates),
        "decision_count": len(seen),
        "accepted_label_count": counts["ACCEPT_AS_LABEL"],
        "rejected_label_count": counts["REJECT_LABEL"],
        "unresolved_count": counts["UNRESOLVED"],
        "reviewer_authentication": "NOT_AUTHENTICATED_BY_LOCAL_TOOL",
        "review_status": "REVIEW_REQUIRED",
        "not_for_sft": True,
        "training_authorized": False,
        "gold_authorized": False,
    }
