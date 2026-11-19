"""Recompute the frozen comparison, including source-cluster equal weighting.

Run with --output NEW_FILE.json. No model call or file replacement is performed.
The source groups are coordinator-declared connected document clusters, not
independently authenticated physical events or formal dataset splits.
"""
import argparse
from collections import defaultdict
from fractions import Fraction
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from dgsi.skill_delivery import DeliveryError, digest, load_json, replay


def cluster_report(decisions, bindings):
    units = {row['comparison_unit_id'] for row in decisions}
    by_unit = {row['comparison_unit_id']: row for row in bindings}
    if len(by_unit) != len(bindings) or set(by_unit) != units:
        raise DeliveryError('SOURCE_CLUSTER_BINDING_INCOMPLETE')
    groups = {}
    for unit, binding in by_unit.items():
        clusters = binding.get('document_clusters')
        if (not isinstance(clusters, list) or len(clusters) != 1
                or not isinstance(clusters[0], str) or not clusters[0].strip()):
            raise DeliveryError('CONNECTED_SOURCE_CLUSTER_REQUIRED')
        groups[unit] = clusters[0]
    arms = defaultdict(lambda: defaultdict(list))
    for row in decisions:
        arms[row['arm']][groups[row['comparison_unit_id']]].append(row)
    result = {}
    for arm, clusters in sorted(arms.items()):
        per_cluster = {}
        means = []
        accepts = []
        for name, rows in sorted(clusters.items()):
            mean = sum(Fraction(str(r['gpt_score_out_of_20'])) for r in rows) / len(rows)
            accept = Fraction(sum(r['decision'] == 'AI_CONSENSUS_ACCEPT_DEV_ONLY'
                                  for r in rows), len(rows))
            means.append(mean)
            accepts.append(accept)
            per_cluster[name] = {'case_count': len(rows), 'gpt_mean_score_out_of_20': float(mean),
                                 'ai_consensus_accept_rate': float(accept)}
        result[arm] = {'clusters': per_cluster,
                       'equal_cluster_mean_score_out_of_20': float(sum(means) / len(means)),
                       'equal_cluster_accept_rate': float(sum(accepts) / len(accepts))}
    return {'connected_document_cluster_count': len(set(groups.values())),
            'primary_event_family_count': len({b['event_family'] for b in bindings}),
            'weighting': 'mean within each source cluster, then equal mean across clusters',
            'arms': result}


def observed_top_ties(arms):
    def key(value):
        return (-value['critical_failure_candidates'], value['ai_consensus_accept_count'],
                value['gpt_mean_score_out_of_20'])
    best = max(map(key, arms.values()))
    return sorted(arm for arm, value in arms.items() if key(value) == best)


def analyze(bundle):
    with tempfile.TemporaryDirectory() as tmp:
        report = replay(bundle, Path(tmp) / 'replay')
    bindings = load_json(bundle / 'coordinator/source_bindings.json')['bindings']
    cases = load_json(bundle / 'shared_cases.json')['cases']
    case_hashes = {row['comparison_unit_id']: digest(row['user']) for row in cases}
    if any(b['shared_input_sha256'] != case_hashes.get(b['comparison_unit_id']) for b in bindings):
        raise DeliveryError('SOURCE_CLUSTER_INPUT_MISMATCH')
    result = {key: report[key] for key in (
        'arms', 'trials', 'gpt_reviewed_candidates', 'gpt_review_records', 'disagreement_count',
        'ai_consensus_accept_count', 'human_expert_review_count', 'gold_eligible',
        'training_authorized', 'admitted_sft_records', 'official_splits_assigned',
        'downstream_sft_result')}
    result.update(schema_version='dgsi-forward-comparison-analysis.v1', not_for_sft=True,
                  source_clusters=cluster_report(report['trials'], bindings),
                  observed_top_ties=observed_top_ties(report['arms']),
                  inference='DESCRIPTIVE_ONLY_NO_GLOBAL_OPTIMUM_OR_DOWNSTREAM_GAIN_CLAIM')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = analyze(Path(__file__).resolve().parent)
    with args.output.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'decision': 'FROZEN_ANALYSIS_RECOMPUTED',
                      'candidates': result['gpt_reviewed_candidates'],
                      'observed_top_ties': result['observed_top_ties']}))
