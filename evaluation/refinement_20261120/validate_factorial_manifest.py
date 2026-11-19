"""Fail-closed validator for the preregistered DGSI 2x2 experiment manifest.

This validates comparability metadata only. It does not generate data, score outputs,
or authorize model calls/training.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ARMS = {
    "A": (False, False),
    "B": (False, True),
    "C": (True, False),
    "D": (True, True),
}
FORBIDDEN_KEYS = {
    "answer", "answers", "gold", "gold_answer", "reference_answer",
    "ground_truth", "target_text", "reviewer_score", "evaluation_score",
}


class ManifestError(ValueError):
    pass


def _canonical_sha256(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_manifest(data: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema_version") != "dgsi-2x2-run-manifest.v1":
        raise ManifestError("MANIFEST_SCHEMA_INVALID")

    def scan(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if str(key).lower() in FORBIDDEN_KEYS:
                    raise ManifestError("REFERENCE_OR_SCORE_LEAKAGE")
                scan(value)
        elif isinstance(node, list):
            for value in node:
                scan(value)
    scan(data)

    if data.get("status") != "PRE_GENERATION_VALIDATION_ONLY":
        raise ManifestError("MANIFEST_STATUS_INVALID")
    if data.get("model_calls_authorized") is not False or data.get("training_authorized") is not False:
        raise ManifestError("UNAUTHORIZED_EXECUTION_FLAG")
    if data.get("retry_budget") != 0 or data.get("regeneration_budget") != 0:
        raise ManifestError("RETRY_OR_REGENERATION_FORBIDDEN")

    gate = data.get("holdout_gate")
    required_gate = (
        "rights_verified", "development_exposure_excluded",
        "source_cluster_independence_verified", "reference_answers_escrowed",
        "case_manifest_frozen",
    )
    if not isinstance(gate, dict) or any(gate.get(key) is not True for key in required_gate):
        raise ManifestError("HOLDOUT_GATE_NOT_PASSED")

    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ManifestError("HOLDOUT_CASES_MISSING")
    canonical_cases = {}
    seen_ids = set()
    for row in cases:
        if not isinstance(row, dict):
            raise ManifestError("CASE_ROW_INVALID")
        if set(row) != {"case_id", "source_cluster_id", "input_sha256", "target_schema_sha256"}:
            raise ManifestError("CASE_ROW_INVALID")
        if any(not isinstance(row[k], str) or not row[k].strip() for k in row):
            raise ManifestError("CASE_ROW_INVALID")
        if row["case_id"] in seen_ids:
            raise ManifestError("DUPLICATE_CASE_ID")
        seen_ids.add(row["case_id"])
        for key in ("input_sha256", "target_schema_sha256"):
            value = row[key]
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ManifestError("CASE_HASH_INVALID")
        canonical_cases[row["case_id"]] = row
    if len({row["source_cluster_id"] for row in cases}) < 2:
        raise ManifestError("INSUFFICIENT_INDEPENDENT_SOURCE_CLUSTERS")

    arms = data.get("arms")
    if not isinstance(arms, list) or len(arms) != 4:
        raise ManifestError("FACTORIAL_ARMS_INCOMPLETE")
    by_id = {}
    for arm in arms:
        if not isinstance(arm, dict) or arm.get("arm_id") not in ARMS:
            raise ManifestError("FACTORIAL_ARM_INVALID")
        arm_id = arm["arm_id"]
        if arm_id in by_id:
            raise ManifestError("FACTORIAL_ARM_DUPLICATED")
        expected = ARMS[arm_id]
        if (arm.get("evolution_enabled"), arm.get("selection_enabled")) != expected:
            raise ManifestError("FACTORIAL_ARM_FACTOR_MISMATCH")
        if arm.get("candidate_count") != (3 if expected[1] else 1):
            raise ManifestError("CANDIDATE_COUNT_MISMATCH")
        if arm.get("policy_sha256") != data.get("policy_sha256"):
            raise ManifestError("POLICY_MISMATCH")
        arm_cases = arm.get("cases")
        if not isinstance(arm_cases, list):
            raise ManifestError("ARM_CASES_MISSING")
        normalized = {}
        for row in arm_cases:
            if not isinstance(row, dict) or set(row) != {"case_id", "input_sha256", "target_schema_sha256"}:
                raise ManifestError("ARM_CASE_ROW_INVALID")
            case_id = row["case_id"]
            if case_id in normalized:
                raise ManifestError("ARM_CASE_DUPLICATED")
            normalized[case_id] = row
        if set(normalized) != set(canonical_cases):
            raise ManifestError("ARM_HOLDOUT_CASE_SET_MISMATCH")
        for case_id, row in normalized.items():
            frozen = canonical_cases[case_id]
            if row["input_sha256"] != frozen["input_sha256"] or row["target_schema_sha256"] != frozen["target_schema_sha256"]:
                raise ManifestError("ARM_INPUT_OR_SCHEMA_MISMATCH")
        by_id[arm_id] = arm
    if set(by_id) != set(ARMS):
        raise ManifestError("FACTORIAL_ARMS_INCOMPLETE")

    return {
        "valid": True,
        "status": "MANIFEST_COMPARABILITY_VALIDATED_NOT_EXECUTED",
        "arm_count": 4,
        "case_count": len(cases),
        "source_cluster_count": len({row["source_cluster_id"] for row in cases}),
        "case_manifest_sha256": _canonical_sha256(cases),
        "model_calls_authorized": False,
        "training_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    try:
        report = validate_manifest(json.loads(args.manifest.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ManifestError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
