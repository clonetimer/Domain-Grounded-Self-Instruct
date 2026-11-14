"""Time-safe screening of AstroGraph *historical* memory references.

AstroGraph confirmed memory is historical precedent, never current-event
ground truth. Its current retrieval hit omits available_at; DGSI must refuse
as-of-cutoff replay until an authorized upstream record supplies that timestamp.
No telemetry or memory case body is copied by this gate.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


class HistoryTemporalGateError(ValueError):
    """Payload-free invalid input error."""


def _datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None or result.utcoffset() is None:
        return None
    return result


def screen_historical_memory_hit(
    hit: dict[str, Any],
    *,
    analysis_cutoff: str,
    current_source_group_id: str,
    equipment_scope: str,
) -> dict[str, Any]:
    """Assess temporal eligibility using metadata only; never return hit content.

    This screens a single retrieval hit, not an authenticated source record.
    PASS_TEMPORAL_METADATA_ONLY still needs actual source/permissions and
    human adjudication. The current AstroGraph retrieve_confirmed payload
    does not carry available_at, so it will be blocked until enriched from
    an authorized, verified memory decision record.
    """
    if not isinstance(hit, dict):
        raise HistoryTemporalGateError("INVALID_HISTORY_HIT")
    cutoff = _datetime(analysis_cutoff)
    if cutoff is None:
        raise HistoryTemporalGateError("INVALID_ANALYSIS_CUTOFF")
    if not isinstance(equipment_scope, str) or not equipment_scope.strip() or (
        equipment_scope.strip().upper() in {"UNKNOWN", "UNSPECIFIED"}
    ):
        raise HistoryTemporalGateError("EQUIPMENT_SCOPE_REQUIRED")
    if not isinstance(current_source_group_id, str) or not current_source_group_id.strip():
        raise HistoryTemporalGateError("INCIDENT_FAMILY_REQUIRED")

    blockers: set[str] = set()
    if hit.get("status") != "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH":
        blockers.add("HISTORICAL_CONFIRMATION_NOT_ESTABLISHED")
    if hit.get("diagnostic_vote_allowed") is not False:
        blockers.add("HISTORICAL_CASE_CANNOT_VOTE_CURRENT_TRUTH")
    if hit.get("equipment_scope") != equipment_scope:
        blockers.add("EQUIPMENT_SCOPE_MISMATCH")
    if hit.get("source_group_id") == current_source_group_id:
        blockers.add("SAME_INCIDENT_FAMILY_REUSE")
    if not isinstance(hit.get("case_id"), str) or not hit["case_id"].strip():
        blockers.add("HISTORY_CASE_REFERENCE_MISSING")
    if not isinstance(hit.get("source_group_id"), str) or not hit["source_group_id"].strip():
        blockers.add("HISTORY_SOURCE_GROUP_MISSING")
    for key in ("verified_fault_id", "proposed_fault_id", "truth_source_ref", "reviewer"):
        if not isinstance(hit.get(key), str) or not hit[key].strip():
            blockers.add("HISTORY_" + key.upper() + "_MISSING")
    version = hit.get("snapshot")
    if type(version) is not int or version < 1:
        blockers.add("HISTORY_SNAPSHOT_UNVERIFIED")
    relation = hit.get("relation_status")
    if isinstance(hit.get("proposed_fault_id"), str) and isinstance(hit.get("verified_fault_id"), str):
        expected = (
            "CONSISTENT_HISTORICAL_CASE"
            if hit["proposed_fault_id"] == hit["verified_fault_id"]
            else "PRIOR_UPSTREAM_MISCLASSIFICATION"
        )
        if relation != expected:
            blockers.add("HISTORY_RELATION_STATUS_MISMATCH")

    # Do not substitute current wall-clock time for historical availability.
    available_at = _datetime(hit.get("available_at"))
    if available_at is None:
        blockers.add("HISTORY_AS_OF_AVAILABILITY_NOT_VERIFIED")
    elif available_at > cutoff:
        blockers.add("HISTORY_AVAILABLE_AFTER_ANALYSIS_CUTOFF")
    verified_at = _datetime(hit.get("verified_at"))
    if verified_at is None:
        blockers.add("HISTORY_INDEPENDENT_VERIFICATION_TIME_NOT_VERIFIED")
    elif verified_at > cutoff:
        blockers.add("HISTORY_VERIFIED_AFTER_ANALYSIS_CUTOFF")
    if available_at is not None and verified_at is not None and available_at < verified_at:
        blockers.add("HISTORY_AVAILABLE_BEFORE_VERIFICATION")

    return {
        "schema_version": "dgsi-history-temporal-screen.v1",
        "decision": "BLOCKED" if blockers else "PASS_TEMPORAL_METADATA_ONLY",
        "blockers": sorted(blockers),
        "blocker_count": len(blockers),
        "gold_eligible": False,
        "current_root_cause_confirmed": False,
        "requires_authenticated_source_and_independent_review": True,
        "note": (
            "Historical memory confirms at most a prior case; availability, reviewer "
            "independence, permission and incident identity require authorized audit."
        ),
    }
