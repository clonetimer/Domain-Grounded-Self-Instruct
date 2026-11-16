"""Local metadata-only preflight for REAL candidate evidence request queues.

Never print case IDs, source text, paths, reviewer identities or review notes.
This is not source/permission verification, expert adjudication or SFT admission.
"""
from __future__ import annotations

from collections import Counter
import json
import re
from typing import Any

VERSION = "dgsi.local-real-candidate-evidence-request.v0.5"
CHECKS = frozenset({
    "SOURCE_RIGHTS", "DEIDENTIFICATION", "EVENT_FAMILY", "UPSTREAM_ML",
    "LOGS_CUTOFF", "MISSION_CONTEXT", "HISTORY_ASOF",
    "EVIDENCE_DISPOSAL", "BLIND_EXPERT",
})
REQUIRED_SAFETY = (
    "internal_review_not_for_sft", "raw_telemetry_not_default_llm_input",
    "historical_no_hit_acceptable_when_proven", "no_automatic_gold",
    "no_training_authorized", "no_fake_ml_runs_or_logs",
)
HEX = re.compile(r"[0-9a-f]{64}\Z")


class ReviewQueuePreflightError(ValueError):
    """A payload-free error code; never user-provided text."""


def load_review_queue(payload: str) -> dict[str, Any]:
    if not isinstance(payload, str) or len(payload) > 2_000_000:
        raise ReviewQueuePreflightError("QUEUE_SIZE_OR_TYPE_INVALID")

    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        output: dict[str, Any] = {}
        for key, value in pairs:
            if key in output:
                raise ReviewQueuePreflightError("DUPLICATE_QUEUE_JSON_KEY")
            output[key] = value
        return output

    def reject_constant(_value: str) -> None:
        raise ReviewQueuePreflightError("NONFINITE_QUEUE_JSON_NUMBER")

    try:
        value = json.loads(payload, object_pairs_hook=unique, parse_constant=reject_constant)
    except ReviewQueuePreflightError:
        raise
    except (ValueError, TypeError):
        raise ReviewQueuePreflightError("INVALID_QUEUE_JSON") from None
    if not isinstance(value, dict):
        raise ReviewQueuePreflightError("QUEUE_NOT_OBJECT")
    return value


def audit_review_queue(queue: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(queue, dict) or queue.get("schema_version") != VERSION:
        raise ReviewQueuePreflightError("QUEUE_SCHEMA_MISMATCH")
    if queue.get("classification") != "LOCAL_REVIEW_WORKSPACE_ONLY":
        raise ReviewQueuePreflightError("QUEUE_SCOPE_INVALID")
    safety = queue.get("safety")
    if not isinstance(safety, dict) or any(safety.get(key) is not True for key in REQUIRED_SAFETY):
        raise ReviewQueuePreflightError("QUEUE_SAFETY_GUARD_MISSING")
    cases = queue.get("cases")
    counts = queue.get("counts")
    if not isinstance(cases, list) or not isinstance(counts, dict):
        raise ReviewQueuePreflightError("QUEUE_CASES_OR_COUNTS_INVALID")
    if (type(counts.get("candidate_count")) is not int
            or counts["candidate_count"] != len(cases)
            or any(type(counts.get(key)) is not int or counts[key] != 0 for key in (
                "real_gold", "upstream_ml_verified", "independent_expert_reviews_completed"
            )) or counts.get("training_authorized") is not False):
        raise ReviewQueuePreflightError("QUEUE_UNVERIFIED_COUNTS_INCONSISTENT")

    case_ids: set[str] = set()
    gap_counts: Counter[str] = Counter()
    unbound_family = 0
    for case in cases:
        if not isinstance(case, dict):
            raise ReviewQueuePreflightError("QUEUE_CASE_NOT_OBJECT")
        cid = case.get("case_id")
        if not isinstance(cid, str) or not cid.strip() or cid in case_ids:
            raise ReviewQueuePreflightError("QUEUE_CASE_ID_INVALID_OR_DUPLICATE")
        case_ids.add(cid)
        digest = case.get("source_case_sha256")
        if not isinstance(digest, str) or HEX.fullmatch(digest) is None:
            raise ReviewQueuePreflightError("QUEUE_SOURCE_HASH_INVALID")
        if (case.get("admission_track") != "REAL_GOLD_TRACK_CANDIDATE"
                or case.get("gold_eligible") is not False
                or case.get("training_authorized") is not False
                or case.get("not_for_sft") is not True):
            raise ReviewQueuePreflightError("QUEUE_PREMATURE_PROMOTION")
        # The v0.5 queue is an evidence-request artifact, not an evidence receipt.
        # These existing fields must remain explicitly unverified and unbound.
        if (case.get("source_permission_verified") is not False
                or case.get("deidentification_verified") is not False
                or "l1_packet_sha256" not in case
                or case["l1_packet_sha256"] is not None):
            raise ReviewQueuePreflightError("QUEUE_EVIDENCE_OR_L1_CLAIM_REQUIRES_SEPARATE_RECEIPT")
        if (case.get("reviewer_1") is not None
                or case.get("reviewer_2") is not None
                or case.get("adjudication_status") != "NOT_STARTED"):
            raise ReviewQueuePreflightError("QUEUE_REVIEW_STATUS_REQUIRES_SEPARATE_RECEIPT")
        family = case.get("event_family_id")
        if family is None:
            unbound_family += 1
        elif not isinstance(family, str) or not family.strip():
            raise ReviewQueuePreflightError("QUEUE_EVENT_FAMILY_INVALID")
        checks = case.get("verification_checklist")
        if not isinstance(checks, list) or len(checks) != len(CHECKS):
            raise ReviewQueuePreflightError("QUEUE_CHECKLIST_INCOMPLETE")
        seen: set[str] = set()
        for check in checks:
            if not isinstance(check, dict):
                raise ReviewQueuePreflightError("QUEUE_CHECK_INVALID")
            code = check.get("check_id")
            if not isinstance(code, str) or code not in CHECKS or code in seen:
                raise ReviewQueuePreflightError("QUEUE_CHECK_ID_INVALID_OR_DUPLICATE")
            seen.add(code)
            if (check.get("review_status") != "NOT_VERIFIED"
                    or check.get("evidence_ref") is not None
                    or check.get("evidence_sha256") is not None
                    or check.get("reviewer_token") is not None
                    or check.get("not_for_sft") is not True):
                raise ReviewQueuePreflightError("QUEUE_CHECK_REQUIRES_SEPARATE_EVIDENCE_RECEIPT")
            gap_counts[code] += 1

    return {
        "schema_version": "dgsi-real-review-queue-preflight.v1",
        "scope": "LOCAL_METADATA_ONLY",
        "case_count": len(cases),
        "unbound_event_family_count": unbound_family,
        "unverified_by_dimension": {key: gap_counts[key] for key in sorted(CHECKS)},
        "expert_review_ready_count": 0,
        "real_gold_count": 0,
        "training_authorized": False,
        "split_assignment_allowed": False,
        "note": "Queue declarations only; source/license, hashes, ML runs, cutoff, evidence and experts need separate review.",
    }
