"""Portable operator entry: preparation and replay, with separate GPT advisory review.

No model calls, human attestation, source-rights decision or training admission.
"""
from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from .l1_blind_review_manifest import build_l1_blind_review_manifest
from .l1_model_projection_preview import SYSTEM_CONTENT
from .sota_construction_scorecard import DIMENSIONS, CRITICAL


class DeliveryError(ValueError):
    """Fixed operator-facing codes, never raw input material."""


def digest(value: Any) -> str:
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                             separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def candidate_digest(row: dict) -> str:
    """Bind the effective instruction, answer and coordinator method attribution.

    Reviewers receive this opaque digest; the arm name stays blinded until review
    finishes. An old review cannot follow an edited instruction or reassigned arm.
    """
    return digest({key: row[key] for key in (
        'trial_id', 'arm', 'comparison_unit_id', 'shared_input_sha256',
        'instruction', 'formal_target')})


def load_json(path: Path) -> Any:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise DeliveryError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def invalid(_):
        raise DeliveryError('NONFINITE_JSON')
    value = json.loads(path.read_text(encoding='utf-8-sig'), object_pairs_hook=unique,
                       parse_constant=invalid)
    digest(value)  # Also reject overflow such as 1e999.
    return value


def _time(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.utcoffset() is None:
        raise ValueError('timezone required')
    return result


def project_user(packet: dict, index: int) -> tuple[dict, list[dict]]:
    """Conservative generation projection; never mutate the frozen packet.

    Current-event literature conclusions are quarantined in preparation. History
    needs a declared, traceable time attestation, not an invented publication time.
    The declared attestation is not independently authenticated by this tool.
    """
    case = packet['case']
    inp = deepcopy(case['input'])
    inp['knowledge_evidence'] = []
    original = {h['case_ref']: h for h in inp.get('historical_cases', [])}
    inp['historical_cases'] = []
    blocked = []
    for hit in packet['history_context']['items']:
        meta = hit.get('hit_metadata', {})
        attestation = meta.get('time_provenance', {})
        reason = 'MISSING_TRUSTED_TIME'
        traceable = (attestation.get('status') == 'TRUSTED_SOURCE_TIME'
                     and bool(attestation.get('available_at_source_ref'))
                     and bool(attestation.get('verified_at_source_ref')))
        if traceable:
            try:
                cutoff = _time(inp['analysis_cutoff'])
                admissible = (_time(meta['available_at']) <= cutoff
                              and _time(meta['verified_at']) <= cutoff)
                reason = 'AFTER_ANALYSIS_CUTOFF'
            except (KeyError, TypeError, AttributeError, ValueError):
                admissible = False
                reason = 'INVALID_TIME'
        else:
            admissible = False
        if admissible and hit['case_ref'] in original:
            item = deepcopy(original[hit['case_ref']])
            item.update({k: deepcopy(hit[k]) for k in (
                'source_refs', 'event_family_id', 'historical_equipment_scope',
                'hardware_compatibility', 'outcome_status')})
            item['available_at'] = meta['available_at']
            item['verified_at'] = meta['verified_at']
            item['time_provenance'] = deepcopy(attestation)
            inp['historical_cases'].append(item)
        else:
            blocked.append({'source_case_ref': hit['case_ref'],
                            'reason': reason, 'summary_withheld': True})
    inp['history_retrieval'] = {
        'status': 'HIT' if inp['historical_cases'] else ('BLOCKED' if blocked else 'NO_HIT'),
        'eligible_hits': len(inp['historical_cases']), 'blocked_hits': blocked,
    }
    return {
        'data_classification': 'LITERATURE_DERIVED_SYNTHETIC_NOT_REAL_RECORD',
        'case_id': f'SYNTHETIC-EVAL-CASE-{index:03d}',
        'task_type': case['task_type'], 'instruction': case['instruction'], 'input': inp,
    }, blocked


def _save(directory: Path, files: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=False)
    for name, value in files.items():
        path = directory / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8', newline='\n') as stream:
            if name.endswith('.jsonl'):
                for row in value:
                    stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
            else:
                stream.write(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def prepare(collection_path: Path, facts_path: Path, output: Path) -> dict:
    collection, facts = load_json(collection_path), load_json(facts_path)
    manifest = build_l1_blind_review_manifest(collection, source_fact_cards=facts['cards'])
    by_task = {r['task_id']: r for r in manifest['review_packets']}
    requests, bindings, blocked = [], [], []
    for index, packet in enumerate(collection['packets'], 1):
        user, rejected = project_user(packet, index)
        blocked.extend(rejected)
        requests.append({'request_id': user['case_id'], 'shared_input_sha256': digest(user),
                         'messages': [{'role': 'system', 'content': SYSTEM_CONTENT},
                                      {'role': 'user', 'content': json.dumps(user, ensure_ascii=False)}]})
        bindings.append({'request_id': user['case_id'], 'task_id': packet['task_id'],
                         'packet_sha256': by_task[packet['task_id']]['packet_sha256'],
                         'source_public_sha256': by_task[packet['task_id']]['source_public_sha256'],
                         'shared_input_sha256': digest(user), 'not_for_sft': True,
                         'projection_changes': ['current-event literature conclusions quarantined',
                                                'opaque case ID', 'untrusted history content withheld']})
    report = {'decision': 'GENERATION_INPUTS_PREPARED', 'request_count': len(requests),
              'blocked_history_items': len(blocked), 'generation_performed': False,
              'human_expert_review_count': 0, 'admitted_sft_records': 0,
              'gold_eligible': False, 'training_authorized': False,
              'scope': 'LITERATURE_DERIVED_SYNTHETIC; host AI performs authoring and review'}
    _save(output, {'generation_requests.jsonl': requests,
                  'coordinator/bindings.json': {'not_for_sft': True, 'bindings': bindings},
                  'coordinator/human_review_manifest.json': manifest, 'status.json': report})
    return report


def summarize_ai_reviews(trials: list[dict], reviews: list[dict]) -> dict:
    indexed = defaultdict(list)
    ids = {row['trial_id'] for row in trials}
    if len(ids) != len(trials):
        raise DeliveryError('DUPLICATE_TRIAL')
    for review in reviews:
        if review.get('trial_id') not in ids:
            raise DeliveryError('UNKNOWN_REVIEW_TRIAL')
        indexed[review['trial_id']].append(review)
    decisions, arms = [], defaultdict(list)
    for row in trials:
        pair = indexed[row['trial_id']]
        if len(pair) != 2:
            raise DeliveryError('TWO_GPT_REVIEWS_REQUIRED')
        tokens = [r.get('reviewer_token') for r in pair]
        if (any(not isinstance(t, str) or not t.strip() for t in tokens)
                or len({t.strip() for t in tokens}) != 2):
            raise DeliveryError('GPT_REVIEWERS_MUST_DIFFER')
        for r in pair:
            if r.get('reviewer_kind') != 'GPT':
                raise DeliveryError('GPT_REVIEW_MUST_BE_LABELED')
            if (r.get('shared_input_sha256') != row['shared_input_sha256']
                    or r.get('target_sha256') != digest(row['formal_target'])
                    or r.get('candidate_sha256') != candidate_digest(row)):
                raise DeliveryError('STALE_GPT_REVIEW')
            scores = r.get('scores', {})
            if (set(scores) != set(DIMENSIONS)
                    or any(type(v) is not int or v not in (0, 1, 2) for v in scores.values())):
                raise DeliveryError('GPT_REVIEW_SCORES_INVALID')
            if (r.get('recommendation') not in ('ACCEPT', 'REVISE', 'REJECT')
                    or not isinstance(r.get('critical_failures'), list)
                    or any(c not in CRITICAL for c in r['critical_failures'])):
                raise DeliveryError('GPT_REVIEW_DECISION_INVALID')
        scores = {d: sum(r['scores'][d] for r in pair) / 2 for d in DIMENSIONS}
        critical = sorted({c for r in pair for c in r['critical_failures']})
        accept = (not critical and all(r['recommendation'] == 'ACCEPT' for r in pair)
                  and all(v > 0 for r in pair for v in r['scores'].values()))
        disagree = (pair[0]['scores'] != pair[1]['scores']
                    or pair[0]['recommendation'] != pair[1]['recommendation']
                    or set(pair[0]['critical_failures']) != set(pair[1]['critical_failures']))
        result = {'trial_id': row['trial_id'], 'arm': row['arm'],
                  'comparison_unit_id': row['comparison_unit_id'],
                  'gpt_mean_dimension_scores': scores, 'gpt_score_out_of_20': sum(scores.values()),
                  'critical_failures': critical, 'reviewer_disagreement': disagree,
                  'decision': 'AI_CONSENSUS_ACCEPT_DEV_ONLY' if accept else 'AI_REVIEW_REQUIRES_REVISION'}
        decisions.append(result)
        arms[row['arm']].append(result)
    return {'schema_version': 'dgsi-gpt-advisory-summary.v1',
            'review_kind': 'GPT_ADVISORY_NOT_HUMAN_EXPERT',
            'gpt_reviewed_candidates': len(trials), 'gpt_review_records': len(reviews),
            'human_expert_review_count': 0,
            'ai_consensus_accept_count': sum(r['decision'] == 'AI_CONSENSUS_ACCEPT_DEV_ONLY' for r in decisions),
            'disagreement_count': sum(r['reviewer_disagreement'] for r in decisions),
            'trials': decisions,
            'arms': {arm: {'candidates': len(rows),
                           'gpt_mean_score_out_of_20': sum(r['gpt_score_out_of_20'] for r in rows) / len(rows),
                           'critical_failure_candidates': sum(bool(r['critical_failures']) for r in rows),
                           'ai_consensus_accept_count': sum(r['decision'] == 'AI_CONSENSUS_ACCEPT_DEV_ONLY' for r in rows)}
                     for arm, rows in sorted(arms.items())},
            'gold_eligible': False, 'training_authorized': False,
            'admitted_sft_records': 0, 'official_splits_assigned': False,
            'downstream_sft_result': 'NOT_RUN'}


def replay(bundle: Path, output: Path) -> dict:
    manifest = load_json(bundle / 'replay_manifest.json')
    listed = set()
    for entry in manifest['files']:
        relative = Path(entry['path'])
        if relative.is_absolute() or '..' in relative.parts or entry['path'] in listed:
            raise DeliveryError('REPLAY_MANIFEST_PATH_INVALID')
        listed.add(entry['path'])
        path = bundle / relative
        if not path.resolve().is_relative_to(bundle.resolve()):
            raise DeliveryError('REPLAY_MANIFEST_PATH_INVALID')
        if sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise DeliveryError('REPLAY_HASH_MISMATCH')
    required = {'shared_cases.json', 'trials.json', 'gpt_reviews.json',
                'target_schema.json', 'protocol.json'}
    if not required.issubset(listed):
        raise DeliveryError('REPLAY_BINDING_INCOMPLETE')
    case_rows = load_json(bundle/'shared_cases.json')['cases']
    cases = {r['comparison_unit_id']: r for r in case_rows}
    trials = load_json(bundle/'trials.json')['trials']
    reviews = load_json(bundle/'gpt_reviews.json')['reviews']
    protocol = load_json(bundle/'protocol.json')
    arms = protocol['method_ids']
    expected = {(unit, arm) for unit in cases for arm in arms}
    actual = [(r['comparison_unit_id'], r['arm']) for r in trials]
    if (not cases or not arms or len(cases) != len(case_rows)
            or len(set(arms)) != len(arms)
            or len(cases) != protocol['cases'] or len(arms) != protocol['methods']
            or len(trials) != protocol['planned_candidates']
            or len(actual) != len(set(actual)) or set(actual) != expected):
        raise DeliveryError('REPLAY_MATRIX_INCOMPLETE')
    validator = Draft202012Validator(load_json(bundle/'target_schema.json'))
    def preview_row(row):
        case = cases[row['comparison_unit_id']]
        if (digest(case['user']) != row['shared_input_sha256']
                or case['shared_input_sha256'] != row['shared_input_sha256']):
            raise DeliveryError('REPLAY_INPUT_MISMATCH')
        validator.validate(row['formal_target'])
        return {'example_id': row['trial_id'], 'preview_only': True,
                         'export_authorized': False, 'split': None,
                         'data_classification': 'LITERATURE_DERIVED_SYNTHETIC',
                         'messages': [{'role': 'system', 'content': SYSTEM_CONTENT},
                                      {'role': 'user', 'content': json.dumps({**case['user'], 'instruction': row['instruction']},ensure_ascii=False)},
                                      {'role': 'assistant', 'content': json.dumps(row['formal_target'],ensure_ascii=False)}]}
    report = summarize_ai_reviews(trials, reviews)
    decisions = {r['trial_id']: r['decision'] for r in report['trials']}
    previews = [dict(preview_row(row), gpt_review_decision=decisions[row['trial_id']])
                for row in trials]
    curated = {r['trial_id']: p for r, p in zip(trials, previews)
               if r['arm'] == 'M4' and decisions[r['trial_id']] == 'AI_CONSENSUS_ACCEPT_DEV_ONLY'}
    revision_report = None
    if 'delivery_revisions.json' in listed:
        revision_bundle = load_json(bundle/'delivery_revisions.json')
        revisions = revision_bundle['revisions']
        revision_report = summarize_ai_reviews(revisions, revision_bundle['reviews'])
        originals = {row['trial_id']: row for row in trials}
        revised_parents = set()
        for row, decision in zip(revisions, revision_report['trials']):
            parent = originals.get(row.get('revision_of'))
            if (parent is None or row['trial_id'] in originals
                    or row['revision_of'] in revised_parents
                    or row['revision_of_candidate_sha256'] != candidate_digest(parent)
                    or row['arm'] != parent['arm']
                    or row['comparison_unit_id'] != parent['comparison_unit_id']
                    or row['shared_input_sha256'] != parent['shared_input_sha256']):
                raise DeliveryError('DELIVERY_REVISION_BINDING_INVALID')
            revised_parents.add(row['revision_of'])
            preview = dict(preview_row(row), gpt_review_decision=decision['decision'],
                           revision_of=row['revision_of'])
            curated.pop(row['revision_of'], None)
            if row['arm'] == 'M4' and decision['decision'] == 'AI_CONSENSUS_ACCEPT_DEV_ONLY':
                curated[row['trial_id']] = preview
    report.update({'decision': 'RECORDED_DEVELOPMENT_RUN_REPLAYED', 'model_calls_this_run': 0,
                   'new_generations_this_run': 0, 'preview_records': len(previews),
                   'case_count': len(cases), 'verified_replay_files': len(listed),
                   'curated_dgsi_preview_records': len(curated),
                   'delivery_revision_review': revision_report,
                   'primary_comparison_changed_by_delivery_revisions': False})
    _save(output, {'preview_messages.jsonl': previews,
                  'dgsi_preview_messages.jsonl': [p for p, r in zip(previews,trials) if r['arm']=='M4'],
                  'dgsi_curated_preview_messages.jsonl': sorted(curated.values(),key=lambda p:p['example_id']),
                  'gpt_review_report.json': report,
                  'source_and_generation_manifest.json': manifest})
    return report
