"""SYNTHETIC_TEST_ONLY: user-facing prepare/replay boundary, no admission."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
ENTRY = ROOT / 'scripts/run_dgsi_skill.py'
COLLECTION = ROOT / 'examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json'
FACTS = ROOT / 'examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json'
BUNDLE = ROOT / 'evaluation/closeout_20261119'
EXPECTED_PACKETS, EXPECTED_BLOCKED = 21, 3
if not COLLECTION.exists():  # Same test can run in the extracted standalone ZIP.
    COLLECTION = BUNDLE / 'fixtures/l1_collection.json'
    FACTS = BUNDLE / 'fixtures/l0_source_facts.json'
    EXPECTED_PACKETS, EXPECTED_BLOCKED = 4, 1


class SkillDeliveryTests(unittest.TestCase):
    def run_entry(self, *args):
        return subprocess.run([sys.executable, str(ENTRY), *map(str, args)],
                              cwd=tempfile.gettempdir(), capture_output=True, text=True,
                              encoding='utf-8', timeout=90)

    def test_entry_help_works_without_pythonpath_or_repo_cwd(self):
        result = self.run_entry('--help')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('prepare', result.stdout)
        self.assertIn('demo', result.stdout)

    def test_prepare_binds_inputs_hides_targets_and_blocks_untrusted_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'prepared'
            result = self.run_entry('prepare', '--collection', COLLECTION,
                                    '--source-facts', FACTS, '--output', out)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            requests = [json.loads(line) for line in (out/'generation_requests.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(requests), EXPECTED_PACKETS)
            for req in requests:
                self.assertEqual([m['role'] for m in req['messages']], ['system','user'])
                visible = json.loads(req['messages'][1]['content'])
                self.assertTrue(visible['case_id'].startswith('SYNTHETIC-EVAL-CASE-'))
                self.assertEqual(visible['input']['knowledge_evidence'], [])
                self.assertNotIn('formal_target', visible)
                self.assertNotIn('expected_output', visible)
                self.assertNotIn('internal_review', visible)
                self.assertEqual(visible['input']['historical_cases'], [])
            report=json.loads((out/'status.json').read_text(encoding='utf-8'))
            self.assertEqual(report['blocked_history_items'],EXPECTED_BLOCKED)
            self.assertEqual(report['admitted_sft_records'],0)
            self.assertFalse(report['training_authorized'])
            again=self.run_entry('prepare','--collection',COLLECTION,'--source-facts',FACTS,'--output',out)
            self.assertEqual(again.returncode,2)
            self.assertEqual(len((out/'generation_requests.jsonl').read_text(encoding='utf-8').splitlines()),EXPECTED_PACKETS)

    def test_missing_source_never_emits_candidate_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'blocked'
            r=self.run_entry('prepare','--collection',COLLECTION,'--source-facts',Path(tmp)/'missing.json','--output',out)
            self.assertEqual(r.returncode,2)
            self.assertEqual(json.loads(r.stdout)['error_code'],'INPUT_FILE_NOT_FOUND')
            self.assertFalse(out.exists())

    def test_same_ai_reviewer_and_stale_hash_cannot_be_two_reviews(self):
        self.assertIsNotNone(importlib.util.find_spec('dgsi.skill_delivery'), 'delivery module missing')
        from dgsi.skill_delivery import summarize_ai_reviews, digest, candidate_digest, DeliveryError, DIMENSIONS
        user={'case_id':'SYNTHETIC-EVAL-CASE-001','input':{}}
        output={'phenomenon_analysis':'SYNTHETIC_TEST_ONLY'}
        row={'trial_id':'T1','arm':'M4','comparison_unit_id':'U1','shared_input_sha256':digest(user),'instruction':'Assess visible evidence','formal_target':output}
        review={'trial_id':'T1','shared_input_sha256':digest(user),'target_sha256':digest(output),'candidate_sha256':candidate_digest(row),'reviewer_kind':'GPT','reviewer_token':'AI-A','scores':dict.fromkeys(DIMENSIONS,2),'critical_failures':[],'recommendation':'ACCEPT','findings':[]}
        with self.assertRaises(DeliveryError):
            summarize_ai_reviews([row],[review,copy.deepcopy(review)])
        whitespace_alias=copy.deepcopy(review);whitespace_alias['reviewer_token']=' AI-A '
        with self.assertRaisesRegex(DeliveryError,'GPT_REVIEWERS_MUST_DIFFER'):
            summarize_ai_reviews([row],[review,whitespace_alias])
        second=copy.deepcopy(review);second['reviewer_token']='AI-B';second['target_sha256']='0'*64
        with self.assertRaises(DeliveryError):
            summarize_ai_reviews([row],[review,second])
        second['target_sha256']=digest(output);second['scores']['uncertainty']=1;second['recommendation']='REVISE'
        report=summarize_ai_reviews([row],[review,second])
        self.assertEqual(report['human_expert_review_count'],0)
        self.assertEqual(report['gpt_reviewed_candidates'],1)
        self.assertEqual(report['ai_consensus_accept_count'],0)
        self.assertEqual(report['disagreement_count'],1)
        self.assertFalse(report['training_authorized'])
        for key, changed in [('instruction','Declare a confirmed failure'),('arm','M0')]:
            altered=copy.deepcopy(row);altered[key]=changed
            with self.assertRaisesRegex(DeliveryError,'STALE_GPT_REVIEW'):
                summarize_ai_reviews([altered],[review,second])

    def test_recorded_demo_replays_actual_candidates_and_paired_gpt_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'demo'
            result=self.run_entry('demo','--output',out)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            report=json.loads(result.stdout)
            self.assertEqual(report['preview_records'],20)
            self.assertEqual(report['gpt_review_records'],40)
            self.assertEqual(report['case_count'],4)
            self.assertEqual(report['model_calls_this_run'],0)
            self.assertEqual(report['human_expert_review_count'],0)
            previews=[json.loads(s) for s in (out/'dgsi_preview_messages.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertEqual(len(previews),4)
            for row in previews:
                self.assertEqual([m['role'] for m in row['messages']],['system','user','assistant'])
                self.assertTrue(row['preview_only'])
                self.assertFalse(row['export_authorized'])
                self.assertIsNone(row['split'])
                user=json.loads(row['messages'][1]['content'])
                self.assertNotIn('internal_review',user)
                self.assertEqual(user['input']['knowledge_evidence'],[])
            again=self.run_entry('demo','--output',out)
            self.assertEqual(json.loads(again.stdout)['error_code'],'OUTPUT_ALREADY_EXISTS')

    def test_replay_rejects_changed_bytes_and_even_rehashed_incomplete_matrix(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle=Path(tmp)/'bundle'
            shutil.copytree(BUNDLE,bundle)
            trials_path=bundle/'trials.json'
            trials=json.loads(trials_path.read_text(encoding='utf-8'))
            trials['trials']=trials['trials'][:1]
            trials_path.write_text(json.dumps(trials),encoding='utf-8')
            for rehash,expected in [(False,'REPLAY_HASH_MISMATCH'),(True,'REPLAY_MATRIX_INCOMPLETE')]:
                if rehash:
                    path=bundle/'replay_manifest.json'
                    m=json.loads(path.read_text(encoding='utf-8'))
                    for entry in m['files']:
                        if entry['path']=='trials.json':
                            entry['sha256']=hashlib.sha256(trials_path.read_bytes()).hexdigest()
                    path.write_text(json.dumps(m),encoding='utf-8')
                out=Path(tmp)/f'output-{rehash}'
                result=self.run_entry('demo','--bundle',bundle,'--output',out)
                self.assertEqual(result.returncode,2)
                self.assertEqual(json.loads(result.stdout)['error_code'],expected)
                self.assertFalse(out.exists())


if __name__ == '__main__':
    unittest.main()
