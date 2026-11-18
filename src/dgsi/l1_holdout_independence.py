"""Conservative L1 independent-holdout *planning* audit, not a split exporter.

Event-family isolation alone misses separate episodes of one publication and a
retrieved historical source appearing as another task's target. Connect tasks
through current L0 event families, source-document identity and referenced
history before judging any proposed partition. All outputs are aggregate.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .l1_task_packet import validate_l1_task_packet_collection


class L1HoldoutIndependenceError(ValueError):
    """Stable, payload-free rejection code."""


def _fail(code: str) -> None:
    raise L1HoldoutIndependenceError(code)


def _components(
    collection: dict[str, Any],
    source_fact_cards: list[dict[str, Any]],
) -> tuple[list[tuple[str, ...]], dict[str, str], int]:
    # Validate the *current* candidate snapshot, including L0, history as-of,
    # synthetic lineage and existing no-formal-split policy, before graphing.
    if not isinstance(collection, dict) or not isinstance(source_fact_cards, list):
        _fail("HOLDOUT_INPUT_SHAPE_INVALID")
    validate_l1_task_packet_collection(
        collection, source_fact_cards=source_fact_cards
    )
    packets = collection["packets"]
    cards = {card["case_id"]: card for card in source_fact_cards}
    identities: dict[str, tuple[str, str | None]] = {}
    for card in source_fact_cards:
        ref = card["source_reference"]
        document_id = ref["source_id"]
        identity = (ref["source_title"], ref.get("source_url"))
        if document_id in identities and identities[document_id] != identity:
            _fail("HOLDOUT_SOURCE_DOCUMENT_ID_COLLISION")
        identities[document_id] = identity

    parent = {p["task_id"]: p["task_id"] for p in packets}
    rank = {p["task_id"]: 0 for p in packets}

    def find(value: str) -> str:
        while parent[value] != value:
            parent[value] = parent[parent[value]]
            value = parent[value]
        return value

    def join(a: str, b: str) -> None:
        x, y = find(a), find(b)
        if x == y:
            return
        if rank[x] < rank[y]:
            x, y = y, x
        parent[y] = x
        if rank[x] == rank[y]:
            rank[x] += 1

    family_first: dict[str, str] = {}
    document_first: dict[str, str] = {}
    # Unknown but explicitly SYNTHETIC history refs still link consumers.
    # Without this, two separate families citing the same simulated history
    # document would be incorrectly counted as independent holdout groups.
    opaque_history_first: dict[str, str] = {}
    current_family_first: dict[str, str] = {}
    task_family: dict[str, str] = {}
    for packet in packets:
        task = packet["task_id"]
        family = packet["case"]["provenance"]["source_group"]
        task_family[task] = family
        if family in family_first:
            join(task, family_first[family])
        else:
            family_first[family] = task
        # One current-event family may have several L0 cards/episodes.
        for ref in packet["source_fact_refs"]:
            family_id = cards[ref]["event_family_id"]
            if family_id in current_family_first:
                join(task, current_family_first[family_id])
            else:
                current_family_first[family_id] = task

    for packet in packets:
        task = packet["task_id"]
        refs = set(packet["source_fact_refs"])
        for hit in packet["history_context"]["items"]:
            # Even when the history source is not directly a current L0 ref,
            # it cannot become an independent holdout target elsewhere.
            target = current_family_first.get(hit["event_family_id"])
            if target is not None:
                join(task, target)
            for ref in hit["source_refs"]:
                if ref in cards:
                    refs.add(ref)
                else:
                    prior_consumer = opaque_history_first.get(ref)
                    if prior_consumer is not None:
                        join(task, prior_consumer)
                    else:
                        opaque_history_first[ref] = task
        for ref in sorted(refs):
            document = cards[ref]["source_reference"]["source_id"]
            earlier = document_first.get(document)
            if earlier is not None:
                join(task, earlier)
            else:
                document_first[document] = task

    groups: dict[str, list[str]] = defaultdict(list)
    for task in parent:
        groups[find(task)].append(task)
    return (
        [tuple(sorted(ids)) for ids in groups.values()],
        task_family,
        len(document_first),
    )


def audit_l1_holdout_independence(
    collection: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Return privacy-safe holdout grouping pressure with NO assigned split.

    Group sizes are guidance for independently reviewed future experiments.
    Source aliases, uncited derivative works and future external data cannot
    be discovered by this metadata-level structural audit.
    """
    groups, task_family, documents = _components(collection, source_fact_cards)
    return {
        "schema_version": "dgsi-l1-holdout-independence.v1",
        "decision": "DOCUMENT_AND_HISTORY_CONNECTED_GROUPS_ONLY",
        "track": collection["track"],
        "task_count": len(collection["packets"]),
        "event_family_count": len(set(task_family.values())),
        "distinct_bound_source_document_count": documents,
        "independent_connected_group_count": len(groups),
        "group_task_sizes": sorted(len(g) for g in groups),
        "group_event_family_sizes": sorted(
            len({task_family[task] for task in group}) for group in groups
        ),
        "cannot_prove_unobserved_source_alias_independence": True,
        "not_for_sft": True,
        "official_splits_assigned": False,
        "gold_eligible": False,
        "training_authorized": False,
    }


def check_hypothetical_holdout_partition(
    collection: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
    hypothetical_task_splits: dict[str, str],
) -> dict[str, Any]:
    """Adversarial-only check; never persist or authorize a real split.

    Caller-supplied labels are hypothetical. In particular, a passing check
    does NOT waive required independent reviews or permit model training.
    """
    groups, _, _ = _components(collection, source_fact_cards)
    tasks = {p["task_id"] for p in collection["packets"]}
    if not isinstance(hypothetical_task_splits, dict):
        _fail("HOLDOUT_PARTITION_SHAPE_INVALID")
    if set(hypothetical_task_splits) != tasks:
        _fail("HOLDOUT_PARTITION_INCOMPLETE_OR_UNKNOWN_TASK")
    if any(
        type(split) is not str
        or split not in {"train", "validation", "test"}
        for split in hypothetical_task_splits.values()
    ):
        _fail("HOLDOUT_PARTITION_INVALID_LABEL")
    if any(
        len({hypothetical_task_splits[task] for task in group}) > 1
        for group in groups
    ):
        _fail("HOLDOUT_CONNECTED_GROUP_CROSSES_SPLITS")
    return {
        "decision": "HYPOTHETICAL_STRUCTURAL_CHECK_ONLY",
        "connected_group_count": len(groups),
        "not_for_sft": True,
        "official_splits_assigned": False,
        "training_authorized": False,
    }
