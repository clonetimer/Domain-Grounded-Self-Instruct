#!/usr/bin/env python3
"""Audit exact document/asset/OCR provenance without printing source payloads."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.diagram_provenance import DiagramProvenanceError, validate_diagram_asset_provenance


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DiagramProvenanceError("DIAGRAM_INPUT_JSON_INVALID") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-manifest", required=True, type=Path)
    parser.add_argument("--ocr-record", required=True, type=Path)
    parser.add_argument("--asset", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_diagram_asset_provenance(
            _read_json(args.document_manifest),
            _read_json(args.ocr_record),
            args.asset,
        )
    except DiagramProvenanceError as error:
        print(json.dumps({
            "decision": "BLOCKED",
            "error_code": str(error),
            "training_authorized": False,
            "gold_authorized": False,
        }))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
