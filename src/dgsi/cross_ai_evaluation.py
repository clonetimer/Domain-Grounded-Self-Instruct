"""Semantic lifecycle checks for blinded cross-AI evaluation records.

Schema validation handles shape. This module checks uniqueness, alias lineage,
and completeness of adjudication. It never ranks providers or authorizes SFT.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/cross_ai_evaluation.schema.json"
DIMENSIONS = {
    "source_coverage", "locator_precision", "fact_fidelity",
    "evidence_classification", "object_hierarchy", "physical_consistency",
    "fault_semantics", "uncertainty", "truth_isolation", "task_value",
    "target_restraint", "schema_lineage",
}


class CrossAIEvaluationError(ValueError):
    pass


def validate_cross_ai_evaluation(record: dict[str, Any]) -> dict[str, Any]:
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise CrossAIEvaluationError("CROSS_AI_SCHEMA_UNAVAILABLE") from None
    errors = list(Draft202012Validator(schema).iter_errors(record))
    if errors:
        raise CrossAIEvaluationError("CROSS_AI_SCHEMA_INVALID")
    runs = record["runs"]
    aliases = [run["blind_alias"] for run in runs]
    if len(aliases) != len(set(aliases)):
        raise CrossAIEvaluationError("CROSS_AI_DUPLICATE_ALIAS")
    alias_set = set(aliases)
    adjudication = record["adjudication"]
    scores = adjudication["dimensions"]
    keys = [(item["blind_alias"], item["dimension"]) for item in scores]
    if len(keys) != len(set(keys)):
        raise CrossAIEvaluationError("CROSS_AI_DUPLICATE_SCORE")
    if any(alias not in alias_set for alias, _ in keys):
        raise CrossAIEvaluationError("CROSS_AI_UNKNOWN_SCORE_ALIAS")
    failures = adjudication["critical_failures"]
    if any(item["blind_alias"] not in alias_set for item in failures):
        raise CrossAIEvaluationError("CROSS_AI_UNKNOWN_FAILURE_ALIAS")
    status = record["status"]
    if status == "ADJUDICATED":
        expected = {(alias, dimension) for alias in alias_set for dimension in DIMENSIONS}
        if set(keys) != expected:
            raise CrossAIEvaluationError("CROSS_AI_ADJUDICATION_INCOMPLETE")
        if adjudication["reference_basis"] == "NOT_ADJUDICATED":
            raise CrossAIEvaluationError("CROSS_AI_ADJUDICATION_BASIS_MISSING")
    return {
        "decision": status,
        "run_count": len(runs),
        "unique_alias_count": len(alias_set),
        "score_count": len(scores),
        "critical_failure_count": len(failures),
        "adjudication_complete": status == "ADJUDICATED",
        "training_authorized": False,
        "gold_authorized": False,
        "sft_export_authorized": False,
    }
