"""Aggregate-only reuse audit for *declared* diagnosis/log file digests.

This complements local byte hashing; it does not access a source file, certify
a digest, establish a true event-family identity, or authorize split/Gold.
Only the already-designated train/validation/test split, if supplied, is
audited; this module never assigns splits.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .real_case_handoff import RealCaseHandoffError, assess_handoff_manifest

_SPLITS = frozenset({"train", "validation", "test"})
_SYNTHETIC = frozenset({"SIMULATION", "SYNTHETIC_FIXTURE"})
_EPISODE_FILE_ROLES = frozenset({
    "diagnosis_result.json", "diagnostic_logs.jsonl", "diagnostic_logs.csv",
})


class HandoffDigestReuseError(ValueError):
    """Constant error code with no restricted identifier or digest."""


def _reject(code: str) -> None:
    raise HandoffDigestReuseError(code)


def audit_handoff_digest_reuse(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Check claimed source-byte reuse and optional pre-existing split labels.

    Entries have exactly {"manifest": object, "split": train|validation|test|null}.
    Null means no pre-existing split. A cohort must be wholly assigned or wholly
    unassigned, so partial labels cannot evade the cross-split audit. Hashes
    are *claims*, even if a separate local verifier previously matched bytes.
    A reused event-specific digest is a manual-family-review signal; a
    cross-split reuse or synthetic/real alias blocks the cohort.
    """
    if not isinstance(entries, list):
        _reject("INVALID_DIGEST_REUSE_BATCH")

    case_ids: set[str] = set()
    family_splits: dict[str, str | None] = {}
    family_counts: Counter[str] = Counter()
    digest_occurrences: dict[tuple[str, str], list[tuple[str, str | None, bool]]] = defaultdict(list)
    split_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    missing_digest_cases = 0
    nonready_manifest_cases = 0
    splits_present: set[bool] = set()

    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"manifest", "split"}:
            _reject("INVALID_DIGEST_REUSE_ENTRY")
        split = entry["split"]
        if split is not None and (not isinstance(split, str) or split not in _SPLITS):
            _reject("INVALID_PREEXISTING_SPLIT")
        splits_present.add(split is not None)
        manifest = entry["manifest"]
        try:
            assessed = assess_handoff_manifest(manifest)
        except (RealCaseHandoffError, KeyError, ValueError, TypeError, AttributeError):
            _reject("INVALID_HANDOFF_MANIFEST")
        case_id = manifest["case_id"]
        family = manifest["event_family_id"]
        source = manifest["source_class"]
        if case_id in case_ids:
            _reject("DUPLICATE_HANDOFF_CASE_ID")
        case_ids.add(case_id)
        if family in family_splits and family_splits[family] != split:
            _reject("CROSS_SPLIT_INCIDENT_FAMILY")
        family_splits[family] = split
        family_counts[family] += 1
        source_counts[source] += 1
        if split is not None:
            split_counts[split] += 1
        if assessed["decision"] not in {"ACCEPT_FOR_EXPERT_REVIEW", "SYNTHETIC_TEST_ONLY"}:
            nonready_manifest_cases += 1

        declared = set(manifest.get("available_files", [])) & _EPISODE_FILE_ROLES
        hashes = manifest.get("input_file_sha256") or {}
        if declared - hashes.keys():
            missing_digest_cases += 1
        for role in sorted(declared & hashes.keys()):
            digest_occurrences[(role, hashes[role])].append(
                (family, split, source in _SYNTHETIC)
            )

    if len(splits_present) > 1:
        _reject("PARTIALLY_ASSIGNED_SPLIT_COHORT")

    blockers: set[str] = set()
    review_codes: set[str] = set()
    family_alias_groups = 0
    cross_split_groups = 0
    synthetic_real_alias_groups = 0
    for occurrences in digest_occurrences.values():
        families = {item[0] for item in occurrences}
        splits = {item[1] for item in occurrences if item[1] is not None}
        classes = {item[2] for item in occurrences}
        if len(families) > 1:
            family_alias_groups += 1
            review_codes.add("DECLARED_EVENT_SOURCE_REUSED_ACROSS_FAMILIES")
        if len(splits) > 1:
            cross_split_groups += 1
            blockers.add("CROSS_SPLIT_DECLARED_EVENT_SOURCE_DIGEST")
        if len(classes) > 1:
            synthetic_real_alias_groups += 1
            blockers.add("SYNTHETIC_REAL_DECLARED_SOURCE_ALIAS")

    if missing_digest_cases:
        review_codes.add("EPISODE_SOURCE_DIGEST_DECLARATIONS_INCOMPLETE")
    if nonready_manifest_cases:
        review_codes.add("MANIFEST_SOURCE_REVIEW_NOT_READY")

    if blockers:
        decision = "BLOCKED_SOURCE_REUSE"
    elif source_counts and all(source in _SYNTHETIC for source in source_counts):
        decision = "SYNTHETIC_TEST_ONLY"
    elif review_codes:
        decision = "MANUAL_EVENT_FAMILY_REVIEW"
    else:
        decision = "PASS_UNTRUSTED_DECLARATIONS_ONLY"

    return {
        "schema_version": "dgsi-handoff-digest-reuse-audit.v1",
        "decision": decision,
        "blocker_codes": sorted(blockers),
        "manual_review_codes": sorted(review_codes),
        "case_count": len(entries),
        "incident_family_count": len(family_counts),
        "repeated_incident_family_count": sum(v > 1 for v in family_counts.values()),
        "event_source_digest_signature_count": len(digest_occurrences),
        "cross_family_digest_reuse_signature_count": family_alias_groups,
        "cross_split_digest_reuse_signature_count": cross_split_groups,
        "synthetic_real_digest_alias_signature_count": synthetic_real_alias_groups,
        "missing_event_digest_case_count": missing_digest_cases,
        "manifest_not_ready_case_count": nonready_manifest_cases,
        "existing_split_counts": {s: split_counts[s] for s in ("train", "validation", "test")},
        "split_labels_provided": bool(splits_present and True in splits_present),
        "split_assignment_allowed": False,
        "source_authenticity_verified": False,
        "input_bytes_verified_by_this_audit": False,
        "gold_eligible": False,
        "training_eligible": False,
        "limitations": [
            "Digest strings are untrusted manifest assertions; local byte verification is separate.",
            "Different bytes, de-identification, timestamps and aliases can hide related episodes.",
            "Generic context and knowledge passages are not event identity signatures.",
            "Shared diagnostic source bytes require manual incident-family and rights review.",
            "This audit never assigns dataset splits or independently approves expert targets.",
        ],
    }
