"""Aggregate-only audit of *declared* upstream diagnosis-run identities.

Input is a pseudonymized manifest plus a separately extracted, minimal
provenance statement. The module does NOT read a Case, diagnostic logs,
expert targets, raw telemetry, or source files. Identifiers are not emitted.
A shared run reference is an alias/split-leakage signal, not proof of event
identity; asserted run references are not authenticated by this audit.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

from .real_case_handoff import RealCaseHandoffError, assess_handoff_manifest

_SPLITS = frozenset({"train", "validation", "test"})
_SYNTHETIC = frozenset({"SIMULATION", "SYNTHETIC_FIXTURE"})
_LINEAGE_FIELDS = frozenset({"case_id", "source_group", "diagnosis_run_refs", "generation_method"})
_SYNTHETIC_METHOD_MARKERS = ("synthetic", "hypothetical", "illustrative", "simulated")


class RunLineageAuditError(ValueError):
    """Fixed error code; never includes input values or identifiers."""


def _reject(code: str) -> None:
    raise RunLineageAuditError(code)


def audit_handoff_run_lineage(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit declared diagnosis-run identity reuse and PREEXISTING split labels.

    Each entry is {"manifest": object, "lineage": object, "split": str|null}.
    The separate lineage object MUST contain only Case provenance identifiers:
    {"case_id", "source_group", "diagnosis_run_refs"} and optional
    "generation_method". A data custodian must derive these from an already
    validated Case in an authorized environment. No target answer is needed.
    An omitted split is allowed only when the entire cohort is unassigned.
    """
    if not isinstance(entries, list):
        _reject("INVALID_RUN_LINEAGE_BATCH")

    case_ids: set[str] = set()
    family_splits: dict[str, str | None] = {}
    family_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    split_counts: Counter[str] = Counter()
    run_occurrences: dict[str, list[tuple[str, str | None, bool]]] = defaultdict(list)
    assigned: set[bool] = set()
    missing_run_cases = 0
    not_ready_cases = 0
    blockers: set[str] = set()
    manual_codes: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"manifest", "lineage", "split"}:
            _reject("INVALID_RUN_LINEAGE_ENTRY")
        split = entry["split"]
        if split is not None and (not isinstance(split, str) or split not in _SPLITS):
            _reject("INVALID_PREEXISTING_SPLIT")
        assigned.add(split is not None)

        manifest = entry["manifest"]
        try:
            triage = assess_handoff_manifest(manifest)
        except (RealCaseHandoffError, ValueError, KeyError, TypeError, AttributeError):
            _reject("INVALID_HANDOFF_MANIFEST")
        lineage = entry["lineage"]
        if not isinstance(lineage, dict) or not {"case_id", "source_group", "diagnosis_run_refs"} <= set(lineage) or not set(lineage) <= _LINEAGE_FIELDS:
            _reject("INVALID_RUN_LINEAGE_SHAPE")
        for field in ("case_id", "source_group"):
            if not isinstance(lineage[field], str) or not lineage[field].strip():
                _reject("INVALID_RUN_LINEAGE_IDENTIFIER")
        if lineage["case_id"] != manifest["case_id"] or lineage["source_group"] != manifest["event_family_id"]:
            _reject("RUN_LINEAGE_MANIFEST_BINDING_MISMATCH")
        refs = lineage["diagnosis_run_refs"]
        if not isinstance(refs, list):
            _reject("INVALID_DIAGNOSIS_RUN_REFERENCES")
        if any(not isinstance(ref, str) or not ref or ref.strip() != ref for ref in refs):
            _reject("INVALID_DIAGNOSIS_RUN_REFERENCES")
        if len(refs) != len(set(refs)):
            _reject("DUPLICATE_DIAGNOSIS_RUN_REFERENCE")
        method = lineage.get("generation_method")
        if method is not None and not isinstance(method, str):
            _reject("INVALID_RUN_LINEAGE_GENERATION_METHOD")

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
        if triage["decision"] not in {"ACCEPT_FOR_EXPERT_REVIEW", "SYNTHETIC_TEST_ONLY"}:
            not_ready_cases += 1

        looks_synthetic = any(ref.casefold().startswith("synthetic://") for ref in refs)
        if method:
            looks_synthetic |= any(word in method.casefold() for word in _SYNTHETIC_METHOD_MARKERS)
        if looks_synthetic and source not in _SYNTHETIC:
            blockers.add("SYNTHETIC_RUN_LINEAGE_MISDECLARED_REAL")
        if not refs:
            missing_run_cases += 1
        for ref in refs:
            run_occurrences[ref].append((family, split, source in _SYNTHETIC))

    if len(assigned) > 1:
        _reject("PARTIALLY_ASSIGNED_SPLIT_COHORT")

    cross_family_groups = 0
    cross_split_groups = 0
    synthetic_real_groups = 0
    for occurrences in run_occurrences.values():
        families = {f for f, _, _ in occurrences}
        splits = {s for _, s, _ in occurrences if s is not None}
        synth = {x for _, _, x in occurrences}
        if len(families) > 1:
            cross_family_groups += 1
            manual_codes.add("DECLARED_DIAGNOSIS_RUN_REUSED_ACROSS_FAMILIES")
        if len(splits) > 1:
            cross_split_groups += 1
            blockers.add("CROSS_SPLIT_DECLARED_DIAGNOSIS_RUN")
        if len(synth) > 1:
            synthetic_real_groups += 1
            blockers.add("SYNTHETIC_REAL_RUN_LINEAGE_ALIAS")

    if missing_run_cases:
        manual_codes.add("DIAGNOSIS_RUN_REFERENCES_MISSING")
    if not_ready_cases:
        manual_codes.add("HANDOFF_SOURCE_REVIEW_NOT_READY")

    if blockers:
        decision = "BLOCKED_RUN_LINEAGE"
    elif source_counts and all(s in _SYNTHETIC for s in source_counts):
        decision = "SYNTHETIC_TEST_ONLY"
    elif manual_codes:
        decision = "MANUAL_RUN_LINEAGE_REVIEW"
    else:
        decision = "PASS_UNTRUSTED_RUN_CLAIMS_ONLY"

    return {
        "schema_version": "dgsi-run-lineage-reuse-audit.v1",
        "decision": decision,
        "blocker_codes": sorted(blockers),
        "manual_review_codes": sorted(manual_codes),
        "case_count": len(entries),
        "incident_family_count": len(family_counts),
        "repeated_incident_family_count": sum(count > 1 for count in family_counts.values()),
        "declared_run_signature_count": len(run_occurrences),
        "cross_family_run_reuse_signature_count": cross_family_groups,
        "cross_split_run_reuse_signature_count": cross_split_groups,
        "synthetic_real_run_alias_signature_count": synthetic_real_groups,
        "missing_run_reference_case_count": missing_run_cases,
        "handoff_not_ready_case_count": not_ready_cases,
        "existing_split_counts": {s: split_counts[s] for s in ("train", "validation", "test")},
        "split_labels_provided": True in assigned,
        "source_authenticity_verified": False,
        "run_identity_authenticated": False,
        "case_provenance_verified_by_this_audit": False,
        "split_assignment_allowed": False,
        "expert_review_verified": False,
        "gold_eligible": False,
        "training_eligible": False,
        "limitations": [
            "Run references are custodian-supplied assertions and may not be globally unique.",
            "Only the already assigned split labels are checked; no split is created.",
            "De-identification or reruns may change run IDs without changing event identity.",
            "Bind the lineage to an authorized validated Case and authenticate upstream runs separately.",
            "A passing audit does not establish rights, source validity, expert approval or Gold.",
        ],
    }
