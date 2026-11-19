"""Strict *model-visible* literature-source holdout audit for DGSI DEV_ONLY.

P5-C15 groups the documents behind current L0 facts. For an unseen-literature
evaluation, documents included as history or knowledge evidence also count as
exposed: a FUSE training prompt mentioning the Cassini source cannot coexist
with a Cassini holdout in an unseen-publication claim.

This is a read-only experimental feasibility audit, NOT a split allocator or
an as-of, provenance-rights, expert-approval or training-authorization gate.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

from .l1_source_document_holdout import (
    L1DocumentHoldoutError,
    audit_l1_source_document_holdout,
)


def audit_l1_model_visible_source_holdout(
    collection: dict[str, Any],
    source_fact_cards: list[dict[str, Any]],
    *,
    hypothetical_splits: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Require no publicly sourced material visible in two hypothetical splits.

    Includes current L0 citations, model-visible knowledge evidence, history
    source references and reused history case IDs. Explicitly synthetic history
    references have no invented literature identity, but repeated identifiers
    must remain in the same split. No content is exposed in the audit report.
    """
    base = audit_l1_source_document_holdout(collection, source_fact_cards)
    packets = collection["packets"]
    cards = {card["case_id"]: card for card in source_fact_cards}
    doc_ids = {card["source_reference"]["source_id"] for card in source_fact_cards}
    task_ids = {p["task_id"] for p in packets}

    parent = {task_id: task_id for task_id in task_ids}

    def find(key: str) -> str:
        if parent[key] != key:
            parent[key] = find(parent[key])
        return parent[key]

    def join(first: str, second: str) -> None:
        a, b = find(first), find(second)
        if a != b:
            parent[max(a, b)] = min(a, b)

    current_doc_tasks: dict[str, set[str]] = defaultdict(set)
    task_source_ids: dict[str, set[str]] = defaultdict(set)
    seen_history_refs: dict[str, set[str]] = defaultdict(set)
    historical_public_documents: set[str] = set()

    for group in base["source_document_groups"]:
        current_doc_tasks[group["source_id"]].update(group["task_ids"])
    for cluster in base["holdout_clusters"]:
        task_list = cluster["task_ids"]
        for task_id in task_list[1:]:
            join(task_list[0], task_id)

    def expose_document(task_id: str, source_id: Any, *, history: bool) -> None:
        if not isinstance(source_id, str) or source_id not in doc_ids:
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_UNRESOLVED_PUBLIC_DOCUMENT")
        task_source_ids[task_id].add(source_id)
        if history:
            historical_public_documents.add(source_id)
        for other_task in current_doc_tasks.get(source_id, set()):
            join(task_id, other_task)

    for packet in packets:
        task_id = packet["task_id"]
        case = packet.get("case")
        if not isinstance(case, dict) or not isinstance(case.get("input"), dict):
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_INPUT_MISSING")
        inputs = case["input"]

        for fact_ref in packet["source_fact_refs"]:
            expose_document(task_id, cards[fact_ref]["source_reference"]["source_id"], history=False)

        evidence = inputs.get("knowledge_evidence", [])
        if not isinstance(evidence, list):
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_EVIDENCE_INVALID")
        for item in evidence:
            if not isinstance(item, dict):
                raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_EVIDENCE_INVALID")
            expose_document(task_id, item.get("source_id"), history=False)

        history = packet.get("history_context")
        items = history.get("items", []) if isinstance(history, dict) else None
        declared = inputs.get("historical_cases", [])
        if not isinstance(items, list) or not isinstance(declared, list):
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_HISTORY_INVALID")
        detail_refs = []
        for item in items:
            if not isinstance(item, dict) or not isinstance(item.get("case_ref"), str) or not item["case_ref"]:
                raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_HISTORY_INVALID")
            case_ref = item["case_ref"]
            detail_refs.append(case_ref)
            seen_history_refs["H:" + case_ref].add(task_id)
            refs = item.get("source_refs")
            if not isinstance(refs, list) or not refs:
                raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_HISTORY_SOURCE_MISSING")
            for ref in refs:
                if ref in cards:
                    expose_document(task_id, cards[ref]["source_reference"]["source_id"], history=True)
                elif isinstance(ref, str) and ref.startswith("SYNTHETIC-HISTORY-"):
                    # Synthetic references are not reinterpreted as genuine literature.
                    seen_history_refs["S:" + ref].add(task_id)
                else:
                    raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_HISTORY_SOURCE_UNRESOLVED")

        prompt_refs = [h.get("case_ref") if isinstance(h, dict) else None for h in declared]
        if len(prompt_refs) != len(set(prompt_refs)) or sorted(prompt_refs) != sorted(detail_refs):
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_HISTORY_PROMPT_MISMATCH")

    for matching in seen_history_refs.values():
        ordered = sorted(matching)
        for other in ordered[1:]:
            join(ordered[0], other)

    clusters: dict[str, set[str]] = defaultdict(set)
    for task_id in task_ids:
        clusters[find(task_id)].add(task_id)
    grouped = []
    for task_set in clusters.values():
        source_ids = set().union(*(task_source_ids[t] for t in task_set))
        grouped.append({"task_ids": sorted(task_set), "visible_source_ids": sorted(source_ids)})
    grouped.sort(key=lambda item: item["task_ids"])

    if hypothetical_splits is not None:
        if (
            not isinstance(hypothetical_splits, dict)
            or set(hypothetical_splits) != task_ids
        ):
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_PLAN_INCOMPLETE")
        if set(hypothetical_splits.values()) - {"train", "validation", "test"}:
            raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_SPLIT_INVALID")
        for group in grouped:
            if len({hypothetical_splits[tid] for tid in group["task_ids"]}) != 1:
                raise L1DocumentHoldoutError("L1_VISIBLE_HOLDOUT_CROSS_SPLIT_EXPOSURE")

    return {
        "decision": ("HYPOTHETICAL_VISIBLE_SOURCE_SAFE"
                     if hypothetical_splits is not None else "REVIEW_ONLY_NO_SPLITS"),
        "collection_id": base["collection_id"],
        "task_count": base["task_count"],
        "primary_document_count": base["source_document_count"],
        "primary_document_cluster_count": base["independent_source_document_cluster_count"],
        "model_visible_document_cluster_count": len(grouped),
        "history_exposed_public_source_ids": sorted(historical_public_documents),
        "model_visible_holdout_clusters": grouped,
        "hypothetical_plan_checked": hypothetical_splits is not None,
        "official_splits_assigned": False,
        "gold_eligible": False,
        "training_authorized": False,
        "expert_review_complete": False,
        "historical_asof_certified": False,
    }
