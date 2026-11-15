"""Bind untrusted handoff metadata to a locally supplied diagnostic Case.

This deliberately does not open files, verify IP rights or source authenticity,
or certify expert conclusions. Results contain fixed error codes only.
Only the authorized data custodian should call this on restricted case content.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .diagnostic_context import validate_diagnostic_case
from .real_case_handoff import assess_handoff_manifest, RealCaseHandoffError

_SYNTHETIC_CLASSES = frozenset({"SIMULATION", "SYNTHETIC_FIXTURE"})
_SYNTHETIC_WORDS = ("synthetic", "illustrative", "hypothetical", "simulated")
_SYNTHETIC_PREFIXES = ("synthetic://", "synth-", "illustrative", "dgsi-adcs-illustrative")
_OPTIONAL_INPUT_FILES = (
    ("historical_cases", "historical_cases.json"),
    ("knowledge_evidence", "knowledge_refs.json"),
)


class HandoffCaseBindingError(ValueError):
    """Payload-free error code; restricted case identifiers are never echoed."""


def _instant(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
        return parsed.astimezone(timezone.utc)
    except (ValueError, TypeError, AttributeError):
        raise HandoffCaseBindingError("INVALID_BINDING_ANALYSIS_CUTOFF") from None


def _synthetic_case_marker(case: dict[str, Any]) -> bool:
    provenance = case["provenance"]
    method = str(provenance.get("generation_method") or "").casefold()
    if any(word in method for word in _SYNTHETIC_WORDS):
        return True
    refs = (
        case["case_id"], provenance["source_group"],
        *provenance["diagnosis_run_refs"],
    )
    return any(
        str(ref).casefold().startswith(_SYNTHETIC_PREFIXES)
        for ref in refs
    )


def assess_handoff_case_binding(manifest: dict[str, Any], case: dict[str, Any]) -> dict[str, Any]:
    """Cross-check one manifest and one Case; no file IO and no approval.

    Matching fields prove only that two submitted payloads agree, not that
    their source, redaction, algorithm, hash, or expert statements are true.
    The target is never copied into the input or returned in this report.
    """
    try:
        manifest_result = assess_handoff_manifest(manifest)
    except (RealCaseHandoffError, KeyError, TypeError, ValueError):
        raise HandoffCaseBindingError("INVALID_HANDOFF_MANIFEST") from None
    try:
        validate_diagnostic_case(case)
    except (KeyError, TypeError, ValueError):
        raise HandoffCaseBindingError("INVALID_DIAGNOSTIC_CASE") from None

    blockers: set[str] = set()
    warnings: set[str] = set()
    inputs = case["input"]
    provenance = case["provenance"]
    declared_files = set(manifest.get("available_files", []))

    if manifest["case_id"] != case["case_id"]:
        blockers.add("CASE_ID_BINDING_MISMATCH")
    if manifest["event_family_id"] != provenance["source_group"]:
        blockers.add("EVENT_FAMILY_BINDING_MISMATCH")
    if _instant(manifest["analysis_cutoff"]) != _instant(inputs["analysis_cutoff"]):
        blockers.add("ANALYSIS_CUTOFF_BINDING_MISMATCH")

    spacecraft = manifest.get("spacecraft_pseudonym")
    if spacecraft is not None and spacecraft != inputs["spacecraft_context"]["spacecraft_id"]:
        blockers.add("SPACECRAFT_PSEUDONYM_BINDING_MISMATCH")

    for field, filename in _OPTIONAL_INPUT_FILES:
        has_entries = bool(inputs.get(field))
        declared = filename in declared_files
        if has_entries != declared:
            blockers.add("OPTIONAL_EVIDENCE_FILE_BINDING_MISMATCH")

    if not provenance["diagnosis_run_refs"]:
        blockers.add("DIAGNOSIS_RUN_REFERENCE_MISSING")
    if not provenance["source_artifact_hashes"]:
        blockers.add("SOURCE_ARTIFACT_HASH_MISSING")

    if manifest.get("outcome_status") in {None, "UNKNOWN"}:
        warnings.add("OUTCOME_NOT_INDEPENDENTLY_ADJUDICATED")
    if case["review"]["status"] == "APPROVED":
        warnings.add("CASE_APPROVAL_ASSERTION_NOT_INDEPENDENT_PROOF")
    if "expert_target.json" in declared_files:
        warnings.add("EXPERT_TARGET_FILE_DECLARATION_UNVERIFIED")
    if manifest.get("permission_status") == "AUTHORIZED_FOR_TRAINING":
        warnings.add("TRAINING_PERMISSION_ASSERTION_UNVERIFIED")

    synthetic_marker = _synthetic_case_marker(case)
    if synthetic_marker and manifest["source_class"] not in _SYNTHETIC_CLASSES:
        blockers.add("SYNTHETIC_CASE_MISDECLARED_REAL")

    if manifest["source_class"] in _SYNTHETIC_CLASSES:
        decision = "SYNTHETIC_TEST_ONLY"
    elif synthetic_marker or manifest_result["decision"] == "REJECT":
        decision = "REJECT"
    elif blockers:
        decision = "BLOCKED_BINDING"
    elif manifest_result["decision"] == "CONDITIONAL_ACCEPT":
        decision = "CONDITIONAL_ACCEPT"
    else:
        decision = "READY_FOR_MANUAL_SOURCE_AUDIT"

    return {
        "schema_version": "dgsi-handoff-case-binding-audit.v1",
        "decision": decision,
        "blocker_codes": sorted(blockers),
        "manifest_blocker_codes": manifest_result["blocker_codes"],
        "warning_codes": sorted(warnings | set(manifest_result["warning_codes"])),
        "case_content_authenticated": False,
        "source_rights_verified": False,
        "source_artifact_hashes_verified": False,
        "independent_expert_review_verified": False,
        "training_eligible": False,
        "gold_eligible": False,
        "split_assignment_allowed": False,
        "note": (
            "Untrusted metadata-to-Case field alignment only. Custodian must independently "
            "check original files, timestamps, source rights, hashes, run identity, "
            "expert outcome and incident family. No Gold or training approval."
        ),
    }
