"""SYNTHETIC_TEST_ONLY: instruction selection never changes source inputs."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import hashlib
import shutil

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from dgsi.skill_delivery import digest, prepare, DeliveryError


class InstructionDesignTests(unittest.TestCase):
    def save_bound_file(self, bundle, relative, value):
        path = bundle / relative
        path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
        manifest_path = bundle / 'replay_manifest.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        checksum = hashlib.sha256(path.read_bytes()).hexdigest()
        entries = [item for item in manifest['files'] if item['path'] == relative]
        if entries:
            entries[0]['sha256'] = checksum
        else:
            manifest['files'].append({'path': relative, 'sha256': checksum})
        manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
        return checksum

    def api(self):
        self.assertIsNotNone(importlib.util.find_spec('dgsi.instruction_design'),
                             'bounded instruction selection is not implemented')
        from dgsi.instruction_design import resolve_instruction_design
        return resolve_instruction_design

    def fixture(self):
        user = {'case_id': 'SYNTHETIC-TEST', 'task_type': 'evidence_sufficiency',
                'instruction': 'Assess supplied evidence', 'input': {'logs': []}}
        scores = {'task_alignment': 2, 'clarity': 2, 'input_answerability': 2,
                  'evidence_roles': 2, 'scope_retention': 2}
        record = {'recipe_id': 'evolve-select', 'recipe_version': '1',
                  'input_sha256': digest(user), 'not_for_sft': True,
                  'candidates': [
                      {'candidate_id': 'I1', 'instruction': 'Assess the observations',
                       'operation': 'comparability', 'scores': dict(scores),
                       'grounding_ok': True, 'scope_ok': True},
                      {'candidate_id': 'I2', 'instruction': 'Separate inference and observations',
                       'operation': 'evidence_roles', 'scores': dict(scores),
                       'grounding_ok': True, 'scope_ok': True},
                      {'candidate_id': 'I3', 'instruction': 'Identify remaining evidence gaps',
                       'operation': 'bounded_scope', 'scores': dict(scores),
                       'grounding_ok': True, 'scope_ok': True}],
                  'selected_candidate_id': 'I1'}
        return user, record

    def test_tie_uses_original_order_and_never_mutates_input(self):
        resolve = self.api()
        user, record = self.fixture()
        before = copy.deepcopy((user, record))
        selected = resolve(user, record)
        self.assertEqual(selected, 'Assess the observations')
        self.assertEqual((user, record), before)

    def test_ineligible_candidate_cannot_win_even_with_higher_scores(self):
        resolve = self.api()
        user, record = self.fixture()
        record['candidates'][0]['grounding_ok'] = False
        record['selected_candidate_id'] = 'I2'
        self.assertEqual(resolve(user, record), 'Separate inference and observations')
        record['selected_candidate_id'] = 'I1'
        with self.assertRaisesRegex(DeliveryError, 'INSTRUCTION_SELECTION_MISMATCH'):
            resolve(user, record)

    def test_changed_input_or_unscoped_answer_cannot_reuse_selection(self):
        resolve = self.api()
        user, record = self.fixture()
        changed = copy.deepcopy(user); changed['input']['logs'].append('new material')
        with self.assertRaisesRegex(DeliveryError, 'INSTRUCTION_INPUT_MISMATCH'):
            resolve(changed, record)
        record['formal_target'] = {'cause': 'unseen answer'}
        with self.assertRaisesRegex(DeliveryError, 'INSTRUCTION_RECORD_INVALID'):
            resolve(user, record)

    def test_duplicate_choices_bad_scores_and_empty_pool_fail_closed(self):
        resolve = self.api()
        for mutation in ('duplicate', 'boolean_score', 'unknown_score', 'empty_pool'):
            user, record = self.fixture()
            if mutation == 'duplicate':
                record['candidates'][1]['instruction'] = '  Assess   the observations  '
            elif mutation == 'boolean_score':
                record['candidates'][0]['scores']['clarity'] = True
            elif mutation == 'unknown_score':
                record['candidates'][0]['scores']['test_set_score'] = 2
            else:
                for candidate in record['candidates']:
                    candidate['grounding_ok'] = False
            with self.subTest(mutation=mutation), self.assertRaises(DeliveryError):
                resolve(user, record)

    def test_prepare_recipe_sidecar_leaves_generation_messages_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            base, refined = Path(tmp)/'base', Path(tmp)/'refined'
            fixtures = ROOT/'evaluation/closeout_20261119/fixtures'
            prepare(fixtures/'l1_collection.json', fixtures/'l0_source_facts.json', base)
            result = subprocess.run([sys.executable, str(ROOT/'scripts/run_dgsi_skill.py'),
                'prepare', '--collection', str(fixtures/'l1_collection.json'),
                '--source-facts', str(fixtures/'l0_source_facts.json'),
                '--recipe', 'evolve-select', '--output', str(refined)],
                cwd=tmp, capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertEqual((base/'generation_requests.jsonl').read_bytes(),
                             (refined/'generation_requests.jsonl').read_bytes())
            recipe = json.loads((refined/'authoring_recipe.json').read_text(encoding='utf-8'))
            self.assertTrue(recipe['not_for_sft'])
            self.assertEqual(recipe['recipe_id'], 'evolve-select')
            self.assertEqual(recipe['candidate_count'], 3)
            self.assertFalse(json.loads(result.stdout)['training_authorized'])

    def test_unknown_recipe_has_no_partial_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)/'output'
            fixtures = ROOT/'evaluation/closeout_20261119/fixtures'
            result = subprocess.run([sys.executable, str(ROOT/'scripts/run_dgsi_skill.py'),
                'prepare', '--collection', str(fixtures/'l1_collection.json'),
                '--source-facts', str(fixtures/'l0_source_facts.json'),
                '--recipe', 'select_by_test_score', '--output', str(out)],
                capture_output=True, text=True, encoding='utf-8', timeout=90)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())

    def test_replay_respects_frozen_curated_arm_and_rejects_unknown_arm(self):
        from dgsi.skill_delivery import replay
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)/'bundle'
            shutil.copytree(ROOT/'evaluation/closeout_20261119', bundle)
            for arm in ('M1', 'not_in_matrix'):
                protocol_path = bundle/'protocol.json'
                protocol = json.loads(protocol_path.read_text(encoding='utf-8'))
                protocol['curated_arm'] = arm
                protocol_path.write_text(json.dumps(protocol), encoding='utf-8')
                manifest_path = bundle/'replay_manifest.json'
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                for item in manifest['files']:
                    if item['path'] == 'protocol.json':
                        item['sha256'] = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
                manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
                if arm == 'M1':
                    report = replay(bundle, Path(tmp)/arm)
                    self.assertEqual(report.get('curated_arm'), 'M1')
                    self.assertEqual(report['curated_dgsi_preview_records'], 3)
                else:
                    with self.assertRaisesRegex(DeliveryError, 'REPLAY_CURATED_ARM_INVALID'):
                        replay(bundle, Path(tmp)/arm)
                    self.assertFalse((Path(tmp)/arm).exists())

    def test_replay_cannot_ignore_recipe_record_or_raw_generation_binding(self):
        from dgsi.skill_delivery import replay
        from dgsi.instruction_design import authoring_recipe
        for mutation in ('invalid_selection', 'missing_required_record', 'changed_raw_answer'):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)/'bundle'
                shutil.copytree(ROOT/'evaluation/closeout_20261119', bundle)
                trials = json.loads((bundle/'trials.json').read_text(encoding='utf-8'))
                row = next(t for t in trials['trials'] if t['arm'] == 'M4')
                raw_path = row['generation_file']
                raw = json.loads((bundle/raw_path).read_text(encoding='utf-8'))
                candidate = next(c for c in raw['candidates']
                                 if c['comparison_unit_id'] == row['comparison_unit_id'])
                if mutation == 'invalid_selection':
                    _, record = self.fixture()
                    record['input_sha256'] = row['shared_input_sha256']
                    record['selected_candidate_id'] = 'I99'
                    candidate['method_record'] = record
                elif mutation == 'missing_required_record':
                    prompt = json.loads((bundle/'prompts/M4.json').read_text(encoding='utf-8'))
                    prompt['authoring_recipe'] = authoring_recipe('evolve')
                    self.save_bound_file(bundle, 'prompts/M4.json', prompt)
                    candidate.pop('method_record')
                else:
                    candidate['formal_target']['phenomenon_analysis'] = 'Unreviewed replacement'
                checksum = self.save_bound_file(bundle, raw_path, raw)
                for trial in trials['trials']:
                    if trial['generation_file'] == raw_path:
                        trial['generation_file_sha256'] = checksum
                self.save_bound_file(bundle, 'trials.json', trials)
                with self.assertRaises(DeliveryError):
                    replay(bundle, Path(tmp)/'out')
                self.assertFalse((Path(tmp)/'out').exists())

    def test_replay_enforces_frozen_zero_regeneration_budget(self):
        from dgsi.skill_delivery import replay
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)/'bundle'
            shutil.copytree(ROOT/'evaluation/closeout_20261119', bundle)
            protocol = json.loads((bundle/'protocol.json').read_text(encoding='utf-8'))
            protocol['max_semantic_regenerations'] = 0
            self.save_bound_file(bundle, 'protocol.json', protocol)
            with self.assertRaisesRegex(DeliveryError, 'REPLAY_REVISIONS_FORBIDDEN'):
                replay(bundle, Path(tmp)/'out')
            self.assertFalse((Path(tmp)/'out').exists())

    def test_replay_checks_prefrozen_hashes_separately_from_output_manifest(self):
        from dgsi.skill_delivery import replay
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp)/'bundle'
            shutil.copytree(ROOT/'evaluation/closeout_20261119', bundle)
            self.save_bound_file(bundle, 'frozen_input_manifest.json',
                {'not_for_sft': True, 'files': [{'path': 'protocol.json', 'sha256': '0'*64}]})
            with self.assertRaisesRegex(DeliveryError, 'REPLAY_FROZEN_INPUT_MISMATCH'):
                replay(bundle, Path(tmp)/'out')
            self.assertFalse((Path(tmp)/'out').exists())

    def comparison_api(self):
        path = ROOT/'evaluation/refinement_20261119/analyze.py'
        spec = importlib.util.spec_from_file_location('forward_analysis', path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_refinement_replay_requires_complete_preregistered_input_coverage(self):
        from dgsi.skill_delivery import replay
        for incomplete in ('empty', 'protocol_only'):
            with self.subTest(incomplete=incomplete), tempfile.TemporaryDirectory() as tmp:
                bundle = Path(tmp)/'bundle'
                shutil.copytree(ROOT/'evaluation/closeout_20261119', bundle)
                protocol = json.loads((bundle/'protocol.json').read_text(encoding='utf-8'))
                protocol['schema_version'] = 'dgsi-refinement-protocol.v1'
                checksum = self.save_bound_file(bundle, 'protocol.json', protocol)
                files = [] if incomplete == 'empty' else [{'path': 'protocol.json', 'sha256': checksum}]
                self.save_bound_file(bundle, 'frozen_input_manifest.json',
                                     {'not_for_sft': True, 'files': files})
                with self.assertRaisesRegex(DeliveryError, 'REPLAY_FROZEN_COVERAGE_INCOMPLETE'):
                    replay(bundle, Path(tmp)/'out')
                self.assertFalse((Path(tmp)/'out').exists())

    def test_cluster_weighting_does_not_count_three_same_document_cases_as_three_sources(self):
        analyze = self.comparison_api()
        decisions = [{'comparison_unit_id': f'U{i}', 'arm': 'A',
                      'gpt_score_out_of_20': score, 'decision': 'AI_CONSENSUS_ACCEPT_DEV_ONLY'}
                     for i, score in enumerate((20, 20, 20, 10))]
        bindings = [{'comparison_unit_id': f'U{i}', 'event_family': f'F{i}',
                     'document_clusters': ['D1' if i < 3 else 'D2']}
                    for i in range(4)]
        grouped = analyze.cluster_report(decisions, bindings)
        self.assertEqual(grouped['connected_document_cluster_count'], 2)
        self.assertEqual(grouped['primary_event_family_count'], 4)
        self.assertEqual(grouped['arms']['A']['equal_cluster_mean_score_out_of_20'], 15)
        for bad in (bindings[:-1], bindings + bindings[:1]):
            with self.assertRaisesRegex(DeliveryError, 'SOURCE_CLUSTER_BINDING_INCOMPLETE'):
                analyze.cluster_report(decisions, bad)

    def test_descriptive_ranking_preserves_ties_and_prioritizes_critical_failures(self):
        analyze = self.comparison_api()
        good = {'critical_failure_candidates': 0, 'ai_consensus_accept_count': 3,
                'gpt_mean_score_out_of_20': 19}
        high_but_critical = {'critical_failure_candidates': 1, 'ai_consensus_accept_count': 4,
                            'gpt_mean_score_out_of_20': 20}
        self.assertEqual(analyze.observed_top_ties({'B': dict(good), 'A': dict(good),
                                                   'C': high_but_critical}), ['A', 'B'])


if __name__ == '__main__':
    unittest.main()
