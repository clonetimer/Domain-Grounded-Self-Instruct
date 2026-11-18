"""Read-only L1-to-SFT release boundary; never serializes training examples.

A successful structural audit, a review receipt, or an APPROVED status string
cannot authenticate a reviewer, source rights, privacy clearance or training
consent. Those authorities do not currently exist in this public repository.
"""
from __future__ import annotations

from typing import Any

from .l1_global_lineage import audit_l1_cross_collection_lineage
from .l1_review_receipts import audit_l1_review_receipt_batch


class L1SftReleaseError(ValueError):
    """Fixed-code failure; never include source material or identifiers."""


def _block(code: str) -> None:
    raise L1SftReleaseError(code)


def preflight_l1_sft_release(
    batches: list[dict[str, Any]],
    *,
    reviewed_aliases: list[dict[str, Any]] | None = None,
    receipt_batches: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Audit all collections before a prospective SFT release.

    This is an advisory, metadata-only gate. Its decision is *always blocked*
    until a separate trusted source/IP/privacy admission and human review
    authority is designed and integrated. No speculative split can be passed
    here, and no prompt, target, review comment, path or ID is returned.
    """
    global_report = audit_l1_cross_collection_lineage(
        batches, reviewed_aliases=reviewed_aliases
    )
    if global_report["decision"] != "STRUCTURAL_PREFLIGHT_ONLY":
        _block("L1_SFT_GLOBAL_PREFLIGHT_NOT_PASSED")

    batch_by_id = {
        batch["collection"]["collection_id"]: batch for batch in batches
    }
    if receipt_batches is not None:
        if not isinstance(receipt_batches, dict) or any(
            not isinstance(key, str) or not isinstance(value, list)
            for key, value in receipt_batches.items()
        ):
            _block("L1_SFT_RECEIPT_BATCHES_INVALID")
        if not set(receipt_batches).issubset(batch_by_id):
            _block("L1_SFT_UNKNOWN_RECEIPT_COLLECTION")

    receipt_validated = 0
    packet_without_receipt = 0
    packet_without_split = 0
    packet_without_l1_approval = 0
    for cid, batch in batch_by_id.items():
        collection = batch["collection"]
        packets = collection["packets"]
        packet_without_split += len(packets) - len(
            collection.get("split_assignments", [])
        )
        packet_without_l1_approval += sum(
            packet["review"]["status"] != "APPROVED_FOR_L1_EXPERIMENT"
            for packet in packets
        )
        if collection["data_status"] != "APPROVED_FOR_L1_EXPERIMENT":
            # An asserted packet status never overrides collection admission.
            packet_without_l1_approval += sum(
                packet["review"]["status"] == "APPROVED_FOR_L1_EXPERIMENT"
                for packet in packets
            )
        if receipt_batches is not None and cid in receipt_batches:
            audit_l1_review_receipt_batch(
                collection,
                source_fact_cards=batch["source_fact_cards"],
                receipts=receipt_batches[cid],
            )
            receipt_validated += len(packets)
        else:
            packet_without_receipt += len(packets)

    blockers = [
        "TRUSTED_SOURCE_IP_PRIVACY_ADMISSION_NOT_ESTABLISHED",
        "INDEPENDENT_REVIEWER_AUTHENTICATION_NOT_ESTABLISHED",
        "EXTERNAL_RELEASE_AND_TRAINING_AUTHORIZATION_NOT_ESTABLISHED",
    ]
    if packet_without_receipt:
        blockers.append("L1_REVIEW_RECEIPTS_INCOMPLETE")
    if packet_without_l1_approval:
        blockers.append("L1_EXPERIMENT_REVIEW_INCOMPLETE")
    if packet_without_split:
        blockers.append("OFFICIAL_SPLIT_ASSIGNMENT_INCOMPLETE")

    return {
        "schema_version": "dgsi-l1-sft-release-preflight.v1",
        "decision": "BLOCKED_PENDING_EXTERNAL_ADMISSION",
        "collection_count": global_report["collection_count"],
        "task_count": global_report["task_count"],
        "track_task_counts": global_report["track_task_counts"],
        "track_family_counts": global_report["track_family_counts"],
        "receipt_bound_packet_count": receipt_validated,
        "receipt_missing_packet_count": packet_without_receipt,
        "official_split_missing_packet_count": packet_without_split,
        "l1_review_incomplete_packet_count": packet_without_l1_approval,
        "blocking_codes": blockers,
        "sft_records_emitted": 0,
        "gold_eligible_count": 0,
        "training_authorized": False,
    }


def require_l1_sft_release(
    batches: list[dict[str, Any]],
    *,
    reviewed_aliases: list[dict[str, Any]] | None = None,
    receipt_batches: dict[str, list[dict[str, Any]]] | None = None,
) -> None:
    """Fail-closed entry for any future serializer.

    Do not replace this with a status-flag or unsigned reviewer-token check.
    A future trusted admission authority must be separately implemented and
    tested before this boundary can permit actual SFT export.
    """
    preflight_l1_sft_release(
        batches, reviewed_aliases=reviewed_aliases,
        receipt_batches=receipt_batches,
    )
    _block("L1_SFT_RELEASE_NOT_AUTHORIZED")
