"""Immutable L1 blind-review material binding; no Gold or training approval.

All input is reviewed offline in an authorized workspace. Only SHA-256
fingerprints and fixed audit codes may be emitted. This does not verify a
reviewer's identity, source authenticity, de-identification, or consent.
"""
from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any

from .l1_coverage_review import L1QualityGateError, validate_blind_l1_review
from .l1_task_packet import validate_l1_task_packet


_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RECEIPT_VERSION = "dgsi-l1-review-binding.v1"


def _fail(code: str) -> None:
    raise L1QualityGateError(code)


def _hash_json(value: Any) -> str:
    """Stable hash over UTF-8 canonical JSON; never echo the hashed payload."""
    try:
        encoded = json.dumps(
            value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        _fail("L1_REVIEW_UNHASHABLE_MATERIAL")
    return sha256(encoded).hexdigest()


def fingerprint_l1_review_material(
    packet: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]
) -> dict[str, Any]:
    """Bind the reviewable Case/target/context and referenced L0 facts.

    The curator-only internal_review and mutable review-status metadata are
    excluded from the fingerprint, because neither is visible to reviewers.
    All model-visible inputs, the formal target, generation provenance, and
    source references remain bound.
    """
    validate_l1_task_packet(packet, source_fact_cards=source_fact_cards)
    case = packet["case"]
    reviewable_case = {
        k: v for k, v in case.items() if k not in ("internal_review", "review")
    }
    reviewable = {
        "task_id": packet["task_id"],
        "track": packet["track"],
        "source_fact_refs": packet["source_fact_refs"],
        "case": reviewable_case,
        "formal_target": packet["formal_target"],
        "history_context": packet["history_context"],
        "synthetic_provenance": packet["synthetic_provenance"],
    }
    by_id = {card["case_id"]: card for card in source_fact_cards}
    refs = set(packet["source_fact_refs"])
    refs.update(
        ref for item in packet["history_context"]["items"]
        for ref in item["source_refs"] if ref in by_id
    )
    bound_facts = [by_id[ref] for ref in sorted(refs)]
    return {
        "packet_sha256": _hash_json(reviewable),
        "source_fact_cards_sha256": _hash_json(bound_facts),
        "source_fact_count": len(bound_facts),
    }


def validate_l1_review_receipt(
    packet: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    """Audit a blind scorecard against *current* packet and L0 source bytes.

    This is a binding/quality gate, never reviewer authentication, a signed
    adjudication record, L1 approval, dataset admission, or training consent.
    """
    required = {
        "schema_version", "packet_sha256", "source_fact_cards_sha256",
        "blind_review", "adjudication_status",
    }
    if not isinstance(receipt, dict) or set(receipt) != required or \
            receipt.get("schema_version") != _RECEIPT_VERSION:
        _fail("INVALID_L1_REVIEW_RECEIPT_ENVELOPE")

    for field in ("packet_sha256", "source_fact_cards_sha256"):
        value = receipt[field]
        if not isinstance(value, str) or not _HEX_SHA256.fullmatch(value):
            _fail("INVALID_L1_REVIEW_FINGERPRINT")

    current = fingerprint_l1_review_material(
        packet, source_fact_cards=source_fact_cards
    )
    if receipt["packet_sha256"] != current["packet_sha256"]:
        _fail("L1_REVIEW_PACKET_CHANGED_SINCE_REVIEW")
    if receipt["source_fact_cards_sha256"] != current["source_fact_cards_sha256"]:
        _fail("L1_REVIEW_L0_FACTS_CHANGED_SINCE_REVIEW")

    form = receipt["blind_review"]
    if not isinstance(form, dict) or form.get("blinded_packet_ref") != \
            "sha256:" + current["packet_sha256"]:
        _fail("L1_REVIEW_BLIND_TOKEN_NOT_BOUND_TO_PACKET")
    result = validate_blind_l1_review(form)
    expected_state = (
        "PENDING_SECURE_ADJUDICATION"
        if result["decision"] == "NEEDS_SECURE_ADJUDICATION"
        else "PENDING_REVIEWER_AUTHENTICATION"
    )
    if receipt["adjudication_status"] != expected_state:
        _fail("L1_REVIEW_ADJUDICATION_STATE_MISMATCH")
    return {
        "schema_version": "dgsi-l1-review-binding-audit.v1",
        "decision": result["decision"],
        "adjudication_status": expected_state,
        "reviewer_count": result["reviewer_count"],
        "source_fact_count": current["source_fact_count"],
        "packet_binding_valid": True,
        "source_fact_binding_valid": True,
        "gold_eligible": False,
        "training_authorized": False,
        "note": (
            "Fingerprint binding does not certify reviewer independence, "
            "source rights, secure adjudication, or Gold."
        ),
    }


def audit_l1_review_receipt_batch(
    collection: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
    receipts: list[dict[str, Any]],
) -> dict[str, Any]:
    """Require one immutable review receipt for every task in an L1 collection.

    The batch result reports only aggregate counts. Receipt validation proves
    that a scorecard is bound to the current task/L0 bytes; it does not
    authenticate the humans behind reviewer tokens or approve SFT admission.
    """
    from .l1_task_packet import validate_l1_task_packet_collection

    validate_l1_task_packet_collection(
        collection, source_fact_cards=source_fact_cards
    )
    if not isinstance(receipts, list):
        _fail("L1_REVIEW_RECEIPT_BATCH_NOT_LIST")

    packets_by_id = {
        packet["task_id"]: packet for packet in collection["packets"]
    }
    receipt_by_id: dict[str, dict[str, Any]] = {}
    for entry in receipts:
        if not isinstance(entry, dict) or set(entry) != {"task_id", "receipt"}:
            _fail("INVALID_L1_REVIEW_RECEIPT_BATCH_ENTRY")
        task_id = entry["task_id"]
        if not isinstance(task_id, str) or not task_id:
            _fail("INVALID_L1_REVIEW_RECEIPT_TASK_ID")
        if task_id not in packets_by_id:
            _fail("UNKNOWN_L1_REVIEW_RECEIPT_TASK")
        if task_id in receipt_by_id:
            _fail("DUPLICATE_L1_REVIEW_RECEIPT_TASK")
        receipt_by_id[task_id] = entry["receipt"]

    if set(receipt_by_id) != set(packets_by_id):
        _fail("L1_REVIEW_RECEIPT_COVERAGE_INCOMPLETE")

    decisions: list[str] = []
    adjudication: dict[str, int] = {}
    source_card_count = 0
    for task_id, packet in packets_by_id.items():
        result = validate_l1_review_receipt(
            packet,
            source_fact_cards=source_fact_cards,
            receipt=receipt_by_id[task_id],
        )
        decisions.append(result["decision"])
        adjudication[result["adjudication_status"]] = (
            adjudication.get(result["adjudication_status"], 0) + 1
        )
        source_card_count += result["source_fact_count"]

    return {
        "schema_version": "dgsi-l1-review-receipt-batch-audit.v1",
        "decision": "RECEIPTS_BOUND_REVIEWER_AUTHENTICATION_PENDING",
        "collection_id": collection["collection_id"],
        "packet_count": len(packets_by_id),
        "receipt_count": len(receipt_by_id),
        "packet_binding_valid_count": len(packets_by_id),
        "source_binding_valid_count": len(packets_by_id),
        "adjudication_status_counts": dict(sorted(adjudication.items())),
        "secure_adjudication_required_count": decisions.count("NEEDS_SECURE_ADJUDICATION"),
        "reviewer_authentication_pending_count": decisions.count(
            "AWAITING_INDEPENDENT_REVIEWER_AUTHENTICATION"
        ),
        "aggregate_source_card_binding_count": source_card_count,
        "l1_experiment_approval_count": 0,
        "gold_eligible_count": 0,
        "training_authorized": False,
        "note": (
            "Complete receipt coverage and immutable binding do not prove reviewer "
            "identity/independence, source rights, or semantic approval."
        ),
    }
