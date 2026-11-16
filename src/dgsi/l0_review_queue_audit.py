"""Read-only preflight for L0 expert-review queues; never an admission action.

Input is a *local* source-fact matrix plus a reviewer queue. No raw sources,
expert identities, diagnostic logs, or private review remarks are exported.
This module does not create Gold cases, L1 packets or SFT records.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

REAL = 'REAL_GOLD_TRACK_CANDIDATE'
LIT = 'LITERATURE_SOURCE_FACT_CARD_ONLY'
DIMENSIONS = (
    'source_fidelity', 'phenomenon_analysis', 'ml_interpretation',
    'fault_source', 'affected_components', 'evidence_fidelity',
    'uncertainty', 'disposal_fidelity', 'historical_context_transfer',
    'engineering_actionability',
)


class L0QueueAuditError(ValueError):
    """Stable, non-sensitive error code."""


def canonical_sha256(value: Any) -> str:
    """Hash JSON semantics, not unstable dict order or formatted source bytes."""
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(',', ':'),
        allow_nan=False,
    ).encode('utf-8')).hexdigest()


def _index(cases: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(cases, list):
        raise L0QueueAuditError('L0_QUEUE_CASES_NOT_ARRAY')
    result = {}
    for case in cases:
        if not isinstance(case, dict) or not isinstance(case.get('case_id'), str) or not case['case_id'].strip():
            raise L0QueueAuditError('L0_QUEUE_CASE_ID_INVALID')
        case_id = case['case_id']
        if case_id in result:
            raise L0QueueAuditError('L0_QUEUE_CASE_ID_DUPLICATE')
        result[case_id] = case
    return result


def _review_blockers(review: Any, source_hash: str, dimensions: tuple[str, ...]) -> list[str]:
    if not isinstance(review, dict):
        return ['REVIEW_RECORD_INVALID']
    if review.get('decision') == 'NOT_SUBMITTED':
        # Never treat an unfinished reviewer placeholder as an approval.
        return ['REVIEW_NOT_SUBMITTED']
    problems = []
    if not isinstance(review.get('token'), str) or not review['token'].strip():
        problems.append('REVIEWER_TOKEN_MISSING')
    if review.get('case_record_sha256') != source_hash:
        problems.append('REVIEW_SOURCE_HASH_NOT_BOUND')
    scores = review.get('scores')
    if not isinstance(scores, dict) or set(scores) != set(dimensions) or any(
        v is None or isinstance(v, bool) or not isinstance(v, (int, float))
        for v in scores.values()
    ):
        problems.append('REVIEW_TEN_DIMENSIONS_INCOMPLETE')
    if not isinstance(review.get('source_refs'), list) or not review['source_refs'] or any(
        not isinstance(x, str) or not x.strip() for x in review['source_refs']
    ):
        problems.append('REVIEW_SOURCE_REFS_MISSING')
    if not isinstance(review.get('finding_codes'), list):
        problems.append('REVIEW_FINDING_CODES_INVALID')
    return problems


def audit_l0_review_queue(source_matrix: dict[str, Any], queue: dict[str, Any]) -> dict[str, Any]:
    """Return blockers only, with no promotion or training authorization.

    A public-literature L0 fact-card review is distinct from REAL_GOLD_TRACK:
    it must NOT require fabricated real ML results or simulated flight logs.
    """
    if not isinstance(source_matrix, dict) or not isinstance(queue, dict):
        raise L0QueueAuditError('L0_QUEUE_ROOT_INVALID')
    if queue.get('schema_version') != 'dgsi.local-l0-expert-preflight.v0.4':
        raise L0QueueAuditError('L0_QUEUE_SCHEMA_UNSUPPORTED')
    if queue.get('training_authorized') is True or queue.get('audit_summary', {}).get('training_authorized') is True:
        raise L0QueueAuditError('L0_QUEUE_TRAINING_AUTHORIZATION_FORBIDDEN')
    original = _index(source_matrix.get('cases'))
    submitted = _index(queue.get('cases'))
    if original.keys() != submitted.keys() or not submitted:
        raise L0QueueAuditError('L0_QUEUE_SOURCE_CASE_SET_MISMATCH')
    if tuple(queue.get('review_dimensions', ())) != DIMENSIONS:
        raise L0QueueAuditError('L0_QUEUE_REVIEW_DIMENSIONS_MISMATCH')

    reports = []
    for case_id, case in submitted.items():
        source = original[case_id]
        expected_hash = canonical_sha256(source)
        if case.get('case_record_sha256') != expected_hash:
            raise L0QueueAuditError('L0_QUEUE_SOURCE_CASE_HASH_MISMATCH')
        if case.get('source_category') != source.get('source_category'):
            raise L0QueueAuditError('L0_QUEUE_SOURCE_CATEGORY_MISMATCH')
        is_real = case['source_category'] == 'USER_SUPPLIED'
        expected_track = REAL if is_real else LIT
        if (case['source_category'] not in ('USER_SUPPLIED', 'PUBLIC_LITERATURE')
                or case.get('admission_path') != expected_track):
            raise L0QueueAuditError('L0_QUEUE_TRACK_MISMATCH')
        if (case.get('not_for_sft') is not True or case.get('sft_eligible') is not False
                or case.get('gold_approved') is not False
                or case.get('training_authorized') is not False):
            raise L0QueueAuditError('L0_QUEUE_PREMATURE_RELEASE_FLAG')

        blockers = []
        if not case.get('source_locator_independently_verified'):
            blockers.append('L0_SOURCE_LOCATOR_UNVERIFIED')
        if not case.get('event_family_id'):
            blockers.append('L0_EVENT_FAMILY_MISSING')
        if is_real:
            if not case.get('source_permission_verified'):
                blockers.append('REAL_SOURCE_PERMISSION_UNVERIFIED')
            if not case.get('deidentification_verified'):
                blockers.append('REAL_DEIDENTIFICATION_UNVERIFIED')
            if not case.get('analysis_cutoff'):
                blockers.append('REAL_ANALYSIS_CUTOFF_MISSING')
            if not case.get('upstream_run_ref') or not case.get('diagnostic_log_refs'):
                blockers.append('REAL_UPSTREAM_DIAGNOSIS_INCOMPLETE')
            if not case.get('l1_packet_sha256'):
                blockers.append('REAL_L1_PACKET_NOT_BOUND')
        # In L0 literature review, an absent REAL run is NOT an error.
        r1, r2 = case.get('reviewer_1'), case.get('reviewer_2')
        for i, r in enumerate((r1, r2), start=1):
            blockers.extend(f'R{i}_{x}' for x in _review_blockers(r, expected_hash, DIMENSIONS))
        if (isinstance(r1, dict) and isinstance(r2, dict)
                and r1.get('token') and r1.get('token') == r2.get('token')):
            blockers.append('REVIEWER_IDENTITY_NOT_INDEPENDENT')
        if case.get('adjudication_status') not in ('ADJUDICATED', 'APPROVED'):
            blockers.append('EXPERT_ADJUDICATION_PENDING')
        reports.append({
            'case_id': case_id,
            'track': expected_track,
            'review_ready': not blockers,
            'blocking_codes': sorted(set(blockers)),
        })
    return {
        'schema_version': 'dgsi.local-l0-queue-audit.v1',
        'case_count': len(reports),
        'real_candidate_count': sum(r['track'] == REAL for r in reports),
        'literature_fact_card_count': sum(r['track'] == LIT for r in reports),
        'review_ready_count': sum(r['review_ready'] for r in reports),
        'release_authorized': False,
        'gold_authorized': False,
        'training_authorized': False,
        'cases': reports,
    }


def audit_l0_review_queue_files(
    source_matrix_path: str | Path, queue_path: str | Path,
) -> dict[str, Any]:
    """Audit exact local files, binding queue to the actual source bytes.

    Callers should keep the returned per-case codes in an authorized review
    workspace. Neither source bytes nor review details are printed.
    """
    matrix_bytes = Path(source_matrix_path).read_bytes()
    queue_bytes = Path(queue_path).read_bytes()
    digest = hashlib.sha256(matrix_bytes).hexdigest()
    source_matrix = json.loads(matrix_bytes)
    queue = json.loads(queue_bytes)
    declared = queue.get('source_artifacts')
    if (not isinstance(declared, list) or not any(
            isinstance(item, dict) and item.get('sha256') == digest
            and item.get('filename') == Path(source_matrix_path).name
            for item in declared)):
        raise L0QueueAuditError('L0_QUEUE_SOURCE_FILE_HASH_NOT_BOUND')
    for case in queue.get('cases', []):
        if case.get('l0_matrix_source_sha256') != digest:
            raise L0QueueAuditError('L0_QUEUE_CASE_MATRIX_HASH_MISMATCH')
    return audit_l0_review_queue(source_matrix, queue)
