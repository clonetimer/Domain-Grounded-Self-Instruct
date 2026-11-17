"""Deterministic three-message preview; never an SFT exporter."""
from __future__ import annotations
import json
from typing import Any
from .l1_model_projection_audit import (
    L1ProjectionAuditError,
    audit_l1_synthetic_model_projection,
)

SYSTEM_CONTENT = (
    "你是航天器故障诊断二次研判助手。仅依据用户提供的当前场景证据、上游机器诊断结果、"
    "诊断日志、航天器构型、任务工况及明确标记的历史参考进行分析。区分故障源与受影响部件，"
    "保留证据不确定性；不得将历史参考当作当前直接证据，不得将建议或条件程序表述为已执行处置。"
    "输出符合任务结构的诊断报告。当前输入属于合成候选场景，不代表真实飞行或试验记录。"
)

def build_l1_preview(packet: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a deterministic preview shape in memory, with no split or release authority."""
    audit_l1_synthetic_model_projection(packet, source_fact_cards=source_fact_cards)
    case = packet["case"]
    user_payload = {
        "data_classification": "LITERATURE_DERIVED_SYNTHETIC_NOT_REAL_RECORD",
        "case_id": case["case_id"],
        "task_type": case["task_type"],
        "instruction": case["instruction"],
        "analysis_cutoff": case["input"]["analysis_cutoff"],
        "input": case["input"],
    }
    target = packet["formal_target"]
    messages = [
        {"role": "system", "content": SYSTEM_CONTENT},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
        {"role": "assistant", "content": json.dumps(target, ensure_ascii=False, sort_keys=True, separators=(",", ":"))},
    ]
    preview = {
        "preview_schema": "dgsi-three-message-preview.v1",
        "preview_only": True,
        "export_authorized": False,
        "split": None,
        "example_id": packet["task_id"],
        "case_ref": case["case_id"],
        "source_group": case["provenance"]["source_group"],
        "messages": messages,
    }
    # Round-trip the actual model-facing surface and compare against canonical source.
    parsed = json.loads(json.dumps(preview, ensure_ascii=False))
    if parsed != preview or len(parsed["messages"]) != 3:
        raise L1ProjectionAuditError("L1_PREVIEW_ROUND_TRIP_FAILED")
    if parsed["messages"][2]["content"] != json.dumps(target, ensure_ascii=False, sort_keys=True, separators=(",", ":")):
        raise L1ProjectionAuditError("L1_PREVIEW_CANONICAL_TARGET_DRIFT")
    if parsed["split"] is not None or parsed["export_authorized"] is not False:
        raise L1ProjectionAuditError("L1_PREVIEW_RELEASE_GATE_DRIFT")
    return parsed

def build_collection_preview(collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]]) -> dict[str, Any]:
    from .l1_model_projection_audit import audit_l1_synthetic_collection_projection
    audit = audit_l1_synthetic_collection_projection(collection, source_fact_cards=source_fact_cards)
    previews = [build_l1_preview(packet, source_fact_cards=source_fact_cards) for packet in collection["packets"]]
    return {
        "schema_version": "dgsi-three-message-preview-collection.v1",
        "decision": "PREVIEW_ONLY_BLOCKED_PENDING_EXTERNAL_ADMISSION",
        "collection_id": collection["collection_id"],
        "packet_count": len(previews),
        "event_family_count": audit["event_family_count"],
        "preview_records": previews,
        "sft_records_emitted": 0,
        "training_authorized": False,
        "gold_eligible": False,
        "official_splits_assigned": False,
    }
