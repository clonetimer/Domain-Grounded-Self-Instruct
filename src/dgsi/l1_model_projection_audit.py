"""SYNTHETIC pilot model-facing *projection audit*, not an SFT serializer.

Construct only an in-memory allowlisted shape and return fixed metadata/digests.
No prompt, target, source text, reviewer material, training row or Gold claim is
exported. A separate authenticated rights/review/release authority is required.
"""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Any

from .l1_task_packet import L1TaskPacketError, validate_l1_task_packet


class L1ProjectionAuditError(ValueError):
    """Fixed-code rejection: never echo case, input or target content."""


def _block(code: str) -> None:
    raise L1ProjectionAuditError(code)


# Versioned, case-specific templates already present in the 15-packet pilot.
# A future change requires independent instruction-template review.
_ALLOWED_INSTRUCTIONS = frozenset({
    "请结合上游机器诊断结果、诊断日志、航天器构型、任务工况及提供的历史经验，形成现象分析、原因定位、证据评价、不确定性和处置状态。仅依据当前输入作出结论。",
    "请结合上游机器诊断结果、诊断日志、航天器/试验构型、任务工况和文献证据，形成现象分析、原因定位、证据评价、不确定性和处置状态。严格区分历史来源事实与当前合成场景，不得将文献处置措施写成当前事件的已执行动作。",
    "请结合上游机器诊断结果、诊断日志、航天器构型和任务工况，判断历史案例是否适用于当前故障研判。保留历史案例的原始结论状态和硬件适用性限制，不得将历史经验作为当前根因确诊证据。",
})
_REQUIRED_INPUT_KEYS = frozenset({
    "machine_diagnosis", "diagnostic_logs", "spacecraft_context",
    "operational_context", "analysis_cutoff", "knowledge_evidence",
    "historical_cases", "raw_telemetry_included",
})
_OPTIONAL_INPUT_KEYS = frozenset({"telemetry_reference"})
_TARGET_KEYS = frozenset({
    "disposition", "phenomenon_analysis", "machine_result_interpretation",
    "cause_localization", "evidence_assessment",
    "historical_experience_relevance", "uncertainty", "disposal_status",
    "disposal_measures", "follow_up_actions", "report_text",
})
_CURATOR_ONLY_KEYS = frozenset({
    "internal_review", "not_for_sft", "curator_prompts",
    "alternative_hypotheses_to_check", "counterexamples",
    "reviewer_questions", "quality_flags", "blind_review",
    "adjudication_status", "reviewer_id", "reviewed_at",
    "synthetic_provenance", "source_fact_refs",
})


def _has_curator_keys(value: Any) -> bool:
    """Inspect keys, not free-text values: avoid false positives in log prose."""
    if isinstance(value, dict):
        return bool(_CURATOR_ONLY_KEYS.intersection(value)) or any(
            _has_curator_keys(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(_has_curator_keys(child) for child in value)
    return False


def _digest(value: Any) -> str:
    try:
        encoded = json.dumps(
            value, ensure_ascii=False, sort_keys=True,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError):
        _block("L1_PROJECTION_UNHASHABLE_CONTENT")
    return sha256(encoded).hexdigest()


def audit_l1_synthetic_model_projection(
    packet: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]
) -> dict[str, Any]:
    """Dry-run the explicit user/assistant allowlist; release stays blocked.

    The two digests are diagnostic integrity markers, not SFT rows or export
    authorization. Neither the case root nor packet root is copied wholesale
    into the candidate user surface. Only the synthetic track is supported.
    """
    if not isinstance(packet, dict) or not isinstance(packet.get("case"), dict):
        _block("L1_PROJECTION_PACKET_SHAPE_INVALID")
    if packet.get("track") != "LITERATURE_DERIVED_SYNTHETIC":
        _block("L1_PROJECTION_REAL_TRACK_NOT_AUTHORIZED")
    case = packet["case"]
    inputs, target = case.get("input"), packet.get("formal_target")
    if not isinstance(inputs, dict) or not isinstance(target, dict):
        _block("L1_PROJECTION_PACKET_SHAPE_INVALID")
    if _has_curator_keys(inputs) or _has_curator_keys(target):
        _block("L1_PROJECTION_CURATOR_FIELD_IN_MODEL_SURFACE")
    keys = set(inputs)
    if not _REQUIRED_INPUT_KEYS.issubset(keys) or keys - (
        _REQUIRED_INPUT_KEYS | _OPTIONAL_INPUT_KEYS
    ):
        _block("L1_PROJECTION_INPUT_ALLOWLIST_MISMATCH")
    if set(target) != _TARGET_KEYS:
        _block("L1_PROJECTION_TARGET_ALLOWLIST_MISMATCH")
    if inputs["raw_telemetry_included"] is not False:
        _block("L1_PROJECTION_RAW_TELEMETRY_NOT_ALLOWED")
    if case.get("instruction") not in _ALLOWED_INSTRUCTIONS:
        _block("L1_PROJECTION_UNREVIEWED_INSTRUCTION")

    try:
        validate_l1_task_packet(packet, source_fact_cards=source_fact_cards)
    except (L1TaskPacketError, KeyError, TypeError, ValueError):
        _block("L1_PROJECTION_SOURCE_PACKET_NOT_VALIDATED")

    # Deliberately reconstruct the *candidate* surfaces from individual fields;
    # never serialize or return them. Mark invented ML/log/context as such.
    user_candidate = {
        "case_id": case["case_id"],
        "task_type": case["task_type"],
        "instruction": case["instruction"],
        "data_classification": "SYNTHETIC_NOT_REAL_ML_OR_FLIGHT_LOG",
        "input": inputs,
    }
    assistant_candidate = target  # canonical packet.formal_target only
    return {
        "schema_version": "dgsi-l1-model-projection-preflight.v1",
        "decision": "BLOCKED_PENDING_EXTERNAL_ADMISSION",
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "user_projection_sha256": _digest(user_candidate),
        "formal_target_sha256": _digest(assistant_candidate),
        "explicit_synthetic_notice_in_candidate": True,
        "curator_subtree_in_candidate": False,
        "internal_review_exported": False,
        "sft_records_emitted": 0,
        "gold_eligible": False,
        "training_authorized": False,
    }


def audit_l1_synthetic_collection_projection(
    collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]
) -> dict[str, Any]:
    """Audit a *whole* synthetic candidate collection without exporting SFT rows.

    Per-packet projection success cannot certify collection membership, split
    isolation, or an omitted packet. Revalidate the collection and bind every
    candidate digest to its task, source group and literature references.
    This never assigns a split, admits Gold or returns input/target content.
    """
    if not isinstance(collection, dict):
        _block("L1_PROJECTION_COLLECTION_SHAPE_INVALID")
    if collection.get("track") != "LITERATURE_DERIVED_SYNTHETIC":
        _block("L1_PROJECTION_COLLECTION_REAL_TRACK_NOT_AUTHORIZED")
    if collection.get("split_assignments"):
        _block("L1_PROJECTION_COLLECTION_SPLIT_NOT_AUTHORIZED")
    # Security boundary before schema validation: an injected curator field
    # must receive the precise isolation rejection, not be obscured by a
    # generic invalid-case schema failure.
    packet_items = collection.get("packets")
    if isinstance(packet_items, list):
        for packet in packet_items:
            if not isinstance(packet, dict):
                continue
            case = packet.get("case")
            candidate_input = case.get("input") if isinstance(case, dict) else None
            if _has_curator_keys(candidate_input) or _has_curator_keys(
                packet.get("formal_target")
            ):
                _block("L1_PROJECTION_CURATOR_FIELD_IN_MODEL_SURFACE")
    try:
        from .l1_task_packet import validate_l1_task_packet_collection
        coverage = validate_l1_task_packet_collection(
            collection, source_fact_cards=source_fact_cards
        )
    except (L1TaskPacketError, KeyError, TypeError, ValueError):
        _block("L1_PROJECTION_COLLECTION_NOT_VALIDATED")

    entries: list[dict[str, Any]] = []
    for packet in collection["packets"]:
        audit = audit_l1_synthetic_model_projection(
            packet, source_fact_cards=source_fact_cards
        )
        entries.append({
            "task_id": packet["task_id"],
            "case_id": packet["case"]["case_id"],
            "source_group": packet["case"]["provenance"]["source_group"],
            "source_fact_refs": sorted(packet["source_fact_refs"]),
            "user_sha256": audit["user_projection_sha256"],
            "target_sha256": audit["formal_target_sha256"],
        })
    # Stable across JSON array ordering, but changes if membership, event
    # family, source refs, input or formal target changes.
    entries.sort(key=lambda item: item["task_id"])
    return {
        "schema_version": "dgsi-l1-model-projection-collection-preflight.v1",
        "decision": "BLOCKED_PENDING_EXTERNAL_ADMISSION",
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "packet_count": coverage["packet_count"],
        "event_family_count": coverage["event_family_count"],
        "collection_projection_sha256": _digest({
            "collection_id": collection["collection_id"],
            "entries": entries,
        }),
        "internal_review_exported": False,
        "sft_records_emitted": 0,
        "gold_eligible": False,
        "training_authorized": False,
    }
