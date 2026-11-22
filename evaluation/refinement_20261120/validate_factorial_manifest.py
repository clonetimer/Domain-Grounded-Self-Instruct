"""Fail-closed validator for the preregistered DGSI 2x2 experiment manifest.

This validates comparability metadata only. It does not generate data, score outputs,
or authorize model calls/training.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
from urllib.parse import urlparse

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

    excluded_clusters = data.get("excluded_source_cluster_ids")
    if not isinstance(excluded_clusters, list) or not excluded_clusters or any(
        not isinstance(value, str) or not value.strip() for value in excluded_clusters
    ):
        raise ManifestError("EXCLUSION_REGISTER_MISSING")
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
        if row["source_cluster_id"] in excluded_clusters:
            raise ManifestError("PREVIOUSLY_EXPOSED_SOURCE_CLUSTER")
        seen_ids.add(row["case_id"])
        for key in ("input_sha256", "target_schema_sha256"):
            value = row[key]
            if len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
                raise ManifestError("CASE_HASH_INVALID")
        canonical_cases[row["case_id"]] = row
    case_clusters = {row["source_cluster_id"] for row in cases}
    if len(case_clusters) < 2:
        raise ManifestError("INSUFFICIENT_INDEPENDENT_SOURCE_CLUSTERS")

    # Each declared source cluster must carry an auditable evidence record.
    # These fields make the evidence trail inspectable; they do not prove that
    # the curator's assertions are true or replace independent legal/exposure review.
    evidence_records = data.get("source_evidence_records")
    if not isinstance(evidence_records, list) or not evidence_records:
        raise ManifestError("SOURCE_EVIDENCE_RECORDS_MISSING")
    required_evidence_keys = {
        "source_cluster_id", "primary_source_url", "source_document_id",
        "source_document_sha256", "source_locators", "rights_basis",
        "rights_scope", "rights_review_ref", "exposure_audit_scope",
        "exposure_audit_ref", "independence_rationale", "review_status",
        "reviewer_token", "reviewed_at",
    }
    required_exposure_scopes = {
        "repository_and_pr_history",
        "prior_development_bundles",
        "connected_retrieval_and_prior_conversations",
    }
    evidence_by_cluster = {}
    for record in evidence_records:
        if not isinstance(record, dict) or set(record) != required_evidence_keys:
            raise ManifestError("SOURCE_EVIDENCE_RECORD_INVALID")
        cluster_id = record.get("source_cluster_id")
        if not isinstance(cluster_id, str) or not cluster_id.strip() or cluster_id in evidence_by_cluster:
            raise ManifestError("SOURCE_EVIDENCE_CLUSTER_DUPLICATE_OR_INVALID")
        parsed_url = urlparse(record.get("primary_source_url", ""))
        if parsed_url.scheme != "https" or not parsed_url.netloc:
            raise ManifestError("SOURCE_PRIMARY_URL_INVALID")
        if not isinstance(record.get("source_document_id"), str) or not record["source_document_id"].strip():
            raise ManifestError("SOURCE_DOCUMENT_ID_MISSING")
        digest = record.get("source_document_sha256")
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ManifestError("SOURCE_DOCUMENT_HASH_INVALID")
        locators = record.get("source_locators")
        if not isinstance(locators, list) or not locators or any(not isinstance(v, str) or not v.strip() for v in locators):
            raise ManifestError("SOURCE_LOCATORS_MISSING")
        for key in ("rights_basis", "rights_scope", "rights_review_ref", "exposure_audit_ref", "independence_rationale", "reviewer_token", "reviewed_at"):
            if not isinstance(record.get(key), str) or not record[key].strip():
                raise ManifestError("SOURCE_REVIEW_EVIDENCE_INCOMPLETE")
        scopes = record.get("exposure_audit_scope")
        if not isinstance(scopes, list) or any(not isinstance(v, str) or not v.strip() for v in scopes):
            raise ManifestError("SOURCE_EXPOSURE_AUDIT_SCOPE_INCOMPLETE")
        if not required_exposure_scopes.issubset(set(scopes)):
            raise ManifestError("SOURCE_EXPOSURE_AUDIT_SCOPE_INCOMPLETE")
        if record.get("review_status") != "PASS":
            raise ManifestError("SOURCE_REVIEW_NOT_PASSED")
        try:
            date.fromisoformat(record["reviewed_at"])
        except (TypeError, ValueError):
            raise ManifestError("SOURCE_REVIEW_DATE_INVALID")
        evidence_by_cluster[cluster_id] = record
    if set(evidence_by_cluster) != case_clusters:
        raise ManifestError("SOURCE_EVIDENCE_CLUSTER_SET_MISMATCH")

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
        "source_cluster_count": len(case_clusters),
        "source_evidence_record_count": len(evidence_records),
        "source_evidence_manifest_sha256": _canonical_sha256(evidence_records),
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
