"""SYNTHETIC_TEST_ONLY: topology metadata is not physical or expert evidence."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def fixture():
    graph = {
        'schema_version': 'dgsi.diagram-annotation.v1', 'source_id': 'TEST-SOURCE',
        'source_sha256': 'a'*64, 'asset_id': 'TEST-IMAGE', 'asset_sha256': 'b'*64,
        'locator': 'SYNTHETIC_TEST_ONLY figure', 'diagram_type': 'UNKNOWN',
        'nodes': [{'node_id': n, 'label': 'SYNTHETIC_TEST_ONLY '+n,
                   'object_type': 'UNKNOWN', 'hierarchy_path': [],
                   'evidence_locator': 'SYNTHETIC_TEST_ONLY label',
                   'review_status': 'AI_PROPOSED'} for n in ('N1', 'N2')],
        'ports': [], 'edges': [], 'claims': [], 'review_status': 'REVIEW_REQUIRED',
        'training_authorized': False,
    }
    receipt = {
        'schema_version': 'dgsi.diagram-topology-review.v1', 'review_id': 'R1',
        'graph_sha256': digest(graph), 'source_sha256': 'a'*64,
        'asset_id': 'TEST-IMAGE', 'asset_sha256': 'b'*64, 'image_size_px': [200, 100],
        'reviewer_ref': 'local-test-alias',
        'reviewer_authentication': 'NOT_AUTHENTICATED_BY_LOCAL_TOOL',
        'reviewed_at': '2026-11-17T03:00:00Z',
        'ports': [], 'edges': [], 'evidence': [], 'not_for_sft': True,
        'review_status': 'REVIEW_REQUIRED', 'training_authorized': False, 'gold_authorized': False,
    }
    def evidence(subject, field, basis='EXPLICIT_TEXT'):
        eid = 'EV'+str(len(receipt['evidence'])+1)
        receipt['evidence'].append({'evidence_id': eid, 'subject_id': subject,
                                   'field': field, 'basis': basis,
                                   'bbox_px': [10, 10, 20, 10]})
        return eid
    for pid, nid, direction in [('P1', 'N1', 'OUTPUT'), ('P2', 'N2', 'INPUT')]:
        receipt['ports'].append({
            'port_id': pid, 'node_id': nid, 'label': 'SYNTHETIC_TEST_ONLY '+pid,
            'direction': direction, 'signal_or_medium': 'UNKNOWN', 'unit': None,
            'evidence': {'label': evidence(pid, 'PORT_LABEL', 'VISIBLE_LABEL'),
                         'direction': evidence(pid, 'PORT_DIRECTION'),
                         'signal_or_medium': None, 'unit': None}})
    receipt['edges'] = [{
        'edge_id': 'E1', 'from_port': 'P1', 'to_port': 'P2', 'relation': 'CONTROL',
        'direction_basis': 'ARROW_IN_DIAGRAM',
        'evidence': {'connection': evidence('E1', 'CONNECTION', 'VISIBLE_CONNECTOR'),
                     'direction': evidence('E1', 'EDGE_DIRECTION', 'ARROW_IN_DIAGRAM'),
                     'relation': evidence('E1', 'RELATION')}}]
    return graph, receipt


class TopologyReviewTests(unittest.TestCase):
    def test_feature_is_available(self):
        self.assertIsNotNone(importlib.util.find_spec('dgsi.diagram_topology_review'))

    def setUp(self):
        self.graph, self.receipt = fixture()

    def audit(self):
        from dgsi.diagram_topology_review import validate_topology_review
        return validate_topology_review(self.graph, self.receipt)

    def convert(self):
        from dgsi.diagram_topology_review import import_topology_review
        return import_topology_review(self.graph, self.receipt)

    def reject(self, code):
        from dgsi.diagram_topology_review import TopologyReviewError
        with self.assertRaisesRegex(TopologyReviewError, '^'+code+'$'):
            self.audit()

    def test_valid_audit_is_aggregate_only(self):
        result = self.audit()
        self.assertEqual(result['port_count'], 2)
        self.assertEqual(result['directed_edge_count'], 1)
        self.assertEqual(result['decision'], 'TOPOLOGY_RECEIPT_BOUND_NOT_AUTHENTICATED')
        for text in ('SYNTHETIC_TEST_ONLY', 'local-test-alias', 'TEST-IMAGE'):
            self.assertNotIn(text, json.dumps(result))
        self.assertFalse(result['training_authorized'])

    def test_import_preserves_inputs_and_only_proposes(self):
        before = copy.deepcopy((self.graph, self.receipt))
        result = self.convert()
        graph = result['diagram_annotation']
        self.assertEqual(graph['nodes'], self.graph['nodes'])
        self.assertEqual(len(graph['ports']), 2)
        self.assertEqual(graph['edges'][0]['relation'], 'CONTROL')
        for item in graph['ports'] + graph['edges']:
            self.assertEqual(item['review_status'], 'AI_PROPOSED')
        self.assertEqual(before, (self.graph, self.receipt))
        self.assertEqual(result['conversion_receipt']['review_sha256'], digest(self.receipt))
        self.assertFalse(result['training_authorized'])

    def test_changed_node_graph_rejected(self):
        self.graph['nodes'][0]['label'] = 'changed'
        self.reject('TOPOLOGY_GRAPH_HASH_MISMATCH')

    def test_source_and_asset_binding(self):
        for field, value in [('source_sha256', 'f'*64), ('asset_id', 'OTHER'), ('asset_sha256', 'f'*64)]:
            with self.subTest(field=field):
                self.graph, self.receipt = fixture()
                self.receipt[field] = value
                self.reject('TOPOLOGY_SOURCE_ASSET_MISMATCH')

    def test_existing_topology_not_silently_merged(self):
        result = self.convert()['diagram_annotation']
        self.graph = result
        self.receipt['graph_sha256'] = digest(result)
        self.reject('TOPOLOGY_BASE_MUST_BE_NODE_ONLY')

    def test_false_confirmed_node_rejected(self):
        self.graph['nodes'][0]['review_status'] = 'HUMAN_CONFIRMED'
        self.receipt['graph_sha256'] = digest(self.graph)
        self.reject('TOPOLOGY_BASE_REVIEW_STATE_INVALID')

    def test_unknown_node_rejected(self):
        self.receipt['ports'][0]['node_id'] = 'OTHER'
        self.reject('TOPOLOGY_NODE_REFERENCE_UNKNOWN')

    def test_duplicate_ports_edges_evidence_rejected(self):
        for key in ('ports', 'edges', 'evidence'):
            with self.subTest(key=key):
                self.graph, self.receipt = fixture()
                self.receipt[key].append(copy.deepcopy(self.receipt[key][0]))
                self.reject('TOPOLOGY_DUPLICATE_ID')

    def test_unknown_port_rejected(self):
        self.receipt['edges'][0]['to_port'] = 'OTHER'
        self.reject('TOPOLOGY_PORT_REFERENCE_UNKNOWN')

    def test_self_loop_rejected(self):
        self.receipt['edges'][0]['to_port'] = 'P1'
        self.reject('TOPOLOGY_SELF_LOOP_UNREVIEWED')

    def test_direction_conflict_rejected(self):
        self.receipt['ports'][1]['direction'] = 'OUTPUT'
        self.reject('TOPOLOGY_PORT_DIRECTION_CONFLICT')

    def test_connection_cannot_stand_in_for_relation_evidence(self):
        self.receipt['edges'][0]['evidence']['relation'] = self.receipt['edges'][0]['evidence']['connection']
        self.reject('TOPOLOGY_EVIDENCE_BINDING_INVALID')

    def test_port_direction_cannot_borrow_other_port_evidence(self):
        self.receipt['ports'][0]['evidence']['direction'] = self.receipt['ports'][1]['evidence']['direction']
        self.reject('TOPOLOGY_EVIDENCE_BINDING_INVALID')

    def test_known_semantics_require_own_evidence(self):
        cases = [('ports', 'direction'), ('edges', 'relation'), ('edges', 'direction'), ('edges', 'connection')]
        for collection, field in cases:
            with self.subTest(collection=collection, field=field):
                self.graph, self.receipt = fixture()
                self.receipt[collection][0]['evidence'][field] = None
                self.reject('TOPOLOGY_REQUIRED_EVIDENCE_MISSING')

    def test_signal_and_unit_cannot_be_invented(self):
        for field, value in [('signal_or_medium', 'power'), ('unit', 'V')]:
            with self.subTest(field=field):
                self.graph, self.receipt = fixture()
                self.receipt['ports'][0][field] = value
                self.reject('TOPOLOGY_REQUIRED_EVIDENCE_MISSING')

    def test_direction_basis_must_match_evidence(self):
        self.receipt['edges'][0]['direction_basis'] = 'EXPLICIT_TEXT'
        self.reject('TOPOLOGY_DIRECTION_BASIS_MISMATCH')

    def test_spatial_proximity_not_accepted_as_evidence(self):
        self.receipt['evidence'][4]['basis'] = 'SPATIAL_PROXIMITY'
        self.reject('TOPOLOGY_RECEIPT_INVALID')

    def test_image_and_region_bounds(self):
        for box in ([190, 10, 20, 10], [0, 95, 1, 10], [0, 0, 0, 10], [True, 0, 10, 10]):
            with self.subTest(box=box):
                self.graph, self.receipt = fixture()
                self.receipt['evidence'][0]['bbox_px'] = box
                self.reject('TOPOLOGY_EVIDENCE_BOUNDS_INVALID')

    def test_unknown_direction_retained_without_directed_graph_edge(self):
        edge = self.receipt['edges'][0]
        edge['direction_basis'] = 'UNKNOWN'
        direction_ref = edge['evidence']['direction']
        edge['evidence']['direction'] = None
        self.receipt['evidence'] = [e for e in self.receipt['evidence'] if e['evidence_id'] != direction_ref]
        result = self.convert()
        self.assertEqual(result['diagram_annotation']['edges'], [])
        self.assertEqual(len(result['unresolved_connections']), 1)
        self.assertEqual(self.audit()['unresolved_connection_count'], 1)

    def test_unknown_relation_stays_unknown(self):
        edge = self.receipt['edges'][0]
        edge['relation'] = 'UNKNOWN'
        ref = edge['evidence']['relation']
        edge['evidence']['relation'] = None
        self.receipt['evidence'] = [e for e in self.receipt['evidence'] if e['evidence_id'] != ref]
        self.assertEqual(self.convert()['diagram_annotation']['edges'][0]['review_status'], 'UNRESOLVED')

    def test_unused_evidence_is_rejected(self):
        item = copy.deepcopy(self.receipt['evidence'][0]); item['evidence_id'] = 'UNUSED'
        self.receipt['evidence'].append(item)
        self.reject('TOPOLOGY_UNUSED_EVIDENCE')

    def test_explicit_timestamp_profile_independent_of_optional_plugins(self):
        for value in ('2026-11-17T03:00:00', '2026-11-17T03:00:00-00:00',
                      '2026-02-30T03:00:00Z', 'not a date'):
            with self.subTest(value=value):
                self.receipt['reviewed_at'] = value
                self.reject('TOPOLOGY_REVIEW_TIME_INVALID')
        self.receipt['reviewed_at'] = '2026-11-17T12:00:00+09:00'
        self.assertEqual(self.audit()['port_count'], 2)

    def test_training_and_authentication_cannot_be_promoted(self):
        for field, value in [('training_authorized', True), ('gold_authorized', True),
                             ('not_for_sft', False), ('reviewer_authentication', 'AUTHENTICATED')]:
            with self.subTest(field=field):
                self.graph, self.receipt = fixture(); self.receipt[field] = value
                self.reject('TOPOLOGY_RECEIPT_INVALID')

    def test_reordered_receipt_keeps_graph_deterministic(self):
        before = self.convert()['diagram_annotation']
        self.receipt['ports'].reverse(); self.receipt['evidence'].reverse()
        self.assertEqual(before, self.convert()['diagram_annotation'])

    def test_nonfinite_input_is_rejected(self):
        self.receipt['image_size_px'][0] = float('nan')
        self.reject('TOPOLOGY_JSON_INVALID')

    def test_empty_topology_does_not_invent_objects(self):
        self.receipt['ports'] = []; self.receipt['edges'] = []; self.receipt['evidence'] = []
        result = self.convert()
        self.assertEqual(result['diagram_annotation'], self.graph)


    def test_locator_ids_reject_trailing_newline(self):
        self.receipt['review_id'] = 'R1\n'
        self.reject('TOPOLOGY_RECEIPT_INVALID')

    def test_unknown_field_cannot_smuggle_evidence(self):
        self.receipt['ports'][0]['signal_or_medium'] = 'UNKNOWN'
        self.receipt['ports'][0]['evidence']['signal_or_medium'] = 'EV1'
        self.reject('TOPOLOGY_UNKNOWN_FIELD_HAS_EVIDENCE')

    def test_explicit_medium_and_unit_evidence_is_preserved(self):
        for field, role, value in [('signal_or_medium', 'PORT_MEDIUM', 'electrical'), ('unit', 'PORT_UNIT', 'V')]:
            eid = 'EXPLICIT-'+role
            self.receipt['ports'][0][field] = value
            self.receipt['ports'][0]['evidence'][field] = eid
            self.receipt['evidence'].append({'evidence_id': eid, 'subject_id': 'P1',
                                             'field': role, 'basis': 'EXPLICIT_TEXT',
                                             'bbox_px': [180, 90, 20, 10]})
        result = self.convert()
        self.assertEqual(result['diagram_annotation']['ports'][0]['unit'], 'V')
        self.assertEqual(result['evidence_receipt'], self.receipt)

    def test_schema_rejects_extra_hidden_claim(self):
        self.receipt['confirmed_root_cause'] = 'SYNTHETIC_TEST_ONLY'
        self.reject('TOPOLOGY_RECEIPT_INVALID')

    def test_schema_itself_is_valid(self):
        from jsonschema import Draft202012Validator
        path = ROOT / 'skills/dgsi-simulation-to-sft/schemas/diagram_topology_review.schema.json'
        Draft202012Validator.check_schema(json.loads(path.read_text(encoding='utf-8')))


class TopologyCliTests(unittest.TestCase):
    SCRIPT = ROOT / 'scripts/audit_diagram_topology_review.py'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.graph, self.receipt = fixture()
        self.graph_path = self.dir / 'graph.json'
        self.receipt_path = self.dir / 'receipt.json'
        self.graph_path.write_text(json.dumps(self.graph), encoding='utf-8')
        self.receipt_path.write_text(json.dumps(self.receipt), encoding='utf-8')

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(self.SCRIPT),
                               '--node-graph', str(self.graph_path),
                               '--review-receipt', str(self.receipt_path), *args],
                              cwd=self.dir, text=True, capture_output=True, check=False)

    def test_cli_is_available(self):
        self.assertTrue(self.SCRIPT.is_file())

    def test_audit_does_not_write_or_echo_payload(self):
        before = sorted(p.name for p in self.dir.iterdir())
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['output_written'])
        self.assertEqual(before, sorted(p.name for p in self.dir.iterdir()))
        self.assertEqual(result.stderr, '')
        for value in ('local-test-alias', 'SYNTHETIC_TEST_ONLY', str(self.dir)):
            self.assertNotIn(value, result.stdout)

    def test_explicit_output_creates_proposed_graph(self):
        output = self.dir / 'proposed.json'
        result = self.run_cli('--output', str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads(output.read_text(encoding='utf-8'))
        self.assertEqual(record['diagram_annotation']['edges'][0]['review_status'], 'AI_PROPOSED')
        self.assertFalse(record['training_authorized'])
        self.assertTrue(json.loads(result.stdout)['output_written'])

    def test_existing_output_remains_unchanged(self):
        output = self.dir / 'keep.json'; output.write_bytes(b'KEEP')
        result = self.run_cli('--output', str(output))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_OUTPUT_EXISTS')
        self.assertEqual(output.read_bytes(), b'KEEP')

    def test_bad_parent_is_payload_free(self):
        output = self.dir / 'missing-parent' / 'result.json'
        result = self.run_cli('--output', str(output))
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_OUTPUT_IO_ERROR')
        self.assertEqual(result.stderr, '')
        self.assertNotIn(str(self.dir), result.stdout)

    def test_invalid_unicode_is_payload_free(self):
        self.receipt_path.write_bytes(b'\xff\xfe')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_INPUT_INVALID')
        self.assertEqual(result.stderr, '')

    def test_duplicate_json_keys_are_rejected(self):
        self.receipt_path.write_text('{"training_authorized":true,"training_authorized":false}')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_INPUT_INVALID')

    def test_nonstandard_json_number_rejected(self):
        self.receipt_path.write_text('{"image_size_px":[NaN,100]}')
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_INPUT_INVALID')

    def test_invalid_receipt_creates_no_output(self):
        self.receipt['graph_sha256'] = 'e'*64
        self.receipt_path.write_text(json.dumps(self.receipt))
        output = self.dir / 'new.json'
        result = self.run_cli('--output', str(output))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())
        self.assertEqual(result.stderr, '')

    def test_input_size_limit(self):
        self.receipt_path.write_bytes(b' '*(2*1024*1024+1))
        result = self.run_cli()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)['error_code'], 'TOPOLOGY_INPUT_INVALID')

    def test_cli_help_is_available(self):
        result = subprocess.run([sys.executable, str(self.SCRIPT), '--help'],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('--review-receipt', result.stdout)


if __name__ == '__main__':
    unittest.main()
