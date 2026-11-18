#!/usr/bin/env python3
"""Create a local, review-required OCR text-region proposal file.

The output contains untrusted OCR text. Choose an explicitly authorized local
annotation workspace. The command prints aggregate metadata only.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.diagram_text_regions import (
    DiagramTextRegionError,
    propose_diagram_text_regions,
)


def _read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DiagramTextRegionError("DIAGRAM_INPUT_JSON_INVALID") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document-manifest", required=True, type=Path)
    parser.add_argument("--ocr-record", required=True, type=Path)
    parser.add_argument("--asset", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        result = propose_diagram_text_regions(
            _read_json(args.document_manifest),
            _read_json(args.ocr_record),
            args.asset,
        )
        output = args.output
        if output.exists() or output.is_symlink():
            raise DiagramTextRegionError("DIAGRAM_OUTPUT_ALREADY_EXISTS")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with output.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        except FileExistsError:
            raise DiagramTextRegionError("DIAGRAM_OUTPUT_ALREADY_EXISTS") from None
        except OSError:
            raise DiagramTextRegionError("DIAGRAM_OUTPUT_IO_ERROR") from None
    except DiagramTextRegionError as error:
        print(json.dumps({
            "decision": "BLOCKED",
            "error_code": str(error),
            "training_authorized": False,
            "gold_authorized": False,
        }))
        return 2

    print(json.dumps({
        "decision": "REVIEW_REQUIRED",
        "candidate_count": len(result["candidates"]),
        "asset_sha256": result["asset_sha256"],
        "output_written": True,
        "not_for_sft": True,
        "training_authorized": False,
        "gold_authorized": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
