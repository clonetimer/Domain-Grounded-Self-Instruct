"""Metadata-only L1 blind review manifest, never an expert admission or SFT export.

Bind two future independent reviews to *exact* task/source bytes without
recording reviewers, private comments, prompt text or assistant targets.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from .l1_model_projection_audit import audit_l1_synthetic_collection_projection


class L1BlindReviewManifestError(ValueError):
    """Payload-free structural review receipt rejection."""


def _digest(value: Any) -> str:
    try:
        data = json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (ValueError, TypeError, UnicodeError) as exc:
        raise L1BlindReviewManifestError("REVIEW_MANIFEST_UNHASHABLE") from exc
    return sha256(data).hexdigest()


def _public_fact(card: dict[str, Any]) -> dict[str, Any]:
    # The internal curator field is never included in the published fingerprint.
    return {key: value for key, value in card.items() if key != "internal_review"}


def build_l1_blind_review_manifest(
    collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]
) -> dict[str, Any]:
    """Prepare a deterministic, unapproved metadata manifest for offline reviews.

    Existing whole-collection projection validation is mandatory. Even a
    structurally clean manifest carries no source rights, reviewer identity
    verification, official split, Gold status or SFT release authority.
    """
    audit = audit_l1_synthetic_collection_projection(
        collection, source_fact_cards=source_fact_cards
    )
    cards = {card["case_id"]: card for card in source_fact_cards}
    entries: list[dict[str, Any]] = []
    for packet in collection["packets"]:
        source_refs = sorted(set(packet["source_fact_refs"]))
        source_bindings = [
            {
                "source_fact_ref": ref,
                "public_fact_sha256": _digest(_public_fact(cards[ref])),
            }
            for ref in source_refs
        ]
        packet_sha = _digest(packet)
        entry = {
            "task_id": packet["task_id"],
            "case_id": packet["case"]["case_id"],
            "event_family": packet["case"]["provenance"]["source_group"],
            "task_type": packet["case"]["task_type"],
            "packet_sha256": packet_sha,
            "source_fact_bindings": source_bindings,
            "source_public_sha256": _digest(source_bindings),
            "review_status": "PENDING_TWO_INDEPENDENT_EXPERTS",
            "reviewer_slots": ["A_UNASSIGNED", "B_UNASSIGNED"],
            "adjudication_status": "NOT_STARTED",
            "rights_status": "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW",
            "training_authorized": False,
            "gold_eligible": False,
        }
        entries.append(entry)
    entries.sort(key=lambda x: x["task_id"])
    return {
        "schema_version": "dgsi-l1-blind-review-fingerprint-manifest.v1",
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "collection_id": collection["collection_id"],
        "collection_projection_sha256": audit["collection_projection_sha256"],
        "packet_count": len(entries),
        "event_family_count": audit["event_family_count"],
        "review_packets": entries,
        "expert_adjudicated_count": 0,
        "rights_cleared_event_family_count": 0,
        "sft_records_emitted": 0,
        "official_splits_assigned": False,
        "gold_eligible": False,
        "training_authorized": False,
        "decision": "MANIFEST_ONLY_PENDING_EXTERNAL_REVIEW_AND_RIGHTS",
    }


def check_blind_review_pair(
    entry: dict[str, Any], receipts: list[dict[str, Any]]
) -> dict[str, Any]:
    """Check *structure* of two offline receipts, not reviewer authenticity.

    This never accepts a packet into Gold, SFT or training even when both
    unauthenticated receipts say ACCEPT. Verification of independent human
    reviewer identities and source rights belongs to a separate authority.
    Raw receipts and reviewer tokens are never returned or persisted here.
    """
    if not isinstance(receipts, list) or len(receipts) != 2:
        raise L1BlindReviewManifestError("REVIEW_RECEIPTS_REQUIRE_TWO")
    tokens: list[str] = []
    statuses: list[str] = []
    for receipt in receipts:
        if not isinstance(receipt, dict):
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_INVALID_SHAPE")
        if receipt.get("task_id") != entry["task_id"]:
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_TASK_DRIFT")
        if receipt.get("packet_sha256") != entry["packet_sha256"]:
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_STALE_PACKET")
        if receipt.get("source_public_sha256") != entry["source_public_sha256"]:
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_STALE_SOURCE")
        token = receipt.get("reviewer_token")
        if not isinstance(token, str) or not token.strip():
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_TOKEN_MISSING")
        status = receipt.get("recommendation")
        if status not in ("ACCEPT", "REVISE", "REJECT"):
            raise L1BlindReviewManifestError("REVIEW_RECEIPT_STATUS_INVALID")
        tokens.append(token)
        statuses.append(status)
    if len(set(tokens)) != 2:
        raise L1BlindReviewManifestError("REVIEW_RECEIPT_REVIEWER_NOT_INDEPENDENT")
    return {
        "task_id": entry["task_id"],
        "receipt_structure": "TWO_DISTINCT_TOKENS_UNAUTHENTICATED",
        "recommendations_agree": statuses[0] == statuses[1],
        "external_identity_verification": "NOT_PERFORMED",
        "source_rights_verified": False,
        "expert_adjudicated": False,
        "gold_eligible": False,
        "training_authorized": False,
        "decision": "RECEIPTS_STRUCTURALLY_CHECKED_EXTERNAL_ADJUDICATION_REQUIRED",
    }
