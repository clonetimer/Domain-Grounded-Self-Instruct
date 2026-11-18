"""Conservative adapters for upstream AstroGraph diagnosis-result contracts.

These adapters translate already-produced diagnosis metadata for LLM review.
They never read telemetry and never turn an upstream candidate into confirmed truth.
"""
from __future__ import annotations

import math
from typing import Any

from .diagnostic_context import DiagnosticContextValidationError


class UpstreamDiagnosisAdapterError(ValueError):
    """Raised when an upstream diagnosis result cannot safely be exposed to the LLM."""


def normalize_astrograph_diagnosis_result(
    result: dict[str, Any],
    *,
    producer_method: str | None = None,
    producer_version: str | None = None,
    model_id: str | None = None,
) -> dict[str, Any]:
    """Normalize unified or legacy AstroGraph result JSON without inferring root cause."""
    if not isinstance(result, dict):
        raise UpstreamDiagnosisAdapterError("upstream diagnosis result must be an object")

    # Treat unknown or malformed provenance flags as unsafe, not as False.
    # Legacy packets may omit flags; that absence is a separate source-audit
    # blocker, not proof that labels/truth were excluded upstream.
    for field in ("truth_used", "labels_used"):
        if field in result and result[field] is not False:
            raise UpstreamDiagnosisAdapterError("UPSTREAM_TRUTH_OR_LABEL_PROVENANCE_UNSAFE")

    is_unified = result.get("schema_version") == "astrograph-unified-diagnosis.v1"
    if is_unified:
        if result.get("truth_used") is not False or result.get("labels_used") is not False:
            raise UpstreamDiagnosisAdapterError("UNVERIFIED_UNIFIED_TRUTH_OR_LABEL_FLAGS")
        status_map = {
            "DIAGNOSED": "FAULT_CANDIDATE",
            "NORMAL": "NORMAL",
            "AMBIGUOUS": "MULTIPLE_CANDIDATES",
            "UNKNOWN_FAULT": "FAULT_CANDIDATE",
            "INSUFFICIENT_DATA": "INSUFFICIENT_DATA",
            "DATA_ERROR": "DATA_QUALITY_ERROR",
            "CONFLICTING_EVIDENCE": "MULTIPLE_CANDIDATES",
        }
        status = status_map.get(result.get("status"))
        if status is None:
            raise UpstreamDiagnosisAdapterError("UNSUPPORTED_UNIFIED_DIAGNOSIS_STATUS")
        candidates = result.get("candidates", [])
        if not isinstance(candidates, list):
            raise UpstreamDiagnosisAdapterError("INVALID_UNIFIED_CANDIDATES")
        evidence_items = result.get("diagnostic_evidence", [])
        if not isinstance(evidence_items, list):
            raise UpstreamDiagnosisAdapterError("INVALID_UNIFIED_EVIDENCE_LIST")
        evidence_ids: set[str] = set()
        for item in evidence_items:
            if not isinstance(item, dict) or not isinstance(item.get("evidence_id"), str) or not item["evidence_id"].strip():
                raise UpstreamDiagnosisAdapterError("UNIFIED_EVIDENCE_ID_MISSING")
            if item["evidence_id"] in evidence_ids:
                raise UpstreamDiagnosisAdapterError("DUPLICATE_UNIFIED_EVIDENCE_ID")
            evidence_ids.add(item["evidence_id"])
        seen_effect_ids: set[str] = set()
        findings: list[dict[str, Any]] = []
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict) or not isinstance(candidate.get("effect_id"), str) or not candidate["effect_id"].strip():
                raise UpstreamDiagnosisAdapterError("INVALID_UNIFIED_CANDIDATE_EFFECT_ID")
            if candidate["effect_id"] in seen_effect_ids:
                raise UpstreamDiagnosisAdapterError("DUPLICATE_UNIFIED_CANDIDATE_EFFECT_ID")
            seen_effect_ids.add(candidate["effect_id"])
            score = candidate.get("screening_score")
            if score is not None and (type(score) not in (float, int) or not 0 <= score <= 1 or not math.isfinite(score)):
                raise UpstreamDiagnosisAdapterError("INVALID_UNIFIED_SCREENING_SCORE")
            for key in ("support_engines", "contradicting_engines"):
                engines = candidate.get(key, [])
                if not isinstance(engines, list) or any(not isinstance(v, str) or not v.strip() for v in engines):
                    raise UpstreamDiagnosisAdapterError("INVALID_UNIFIED_ENGINE_REFERENCES")
            findings.append({
                "finding_id": f"ASTROGRAPH-CANDIDATE-{index + 1:03d}",
                "finding_type": "FAULT_CLASS",
                "target": result.get("primary_component") or result.get("primary_subsystem") or "UNRESOLVED",
                "result": candidate["effect_id"],
                "score": score,
                "score_semantics": (
                    "deterministic evidence-coverage screening score; not a calibrated probability"
                    if score is not None else None
                ),
                # UnifiedCandidate does not bind diagnostic_evidence IDs to a
                # specific candidate. Assigning all evidence to every fault
                # would fabricate support and contaminate conflict examples.
                "supporting_evidence_ids": [],
                "limitations": [
                    "upstream candidate is not a confirmed root cause",
                    "candidate score is not a calibrated probability",
                    "candidate-specific diagnostic evidence links were not supplied",
                    "upstream reports contradicting engines; resolution required"
                    if candidate.get("contradicting_engines") else "no engine-level conflict claim is inferred",
                    result.get("claim_boundary") or "upstream claim boundary not supplied",
                ],
            })
        for index, evidence in enumerate(evidence_items):
            findings.append({
                "finding_id": f"ASTROGRAPH-EVIDENCE-{index + 1:03d}",
                "finding_type": "RESIDUAL",
                "target": evidence.get("field") or "UNRESOLVED",
                "result": evidence.get("interpretation") or "evidence interpretation not supplied",
                "score": None,
                "score_semantics": None,
                "supporting_evidence_ids": [evidence["evidence_id"]] if evidence.get("evidence_id") else [],
                "limitations": ["derived diagnostic evidence; not raw telemetry"],
            })
        analysis_scope = "; ".join(
            part for part in (
                result.get("primary_subsystem"),
                result.get("primary_component"),
                result.get("resolution_basis"),
            ) if isinstance(part, str) and part
        ) or "AstroGraph unified diagnosis result"
        method = producer_method or result.get("backend") or "NOT_RECORDED"
        version = producer_version or "NOT_RECORDED"
        summary = (
            f"Upstream diagnosis status={result.get('status')}; "
            f"primary_effect_id={result.get('primary_effect_id')}; "
            f"candidate_count={len(candidates)}."
        )
        known_limitations = [
            result.get("claim_boundary", "upstream claim boundary not supplied"),
            "upstream diagnosis metadata is a candidate/result summary, not raw telemetry",
            "unified contract does not establish candidate-to-evidence attribution",
        ]
    else:
        if result.get("schema_version") not in (None, "external-diagnosis-result.v1"):
            raise UpstreamDiagnosisAdapterError("UNSUPPORTED_UPSTREAM_DIAGNOSIS_SCHEMA")
        status_value = result.get("status")
        candidate_items = result.get("candidate_faults")
        if isinstance(candidate_items, list):
            candidates = candidate_items
        elif result.get("candidate_fault_id"):
            candidates = [{
                "fault_id": result.get("candidate_fault_id"),
                "status": result.get("review_status", "UNVERIFIED"),
            }]
        else:
            candidates = []
        if status_value == "NORMAL" and not candidates:
            status = "NORMAL"
        elif not candidates:
            status = "INSUFFICIENT_DATA"
        elif len(candidates) > 1:
            status = "MULTIPLE_CANDIDATES"
        else:
            status = "FAULT_CANDIDATE"
        findings = []
        for index, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise UpstreamDiagnosisAdapterError(f"malformed legacy candidate at index {index}")
            fault_id = candidate.get("fault_id") or candidate.get("candidate_fault_id")
            if not isinstance(fault_id, str) or not fault_id:
                raise UpstreamDiagnosisAdapterError(f"legacy candidate {index} has no fault identifier")
            findings.append({
                "finding_id": f"LEGACY-CANDIDATE-{index + 1:03d}",
                "finding_type": "FAULT_CLASS",
                "target": candidate.get("component") or candidate.get("subsystem") or result.get("subsystem") or "UNRESOLVED",
                "result": fault_id,
                "score": None,
                "score_semantics": None,
                "supporting_evidence_ids": [],
                "limitations": [
                    f"upstream review status: {candidate.get('status') or result.get('review_status') or 'NOT_RECORDED'}",
                    "legacy result has no structured evidence IDs or calibrated score",
                    "candidate is not a confirmed root cause",
                ],
            })
        method = producer_method or "NOT_RECORDED"
        version = producer_version or "NOT_RECORDED"
        analysis_scope = result.get("subsystem") or result.get("equipment_scope") or "legacy external diagnosis result"
        summary = result.get("diagnostic_summary") or "upstream summary not supplied"
        known_limitations = [
            "legacy result format does not provide structured engine execution metadata",
            "candidate status is not an expert-confirmed root cause",
        ]

    return {
        "producer": {"method": method, "version": version, "model_id": model_id},
        "analysis_scope": analysis_scope,
        "status": status,
        "findings": findings,
        "machine_summary": summary,
        "known_limitations": known_limitations,
    }
