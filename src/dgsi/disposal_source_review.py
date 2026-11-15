"""Fail-closed local audit of human-attested disposal source passages.

This is a review aid, not an NLP action detector, provenance authentication,
independent-expert credential check, or Gold approval. Keep reviews local;
never put the review packet, excerpts, or curator notes in SFT messages.
"""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from typing import Any

from .diagnostic_context import (
    DiagnosticContextValidationError,
    validate_diagnostic_case,
)


class DisposalSourceReviewError(ValueError):
    """Sanitized fixed-code failure; must not include source passages or IDs."""


def _check(condition: bool, code: str) -> None:
    if not condition:
        raise DisposalSourceReviewError(code)


def _time(value: Any, code: str) -> datetime:
    _check(isinstance(value, str), code)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise DisposalSourceReviewError(code) from None
    _check(result.tzinfo is not None and result.utcoffset() is not None, code)
    return result


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def audit_disposal_source_review(
    case: dict[str, Any], review_packet: dict[str, Any],
) -> dict[str, Any]:
    """Validate evidence excerpts and independent-review *claims* for disposal.

    One review attestation is required per documented measure. Each one must
    cite an actual source in that measure's evidence_refs, contain a literal
    excerpt from the supplied source, bind the exact action wording by digest,
    and record an explicit human verdict. This does not interpret the excerpt:
    the reviewer remains responsible for semantic support and identity proof.

    The return value and exceptions intentionally contain no case IDs, source
    text, review excerpts, local paths, or hashes.
    """
    try:
        validate_diagnostic_case(case)
    except (DiagnosticContextValidationError, TypeError, KeyError):
        raise DisposalSourceReviewError("INVALID_SOURCE_CASE") from None

    _check(isinstance(review_packet, dict), "INVALID_REVIEW_PACKET")
    _check(
        set(review_packet) == {
            "schema_version", "case_ref", "not_for_sft", "reviewer_id",
            "reviewer_role", "reviewed_at", "attestations",
        },
        "INVALID_REVIEW_PACKET_FIELDS",
    )
    _check(
        review_packet["schema_version"] == "dgsi-disposal-source-review.v1",
        "UNSUPPORTED_SOURCE_REVIEW_VERSION",
    )
    _check(review_packet["case_ref"] == case["case_id"], "SOURCE_REVIEW_CASE_MISMATCH")
    _check(review_packet["not_for_sft"] is True, "SOURCE_REVIEW_MUST_BE_INTERNAL")
    _check(
        isinstance(review_packet["reviewer_id"], str)
        and bool(review_packet["reviewer_id"].strip()),
        "MISSING_DISPOSAL_REVIEWER",
    )
    _check(
        review_packet["reviewer_role"] == "INDEPENDENT_DOMAIN_EXPERT",
        "DISPOSAL_REVIEWER_ROLE_NOT_DECLARED",
    )
    reviewed_at = _time(review_packet["reviewed_at"], "INVALID_DISPOSAL_REVIEW_TIME")
    cutoff = _time(case["input"]["analysis_cutoff"], "INVALID_DISPOSAL_CASE_CUTOFF")
    measures = case["expected_output"]["disposal_measures"]
    attestations = review_packet["attestations"]
    _check(isinstance(attestations, list), "INVALID_DISPOSAL_ATTESTATIONS")
    _check(len(attestations) == len(measures), "DISPOSAL_REVIEW_COVERAGE_MISMATCH")

    logs = {entry["log_id"]: entry for entry in case["input"]["diagnostic_logs"]}
    knowledge = {entry["evidence_id"]: entry for entry in case["input"].get("knowledge_evidence", [])}
    indices: set[int] = set()
    for entry in attestations:
        _check(isinstance(entry, dict), "INVALID_DISPOSAL_ATTESTATION")
        required = {
            "measure_index", "measure_sha256", "evidence_ref", "verbatim_excerpt",
            "source_action_type", "verdict",
        }
        _check(set(entry) in (required, required | {"source_published_at"}), "INVALID_DISPOSAL_ATTESTATION_FIELDS")
        index = entry["measure_index"]
        _check(type(index) is int and 0 <= index < len(measures), "INVALID_DISPOSAL_MEASURE_INDEX")
        _check(index not in indices, "DUPLICATE_DISPOSAL_MEASURE_REVIEW")
        indices.add(index)
        measure = measures[index]
        _check(entry["measure_sha256"] == _digest(measure["measure"]), "DISPOSAL_MEASURE_CHANGED_AFTER_REVIEW")
        _check(entry["source_action_type"] == measure["measure_type"], "DISPOSAL_ACTION_TYPE_MISMATCH")
        ref = entry["evidence_ref"]
        _check(isinstance(ref, str) and ref in measure["evidence_refs"], "UNBOUND_DISPOSAL_SOURCE_REVIEW")
        excerpt = entry["verbatim_excerpt"]
        _check(isinstance(excerpt, str) and len(excerpt.strip()) >= 8, "MISSING_DISPOSAL_SOURCE_EXCERPT")
        if ref in logs:
            _check("source_published_at" not in entry, "UNEXPECTED_DISPOSAL_SOURCE_TIME")
            source = logs[ref]
            _check(source["timestamp"] is not None, "DISPOSAL_SOURCE_TIME_MISSING")
            recorded_at = _time(source["timestamp"], "INVALID_DISPOSAL_SOURCE_TIME")
            source_text = source["content"]
        elif ref in knowledge:
            _check(measure["measure_type"] != "EXECUTED", "EXECUTED_DISPOSAL_NOT_IN_LOG")
            _check("source_published_at" in entry, "DISPOSAL_PUBLICATION_TIME_MISSING")
            recorded_at = _time(entry["source_published_at"], "INVALID_DISPOSAL_PUBLICATION_TIME")
            source_text = knowledge[ref].get("excerpt")
        else:
            raise DisposalSourceReviewError("DISPOSAL_SOURCE_NOT_AVAILABLE")
        _check(recorded_at <= cutoff, "DISPOSAL_SOURCE_AFTER_DECISION_CUTOFF")
        _check(recorded_at <= reviewed_at, "DISPOSAL_REVIEW_BEFORE_SOURCE_RECORD")
        _check(
            isinstance(source_text, str) and excerpt.strip() in source_text,
            "DISPOSAL_EXCERPT_NOT_IN_CITED_SOURCE",
        )
        _check(entry["verdict"] == "SUPPORTED", "DISPOSAL_SOURCE_NOT_EXPERT_SUPPORTED")

    return {
        "status": "STRUCTURAL_SOURCE_REVIEW_PASS_NOT_GOLD",
        "measure_count": len(measures),
        "source_review_count": len(attestations),
        "expert_identity_verified": False,
        "semantic_support_independently_verified_by_tool": False,
        "gold_approved": False,
    }
