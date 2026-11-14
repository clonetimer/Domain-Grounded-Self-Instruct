"""Validation helpers for diagnosis-context SFT cases.

This layer validates the LLM-facing packet, not raw telemetry or upstream ML
correctness. It is intentionally dependency-free and fail-closed.
"""
from __future__ import annotations

import re
import math
from datetime import datetime
from collections import defaultdict
from typing import Any

from .schema_validation import SchemaContractError, validate_payload_schema

HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
TASK_TYPES = {
    "diagnostic_synthesis",
    "historical_case_reuse",
    "conflict_reconciliation",
    "evidence_sufficiency",
    "next_step_recommendation",
    "handover_summary",
}
SPLITS = {"train", "validation", "test"}
ROLES = ["system", "user", "assistant"]
FORBIDDEN_TELEMETRY_KEYS = {
    "telemetry",
    "raw_telemetry",
    "telemetry_rows",
    "waveform",
    "waveforms",
    "time_series",
    "timeseries",
    "samples",
    "raw_signal",
    "injection_truth",
    "fault_truth",
    "ground_truth",
    "hidden_label",
    "gold_label",
    "fault_label",
    "labels_used",
    "truth_used",
    "expected_output",
}


class DiagnosticContextValidationError(ValueError):
    """Raised when a diagnostic-context packet violates the SFT contract."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise DiagnosticContextValidationError(message)


def _nonempty(value: Any, field: str) -> None:
    _require(isinstance(value, str) and bool(value.strip()), f"{field} must be a non-empty string")


def _string_list(value: Any, field: str) -> None:
    _require(isinstance(value, list), f"{field} must be a list")
    for index, item in enumerate(value):
        _nonempty(item, f"{field}[{index}]")


def _reject_raw_telemetry(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_")
            _require(
                normalized not in FORBIDDEN_TELEMETRY_KEYS,
                f"raw telemetry field is forbidden in LLM input: {path}.{key}",
            )
            _reject_raw_telemetry(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_raw_telemetry(child, f"{path}[{index}]")



def _validate_evidence_reference_integrity(case: dict[str, Any]) -> None:
    """Check evidence IDs cited by the target against the supplied case packet.

    Machine evidence IDs are *declared* by upstream findings; this gate checks
    referential consistency, not whether the upstream evidence is authentic.
    """
    inputs = case["input"]
    expected = case["expected_output"]
    findings = inputs["machine_diagnosis"]["findings"]
    machine_finding_ids = [item["finding_id"] for item in findings]
    machine_evidence_ids = {
        ref for finding in findings for ref in finding.get("supporting_evidence_ids", [])
    }
    log_ids = [item["log_id"] for item in inputs["diagnostic_logs"]]
    knowledge_ids = [item["evidence_id"] for item in inputs.get("knowledge_evidence", [])]
    history_ids = [item["case_ref"] for item in inputs.get("historical_cases", [])]

    for group, code in (
        (machine_finding_ids, "DUPLICATE_MACHINE_FINDING_ID"),
        (knowledge_ids, "DUPLICATE_KNOWLEDGE_EVIDENCE_ID"),
        (history_ids, "DUPLICATE_HISTORICAL_CASE_REFERENCE"),
    ):
        _require(len(group) == len(set(group)), code)

    # All citations must resolve unambiguously to one namespace. Machine
    # evidence may legitimately support several different upstream findings.
    groups = [
        set(machine_finding_ids), machine_evidence_ids,
        set(log_ids), set(knowledge_ids), set(history_ids),
    ]
    seen: set[str] = set()
    for group in groups:
        _require(not (seen & group), "AMBIGUOUS_CROSS_SOURCE_EVIDENCE_ID")
        seen.update(group)

    evidence = expected["evidence_assessment"]
    refs = [*evidence["supporting_refs"], *evidence["contradicting_refs"]]
    for candidate in expected["fault_source_assessment"]["candidates"]:
        refs.extend(candidate["supporting_refs"])
    _require(all(ref in seen for ref in refs), "UNRESOLVED_EXPECTED_EVIDENCE_REFERENCE")

    previous_cases = set(history_ids)
    _require(
        all(item["case_ref"] in previous_cases for item in expected.get("historical_experience_relevance", [])),
        "UNRESOLVED_HISTORICAL_EXPERIENCE_REFERENCE",
    )
    _require(
        all(ref in previous_cases for ref in case["provenance"].get("historical_case_refs", [])),
        "UNRESOLVED_PROVENANCE_HISTORY_REFERENCE",
    )


def validate_diagnostic_case(case: dict[str, Any]) -> list[str]:
    """Validate a diagnosis-result/log/context case and return non-fatal warnings."""
    _require(isinstance(case, dict), "case must be an object")
    _require(case.get("schema_version") == "dgsi-diagnostic-case.v1", "unsupported case schema_version")
    _nonempty(case.get("case_id"), "case_id")
    _require(case.get("domain") in {"adcs", "eps", "comm", "thermal", "integrated"}, "unsupported domain")
    _require(case.get("task_type") in TASK_TYPES, "unsupported task_type")

    inputs = case.get("input")
    _require(isinstance(inputs, dict), "input must be an object")
    _require(inputs.get("raw_telemetry_included") is False, "raw_telemetry_included must be false")
    _reject_raw_telemetry({k: v for k, v in inputs.items() if k not in {"telemetry_reference"}})

    machine = inputs.get("machine_diagnosis")
    _require(isinstance(machine, dict), "machine_diagnosis is required")
    producer = machine.get("producer")
    _require(isinstance(producer, dict), "machine_diagnosis.producer is required")
    _nonempty(producer.get("method"), "machine_diagnosis.producer.method")
    _nonempty(producer.get("version"), "machine_diagnosis.producer.version")
    _nonempty(machine.get("analysis_scope"), "machine_diagnosis.analysis_scope")
    _require(
        machine.get("status") in {
            "NORMAL", "ANOMALY", "FAULT_CANDIDATE", "MULTIPLE_CANDIDATES",
            "INSUFFICIENT_DATA", "DATA_QUALITY_ERROR",
        },
        "unsupported machine diagnosis status",
    )
    findings = machine.get("findings")
    _require(isinstance(findings, list), "machine_diagnosis.findings must be a list")
    for index, finding in enumerate(findings):
        prefix = f"machine_diagnosis.findings[{index}]"
        _require(isinstance(finding, dict), f"{prefix} must be an object")
        for field in ("finding_id", "finding_type", "target", "result"):
            _nonempty(finding.get(field), f"{prefix}.{field}")
        if finding.get("score") is not None:
            score = finding["score"]
            _require(isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(float(score)), f"{prefix}.score must be finite numeric or null")
            _nonempty(finding.get("score_semantics"), f"{prefix}.score_semantics is required whenever score is supplied")
        _string_list(finding.get("supporting_evidence_ids", []), f"{prefix}.supporting_evidence_ids")
        _string_list(finding.get("limitations", []), f"{prefix}.limitations")

    cutoff_text = inputs.get("analysis_cutoff")
    _nonempty(cutoff_text, "input.analysis_cutoff")
    try:
        cutoff = datetime.fromisoformat(cutoff_text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise DiagnosticContextValidationError("input.analysis_cutoff must be ISO-8601") from exc
    _require(cutoff.tzinfo is not None, "input.analysis_cutoff must include a timezone")

    logs = inputs.get("diagnostic_logs")
    _require(isinstance(logs, list), "diagnostic_logs must be a list")
    log_ids: set[str] = set()
    for index, log in enumerate(logs):
        prefix = f"diagnostic_logs[{index}]"
        _require(isinstance(log, dict), f"{prefix} must be an object")
        for field in ("log_id", "timestamp", "log_type", "content"):
            if field == "timestamp" and log.get(field) is None:
                continue
            _nonempty(log.get(field), f"{prefix}.{field}")
        _require(log["log_id"] not in log_ids, f"duplicate diagnostic log id: {log['log_id']}")
        log_ids.add(log["log_id"])
        if log.get("timestamp") is not None:
            try:
                log_time = datetime.fromisoformat(str(log["timestamp"]).replace("Z", "+00:00"))
            except ValueError as exc:
                raise DiagnosticContextValidationError(f"{prefix}.timestamp must be ISO-8601") from exc
            _require(log_time.tzinfo is not None, f"{prefix}.timestamp must include a timezone")
            _require(log_time <= cutoff, f"{prefix} occurs after analysis_cutoff; post-decision information leakage")

    spacecraft = inputs.get("spacecraft_context")
    _require(isinstance(spacecraft, dict), "spacecraft_context is required")
    _nonempty(spacecraft.get("spacecraft_id"), "spacecraft_context.spacecraft_id")
    _require(isinstance(spacecraft.get("configuration"), dict), "spacecraft_context.configuration must be an object")
    subsystems = spacecraft.get("subsystem_context")
    _require(isinstance(subsystems, list), "spacecraft_context.subsystem_context must be a list")
    for index, subsystem in enumerate(subsystems):
        _require(isinstance(subsystem, dict), f"subsystem_context[{index}] must be an object")
        _nonempty(subsystem.get("subsystem"), f"subsystem_context[{index}].subsystem")
        _string_list(subsystem.get("components"), f"subsystem_context[{index}].components")

    operational = inputs.get("operational_context")
    _require(isinstance(operational, dict), "operational_context is required")
    _nonempty(operational.get("mission_phase"), "operational_context.mission_phase")
    _nonempty(operational.get("operating_mode"), "operational_context.operating_mode")

    for index, history in enumerate(inputs.get("historical_cases", [])):
        prefix = f"historical_cases[{index}]"
        _require(isinstance(history, dict), f"{prefix} must be an object")
        for field in ("case_ref", "prior_conclusion", "outcome_status"):
            _nonempty(history.get(field), f"{prefix}.{field}")
        _string_list(history.get("similarity_basis", []), f"{prefix}.similarity_basis")
        _string_list(history.get("applicability_limitations", []), f"{prefix}.applicability_limitations")

    for index, evidence in enumerate(inputs.get("knowledge_evidence", [])):
        prefix = f"knowledge_evidence[{index}]"
        _require(isinstance(evidence, dict), f"{prefix} must be an object")
        for field in ("evidence_id", "source_id", "passage_id", "claim_boundary"):
            _nonempty(evidence.get(field), f"{prefix}.{field}")

    expected = case.get("expected_output")
    _require(isinstance(expected, dict), "expected_output must be an object")
    _require(expected.get("disposition") in {
        "ACCEPT_MACHINE_FINDING", "ACCEPT_WITH_QUALIFICATION", "REQUEST_ADDITIONAL_ANALYSIS",
        "CONFLICTING_EVIDENCE", "INSUFFICIENT_CONTEXT", "NO_FAULT_INDICATED",
    }, "unsupported expected disposition")
    fault = expected.get("fault_source_assessment")
    _require(isinstance(fault, dict), "fault_source_assessment is required")
    _require(fault.get("status") in {"SUPPORTED", "CANDIDATE_ONLY", "UNRESOLVED", "NOT_APPLICABLE"}, "unsupported fault-source status")
    _string_list(fault.get("affected_components"), "fault_source_assessment.affected_components")
    evidence_assessment = expected.get("evidence_assessment")
    _require(isinstance(evidence_assessment, dict), "evidence_assessment is required")
    for field in ("supporting_refs", "contradicting_refs", "missing_information"):
        _string_list(evidence_assessment.get(field), f"evidence_assessment.{field}")
    uncertainty = expected.get("uncertainty")
    _require(isinstance(uncertainty, dict), "uncertainty is required")
    _require(uncertainty.get("level") in {"LOW", "MODERATE", "HIGH", "UNRESOLVED"}, "unsupported uncertainty level")
    _string_list(uncertainty.get("reasons"), "uncertainty.reasons")
    _require(isinstance(expected.get("recommended_next_steps"), list), "recommended_next_steps must be a list")

    provenance = case.get("provenance")
    _require(isinstance(provenance, dict), "provenance is required")
    _nonempty(provenance.get("source_group"), "provenance.source_group")
    hashes = provenance.get("source_artifact_hashes")
    _require(isinstance(hashes, list), "source_artifact_hashes must be a list")
    for index, digest in enumerate(hashes):
        _require(isinstance(digest, str) and bool(HEX_SHA256.fullmatch(digest)), f"source_artifact_hashes[{index}] must be lowercase SHA-256")

    review = case.get("review")
    _require(isinstance(review, dict), "review is required")
    _require(review.get("status") in {"DRAFT", "REVIEW_REQUIRED", "APPROVED", "REJECTED"}, "unsupported review status")

    try:
        validate_payload_schema("case", case)
    except SchemaContractError as exc:
        raise DiagnosticContextValidationError(str(exc)) from exc
    _validate_evidence_reference_integrity(case)

    warnings: list[str] = []
    if not logs:
        warnings.append("NO_DIAGNOSTIC_LOGS")
    if not inputs.get("historical_cases"):
        warnings.append("NO_HISTORICAL_EXPERIENCE")
    if not inputs.get("knowledge_evidence"):
        warnings.append("NO_REGISTERED_KNOWLEDGE_EVIDENCE")
    if review.get("status") != "APPROVED":
        warnings.append("NOT_GOLD_REVIEWED")
    return warnings



# A case's expected answer and expert adjudication are targets/metadata, NEVER
# user-facing evidence. This check catches serialized JSON fields embedded in
# a chat message, including the nested full-case leak in the original fixture.
# It is deliberately conservative and not a substitute for source inspection.
_FORBIDDEN_PROMPT_JSON_KEYS = re.compile(
    r'"(?:expected_output|review|answer_key|target_report|gold_answer|'
    r'ground_truth|fault_truth|injection_truth|hidden_label|gold_label|'
    r'labels_used|truth_used|raw_telemetry|telemetry_rows|waveforms?|'
    r'time_series|timeseries|raw_signal|samples)"\s*:',
    re.IGNORECASE,
)


def _reject_sft_target_leakage(user_prompt: str) -> None:
    match = _FORBIDDEN_PROMPT_JSON_KEYS.search(user_prompt)
    _require(
        match is None,
        "SFT user prompt contains a forbidden target, review, truth or raw-telemetry JSON key",
    )


def validate_sft_example(example: dict[str, Any]) -> None:
    """Validate a chat SFT example and enforce its provenance/review boundary."""
    _require(isinstance(example, dict), "SFT example must be an object")
    _require(example.get("schema_version") == "dgsi-diagnostic-sft.v1", "unsupported SFT schema_version")
    _nonempty(example.get("example_id"), "example_id")
    _require(example.get("task_type") in TASK_TYPES, "unsupported SFT task_type")
    messages = example.get("messages")
    _require(isinstance(messages, list) and len(messages) == 3, "messages must contain exactly system/user/assistant")
    _require([m.get("role") for m in messages if isinstance(m, dict)] == ROLES, "messages roles must be system/user/assistant")
    for index, message in enumerate(messages):
        _nonempty(message.get("content"), f"messages[{index}].content")
    _require("raw telemetry" in messages[1]["content"].lower() or "原始遥测" in messages[1]["content"], "user prompt must state the raw-telemetry boundary")
    _reject_sft_target_leakage(messages[1]["content"])
    _nonempty(example.get("case_ref"), "case_ref")
    _nonempty(example.get("source_group"), "source_group")
    _require(example.get("split") in SPLITS, "unsupported split")
    provenance = example.get("provenance")
    _require(isinstance(provenance, dict), "provenance is required")
    for field in ("diagnosis_result_refs", "diagnostic_log_refs", "context_refs", "knowledge_passage_ids", "source_artifact_hashes"):
        _string_list(provenance.get(field), f"provenance.{field}")
    for index, digest in enumerate(provenance["source_artifact_hashes"]):
        _require(bool(HEX_SHA256.fullmatch(digest)), f"provenance.source_artifact_hashes[{index}] must be lowercase SHA-256")
    review = example.get("review")
    _require(isinstance(review, dict), "review is required")
    _require(review.get("status") in {"REVIEW_REQUIRED", "APPROVED", "REJECTED"}, "unsupported SFT review status")
    try:
        validate_payload_schema("sft", example)
    except SchemaContractError as exc:
        raise DiagnosticContextValidationError(str(exc)) from exc


def audit_split_groups(examples: list[dict[str, Any]]) -> dict[str, Any]:
    """Reject one source_group or case_ref appearing in multiple dataset splits."""
    groups: dict[str, set[str]] = defaultdict(set)
    cases: dict[str, set[str]] = defaultdict(set)
    for index, example in enumerate(examples):
        _require(isinstance(example, dict), f"examples[{index}] must be an object")
        group = example.get("source_group")
        case_ref = example.get("case_ref")
        split = example.get("split")
        _nonempty(group, f"examples[{index}].source_group")
        _nonempty(case_ref, f"examples[{index}].case_ref")
        _require(split in SPLITS, f"examples[{index}].split is invalid")
        groups[group].add(split)
        cases[case_ref].add(split)
    leaking_groups = sorted(key for key, values in groups.items() if len(values) > 1)
    leaking_cases = sorted(key for key, values in cases.items() if len(values) > 1)
    _require(not leaking_groups, f"source_group leakage across splits: {leaking_groups}")
    _require(not leaking_cases, f"case_ref leakage across splits: {leaking_cases}")
    return {
        "example_count": len(examples),
        "source_group_count": len(groups),
        "case_count": len(cases),
        "split_counts": {split: sum(1 for item in examples if item["split"] == split) for split in sorted(SPLITS)},
        "leaking_source_groups": leaking_groups,
        "leaking_cases": leaking_cases,
    }


def evaluate_case_readiness(case: dict[str, Any]) -> dict[str, Any]:
    """Assess whether a structurally valid case may enter expert review for Gold SFT.

    This is a fail-closed intake gate, not an automated scientific approval.
    """
    warnings = validate_diagnostic_case(case)
    inputs = case["input"]
    provenance = case["provenance"]
    review = case["review"]
    blockers: list[str] = []

    if not provenance.get("diagnosis_run_refs"):
        blockers.append("MISSING_UPSTREAM_DIAGNOSIS_RUN_REFERENCE")
    if not provenance.get("source_artifact_hashes"):
        blockers.append("MISSING_SOURCE_ARTIFACT_HASH")
    producer = inputs["machine_diagnosis"]["producer"]
    if producer.get("method") == "NOT_RECORDED" or producer.get("version") == "NOT_RECORDED":
        blockers.append("UPSTREAM_ALGORITHM_PROVENANCE_INCOMPLETE")
    if not inputs.get("diagnostic_logs"):
        blockers.append("MISSING_DIAGNOSTIC_LOGS")
    if any(not log.get("timestamp") for log in inputs.get("diagnostic_logs", [])):
        blockers.append("DIAGNOSTIC_LOG_TIMESTAMP_INCOMPLETE")
    if not inputs["spacecraft_context"].get("configuration"):
        blockers.append("MISSING_SPACECRAFT_CONFIGURATION")
    if not inputs.get("operational_context", {}).get("mission_phase") or not inputs.get("operational_context", {}).get("operating_mode"):
        blockers.append("MISSING_OPERATIONAL_CONTEXT")
    if not inputs.get("knowledge_evidence") and any(
        claim_type in {"MECHANISM", "CAUSAL"}
        for claim_type in case.get("expected_output", {}).get("claim_types", [])
    ):
        blockers.append("MISSING_KNOWLEDGE_SUPPORT_FOR_MECHANISM_OR_CAUSAL_CLAIM")
    if review.get("status") == "APPROVED":
        if not review.get("reviewer_id"):
            blockers.append("APPROVED_WITHOUT_REVIEWER_ID")
        if not review.get("reviewed_at"):
            blockers.append("APPROVED_WITHOUT_REVIEW_TIMESTAMP")
    else:
        blockers.append("EXPERT_APPROVAL_REQUIRED")

    # A history item may be absent in a new incident, but it must not be fabricated.
    if not inputs.get("historical_cases"):
        warnings.append("HISTORICAL_CASE_NOT_AVAILABLE")

    return {
        "schema_version": "dgsi-case-readiness.v1",
        "decision": "BLOCKED" if blockers else "READY_FOR_EXPERT_GOLD_REVIEW",
        "gold_eligible": False,
        "blockers": sorted(set(blockers)),
        "warnings": sorted(set(warnings)),
        "note": "READY_FOR_EXPERT_GOLD_REVIEW is not Gold approval; only the authorized expert review workflow may approve a Gold case.",
    }
