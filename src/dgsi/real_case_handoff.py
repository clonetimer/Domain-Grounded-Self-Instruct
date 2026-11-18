"""Metadata-only review triage for DGSI real diagnostic case handoffs.

The manifest and its claims are untrusted. This module never opens source
packets, validates diagnosis truth, certifies intellectual-property rights, or
makes a sample eligible for Gold/training. Errors and reports omit identifiers.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from functools import lru_cache
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

_SCHEMA = Path(__file__).resolve().parents[2] / "resources" / "real_case_handoff.schema.json"
_REAL_SOURCE_CLASSES = frozenset({"REAL_FLIGHT", "REAL_GROUND_TEST", "ENGINEERING_TEST"})
_SYNTHETIC_SOURCE_CLASSES = frozenset({"SIMULATION", "SYNTHETIC_FIXTURE"})
_REQUIRED_INPUT_FILES = frozenset({
    "diagnosis_result.json", "spacecraft_context.json", "operational_context.json",
})
_LOG_FILES = frozenset({"diagnostic_logs.jsonl", "diagnostic_logs.csv"})


class RealCaseHandoffError(ValueError):
    """A payload-free code indicating an invalid or ambiguous handoff manifest."""


@lru_cache(maxsize=1)
def _validator() -> Draft202012Validator:
    schema = json.loads(_SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def load_handoff_manifest(text: str) -> dict[str, Any]:
    """Parse JSON without allowing duplicate keys or non-finite JSON numbers."""
    def unique_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        obj: dict[str, Any] = {}
        for key, value in pairs:
            if key in obj:
                raise RealCaseHandoffError("DUPLICATE_MANIFEST_JSON_KEY")
            obj[key] = value
        return obj

    def no_constant(_value: str) -> None:
        raise RealCaseHandoffError("NONFINITE_MANIFEST_JSON_NUMBER")

    if not isinstance(text, str):
        raise RealCaseHandoffError("MANIFEST_NOT_TEXT")
    try:
        result = json.loads(text, object_pairs_hook=unique_keys, parse_constant=no_constant)
    except RealCaseHandoffError:
        raise
    except (ValueError, TypeError):
        raise RealCaseHandoffError("INVALID_MANIFEST_JSON") from None
    if not isinstance(result, dict):
        raise RealCaseHandoffError("MANIFEST_NOT_OBJECT")
    return result


def _require_valid(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise RealCaseHandoffError("MANIFEST_NOT_OBJECT")
    error = next(_validator().iter_errors(manifest), None)
    if error is not None:
        raise RealCaseHandoffError(f"HANDOFF_SCHEMA_{str(error.validator).upper()}")
    try:
        cutoff = datetime.fromisoformat(manifest["analysis_cutoff"].replace("Z", "+00:00"))
    except (ValueError, TypeError, AttributeError):
        raise RealCaseHandoffError("INVALID_HANDOFF_ANALYSIS_CUTOFF") from None
    if cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise RealCaseHandoffError("INVALID_HANDOFF_ANALYSIS_CUTOFF")
    if any(not manifest[key].strip() for key in ("case_id", "event_family_id")):
        raise RealCaseHandoffError("INVALID_HANDOFF_PSEUDONYM")
    files = manifest.get("available_files", [])
    if len(files) != len(set(files)):
        raise RealCaseHandoffError("DUPLICATE_HANDOFF_FILE_ENTRY")
    return manifest


def assess_handoff_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Conservative metadata triage; an assertion is not a source verification."""
    manifest = _require_valid(manifest)
    source_class = manifest["source_class"]
    permission = manifest["permission_status"]
    redaction = manifest["redaction"]
    files = set(manifest.get("available_files", []))
    blockers: set[str] = set()
    warnings: set[str] = set()

    if source_class == "UNKNOWN":
        blockers.add("SOURCE_CLASS_UNKNOWN")
    if permission == "UNKNOWN":
        blockers.add("PERMISSION_NOT_ESTABLISHED")
    elif permission == "RESTRICTED_REVIEW_ONLY":
        blockers.add("RESTRICTED_LOCAL_REVIEW_ONLY")
    if not redaction["personal_identifiers_removed"]:
        blockers.add("PERSONAL_IDENTIFIERS_NOT_REMOVED")
    if not redaction["sensitive_ids_pseudonymized"]:
        blockers.add("SENSITIVE_IDENTIFIERS_NOT_PSEUDONYMIZED")
    if not isinstance(manifest.get("source_owner"), str) or not manifest["source_owner"].strip():
        blockers.add("SOURCE_OWNER_NOT_DOCUMENTED")
    if not _REQUIRED_INPUT_FILES.issubset(files):
        blockers.add("MISSING_CORE_INPUT_FILE_DECLARATION")
    if not files.intersection(_LOG_FILES):
        blockers.add("MISSING_DIAGNOSTIC_LOG_FILE_DECLARATION")
    if "expert_target.json" not in files:
        blockers.add("EXPERT_TARGET_NOT_DECLARED")
    if manifest.get("timestamp_policy") in {None, "PARTIALLY_UNKNOWN"}:
        blockers.add("TIMESTAMP_PROVENANCE_INCOMPLETE")
    if redaction["time_shifted"] != (manifest.get("timestamp_policy") == "CONSISTENTLY_SHIFTED"):
        blockers.add("INCONSISTENT_TIME_SHIFT_DECLARATION")
    if manifest.get("outcome_status", "UNKNOWN") == "UNKNOWN":
        warnings.add("OUTCOME_NOT_ADJUDICATED")
    if manifest.get("outcome_status") == "UNRESOLVED":
        warnings.add("OUTCOME_UNRESOLVED_PRESERVE_UNCERTAINTY")
    if source_class in _SYNTHETIC_SOURCE_CLASSES:
        decision = "SYNTHETIC_TEST_ONLY"
    elif source_class not in _REAL_SOURCE_CLASSES or permission == "UNKNOWN" or any(
        b in blockers for b in (
            "PERSONAL_IDENTIFIERS_NOT_REMOVED", "SENSITIVE_IDENTIFIERS_NOT_PSEUDONYMIZED",
        )
    ):
        decision = "REJECT"
    elif blockers:
        decision = "CONDITIONAL_ACCEPT"
    else:
        decision = "ACCEPT_FOR_EXPERT_REVIEW"

    return {
        "schema_version": "dgsi-handoff-metadata-audit.v1",
        "decision": decision,
        "blocker_codes": sorted(blockers),
        "warning_codes": sorted(warnings),
        "gold_eligible": False,
        "training_eligible": False,
        "authorization_verified_by_software": False,
        "source_content_reviewed": False,
        "note": "Metadata only; human source, permissions, temporal, evidence, and expert review remains mandatory.",
    }


def audit_handoff_cohort(manifests: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate-only batch triage; no identities or restricted text are returned.

    Even identical incident families may be legitimate related episodes. They
    must be grouped before any split; this function does not assign splits.
    """
    if not isinstance(manifests, list):
        raise RealCaseHandoffError("HANDOFF_COHORT_NOT_LIST")
    decisions = []
    case_ids: set[str] = set()
    family_counts: Counter[str] = Counter()
    for manifest in manifests:
        _require_valid(manifest)
        if manifest["case_id"] in case_ids:
            raise RealCaseHandoffError("DUPLICATE_HANDOFF_CASE_ID")
        case_ids.add(manifest["case_id"])
        family_counts[manifest["event_family_id"]] += 1
        decisions.append(assess_handoff_manifest(manifest)["decision"])
    counts = Counter(decisions)
    repeated = sum(count > 1 for count in family_counts.values())
    return {
        "schema_version": "dgsi-handoff-cohort-audit.v1",
        "case_count": len(manifests),
        "event_family_count": len(family_counts),
        "repeated_event_family_count": repeated,
        "decision_counts": {decision: counts[decision] for decision in (
            "ACCEPT_FOR_EXPERT_REVIEW", "CONDITIONAL_ACCEPT", "REJECT", "SYNTHETIC_TEST_ONLY"
        )},
        "split_assignment_allowed": False,
        "gold_eligible_count": 0,
        "note": "Repeated event families require manual grouping; no split, Gold or training approval is inferred.",
    }
