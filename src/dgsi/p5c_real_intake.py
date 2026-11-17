"""Fail-closed, aggregate-only preflight for the five P5-C1 REAL candidates.

This is intentionally a *frozen intake snapshot* validator, not a Gold
admission workflow. Later evidence submissions must use separate receipts;
editing this register cannot manufacture validated upstream runs or reviews.
"""
from __future__ import annotations

from collections import Counter
from typing import Any


class RealCandidateIntakeError(ValueError):
    """Public fixed-code failure: no private case contents are echoed."""


def _block(code: str) -> None:
    raise RealCandidateIntakeError(code)


EXPECTED_CASES = {
    "USER-ADCS-SADA-001": ("ADCS", "SOURCE_RECORDS_MEASURE", "time_aligned_sensor_definitions"),
    "USER-COMM-TWTA-002": ("COMM", "SOURCE_RECORDS_TEXT", None),
    "USER-COMM-KU-TWTA-003": ("COMM", "SOURCE_RECORDS_CONDITIONAL_PROCEDURE", "protection_and_shutdown_state_evidence"),
    "USER-PROP-THRUSTER-004": ("PROPULSION", "SOURCE_RECORDS_MEASURE", "time_aligned_temperature_and_thrust_evidence"),
    "USER-ADCS-RW-BEARING-005": ("ADCS", "SOURCE_RECORDS_CONDITIONAL_MEASURE", "time_aligned_temperature_and_speed_evidence"),
}
_TOP_KEYS = frozenset({
    "schema_version", "intake_id", "track", "source_document",
    "case_count", "cases", "aggregate", "required_next_evidence", "policy",
})
_SOURCE_KEYS = frozenset({
    "name", "origin", "storage_policy", "content_reviewed_artifact", "review_scope",
})
_CASE_KEYS = frozenset({
    "case_id", "domain", "source_fact_status", "phenomenon_cause_available",
    "disposal_record_type", "disposal_text_present", "independent_case_review",
    "upstream_ml_result", "diagnostic_logs", "spacecraft_configuration",
    "mission_phase_and_operating_mode", "time_aligned_sensor_definitions",
    "protection_and_shutdown_state_evidence",
    "time_aligned_temperature_and_thrust_evidence",
    "time_aligned_temperature_and_speed_evidence",
    "disposal_execution_and_effectiveness", "target_adjudication",
    "sft_eligibility", "notes",
})
_REQUIRED_CASE_KEYS = _CASE_KEYS - frozenset({
    "time_aligned_sensor_definitions", "protection_and_shutdown_state_evidence",
    "time_aligned_temperature_and_thrust_evidence",
    "time_aligned_temperature_and_speed_evidence",
})
_AGGREGATE_KEYS = frozenset({
    "source_fact_cards_transcribed", "independent_expert_approved",
    "complete_dgsi_input_packets", "real_gold_admitted",
    "official_split_assignments", "authorized_sft_records", "training_authorized",
})
_POLICY_KEYS = frozenset({
    "no_synthetic_filling_of_missing_real_case_fields",
    "historical_experience_role", "do_not_convert_to_sft_until_complete_and_admitted",
    "source_document_not_committed",
})


def _object(value: Any, keys: frozenset[str], code: str, *, optional: frozenset[str] = frozenset()) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) - keys or keys - optional - set(value):
        _block(code)
    return value


def audit_real_candidate_intake(payload: dict[str, Any]) -> dict[str, Any]:
    """Audit *only* the frozen, incomplete five-case register.

    Success means BLOCKED_PENDING_REAL_EVIDENCE, not source authentication,
    expert approval, case independence, SFT eligibility or training rights.
    """
    item = _object(payload, _TOP_KEYS, "REAL_INTAKE_STRUCTURE_INVALID")
    if item["schema_version"] != "dgsi-real-case-candidate-intake.v1":
        _block("REAL_INTAKE_SCHEMA_INVALID")
    if item["track"] != "REAL_CASE_CANDIDATE":
        _block("REAL_INTAKE_TRACK_ESCALATION")
    if item["intake_id"] != "DGSI-P5C1-USER-CASES-2026-11-17":
        _block("REAL_INTAKE_ID_DRIFT")

    source = _object(item["source_document"], _SOURCE_KEYS, "REAL_INTAKE_SOURCE_INVALID")
    if (source["name"] != "故障案例参考.docx"
            or source["origin"] != "USER_SUPPLIED_WORD"
            or source["storage_policy"] != "SOURCE_DOCUMENT_REMAINS_IN_USER_LIBRARY; DO_NOT_COPY_RAW_DOCUMENT_OR_PRIVATE_DETAILS_TO_PUBLIC_REPOSITORY"):
        _block("REAL_INTAKE_SOURCE_INVALID")
    if not isinstance(source["content_reviewed_artifact"], str) or not source["content_reviewed_artifact"]:
        _block("REAL_INTAKE_SOURCE_INVALID")
    if not isinstance(source["review_scope"], str) or not source["review_scope"]:
        _block("REAL_INTAKE_SOURCE_INVALID")

    cases = item["cases"]
    if (not isinstance(cases, list) or type(item["case_count"]) is not int
            or item["case_count"] != len(EXPECTED_CASES) or len(cases) != len(EXPECTED_CASES)):
        _block("REAL_INTAKE_CASE_COUNT_DRIFT")

    seen: set[str] = set()
    domains: Counter[str] = Counter()
    disposals: Counter[str] = Counter()
    for raw in cases:
        case = _object(raw, _CASE_KEYS, "REAL_INTAKE_CASE_STRUCTURE_INVALID",
                       optional=_CASE_KEYS - _REQUIRED_CASE_KEYS)
        case_id = case["case_id"]
        if not isinstance(case_id, str) or case_id not in EXPECTED_CASES or case_id in seen:
            _block("REAL_INTAKE_CASE_ID_DRIFT")
        seen.add(case_id)
        domain, disposal, evidence_field = EXPECTED_CASES[case_id]
        if case["domain"] != domain or case["disposal_record_type"] != disposal:
            _block("REAL_INTAKE_CASE_SEMANTIC_DRIFT")
        if evidence_field is not None and case.get(evidence_field) != "MISSING":
            _block("REAL_INTAKE_UNVERIFIED_EVIDENCE")
        if case["source_fact_status"] != "USER_SUPPLIED_FACTS_TRANSCRIBED":
            _block("REAL_INTAKE_SOURCE_CLAIM_ESCALATION")
        if case["phenomenon_cause_available"] is not True or case["disposal_text_present"] is not True:
            _block("REAL_INTAKE_CASE_SEMANTIC_DRIFT")
        if (case["independent_case_review"] != "PENDING"
                or case["target_adjudication"] != "NOT_STARTED"
                or case["sft_eligibility"] is not False):
            _block("REAL_INTAKE_UNAUTHORIZED_PROMOTION")
        for field in (
            "upstream_ml_result", "diagnostic_logs", "spacecraft_configuration",
            "mission_phase_and_operating_mode", "disposal_execution_and_effectiveness",
        ):
            if case[field] != "MISSING":
                _block("REAL_INTAKE_UNVERIFIED_EVIDENCE")
        for key in _CASE_KEYS - _REQUIRED_CASE_KEYS:
            if key in case and case[key] != "MISSING":
                _block("REAL_INTAKE_UNVERIFIED_EVIDENCE")
        if (not isinstance(case["notes"], list)
                or not all(isinstance(note, str) for note in case["notes"])):
            _block("REAL_INTAKE_CASE_STRUCTURE_INVALID")
        domains[domain] += 1
        disposals[disposal] += 1

    if seen != set(EXPECTED_CASES):
        _block("REAL_INTAKE_CASE_ID_DRIFT")

    aggregate = _object(item["aggregate"], _AGGREGATE_KEYS, "REAL_INTAKE_AGGREGATE_INVALID")
    for key in _AGGREGATE_KEYS - {"training_authorized"}:
        required = len(EXPECTED_CASES) if key == "source_fact_cards_transcribed" else 0
        if type(aggregate[key]) is not int or aggregate[key] != required:
            _block("REAL_INTAKE_AGGREGATE_ESCALATION")
    if aggregate["training_authorized"] is not False:
        _block("REAL_INTAKE_UNAUTHORIZED_PROMOTION")

    policy = _object(item["policy"], _POLICY_KEYS, "REAL_INTAKE_POLICY_INVALID")
    if (policy["no_synthetic_filling_of_missing_real_case_fields"] is not True
            or policy["do_not_convert_to_sft_until_complete_and_admitted"] is not True
            or policy["source_document_not_committed"] is not True
            or policy["historical_experience_role"] != "CONTEXT_ONLY_NOT_DIRECT_CURRENT_EVENT_EVIDENCE"):
        _block("REAL_INTAKE_POLICY_INVALID")
    evidence_request = item["required_next_evidence"]
    if (not isinstance(evidence_request, list) or not evidence_request
            or not all(isinstance(v, str) and v for v in evidence_request)):
        _block("REAL_INTAKE_STRUCTURE_INVALID")

    return {
        "schema_version": "dgsi-real-candidate-intake-audit.v1",
        "decision": "BLOCKED_PENDING_REAL_EVIDENCE",
        "real_case_candidates": len(cases),
        "domains": dict(sorted(domains.items())),
        "source_disposal_notations": dict(sorted(disposals.items())),
        "independently_approved": 0,
        "complete_dgsi_input_packets": 0,
        "real_gold_admitted": 0,
        "official_splits": 0,
        "authorized_sft_records": 0,
        "training_authorized": False,
    }
