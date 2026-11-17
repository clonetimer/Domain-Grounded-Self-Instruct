"""Bind manually supplied port/link evidence, never authenticate engineering truth."""
from __future__ import annotations

import copy
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator
from dgsi.diagram_annotation import DiagramAnnotationError, validate_diagram_annotation

SCHEMA = Path(__file__).resolve().parents[2] / 'skills/dgsi-simulation-to-sft/schemas/diagram_topology_review.schema.json'
TIME = re.compile(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})\Z')
TEXT_BASES = {'VISIBLE_LABEL', 'EXPLICIT_TEXT'}
BASES = {
    'PORT_LABEL': TEXT_BASES, 'PORT_DIRECTION': TEXT_BASES | {'ARROW_IN_DIAGRAM'},
    'PORT_MEDIUM': TEXT_BASES, 'PORT_UNIT': TEXT_BASES, 'RELATION': TEXT_BASES,
    'CONNECTION': {'VISIBLE_CONNECTOR', 'EXPLICIT_TEXT'},
    'EDGE_DIRECTION': {'ARROW_IN_DIAGRAM', 'EXPLICIT_TEXT'},
}


class TopologyReviewError(ValueError):
    """Stable code only; never echo caller payloads."""


def canonical_digest(value: Any) -> str:
    try:
        data = json.dumps(value, sort_keys=True, ensure_ascii=False,
                          separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError, UnicodeError, RecursionError):
        raise TopologyReviewError('TOPOLOGY_JSON_INVALID') from None
    return hashlib.sha256(data).hexdigest()


def _unique(items: list[dict], key: str) -> dict:
    result = {item[key]: item for item in items}
    if len(result) != len(items):
        raise TopologyReviewError('TOPOLOGY_DUPLICATE_ID')
    return result


def _check(graph: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    graph_hash = canonical_digest(graph)
    canonical_digest(receipt)
    try:
        schema = json.loads(SCHEMA.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise TopologyReviewError('TOPOLOGY_SCHEMA_UNAVAILABLE') from None
    if not Draft202012Validator(schema).is_valid(receipt):
        raise TopologyReviewError('TOPOLOGY_RECEIPT_INVALID')
    try:
        validate_diagram_annotation(graph)
    except DiagramAnnotationError:
        raise TopologyReviewError('TOPOLOGY_BASE_GRAPH_INVALID') from None
    if graph_hash != receipt['graph_sha256']:
        raise TopologyReviewError('TOPOLOGY_GRAPH_HASH_MISMATCH')
    if any(graph[k] != receipt[k] for k in ('source_sha256', 'asset_id', 'asset_sha256')):
        raise TopologyReviewError('TOPOLOGY_SOURCE_ASSET_MISMATCH')
    if graph['ports'] or graph['edges']:
        raise TopologyReviewError('TOPOLOGY_BASE_MUST_BE_NODE_ONLY')
    if (any(n['review_status'] == 'HUMAN_CONFIRMED' for n in graph['nodes'])
            or any(c['certainty'] == 'OBSERVED_IN_SOURCE' for c in graph['claims'])):
        raise TopologyReviewError('TOPOLOGY_BASE_REVIEW_STATE_INVALID')
    stamp = receipt['reviewed_at']
    try:
        if not TIME.fullmatch(stamp) or stamp.endswith('-00:00'):
            raise ValueError
        if datetime.fromisoformat(stamp.replace('Z', '+00:00')).utcoffset() is None:
            raise ValueError
    except ValueError:
        raise TopologyReviewError('TOPOLOGY_REVIEW_TIME_INVALID') from None
    width, height = receipt['image_size_px']
    if any(type(v) is not int or v <= 0 for v in (width, height)) or width*height > 100_000_000:
        raise TopologyReviewError('TOPOLOGY_EVIDENCE_BOUNDS_INVALID')
    nodes = {n['node_id'] for n in graph['nodes']}
    ports = _unique(receipt['ports'], 'port_id')
    edges = _unique(receipt['edges'], 'edge_id')
    evidence = _unique(receipt['evidence'], 'evidence_id')
    if nodes & set(ports) or nodes & set(edges) or set(ports) & set(edges):
        raise TopologyReviewError('TOPOLOGY_OBJECT_ID_COLLISION')
    for item in evidence.values():
        x, y, w, h = item['bbox_px']
        if (any(type(v) is not int for v in (x, y, w, h)) or min(x, y) < 0
                or min(w, h) <= 0 or x+w > width or y+h > height):
            raise TopologyReviewError('TOPOLOGY_EVIDENCE_BOUNDS_INVALID')
    used: set[str] = set()

    def require(ref: str | None, subject: str, field: str, known: bool = True):
        if not known:
            if ref is not None:
                raise TopologyReviewError('TOPOLOGY_UNKNOWN_FIELD_HAS_EVIDENCE')
            return
        if ref is None:
            raise TopologyReviewError('TOPOLOGY_REQUIRED_EVIDENCE_MISSING')
        item = evidence.get(ref)
        if (item is None or item['subject_id'] != subject or item['field'] != field
                or item['basis'] not in BASES[field]):
            raise TopologyReviewError('TOPOLOGY_EVIDENCE_BINDING_INVALID')
        used.add(ref)

    for pid, port in ports.items():
        if port['node_id'] not in nodes:
            raise TopologyReviewError('TOPOLOGY_NODE_REFERENCE_UNKNOWN')
        ev = port['evidence']
        require(ev['label'], pid, 'PORT_LABEL')
        require(ev['direction'], pid, 'PORT_DIRECTION', port['direction'] != 'UNKNOWN')
        require(ev['signal_or_medium'], pid, 'PORT_MEDIUM', port['signal_or_medium'] != 'UNKNOWN')
        require(ev['unit'], pid, 'PORT_UNIT', port['unit'] is not None)
    for eid, edge in edges.items():
        if edge['from_port'] not in ports or edge['to_port'] not in ports:
            raise TopologyReviewError('TOPOLOGY_PORT_REFERENCE_UNKNOWN')
        if edge['from_port'] == edge['to_port']:
            raise TopologyReviewError('TOPOLOGY_SELF_LOOP_UNREVIEWED')
        ev = edge['evidence']
        require(ev['connection'], eid, 'CONNECTION')
        directed = edge['direction_basis'] != 'UNKNOWN'
        require(ev['direction'], eid, 'EDGE_DIRECTION', directed)
        require(ev['relation'], eid, 'RELATION', edge['relation'] != 'UNKNOWN')
        if directed:
            if evidence[ev['direction']]['basis'] != edge['direction_basis']:
                raise TopologyReviewError('TOPOLOGY_DIRECTION_BASIS_MISMATCH')
            if (ports[edge['from_port']]['direction'] == 'INPUT'
                    or ports[edge['to_port']]['direction'] == 'OUTPUT'):
                raise TopologyReviewError('TOPOLOGY_PORT_DIRECTION_CONFLICT')
    if used != set(evidence):
        raise TopologyReviewError('TOPOLOGY_UNUSED_EVIDENCE')
    return {
        'decision': 'TOPOLOGY_RECEIPT_BOUND_NOT_AUTHENTICATED',
        'port_count': len(ports),
        'directed_edge_count': sum(e['direction_basis'] != 'UNKNOWN' for e in edges.values()),
        'unresolved_connection_count': sum(e['direction_basis'] == 'UNKNOWN' for e in edges.values()),
        'reviewer_authentication': 'NOT_AUTHENTICATED_BY_LOCAL_TOOL',
        'image_geometry': 'DECLARED_NOT_DECODED', 'review_status': 'REVIEW_REQUIRED',
        'not_for_sft': True, 'training_authorized': False, 'gold_authorized': False,
    }


def validate_topology_review(graph: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    """Audit caller-supplied declarations only; no image/identity verification."""
    return _check(graph, receipt)


def import_topology_review(graph: dict[str, Any], receipt: dict[str, Any]) -> dict[str, Any]:
    """Create a new graph. Unknown-direction links stay outside directed edges."""
    summary = _check(graph, receipt)
    result = copy.deepcopy(graph)
    evidence = {e['evidence_id']: e for e in receipt['evidence']}

    def locator(ref):
        coords = ','.join(map(str, evidence[ref]['bbox_px']))
        return (f"asset:{receipt['asset_id']}@sha256:{receipt['asset_sha256']}"
                f"#region-px:{coords}#review:{receipt['review_id']}")

    for port in sorted(receipt['ports'], key=lambda p: p['port_id']):
        item = {k: port[k] for k in ('port_id', 'node_id', 'label', 'direction', 'signal_or_medium', 'unit')}
        item.update(evidence_locator=locator(port['evidence']['label']),
                    review_status='UNRESOLVED' if port['direction'] == 'UNKNOWN' else 'AI_PROPOSED')
        result['ports'].append(item)
    unresolved = []
    for edge in sorted(receipt['edges'], key=lambda e: e['edge_id']):
        if edge['direction_basis'] == 'UNKNOWN':
            unresolved.append(copy.deepcopy(edge))
            continue
        item = {k: edge[k] for k in ('edge_id', 'from_port', 'to_port', 'relation', 'direction_basis')}
        item.update(evidence_locator=locator(edge['evidence']['connection']),
                    review_status='UNRESOLVED' if edge['relation'] == 'UNKNOWN' else 'AI_PROPOSED')
        result['edges'].append(item)
    try:
        validate_diagram_annotation(result)
    except DiagramAnnotationError:
        raise TopologyReviewError('TOPOLOGY_IMPORTED_GRAPH_INVALID') from None
    # Keep the complete receipt separately so directional and relation evidence
    # are not lost behind the generic graph's single evidence_locator field.
    return {
        'schema_version': 'dgsi.diagram-topology-import.v1', 'diagram_annotation': result,
        'unresolved_connections': unresolved, 'evidence_receipt': copy.deepcopy(receipt),
        'conversion_receipt': {**summary, 'graph_sha256': receipt['graph_sha256'],
                               'review_sha256': canonical_digest(receipt),
                               'output_graph_sha256': canonical_digest(result)},
        'not_for_sft': True, 'training_authorized': False, 'gold_authorized': False,
    }
