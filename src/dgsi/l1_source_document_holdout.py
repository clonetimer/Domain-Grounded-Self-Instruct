"""Read-only, source-document-level holdout design audit for DGSI L1.

A distinct event_family_id does NOT imply an independent source document.
This script never assigns official splits, authorizes training, or authenticates
source rights, expert receipts, history as-of status, or real evidence.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any


class L1DocumentHoldoutError(ValueError):
    """Fail closed using a stable, payload-free rejection code."""


def _reject(code: str) -> None:
    raise L1DocumentHoldoutError(code)


def audit_l1_source_document_holdout(
    collection: dict[str, Any],
    source_fact_cards: list[dict[str, Any]],
    *,
    hypothetical_splits: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Derive source-document-connected independent holdout units.

    Graph nodes are *document IDs* and *event family IDs*. A task citing
    one or more L0 cards connects the relevant nodes; all reachable tasks
    must occupy one hypothetical split. The returned plan is advisory only.
    """
    if collection.get("track") != "LITERATURE_DERIVED_SYNTHETIC":
        _reject("L1_HOLDOUT_TRACK_UNSUPPORTED")
    packets = collection.get("packets")
    if not isinstance(packets, list) or not packets:
        _reject("L1_HOLDOUT_PACKETS_MISSING")
    if not isinstance(source_fact_cards, list) or not source_fact_cards:
        _reject("L1_HOLDOUT_SOURCE_CARDS_MISSING")

    cards: dict[str, dict[str, Any]] = {}
    for card in source_fact_cards:
        if not isinstance(card, dict):
            _reject("L1_HOLDOUT_SOURCE_CARD_INVALID")
        ref = card.get("case_id")
        if not isinstance(ref, str) or not ref or ref in cards:
            _reject("L1_HOLDOUT_SOURCE_ID_DUPLICATE_OR_MISSING")
        cards[ref] = card

    parent: dict[str, str] = {}

    def find(node: str) -> str:
        parent.setdefault(node, node)
        if parent[node] != node:
            parent[node] = find(parent[node])
        return parent[node]

    def join(a: str, b: str) -> None:
        aa, bb = find(a), find(b)
        if aa != bb:
            parent[max(aa, bb)] = min(aa, bb)

    doc_tasks: dict[str, set[str]] = defaultdict(set)
    doc_families: dict[str, set[str]] = defaultdict(set)
    task_nodes: dict[str, set[str]] = {}
    all_tasks: set[str] = set()
    all_families: set[str] = set()

    for packet in packets:
        if not isinstance(packet, dict):
            _reject("L1_HOLDOUT_PACKET_INVALID")
        task_id = packet.get("task_id")
        refs = packet.get("source_fact_refs")
        if not isinstance(task_id, str) or not task_id or task_id in all_tasks:
            _reject("L1_HOLDOUT_TASK_ID_DUPLICATE_OR_MISSING")
        if not isinstance(refs, list) or not refs or len(refs) != len(set(refs)):
            _reject("L1_HOLDOUT_SOURCE_REFS_MISSING_OR_DUPLICATE")
        all_tasks.add(task_id)
        nodes: set[str] = set()
        for ref in refs:
            if not isinstance(ref, str) or ref not in cards:
                _reject("L1_HOLDOUT_SOURCE_REF_UNRESOLVED")
            card = cards[ref]
            sr = card.get("source_reference")
            doc = sr.get("source_id") if isinstance(sr, dict) else None
            family = card.get("event_family_id")
            if not isinstance(doc, str) or not doc.strip():
                _reject("L1_HOLDOUT_DOCUMENT_ID_MISSING")
            if not isinstance(family, str) or not family.strip():
                _reject("L1_HOLDOUT_EVENT_FAMILY_MISSING")
            dnode, fnode = "D:" + doc, "F:" + family
            join(dnode, fnode)
            nodes.update((dnode, fnode))
            doc_tasks[doc].add(task_id)
            doc_families[doc].add(family)
            all_families.add(family)
        first = min(nodes)
        for node in nodes:
            join(first, node)
        task_nodes[task_id] = nodes

    groups: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: {"task_ids": set(), "source_ids": set(), "event_family_ids": set()}
    )
    for doc, tasks in doc_tasks.items():
        group = groups[find("D:" + doc)]
        group["source_ids"].add(doc)
        group["task_ids"].update(tasks)
        group["event_family_ids"].update(doc_families[doc])

    clusters = [
        {key: sorted(values) for key, values in group.items()}
        for group in groups.values()
    ]
    clusters.sort(key=lambda item: item["source_ids"])

    if hypothetical_splits is not None:
        if not isinstance(hypothetical_splits, dict) or set(hypothetical_splits) != all_tasks:
            _reject("L1_HOLDOUT_HYPOTHETICAL_PLAN_INCOMPLETE")
        if set(hypothetical_splits.values()) - {"train", "validation", "test"}:
            _reject("L1_HOLDOUT_HYPOTHETICAL_SPLIT_INVALID")
        for group in clusters:
            if len({hypothetical_splits[tid] for tid in group["task_ids"]}) != 1:
                _reject("L1_HOLDOUT_SHARED_DOCUMENT_OR_FAMILY_CROSS_SPLIT")

    return {
        "decision": ("HYPOTHETICAL_DOCUMENT_HOLDOUT_SAFE"
                     if hypothetical_splits is not None else "REVIEW_ONLY_NO_SPLITS"),
        "collection_id": collection.get("collection_id"),
        "task_count": len(all_tasks),
        "event_family_count": len(all_families),
        "source_document_count": len(doc_tasks),
        "independent_source_document_cluster_count": len(clusters),
        "source_document_groups": [
            {"source_id": doc, "task_ids": sorted(doc_tasks[doc]),
             "event_family_ids": sorted(doc_families[doc])}
            for doc in sorted(doc_tasks)
        ],
        "holdout_clusters": clusters,
        "hypothetical_plan_checked": hypothetical_splits is not None,
        "official_splits_assigned": False,
        "expert_review_complete": False,
        "gold_eligible": False,
        "training_authorized": False,
    }
