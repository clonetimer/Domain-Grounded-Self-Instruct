"""Fail-closed, review-only intake audit for C2 source-rights worksheets.

This compares an offline edited worksheet with its immutable blank source-rights
queue. Referenced permission evidence is not authenticated or interpreted as a
grant. No review receipt from this module can authorize SFT or training.
"""
from __future__ import annotations

from collections import Counter
import re
from typing import Any

_SHA256_REF = re.compile(r"^sha256:[0-9a-f]{64}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_STATUS = frozenset({
    "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW",
    "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW",
    "REUSE_DENIED",
    "UNRESOLVED",
})
_MUTABLE = frozenset({
    "rights_review_status",
    "license_or_permission_evidence_ref",
    "permitted_reuse_scope",
    "rights_decision",
    "rights_cleared",
})


class C2SourceRightsIntakeError(ValueError):
    """An offline rights worksheet is malformed, stale, or grants false rights."""


def _reject(code: str) -> None:
    raise C2SourceRightsIntakeError(code)


def _docs(queue: dict[str, Any]) -> dict[str, dict[str, Any]]:
    docs = queue.get("source_documents")
    if not isinstance(docs, list) or not docs:
        _reject("C2_RIGHTS_INTAKE_DOCUMENTS_INVALID")
    index: dict[str, dict[str, Any]] = {}
    for item in docs:
        if not isinstance(item, dict) or not isinstance(item.get("source_id"), str):
            _reject("C2_RIGHTS_INTAKE_DOCUMENT_INVALID")
        source_id = item["source_id"]
        if not source_id or source_id in index:
            _reject("C2_RIGHTS_INTAKE_DUPLICATE_SOURCE")
        index[source_id] = item
    if len(index) != queue.get("distinct_source_document_count"):
        _reject("C2_RIGHTS_INTAKE_DOCUMENT_COUNT_DRIFT")
    return index


def audit_c2_source_rights_intake(
    blank_queue: dict[str, Any], submitted_queue: dict[str, Any]
) -> dict[str, Any]:
    """Check an edited source-rights worksheet without clearing any rights.

    The blank queue must come from the fingerprint-bound C2 kit, independently
    obtained through an authorized channel. This function cannot authenticate
    the document's actual copyright status, evidence, signer or authority.
    """
    if not isinstance(blank_queue, dict) or not isinstance(submitted_queue, dict):
        _reject("C2_RIGHTS_INTAKE_ENVELOPE_INVALID")
    if (
        blank_queue.get("schema_version") != "dgsi-c2-source-rights-review-queue.v1"
        or blank_queue.get("purpose") != "BLANK_SOURCE_RIGHTS_INTAKE_ONLY_NOT_CLEARANCE"
        or blank_queue.get("track") != "LITERATURE_DERIVED_SYNTHETIC"
        or not isinstance(blank_queue.get("collection_projection_sha256"), str)
        or not _SHA256.fullmatch(blank_queue["collection_projection_sha256"])
    ):
        _reject("C2_RIGHTS_INTAKE_REFERENCE_INVALID")

    expected_constants = {
        "not_for_sft": True,
        "source_rights_verified": False,
        "expert_review_complete": False,
        "gold_eligible": False,
        "official_splits_assigned": False,
        "training_authorized": False,
        "rights_cleared_document_count": 0,
        "sft_records_emitted": 0,
    }
    if any(blank_queue.get(k) != v for k, v in expected_constants.items()):
        _reject("C2_RIGHTS_INTAKE_REFERENCE_NOT_BLOCKED")
    if set(submitted_queue) != set(blank_queue):
        _reject("C2_RIGHTS_INTAKE_ENVELOPE_FIELDS_DRIFT")
    for key, value in blank_queue.items():
        if key != "source_documents" and submitted_queue[key] != value:
            _reject("C2_RIGHTS_INTAKE_COHORT_OR_FLAGS_DRIFT")

    baseline = _docs(blank_queue)
    supplied = _docs(submitted_queue)
    if set(baseline) != set(supplied):
        _reject("C2_RIGHTS_INTAKE_SOURCE_SET_DRIFT")

    counts: Counter[str] = Counter()
    evidence_references = 0
    for source_id, expected in baseline.items():
        record = supplied[source_id]
        if set(record) != set(expected):
            _reject("C2_RIGHTS_INTAKE_DOCUMENT_FIELDS_DRIFT")
        if any(record[key] != value for key, value in expected.items()
               if key not in _MUTABLE):
            _reject("C2_RIGHTS_INTAKE_DOCUMENT_BINDING_DRIFT")
        if (
            expected.get("rights_review_status") !=
            "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW"
            or expected.get("license_or_permission_evidence_ref") is not None
            or expected.get("permitted_reuse_scope") is not None
            or expected.get("rights_decision") is not None
            or expected.get("rights_cleared") is not False
        ):
            _reject("C2_RIGHTS_INTAKE_REFERENCE_NOT_BLANK")
        status = record["rights_review_status"]
        if not isinstance(status, str) or status not in _STATUS:
            _reject("C2_RIGHTS_INTAKE_REVIEW_STATUS_INVALID")
        if record["rights_cleared"] is not False:
            _reject("C2_RIGHTS_INTAKE_FALSE_CLEARANCE")
        if record["permitted_reuse_scope"] is not None:
            _reject("C2_RIGHTS_INTAKE_SCOPE_NOT_AUTHENTICATED")
        verdict = record["rights_decision"]
        if verdict is not None and not (
            status == "REUSE_DENIED" and verdict == "DENIED"
        ):
            _reject("C2_RIGHTS_INTAKE_PERMISSION_NOT_AUTHENTICATED")
        evidence_ref = record["license_or_permission_evidence_ref"]
        if evidence_ref is not None:
            if not isinstance(evidence_ref, str) or not _SHA256_REF.fullmatch(evidence_ref):
                _reject("C2_RIGHTS_INTAKE_EVIDENCE_REF_INVALID")
            evidence_references += 1
        if status == "EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW" and evidence_ref is None:
            _reject("C2_RIGHTS_INTAKE_EVIDENCE_MISSING")
        if status == "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW" and evidence_ref is not None:
            _reject("C2_RIGHTS_INTAKE_PENDING_WITH_EVIDENCE")
        counts[status] += 1

    return {
        "schema_version": "dgsi-c2-source-rights-intake-audit.v1",
        "decision": "STRUCTURALLY_BOUND_RIGHTS_REVIEW_ONLY_NOT_CLEARANCE",
        "collection_projection_sha256": blank_queue["collection_projection_sha256"],
        "distinct_source_document_count": len(baseline),
        "status_counts": {status: counts[status] for status in sorted(_STATUS)},
        "referenced_evidence_document_count": evidence_references,
        "rights_cleared_document_count": 0,
        "source_rights_verified": False,
        "expert_review_complete": False,
        "not_for_sft": True,
        "gold_eligible": False,
        "official_splits_assigned": False,
        "training_authorized": False,
        "sft_records_emitted": 0,
    }
