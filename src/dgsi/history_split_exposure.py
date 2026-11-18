"""Fail-closed split audit for historical-memory reuse in diagnostic SFT.

This checks whether an evaluation case or episode is exposed to a different
split as a "historical" reference. It does not load historical records, verify
their availability time, or approve any training/Gold data. All output is
aggregate-only and no case identifier or diagnostic text is emitted.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .diagnostic_context import validate_diagnostic_case

_ALLOWED_SPLITS = frozenset({"train", "validation", "test"})


class HistorySplitExposureError(ValueError):
    """Stable rejection code; deliberately excludes source identifiers."""


def _reject(code: str) -> None:
    raise HistorySplitExposureError(code)


def audit_history_split_exposure(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit local case packets already assigned to dataset splits.

    Each entry contains exactly {"case": <diagnostic_case>, "split": ...}.
    Direct references to known cases or episode groups in another split are
    blocked. Reusing an unknown external history reference across splits is
    conservatively flagged for independent review, not silently accepted.

    A passing structural check does NOT establish historical availability:
    each cited record still needs as-of cutoff verification and source rights.
    """
    if not isinstance(entries, list):
        _reject("INVALID_CASE_BATCH")

    case_splits: dict[str, str] = {}
    group_splits: dict[str, str] = {}
    case_groups: dict[str, str] = {}
    declared: list[tuple[str, str, str, tuple[str, ...]]] = []
    split_counts: Counter[str] = Counter()
    history_occurrences: Counter[str] = Counter()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"case", "split"}:
            _reject("INVALID_CASE_BATCH_ENTRY")
        split = entry["split"]
        if not isinstance(split, str) or split not in _ALLOWED_SPLITS:
            _reject("INVALID_SPLIT")
        case = entry["case"]
        try:
            validate_diagnostic_case(case)
        except (ValueError, KeyError, TypeError, AttributeError):
            _reject("INVALID_DIAGNOSTIC_CASE")
        case_id = case["case_id"]
        source_group = case["provenance"]["source_group"]
        if case_id in case_splits and case_splits[case_id] != split:
            _reject("CROSS_SPLIT_CASE_ID")
        if source_group in group_splits and group_splits[source_group] != split:
            _reject("CROSS_SPLIT_INCIDENT_FAMILY")
        if case_id in case_groups and case_groups[case_id] != source_group:
            _reject("CASE_INCIDENT_FAMILY_CHANGED")
        case_splits[case_id] = split
        group_splits[source_group] = split
        case_groups[case_id] = source_group
        history_refs = tuple(item["case_ref"] for item in case["input"].get("historical_cases", []))
        declared.append((case_id, source_group, split, history_refs))
        split_counts[split] += 1

    history_ref_splits: dict[str, set[str]] = defaultdict(set)
    for case_id, source_group, split, history_refs in declared:
        for ref in history_refs:
            if ref in (case_id, source_group):
                _reject("SELF_REFERENTIAL_HISTORICAL_CASE")
            if ref in case_splits and case_splits[ref] != split:
                _reject("CROSS_SPLIT_HISTORY_CASE_REFERENCE")
            if ref in group_splits and group_splits[ref] != split:
                _reject("CROSS_SPLIT_HISTORY_EPISODE_REFERENCE")
            history_ref_splits[ref].add(split)
            history_occurrences[split] += 1

    shared_count = sum(len(splits) > 1 for splits in history_ref_splits.values())
    return {
        "schema_version": "dgsi-history-split-exposure.v1",
        "decision": (
            "MANUAL_HISTORY_REFERENCE_REVIEW"
            if shared_count else "PASS_STRUCTURAL_ONLY"
        ),
        "case_packet_count": len(entries),
        "distinct_case_count": len(case_splits),
        "incident_family_count": len(group_splits),
        "split_counts": {key: split_counts[key] for key in ("train", "validation", "test")},
        "history_reference_count": sum(history_occurrences.values()),
        "distinct_history_reference_count": len(history_ref_splits),
        "shared_history_reference_across_split_count": shared_count,
        "gold_eligible": False,
        "training_authorized": False,
        "history_asof_and_identity_review_required": bool(history_ref_splits),
        "limitations": [
            "Only exact case and episode IDs can be matched; aliases require authorized audit.",
            "Shared external historical references may be legitimate, but require "
            "pre-cutoff availability proof and holdout contamination review.",
            "Source access, de-identification and independent expert adjudication "
            "are not established by this structural audit.",
        ],
    }
