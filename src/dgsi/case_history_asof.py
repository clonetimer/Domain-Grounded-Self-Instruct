"""Bind cited historical cases to as-of-cutoff memory evidence, without promoting truth.

This local-only audit reads an already validated diagnostic Case and the minimal,
explicitly supplied historical memory hit metadata. It does not retrieve memory,
inspect telemetry, authenticate provenance, or certify an expert-reviewed Gold
sample. Reports and exceptions intentionally never echo source identifiers.
"""
from __future__ import annotations

from typing import Any

from .diagnostic_context import validate_diagnostic_case
from .history_temporal_gate import screen_historical_memory_hit


class CaseHistoryAsOfError(ValueError):
    """Stable input-error code; never contains case material."""


_ALLOWED_HIT_FIELDS = frozenset({
    "case_id", "source_group_id", "verified_fault_id", "proposed_fault_id",
    "truth_source_ref", "reviewer", "equipment_scope", "snapshot", "status",
    "diagnostic_vote_allowed", "relation_status", "verified_at", "available_at",
    "approved_actions",
})


def _reject(code: str) -> None:
    raise CaseHistoryAsOfError(code)


def audit_case_history_asof(
    case: dict[str, Any],
    history_hits: list[dict[str, Any]],
    *,
    equipment_scope: str,
) -> dict[str, Any]:
    """Compare actual prompt history refs to verified pre-cutoff history hits.

    Only history explicitly marked CONFIRMED in the Case is eligible for
    timestamp screening. Unresolved, unknown, rejected or partially confirmed
    history remains in the prompt with its original qualification and requires
    manual review; a supplied confirmed hit must not silently override that
    qualification. This gate never adds or edits a prompt, target or source.
    """
    try:
        validate_diagnostic_case(case)
    except (ValueError, TypeError, KeyError, AttributeError):
        _reject("INVALID_DIAGNOSTIC_CASE")
    if not isinstance(history_hits, list):
        _reject("INVALID_HISTORY_HIT_BATCH")
    if not isinstance(equipment_scope, str) or not equipment_scope.strip():
        _reject("EQUIPMENT_SCOPE_REQUIRED")

    try:
        context = case["input"]["spacecraft_context"]
        components = {
            item for subsystem in context["subsystem_context"]
            for item in subsystem["components"]
            if isinstance(item, str)
        }
    except (TypeError, KeyError, AttributeError):
        _reject("INVALID_CASE_EQUIPMENT_CONTEXT")
    if equipment_scope not in components:
        _reject("EQUIPMENT_SCOPE_NOT_BOUND_TO_CASE")

    history = case["input"].get("historical_cases", [])
    refs = {entry["case_ref"]: entry["outcome_status"] for entry in history}
    if len(refs) != len(history):
        _reject("DUPLICATE_CASE_HISTORY_REFERENCE")

    hits: dict[str, dict[str, Any]] = {}
    for hit in history_hits:
        if not isinstance(hit, dict) or set(hit) - _ALLOWED_HIT_FIELDS:
            _reject("INVALID_HISTORY_HIT_SHAPE")
        ref = hit.get("case_id")
        if not isinstance(ref, str) or not ref.strip():
            _reject("HISTORY_HIT_REFERENCE_MISSING")
        if ref in hits:
            _reject("DUPLICATE_HISTORY_HIT_REFERENCE")
        hits[ref] = hit

    blockers: set[str] = set()
    review: set[str] = set()
    temporal_pass_count = 0
    for ref, outcome in refs.items():
        hit = hits.get(ref)
        if outcome == "CONFIRMED":
            if hit is None:
                blockers.add("CONFIRMED_HISTORY_HIT_MISSING")
                continue
            screened = screen_historical_memory_hit(
                hit,
                analysis_cutoff=case["input"]["analysis_cutoff"],
                current_source_group_id=case["provenance"]["source_group"],
                equipment_scope=equipment_scope,
            )
            if screened["decision"] == "BLOCKED":
                blockers.update(screened["blockers"])
            else:
                temporal_pass_count += 1
        elif hit is not None:
            blockers.add("UNCONFIRMED_HISTORY_CANNOT_BE_UPGRADED")
        else:
            review.add("NONCONFIRMED_HISTORY_REQUIRES_REVIEW")

    if set(hits) - set(refs):
        blockers.add("UNREFERENCED_HISTORY_HIT")
    decision = (
        "BLOCKED" if blockers else
        "MANUAL_HISTORY_REVIEW" if review else
        "PASS_ASOF_METADATA_ONLY" if refs else
        "NO_HISTORY_REFERENCES"
    )
    return {
        "schema_version": "dgsi-case-history-asof-binding.v1",
        "decision": decision,
        "history_reference_count": len(refs),
        "supplied_hit_count": len(hits),
        "temporally_screened_count": temporal_pass_count,
        "blocker_codes": sorted(blockers),
        "manual_review_codes": sorted(review),
        "gold_eligible": False,
        "training_authorized": False,
        "current_root_cause_confirmed": False,
        "source_authenticated": False,
        "note": (
            "Metadata binding and time comparison only; permission, historical "
            "source authenticity, expert independence and split leakage need separate audit."
        ),
    }
