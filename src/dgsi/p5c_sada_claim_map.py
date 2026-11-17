"""Fail-closed, metadata-only audit for the SADA first REAL candidate claim map.

This is NOT evidence authentication, expert review, Gold admission or SFT release.
Curator prompts are held outside this public record; only opaque private refs
exist at Case root internal_review with not_for_sft=true.
"""
from __future__ import annotations

from typing import Any


class SadaClaimMapError(ValueError):
    """Stable, payload-free audit error."""


def _block(code: str) -> None:
    raise SadaClaimMapError(code)


_TOP = {
    "schema_version", "case_id", "track", "status", "source",
    "formal_source_claims", "internal_review", "required_dgsi_inputs",
    "target_admission", "source_handling",
}
_EXPECTED_CLAIMS = {
    "SADA-C01": ("OBSERVED_PHENOMENON", "输出总电流和主误差电压发生 3 次跌落",
                 "SOURCE_STATED_NOT_INDEPENDENTLY_VERIFIED",
                 ("original_parameter_time_series", "channel_dictionary", "timestamp_time_basis"),
                 "SOURCE_ATTRIBUTED_CASE_DESCRIPTION_ONLY"),
    "SADA-C02": ("OBSERVED_PHENOMENON", "轴温最高升至 181°C，壳温最高升至 150°C",
                 "SOURCE_STATED_NOT_INDEPENDENTLY_VERIFIED",
                 ("sensor_ids_and_physical_locations", "calibration_and_validity", "time_stamped_temperature_series"),
                 "SOURCE_ATTRIBUTED_CASE_DESCRIPTION_ONLY"),
    "SADA-C03": ("OBSERVED_PHENOMENON", "调整南太阳翼角度时出现堵转",
                 "SOURCE_STATED_NOT_INDEPENDENTLY_VERIFIED",
                 ("solar_array_angle_commands", "drive_state_and_stall_logs", "time_aligned_current_and_voltage"),
                 "SOURCE_ATTRIBUTED_CASE_DESCRIPTION_ONLY"),
    "SADA-C04": ("SOURCE_CAUSE_LOCALIZATION",
                 "盘环与电刷摩擦产生的碎屑引发内功率通路弧光放电，导致短路。",
                 "NOT_EXPLICITLY_STATED",
                 ("inspection_or_failure_analysis_for_brush_debris", "arc_or_short_circuit_test_evidence",
                  "disc_ring_brush_assembly_configuration"),
                 "SOURCE_ATTRIBUTED_CAUSE_HYPOTHESIS_NOT_EXPERT_CONFIRMED"),
    "SADA-C05": ("SOURCE_DISPOSAL", "停用南太阳翼",
                 None,
                 ("command_or_operation_record", "execution_timestamp", "post_shutdown_status_and_effect"),
                 "RECORDED_MEASURE_ONLY_NOT_VERIFIED_EXECUTION"),
}
_COMMON_CLAIM = {
    "claim_id", "claim_type", "source_text", "evidence_needed",
    "current_evidence_status", "allowed_current_use",
}
_INPUT_STATES = {
    "upstream_ml_result": "NOT_RECEIVED",
    "diagnostic_logs": "NOT_RECEIVED",
    "spacecraft_context": "NOT_RECEIVED",
    "history_context": "NOT_PROVIDED",
}
_REQUIRED_FALSE = {
    "complete_l1_input", "formal_assistant_target_created", "real_gold_admitted",
    "official_split_assigned", "sft_export_authorized", "training_authorized",
}
_HANDLING_TRUE = {
    "no_raw_logs_or_private_telemetry_in_repository",
    "no_synthetic_values_in_real_case",
    "source_attribution_must_be_preserved", "no_inferred_temporal_order",
    "no_claim_of_verified_execution_without_command_and_state_evidence",
}


def _object(value: Any, keys: set[str], code: str) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != keys:
        _block(code)
    return value


def audit_sada_claim_map(payload: Any) -> dict[str, Any]:
    """Read-only audit; success intentionally remains BLOCKED_PENDING_EVIDENCE."""
    item = _object(payload, _TOP, "SADA_MAP_STRUCTURE_INVALID")
    if (item["schema_version"] != "dgsi-real-case-claim-evidence-map.v1"
            or item["case_id"] != "USER-ADCS-SADA-001"
            or item["track"] != "REAL_CASE_CANDIDATE"
            or item["status"] != "SOURCE_FACTS_TRANSCRIBED_EVIDENCE_NOT_RECEIVED"):
        _block("SADA_MAP_TRACK_OR_STATUS_INVALID")

    source = _object(item["source"],
        {"artifact_ref", "page", "source_type", "source_sha256", "rights_and_training_use"},
        "SADA_MAP_SOURCE_INVALID")
    if (source["artifact_ref"] != "USER_LIBRARY:DGSI_用户原始5例_正式结论与内部审核分离_v0.1.docx"
            or type(source["page"]) is not int or source["page"] != 2
            or source["source_type"] != "USER_SUPPLIED_WORD_L0_FACT_CARD"
            or source["source_sha256"] is not None
            or source["rights_and_training_use"] != "PENDING_SOURCE_OWNER"):
        _block("SADA_MAP_SOURCE_INVALID")

    review = _object(item["internal_review"],
        {"not_for_sft", "storage", "curator_prompt_refs", "public_text_included"},
        "SADA_MAP_INTERNAL_REVIEW_INVALID")
    if (review["not_for_sft"] is not True
            or review["storage"] != "AUTHORIZED_PRIVATE_REVIEW_ONLY"
            or review["public_text_included"] is not False
            or review["curator_prompt_refs"] != ["SADA-IR-01", "SADA-IR-02", "SADA-IR-03"]):
        _block("SADA_MAP_INTERNAL_REVIEW_INVALID")

    claims = item["formal_source_claims"]
    if not isinstance(claims, list) or len(claims) != 5:
        _block("SADA_MAP_CLAIMS_INVALID")
    seen: set[str] = set()
    for claim in claims:
        if not isinstance(claim, dict) or not isinstance(claim.get("claim_id"), str):
            _block("SADA_MAP_CLAIMS_INVALID")
        cid = claim["claim_id"]
        if cid not in _EXPECTED_CLAIMS or cid in seen:
            _block("SADA_MAP_CLAIMS_INVALID")
        seen.add(cid)
        expected_keys = _COMMON_CLAIM | ({"source_certainty"} if cid != "SADA-C05" else
            {"disposal_record_type", "execution_status"}) | ({"fault_source_as_stated", "affected_objects_as_stated"} if cid == "SADA-C04" else set())
        _object(claim, expected_keys, "SADA_MAP_CLAIM_STRUCTURE_INVALID")
        kind, source_text, certainty, evidence, allowed_use = _EXPECTED_CLAIMS[cid]
        if (claim["claim_type"] != kind or claim["source_text"] != source_text
                or claim["evidence_needed"] != list(evidence)
                or claim["allowed_current_use"] != allowed_use):
            _block("SADA_MAP_SOURCE_CLAIM_DRIFT")
        if claim["current_evidence_status"] != "NOT_RECEIVED":
            _block("SADA_MAP_UNVERIFIED_EVIDENCE")
        if cid != "SADA-C05" and claim["source_certainty"] != certainty:
            _block("SADA_MAP_CERTAINTY_ESCALATION")
        if cid == "SADA-C04" and (
            claim["fault_source_as_stated"] != "SADA 盘环/电刷接触组件"
            or claim["affected_objects_as_stated"] != "南太阳翼驱动/供电相关通路；具体边界需依据原始系统定义"
        ):
            _block("SADA_MAP_SOURCE_CLAIM_DRIFT")
        if cid == "SADA-C05" and (
            claim["disposal_record_type"] != "SOURCE_RECORDS_MEASURE"
            or claim["execution_status"] != "NOT_STATED_IN_SOURCE"
        ):
            _block("SADA_MAP_DISPOSAL_ESCALATION")
    if seen != set(_EXPECTED_CLAIMS):
        _block("SADA_MAP_CLAIMS_INVALID")

    inputs = _object(item["required_dgsi_inputs"], set(_INPUT_STATES), "SADA_MAP_INPUTS_INVALID")
    for name, status in _INPUT_STATES.items():
        expected = {"status", "rule"} if name == "history_context" else {"status", "required"}
        detail = _object(inputs[name], expected, "SADA_MAP_INPUTS_INVALID")
        if detail["status"] != status:
            _block("SADA_MAP_UNVERIFIED_EVIDENCE")
        if name == "history_context":
            if detail["rule"] != "CONTEXT_ONLY_NOT_DIRECT_CURRENT_EVENT_EVIDENCE":
                _block("SADA_MAP_HISTORY_ESCALATION")
        elif (not isinstance(detail["required"], list) or not detail["required"]
                or len(set(map(str, detail["required"]))) != len(detail["required"])
                or not all(isinstance(x, str) and x for x in detail["required"])):
            _block("SADA_MAP_INPUTS_INVALID")

    admission = _object(item["target_admission"],
        _REQUIRED_FALSE | {"l0_fact_card_preserved", "independent_reviews_complete"},
        "SADA_MAP_ADMISSION_INVALID")
    if admission["l0_fact_card_preserved"] is not True:
        _block("SADA_MAP_ADMISSION_INVALID")
    if type(admission["independent_reviews_complete"]) is not int or admission["independent_reviews_complete"] != 0:
        _block("SADA_MAP_UNAUTHORIZED_PROMOTION")
    if any(admission[k] is not False for k in _REQUIRED_FALSE):
        _block("SADA_MAP_UNAUTHORIZED_PROMOTION")

    handling = _object(item["source_handling"], _HANDLING_TRUE, "SADA_MAP_HANDLING_INVALID")
    if any(handling[k] is not True for k in _HANDLING_TRUE):
        _block("SADA_MAP_HANDLING_INVALID")
    return {
        "decision": "BLOCKED_PENDING_REAL_EVIDENCE",
        "source_attributed_claims": len(claims),
        "received_case_specific_evidence": 0,
        "private_curator_prompt_refs": len(review["curator_prompt_refs"]),
        "sft_eligible": False,
        "training_authorized": False,
    }
