#!/usr/bin/env python3
"""Audit port/link review metadata; --output explicitly writes a proposed graph."""
from __future__ import annotations
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from dgsi.diagram_topology_review import (
    TopologyReviewError, import_topology_review, validate_topology_review,
)

MAX_INPUT_BYTES = 2 * 1024 * 1024


def _invalid(*_):
    raise TopologyReviewError('TOPOLOGY_INPUT_INVALID')


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            _invalid()
        result[key] = value
    return result


def read_input(path: Path):
    try:
        if path.is_symlink() or not path.is_file():
            _invalid()
        with path.open('rb') as stream:
            data = stream.read(MAX_INPUT_BYTES + 1)
        if len(data) > MAX_INPUT_BYTES:
            _invalid()
        return json.loads(data.decode('utf-8'), object_pairs_hook=_unique_object,
                          parse_constant=_invalid)
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise TopologyReviewError('TOPOLOGY_INPUT_INVALID') from None


def write_new(path: Path, value) -> None:
    # Serialize first, then create exclusively; no partially serialized JSON.
    try:
        data = (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n').encode('utf-8')
    except (ValueError, TypeError, UnicodeError):
        raise TopologyReviewError('TOPOLOGY_OUTPUT_INVALID') from None
    created = False
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        created = True
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
    except FileExistsError:
        raise TopologyReviewError('TOPOLOGY_OUTPUT_EXISTS') from None
    except OSError:
        if created:
            try:
                path.unlink()
            except OSError:
                pass
        raise TopologyReviewError('TOPOLOGY_OUTPUT_IO_ERROR') from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--node-graph', required=True, type=Path)
    parser.add_argument('--review-receipt', required=True, type=Path)
    parser.add_argument('--output', type=Path, help='New file in an existing authorized local directory.')
    args = parser.parse_args()
    try:
        graph = read_input(args.node_graph)
        receipt = read_input(args.review_receipt)
        summary = validate_topology_review(graph, receipt)
        if args.output is not None:
            write_new(args.output, import_topology_review(graph, receipt))
        print(json.dumps({**summary, 'output_written': args.output is not None}, sort_keys=True))
        return 0
    except TopologyReviewError as error:
        print(json.dumps({'decision': 'BLOCKED', 'error_code': str(error),
                          'training_authorized': False, 'gold_authorized': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
