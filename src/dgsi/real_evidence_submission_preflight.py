"""Local binding-only audit for REAL evidence submissions.

This module only inspects metadata supplied explicitly by the local operator.
A hash or source reference is not proof of permission, authenticity, independent
expert review, valid ML results, as-of eligibility or Gold admission.

No case identifiers, artifact refs, private comments or reviewer data are emitted.
"""
from __future__ import annotations

from collections import Counter
import re
from typing import Any

from dgsi.real_review_queue_preflight import CHECKS, audit_review_queue

VERSION = "dgsi.local-real-evidence-submissions.v1"
CLASSIFICATION = "LOCAL_REVIEW_WORKSPACE_ONLY"
HEX = re.compile(r"[0-9a-f]{64}\Z")
EVIDENCE_TYPES = {
    "SOURCE_RIGHTS": {"SOURCE_PERMISSION_RECORD"},
    "DEIDENTIFICATION": {"DEIDENTIFICATION_REPORT"},
    "EVENT_FAMILY": {"EVENT_FAMILY_RECORD"},
    "UPSTREAM_ML": {"ML_RESULT"},
    "LOGS_CUTOFF": {"DIAGNOSTIC_LOG", "ANALYSIS_CUTOFF_RECORD"},
    "MISSION_CONTEXT": {"MISSION_CONTEXT"},
    "HISTORY_ASOF": {"HISTORY_ASOF_RETRIEVAL"},
    "EVIDENCE_DISPOSAL": {"EVIDENCE_LINK", "DISPOSAL_RECORD"},
    "BLIND_EXPERT": {"BLIND_REVIEW_REQUEST"},
}


class RealEvidenceSubmissionError(ValueError):
    """Only stable, payload-free error codes are exposed."""


def _keys(value: Any, expected: set[str], code: str) -> None:
    if not isinstance(value, dict) or set(value) != expected:
        raise RealEvidenceSubmissionError(code)


def audit_evidence_submissions(queue: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Check candidate-to-source bindings and declarations; never verify evidence.

    The v0.5 intake queue must itself pass its stricter unverified-only gate.
    Submitted artifacts remain untrusted and do not make a case review-ready.
    """
    audit_review_queue(queue)
    _keys(
        bundle,
        {"schema_version", "classification", "candidate_count", "cases",
         "not_for_sft", "gold_eligible", "training_authorized", "split_assignment_allowed"},
        "SUBMISSION_ROOT_FIELDS_INVALID",
    )
    if (bundle["schema_version"] != VERSION
            or bundle["classification"] != CLASSIFICATION
            or bundle["not_for_sft"] is not True
            or bundle["gold_eligible"] is not False
            or bundle["training_authorized"] is not False
            or bundle["split_assignment_allowed"] is not False):
        raise RealEvidenceSubmissionError("SUBMISSION_SCOPE_OR_PROMOTION_INVALID")
    cases = bundle["cases"]
    if (not isinstance(cases, list)
            or type(bundle["candidate_count"]) is not int
            or bundle["candidate_count"] != len(cases)
            or len(cases) != len(queue["cases"])
            or len(cases) > 1000):
        raise RealEvidenceSubmissionError("SUBMISSION_CASE_COUNT_MISMATCH")

    expected_cases = {c["case_id"]: c["source_case_sha256"] for c in queue["cases"]}
    seen_cases: set[str] = set()
    ref_hash: dict[str, str] = {}
    submitted: Counter[str] = Counter()
    missing: Counter[str] = Counter()
    declaration_count = 0
    for case in cases:
        _keys(case, {"case_id", "source_case_sha256", "submissions", "not_for_sft"},
              "SUBMISSION_CASE_FIELDS_INVALID")
        case_id = case["case_id"]
        if (not isinstance(case_id, str)
                or case_id not in expected_cases
                or case_id in seen_cases
                or case["source_case_sha256"] != expected_cases[case_id]
                or case["not_for_sft"] is not True):
            raise RealEvidenceSubmissionError("SUBMISSION_CASE_BINDING_INVALID")
        seen_cases.add(case_id)
        slots = case["submissions"]
        if not isinstance(slots, list) or len(slots) != len(CHECKS):
            raise RealEvidenceSubmissionError("SUBMISSION_CHECKSET_INCOMPLETE")
        seen_checks: set[str] = set()
        for slot in slots:
            _keys(slot, {"check_id", "status", "artifacts", "not_for_sft"},
                  "SUBMISSION_CHECK_FIELDS_INVALID")
            code = slot["check_id"]
            if not isinstance(code, str) or code not in CHECKS or code in seen_checks:
                raise RealEvidenceSubmissionError("SUBMISSION_CHECK_INVALID_OR_DUPLICATE")
            seen_checks.add(code)
            if slot["not_for_sft"] is not True:
                raise RealEvidenceSubmissionError("SUBMISSION_NOT_FOR_SFT_REQUIRED")
            status = slot["status"]
            artifacts = slot["artifacts"]
            if not isinstance(artifacts, list) or len(artifacts) > 20:
                raise RealEvidenceSubmissionError("SUBMISSION_ARTIFACT_LIST_INVALID")
            if status == "NOT_SUBMITTED":
                if artifacts:
                    raise RealEvidenceSubmissionError("SUBMISSION_MISSING_WITH_ARTIFACTS")
                missing[code] += 1
            elif status == "SUBMITTED_FOR_REVIEW":
                if not artifacts:
                    raise RealEvidenceSubmissionError("SUBMISSION_SUBMITTED_WITHOUT_ARTIFACTS")
                submitted[code] += 1
            else:
                # VERIFIED, ACCEPTED, APPROVED and any fabricated expert conclusions
                # are outside the evidence-submission contract.
                raise RealEvidenceSubmissionError("SUBMISSION_UNSUPPORTED_VERIFICATION_CLAIM")
            for artifact in artifacts:
                _keys(artifact, {"evidence_ref", "evidence_sha256", "evidence_type"},
                      "SUBMISSION_ARTIFACT_FIELDS_INVALID")
                ref = artifact["evidence_ref"]
                sha = artifact["evidence_sha256"]
                kind = artifact["evidence_type"]
                if (not isinstance(ref, str) or not 1 <= len(ref) <= 512
                        or not ref.strip()
                        or any(ord(ch) < 32 or ord(ch) == 127 for ch in ref)
                        or not isinstance(sha, str) or HEX.fullmatch(sha) is None
                        or not isinstance(kind, str) or kind not in EVIDENCE_TYPES[code]):
                    raise RealEvidenceSubmissionError("SUBMISSION_ARTIFACT_METADATA_INVALID")
                prior = ref_hash.setdefault(ref, sha)
                if prior != sha:
                    raise RealEvidenceSubmissionError("SUBMISSION_EVIDENCE_REF_HASH_CONFLICT")
                declaration_count += 1
    if seen_cases != set(expected_cases):
        raise RealEvidenceSubmissionError("SUBMISSION_CASESET_INCOMPLETE")
    return {
        "schema_version": "dgsi.real-evidence-submission-preflight.v1",
        "scope": "LOCAL_METADATA_ONLY",
        "case_count": len(cases),
        "submitted_for_review_by_dimension": {k: submitted[k] for k in sorted(CHECKS)},
        "not_submitted_by_dimension": {k: missing[k] for k in sorted(CHECKS)},
        "artifact_declaration_count": declaration_count,
        "distinct_artifact_ref_count": len(ref_hash),
        "evidence_verified_count": 0,
        "expert_review_ready_count": 0,
        "real_gold_count": 0,
        "training_authorized": False,
        "split_assignment_allowed": False,
        "note": "Submission metadata only. Source rights, file hashes, ML runs, history as-of and expert conclusions require independent evidence verification.",
    }
