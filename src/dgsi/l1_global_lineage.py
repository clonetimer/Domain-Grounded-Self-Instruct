from __future__ import annotations

"""Read-only cross-collection lineage preflight for L1 diagnosis tasks.

Proposed split plans are *hypothetical fixtures*, never approved assignments.
Every L1 packet and its L0 facts are first checked by the existing validators.
This module does not adjudicate expert identities, literature truth, or Gold.
"""

import hashlib
import json
from typing import Any

from .l1_task_packet import L1TaskPacketError, validate_l1_task_packet_collection


class L1GlobalLineageError(ValueError):
    """Stable payload-free error for a global lineage inconsistency."""


def _reject(code: str) -> None:
    raise L1GlobalLineageError(code)


def _digest(value: dict[str, Any]) -> str:
    serialized = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def audit_l1_cross_collection_lineage(
    batches: list[dict[str, Any]],
    *,
    hypothetical_splits: dict[str, dict[str, str]] | None = None,
    reviewed_aliases: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Check collection identities and cross-collection target/history leakage.

    Each batch supplies `collection` and `source_fact_cards`. In ordinary
    operation no extra splits are assigned. For adversarial experiments only,
    `hypothetical_splits` can supply an *advisory* full task-to-split map; this
    does not mutate collections or authorize training. Reviewed aliases must
    have source facts covering both claimed families. An asserted review token
    is not independent authentication.
    """
    if not isinstance(batches, list) or not batches:
        _reject("GLOBAL_BATCHES_MISSING")
    if hypothetical_splits is not None and not isinstance(hypothetical_splits, dict):
        _reject("GLOBAL_HYPOTHETICAL_SPLITS_INVALID")
    if reviewed_aliases is not None and not isinstance(reviewed_aliases, list):
        _reject("GLOBAL_ALIASES_INVALID")

    collections: dict[str, dict[str, Any]] = {}
    all_cards: dict[str, dict[str, Any]] = {}
    all_hashes: dict[str, str] = {}
    all_task_ids: set[str] = set()
    for batch in batches:
        if not isinstance(batch, dict) or set(batch) != {"collection", "source_fact_cards"}:
            _reject("GLOBAL_BATCH_SHAPE_INVALID")
        collection, cards = batch["collection"], batch["source_fact_cards"]
        try:
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)
        except (L1TaskPacketError, TypeError, KeyError, AttributeError):
            _reject("GLOBAL_L1_BATCH_FAILED_LOCAL_VALIDATION")
        cid = collection["collection_id"]
        if cid in collections:
            _reject("GLOBAL_DUPLICATE_COLLECTION_ID")
        collections[cid] = collection
        for card in cards:
            ref = card["case_id"]
            signature = _digest(card)
            if ref in all_hashes and all_hashes[ref] != signature:
                _reject("GLOBAL_SOURCE_CARD_VERSION_CONFLICT")
            all_hashes[ref] = signature
            all_cards[ref] = card
        for packet in collection["packets"]:
            tid = packet["task_id"]
            if tid in all_task_ids:
                _reject("GLOBAL_DUPLICATE_TASK_ID")
            all_task_ids.add(tid)

    if hypothetical_splits is not None and set(hypothetical_splits) != set(collections):
        _reject("GLOBAL_HYPOTHETICAL_COLLECTION_COVERAGE_INCOMPLETE")

    known_families = {card["event_family_id"] for card in all_cards.values()}
    aliases: dict[str, str] = {}
    canonical_ids: set[str] = set()
    for record in reviewed_aliases or []:
        if not isinstance(record, dict) or set(record) != {
            "alias_family_id", "canonical_family_id", "source_fact_refs",
            "review_status"
        }:
            _reject("GLOBAL_ALIAS_SHAPE_INVALID")
        alias, canonical = record["alias_family_id"], record["canonical_family_id"]
        refs = record["source_fact_refs"]
        if (not isinstance(alias, str) or not isinstance(canonical, str)
                or alias == canonical or alias not in known_families
                or canonical not in known_families):
            _reject("GLOBAL_ALIAS_UNRESOLVED_FAMILY")
        if record["review_status"] != "DOMAIN_EXPERT_CONFIRMED":
            _reject("GLOBAL_ALIAS_NOT_DOMAIN_REVIEWED")
        if not isinstance(refs, list) or len(refs) != len(set(refs)) or len(refs) < 2:
            _reject("GLOBAL_ALIAS_SOURCE_EVIDENCE_INCOMPLETE")
        if any(ref not in all_cards for ref in refs):
            _reject("GLOBAL_ALIAS_SOURCE_EVIDENCE_INCOMPLETE")
        covered = {all_cards[ref]["event_family_id"] for ref in refs}
        if not {alias, canonical}.issubset(covered):
            _reject("GLOBAL_ALIAS_SOURCE_FAMILY_MISMATCH")
        if alias in aliases and aliases[alias] != canonical:
            _reject("GLOBAL_ALIAS_AMBIGUOUS_CANONICAL")
        aliases[alias] = canonical
        canonical_ids.add(canonical)
    if set(aliases) & canonical_ids:
        _reject("GLOBAL_ALIAS_CHAIN_OR_CYCLE")

    target_splits: dict[str, set[str]] = {}
    history_links: list[tuple[str, str, str | None]] = []
    tracked_task_count = 0
    tracks: dict[str, int] = {}
    for cid, collection in collections.items():
        packets = collection["packets"]
        if hypothetical_splits is not None:
            if collection.get("split_assignments"):
                _reject("GLOBAL_HYPOTHETICAL_CANNOT_OVERWRITE_OFFICIAL_SPLIT")
            assignments = hypothetical_splits[cid]
        else:
            assignments = {row["task_id"]: row["split"]
                           for row in collection.get("split_assignments", [])}
        if not isinstance(assignments, dict):
            _reject("GLOBAL_SPLIT_MAP_INVALID")
        ids = {p["task_id"] for p in packets}
        if (hypothetical_splits is not None or assignments) and set(assignments) != ids:
            _reject("GLOBAL_SPLIT_MAP_INCOMPLETE")
        if any(value not in {"train", "validation", "test"} for value in assignments.values()):
            _reject("GLOBAL_SPLIT_NAME_INVALID")
        for packet in packets:
            tracked_task_count += 1
            tracks[packet["track"]] = tracks.get(packet["track"], 0) + 1
            task_split = assignments.get(packet["task_id"])
            current = {
                aliases.get(all_cards[ref]["event_family_id"],
                            all_cards[ref]["event_family_id"])
                for ref in packet["source_fact_refs"]
            }
            for family in current:
                if task_split is not None:
                    target_splits.setdefault(family, set()).add(task_split)
            for history in packet["history_context"]["items"]:
                prior = aliases.get(history["event_family_id"], history["event_family_id"])
                if prior in current:
                    _reject("GLOBAL_ALIAS_HISTORY_IS_CURRENT_EVENT")
                history_links.append((prior, packet["task_id"], task_split))

    if any(len(splits) > 1 for splits in target_splits.values()):
        _reject("GLOBAL_EVENT_FAMILY_CROSSES_SPLITS")
    for prior, _task, consumer_split in history_links:
        if consumer_split is None:
            continue
        if prior in target_splits and consumer_split not in target_splits[prior]:
            _reject("GLOBAL_HISTORY_EXPOSES_OTHER_SPLIT_TARGET")

    return {
        "schema_version": "dgsi-l1-cross-collection-lineage-audit.v1",
        "decision": "STRUCTURAL_PREFLIGHT_ONLY",
        "collection_count": len(collections),
        "task_count": tracked_task_count,
        "source_card_count": len(all_cards),
        "canonical_target_family_count": len(target_splits) if target_splits else len(
            {aliases.get(c["event_family_id"], c["event_family_id"])
             for c in all_cards.values()}
        ),
        "history_hit_count": len(history_links),
        "reviewed_alias_declaration_count": len(aliases),
        "track_task_counts": tracks,
        "split_check_mode": ("HYPOTHETICAL_TEST_ONLY" if hypothetical_splits is not None
                             else "EXISTING_ASSIGNMENTS_ONLY"),
        "gold_eligible_count": 0,
        "training_authorized": False,
    }
