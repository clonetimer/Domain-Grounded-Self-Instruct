"""Read-only historical Context *coverage*, never scientific or SFT admission.

Counts scenario representation in a validated L1 synthetic collection. A
scenario label is only a metadata observation, not an expert-approved example.
Invalid future/same-family/no-timestamp history belongs in negative validator
tests and must never be counted as admitted positive training data.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

from .l1_task_packet import L1TaskPacketError, validate_l1_task_packet_collection


class L1ContextCoverageError(ValueError):
    """Fixed-code error; no task IDs, source refs or case text."""


# Nonexclusive per-packet labels. Their sums can exceed the packet count.
VARIANTS = (
    "NO_HIT",
    "CONFIRMED_APPLICABLE",
    "CONFIRMED_LIMITED_TRANSFER",
    "REJECTED_PRESERVED",
    "UNRESOLVED_PRESERVED",
    "PARTIALLY_CONFIRMED_PRESERVED",
    "UNKNOWN_OUTCOME_PRESERVED",
    "HARDWARE_INCOMPATIBLE",
    "HARDWARE_UNKNOWN",
    "MULTIPLE_HITS",
    "MIXED_OUTCOME_HITS",
)

# These are rejection fixtures, not valid SFT context variants.
NEGATIVE_VALIDATOR_CONTROLS = (
    "HISTORY_AVAILABLE_AFTER_CUTOFF",
    "HISTORY_VERIFIED_AFTER_CUTOFF",
    "HISTORY_AVAILABLE_BEFORE_VERIFICATION",
    "HISTORY_WITHOUT_TRUSTED_AVAILABILITY",
    "CURRENT_EVENT_FAMILY_AS_HISTORY",
    "HISTORICAL_VOTE_ON_CURRENT_ROOT_CAUSE",
)


def _packet_variants(packet: dict[str, Any]) -> set[str]:
    context = packet["history_context"]
    if context["retrieval_status"] == "NO_HIT":
        return {"NO_HIT"}

    items = context["items"]
    labels: set[str] = set()
    statuses = {item["outcome_status"] for item in items}
    if len(items) > 1:
        labels.add("MULTIPLE_HITS")
    if len(statuses) > 1:
        labels.add("MIXED_OUTCOME_HITS")

    for item in items:
        status = item["outcome_status"]
        hardware = item["hardware_compatibility"]
        if status == "CONFIRMED":
            if hardware == "COMPATIBLE":
                labels.add("CONFIRMED_APPLICABLE")
            else:
                labels.add("CONFIRMED_LIMITED_TRANSFER")
        elif status == "REJECTED":
            labels.add("REJECTED_PRESERVED")
        elif status == "UNRESOLVED":
            labels.add("UNRESOLVED_PRESERVED")
        elif status == "PARTIALLY_CONFIRMED":
            labels.add("PARTIALLY_CONFIRMED_PRESERVED")
        elif status == "UNKNOWN":
            labels.add("UNKNOWN_OUTCOME_PRESERVED")

        if hardware == "INCOMPATIBLE":
            labels.add("HARDWARE_INCOMPATIBLE")
        elif hardware == "UNKNOWN":
            labels.add("HARDWARE_UNKNOWN")
    return labels


def audit_l1_context_coverage(
    collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]
) -> dict[str, Any]:
    """Validate the full current cohort then return aggregate-only gap counts.

    No task identity, raw ML result, diagnostic log, reviewer identity, actual
    historical text, or unapproved target is returned. A valid synthetic
    fixture cannot establish training eligibility or expert source fidelity.
    """
    if not isinstance(collection, dict) or not isinstance(source_fact_cards, list):
        raise L1ContextCoverageError("INVALID_CONTEXT_COVERAGE_INPUT")
    if collection.get("track") != "LITERATURE_DERIVED_SYNTHETIC":
        raise L1ContextCoverageError("CONTEXT_COVERAGE_SYNTHETIC_TRACK_ONLY")
    try:
        validated = validate_l1_task_packet_collection(
            collection, source_fact_cards=source_fact_cards
        )
    except (L1TaskPacketError, ValueError, KeyError, TypeError, AttributeError):
        raise L1ContextCoverageError("CONTEXT_COVERAGE_COLLECTION_NOT_VALIDATED") from None

    packet_counts: Counter[str] = Counter()
    task_counts: Counter[str] = Counter()
    no_hit = 0
    history_hit_items = 0
    not_reviewed = 0
    for packet in collection["packets"]:
        task_counts[packet["case"]["task_type"]] += 1
        labels = _packet_variants(packet)
        for label in labels:
            packet_counts[label] += 1
        if "NO_HIT" in labels:
            no_hit += 1
        history_hit_items += len(packet["history_context"]["items"])
        not_reviewed += packet["review"]["status"] != "APPROVED_FOR_L1_EXPERIMENT"

    represented = {name: packet_counts[name] for name in VARIANTS}
    return {
        "schema_version": "dgsi-l1-context-coverage-gaps.v1",
        "decision": "REVIEW_REQUIRED_NOT_TRAINING_ADMISSION",
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "packet_count": validated["packet_count"],
        "event_family_count": validated["event_family_count"],
        "no_hit_packet_count": no_hit,
        "history_hit_packet_count": validated["packet_count"] - no_hit,
        "history_hit_item_count": history_hit_items,
        "task_type_counts": dict(sorted(task_counts.items())),
        "variant_packet_counts": represented,
        "missing_positive_variants": [
            name for name in VARIANTS if represented[name] == 0
        ],
        "negative_validator_controls_not_positive_sft": list(
            NEGATIVE_VALIDATOR_CONTROLS
        ),
        "review_pending_packet_count": not_reviewed,
        "scenario_labels_are_not_expert_approvals": True,
        "unassessable_from_metadata": [
            "CURRENT_LOGS_CONTRADICT_HISTORY",
            "HISTORY_MECHANISM_SUPPORTS_BUT_CANNOT_CONFIRM_CURRENT_FAULT",
            "CONFLICTING_HISTORY_SCIENTIFIC_CORRECTNESS",
        ],
        "official_split_count": len(collection.get("split_assignments", [])),
        "gold_eligible_count": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
    }
