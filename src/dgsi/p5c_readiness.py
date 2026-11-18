"""Fail-closed, aggregate-only P5-C0 SFT readiness snapshot audit.

An inventory snapshot is not an admission receipt. This validator detects drift
between the declared baseline and current L0/L1 fixtures, while refusing to
infer source truth, independent review, real Gold, or training authorization.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

TRACK = "LITERATURE_DERIVED_SYNTHETIC"
PENDING = "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION"


class P5CReadinessError(ValueError):
    """Fixed-code audit failure; never echo a case, path or source excerpt."""


def _block(code: str) -> None:
    raise P5CReadinessError(code)


def _field(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            _block("P5C_INPUT_STRUCTURE_INVALID")
        value = value[key]
    return value


def _same(actual: Any, declared: Any) -> None:
    if actual != declared:
        _block("P5C_SNAPSHOT_STALE")


def audit_p5c_sft_readiness(
    snapshot: dict[str, Any],
    collection: dict[str, Any],
    l0_registry: dict[str, Any],
) -> dict[str, Any]:
    """Check current file contents against a declared *unapproved* baseline.

    Report contains only aggregate metadata. Even success means
    BLOCKED_PENDING_INDEPENDENT_REVIEW and never authorizes SFT serialization.
    """
    if not all(isinstance(x, dict) for x in (snapshot, collection, l0_registry)):
        _block("P5C_INPUT_STRUCTURE_INVALID")
    if snapshot.get("schema_version") != "dgsi-sft-readiness-baseline.v1":
        _block("P5C_BASELINE_SCHEMA_INVALID")
    if snapshot.get("status") != "REVIEW_REQUIRED_NOT_TRAINING_AUTHORIZED":
        _block("P5C_UNAUTHORIZED_TRANSITION")
    if collection.get("track") != TRACK or collection.get("data_status") != "REVIEW_REQUIRED":
        _block("P5C_UNAUTHORIZED_TRANSITION")
    if collection.get("gold_eligible") is not False or collection.get("training_authorized") is not False:
        _block("P5C_UNAUTHORIZED_TRANSITION")
    if collection.get("split_assignments"):
        _block("P5C_UNAUTHORIZED_SPLIT")
    if any(v is not False for v in _field(snapshot, "tracks", "hard_gates").values()):
        _block("P5C_UNAUTHORIZED_TRANSITION")

    cards = _field(l0_registry, "cards")
    packets = _field(collection, "packets")
    if not isinstance(cards, list) or not isinstance(packets, list) or not packets:
        _block("P5C_INPUT_STRUCTURE_INVALID")
    cards_by_id: dict[str, dict[str, Any]] = {}
    for card in cards:
        if not isinstance(card, dict) or not isinstance(card.get("case_id"), str):
            _block("P5C_INPUT_STRUCTURE_INVALID")
        if card["case_id"] in cards_by_id:
            _block("P5C_DUPLICATE_SOURCE_CARD")
        cards_by_id[card["case_id"]] = card

    tasks: Counter[str] = Counter()
    families: Counter[str] = Counter()
    context: Counter[str] = Counter()
    seen_tasks: set[str] = set()
    referenced_cards: set[str] = set()
    for packet in packets:
        if not isinstance(packet, dict) or not isinstance(packet.get("case"), dict):
            _block("P5C_INPUT_STRUCTURE_INVALID")
        case = packet["case"]
        task_id = packet.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in seen_tasks:
            _block("P5C_DUPLICATE_OR_INVALID_TASK")
        seen_tasks.add(task_id)
        if packet.get("track") != TRACK:
            _block("P5C_CROSS_TRACK_PACKET")
        if _field(packet, "synthetic_provenance", "classification") != "SYNTHETIC":
            _block("P5C_CROSS_TRACK_PACKET")
        if _field(case, "provenance", "generation_method") != TRACK:
            _block("P5C_CROSS_TRACK_PACKET")
        if _field(case, "input", "raw_telemetry_included") is not False:
            _block("P5C_RAW_TELEMETRY_IN_DEFAULT_INPUT")
        if _field(case, "internal_review", "not_for_sft") is not True:
            _block("P5C_INTERNAL_REVIEW_LEAK_RISK")
        if _field(packet, "review", "status") != "REVIEW_REQUIRED":
            _block("P5C_UNAUTHORIZED_TRANSITION")
        refs = packet.get("source_fact_refs")
        group = _field(case, "provenance", "source_group")
        if not isinstance(group, str) or not group.startswith("LITERATURE-DERIVED:"):
            _block("P5C_SOURCE_FAMILY_MISMATCH")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            _block("P5C_SOURCE_REF_INVALID")
        for ref in refs:
            if not isinstance(ref, str) or ref not in cards_by_id:
                _block("P5C_SOURCE_REF_INVALID")
            card = cards_by_id[ref]
            if card.get("knowledge_source_not_event") is not False:
                _block("P5C_NON_EVENT_SOURCE_AS_FAULT")
            if group != "LITERATURE-DERIVED:" + str(card.get("event_family_id")):
                _block("P5C_SOURCE_FAMILY_MISMATCH")
            referenced_cards.add(ref)
        tasks[_field(case, "task_type")] += 1
        families[group] += 1
        h = _field(packet, "history_context")
        status = _field(h, "retrieval_status")
        items = _field(h, "items")
        if status not in {"NO_HIT", "HIT"} or not isinstance(items, list):
            _block("P5C_HISTORY_STATUS_INVALID")
        if (status == "NO_HIT" and items) or (status == "HIT" and not items):
            _block("P5C_HISTORY_STATUS_INVALID")
        context[status] += 1

    source_classes: Counter[str] = Counter()
    for card_id in referenced_cards:
        card = cards_by_id[card_id]
        if card.get("domain_review_status") != PENDING or card.get("domain_review_evidence_sha256") is not None:
            _block("P5C_SOURCE_REVIEW_NOT_AUTHENTICATED")
        if card.get("sft_eligible") is not False:
            _block("P5C_UNAUTHORIZED_TRANSITION")
        cls = card.get("event_status")
        if cls not in {"FLIGHT_EVENT", "GROUND_TEST_EVENT"}:
            _block("P5C_SOURCE_EVENT_CLASS_INVALID")
        source_classes[cls] += 1

    unreferenced = [c for cid, c in cards_by_id.items() if cid not in referenced_cards]
    if any(c.get("knowledge_source_not_event") is not True for c in unreferenced):
        _block("P5C_UNREFERENCED_EVENT_CARD_NOT_ACCOUNTED")

    synth = _field(snapshot, "tracks", "LITERATURE_DERIVED_SYNTHETIC")
    metrics = {
        "packet_count": len(packets),
        "event_family_count": len(families),
        "review_required_count": len(packets),
        "approved_for_l1_experiment_count": 0,
        "official_split_assignment_count": 0,
        "task_type_counts": dict(tasks),
        "history_context": dict(context),
        "event_class_counts": dict(source_classes),
        "source_family_packet_counts": dict(families),
    }
    _same(collection.get("packet_count"), len(packets))
    for key, actual in metrics.items():
        _same(actual, _field(synth, key))
    l0 = _field(snapshot, "tracks", "L0_source_cards")
    for key, actual in {
        "total_count": len(cards),
        "referenced_by_l1_count": len(referenced_cards),
        "referenced_and_pending_domain_expert_confirmation_count": len(referenced_cards),
        "unreferenced_knowledge_source_not_event_count": len(unreferenced),
        "domain_expert_confirmed_count": 0,
        "domain_expert_rejected_count": 0,
    }.items():
        _same(actual, _field(l0, key))

    real = _field(snapshot, "tracks", "real_case_track")
    if real.get("real_gold_admitted_count") != 0 or real.get("real_gold_training_authorized_count") != 0:
        _block("P5C_UNAUTHORIZED_TRANSITION")
    downstream = _field(snapshot, "tracks", "downstream")
    for key in (
        "authorized_sft_serialized_count",
        "official_train_validation_test_assignment_count",
        "fine_tuning_run_count",
    ):
        if downstream.get(key) != 0:
            _block("P5C_UNAUTHORIZED_TRANSITION")
    if downstream.get("effectiveness_result") != "NOT_MEASURED":
        _block("P5C_UNAUTHORIZED_TRANSITION")

    return {
        "schema_version": "dgsi-p5c-readiness-audit.v1",
        "decision": "BLOCKED_PENDING_INDEPENDENT_REVIEW",
        "literature_synthetic_candidate_packets": len(packets),
        "literature_event_families": len(families),
        "l0_source_cards_pending_domain_review": len(referenced_cards),
        "real_gold_admitted": 0,
        "official_splits": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
        "note": "A matching inventory is not source admission, reviewer authentication or training approval.",
    }
