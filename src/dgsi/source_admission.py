"""Metadata-only pre-admission gate for diagnosis-context SFT source candidates.

Consumes a case and a *local* auditor attestation; never reads original source files.
An attestation is a claim, NOT independent verification of authenticity or IP rights.
Passing this gate never authorizes upload, Gold designation or model training.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from .diagnostic_context import validate_diagnostic_case

SOURCE_CLASSES = frozenset({
    "PUBLIC_SYNTHETIC_FIXTURE",
    "INTERNAL_SYNTHETIC_SIMULATION",
    "REAL_ENGINEERING_DIAGNOSIS",
    "REAL_ON_ORBIT_RECORD",
})
REAL_CLASSES = frozenset({"REAL_ENGINEERING_DIAGNOSIS", "REAL_ON_ORBIT_RECORD"})
PERMISSION_KEYS = (
    "access_authorized", "ip_rights_checked",
    "deidentification_checked", "internal_sft_use_authorized",
)
CHECK_KEYS = (
    "upstream_run_verified", "log_provenance_verified",
    "spacecraft_and_mission_context_verified", "historical_outcomes_verified",
    "evidence_citations_verified", "source_hashes_verified",
    "incident_family_deduplicated", "cross_split_leakage_checked",
    "score_semantics_verified",
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")


class SourceAdmissionError(ValueError):
    """A redacted, machine-readable error; does not echo source content."""


def _reject(code: str) -> None:
    raise SourceAdmissionError(code)


def _datetime(value: Any) -> datetime:
    if not isinstance(value, str):
        _reject("INVALID_SOURCE_RUN_TIME")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        _reject("INVALID_SOURCE_RUN_TIME")
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        _reject("INVALID_SOURCE_RUN_TIME")
    return parsed


def _attestation_shape(a: Any) -> None:
    if not isinstance(a, dict) or set(a) != {
        "schema_version", "case_ref", "incident_family", "source_class",
        "permissions", "checks", "producer", "run_completed_at",
        "audit_evidence_sha256",
    }:
        _reject("INVALID_ATTESTATION_SHAPE")
    if a["schema_version"] != "dgsi-source-admission.v1" or a["source_class"] not in SOURCE_CLASSES:
        _reject("INVALID_ATTESTATION_CLASS")
    if not isinstance(a["case_ref"], str) or not isinstance(a["incident_family"], str):
        _reject("INVALID_ATTESTATION_IDENTITY")
    for field, required in (("permissions", PERMISSION_KEYS), ("checks", CHECK_KEYS)):
        value = a[field]
        if not isinstance(value, dict) or set(value) != set(required):
            _reject("INVALID_ATTESTATION_SHAPE")
        if any(type(value[key]) is not bool for key in required):
            _reject("INVALID_ATTESTATION_BOOLEAN")
    producer = a["producer"]
    if not isinstance(producer, dict) or set(producer) != {"method", "version"}:
        _reject("INVALID_ATTESTATION_PRODUCER")
    if any(not isinstance(producer[k], str) or not producer[k].strip() for k in ("method", "version")):
        _reject("INVALID_ATTESTATION_PRODUCER")
    digest = a["audit_evidence_sha256"]
    if digest is not None and (not isinstance(digest, str) or SHA256.fullmatch(digest) is None):
        _reject("INVALID_ATTESTATION_DIGEST")


def assess_source_admission(case: dict[str, Any], attestation: dict[str, Any]) -> dict[str, Any]:
    """Return only blocker codes and counts, no case identifiers or source text.

    The caller must independently verify signed/approved evidence behind every
    attestation. This is a pre-expert-review checklist, NOT a Gold approval.
    """
    try:
        validate_diagnostic_case(case)
    except (KeyError, TypeError, ValueError):
        _reject("INVALID_SOURCE_CASE")
    _attestation_shape(attestation)
    blockers: set[str] = set()
    if attestation["case_ref"] != case["case_id"] or (
        attestation["incident_family"] != case["provenance"]["source_group"]
    ):
        _reject("CASE_ATTESTATION_BINDING_MISMATCH")
    producer = case["input"]["machine_diagnosis"]["producer"]
    if attestation["producer"] != {
        "method": producer["method"], "version": producer["version"],
    }:
        _reject("UPSTREAM_PRODUCER_BINDING_MISMATCH")
    completed_at = _datetime(attestation["run_completed_at"])
    cutoff = _datetime(case["input"]["analysis_cutoff"])
    if completed_at > cutoff:
        blockers.add("UPSTREAM_RUN_AFTER_ANALYSIS_CUTOFF")

    if attestation["source_class"] not in REAL_CLASSES:
        blockers.add("SYNTHETIC_SOURCE_NOT_REAL_CASE")
    generation = str(case["provenance"].get("generation_method") or "").casefold()
    identifiers = (
        case["case_id"], case["provenance"]["source_group"],
        *case["provenance"]["diagnosis_run_refs"],
    )
    if any(term in generation for term in ("synthetic", "illustrative", "hypothetical")) or any(
        str(ref).casefold().startswith(("synthetic://", "synth-", "illustrative", "dgsi-adcs-illustrative"))
        for ref in identifiers
    ):
        blockers.add("SYNTHETIC_PROVENANCE_MARKER")
    if not attestation["audit_evidence_sha256"]:
        blockers.add("MISSING_AUTHORIZATION_AUDIT_EVIDENCE_DIGEST")
    if not case["provenance"]["source_artifact_hashes"]:
        blockers.add("MISSING_SOURCE_ARTIFACT_HASHES")
    if not case["provenance"]["diagnosis_run_refs"]:
        blockers.add("MISSING_DIAGNOSIS_RUN_REFERENCE")
    if not case["input"]["diagnostic_logs"]:
        blockers.add("MISSING_DIAGNOSTIC_LOGS")
    if producer["method"].strip().upper() in {"NOT_RECORDED", "UNKNOWN"} or (
        producer["version"].strip().upper() in {"NOT_RECORDED", "UNKNOWN"}
    ):
        blockers.add("UNKNOWN_UPSTREAM_PRODUCER")
    if not case["input"]["spacecraft_context"]["configuration"]:
        blockers.add("MISSING_SPACECRAFT_CONFIGURATION")
    if not case["input"]["operational_context"]["mission_phase"].strip() or (
        not case["input"]["operational_context"]["operating_mode"].strip()
    ):
        blockers.add("MISSING_MISSION_CONTEXT")
    if any(not log.get("timestamp") for log in case["input"]["diagnostic_logs"]):
        blockers.add("INCOMPLETE_LOG_TIMESTAMPS")
    for name in PERMISSION_KEYS:
        if not attestation["permissions"][name]:
            blockers.add("PERMISSION_" + name.upper() + "_NOT_VERIFIED")
    for name in CHECK_KEYS:
        if not attestation["checks"][name]:
            blockers.add("CHECK_" + name.upper() + "_NOT_VERIFIED")
    # Incomplete historical conclusions must remain so; an attestation of
    # reviewability does not convert UNRESOLVED or UNKNOWN to CONFIRMED.
    unresolved_count = sum(
        h["outcome_status"] in {"UNRESOLVED", "UNKNOWN"}
        for h in case["input"].get("historical_cases", [])
    )
    return {
        "schema_version": "dgsi-source-admission-assessment.v1",
        "decision": "BLOCKED" if blockers else "READY_FOR_MANUAL_SOURCE_AUDIT",
        "blockers": sorted(blockers),
        "blocker_count": len(blockers),
        "unresolved_history_count": unresolved_count,
        "gold_eligible": False,
        "eligible_for_training": False,
        "authorization_verified_by_software": False,
        "note": (
            "Attestation fields are untrusted assertions until the authorized custodian "
            "checks the underlying permissions, source records, hashes, event identity "
            "and independent expert verdict. Never upload restricted case material."
        ),
    }
