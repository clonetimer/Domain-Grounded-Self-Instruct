#!/usr/bin/env python3
"""Import bound text-region decisions as AI-proposed diagram labels only."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.diagram_review_import import DiagramReviewImportError, import_reviewed_text_as_proposed_graph


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DiagramReviewImportError("DIAGRAM_REVIEW_IMPORT_INPUT_INVALID") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-record", required=True, type=Path)
    parser.add_argument("--review-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = import_reviewed_text_as_proposed_graph(
            read_json(args.candidate_record),
            read_json(args.review_receipt),
        )
        if args.output.exists() or args.output.is_symlink():
            raise DiagramReviewImportError("DIAGRAM_REVIEW_IMPORT_OUTPUT_ALREADY_EXISTS")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(result, stream, ensure_ascii=False, indent=2)
                stream.write("\n")
        except FileExistsError:
            raise DiagramReviewImportError("DIAGRAM_REVIEW_IMPORT_OUTPUT_ALREADY_EXISTS") from None
        except OSError:
            raise DiagramReviewImportError("DIAGRAM_REVIEW_IMPORT_OUTPUT_IO_ERROR") from None
    except DiagramReviewImportError as error:
        print(json.dumps({
            "decision": "BLOCKED",
            "error_code": str(error),
            "training_authorized": False,
            "gold_authorized": False,
        }))
        return 2
    print(json.dumps({
        "decision": "REVIEW_REQUIRED",
        "proposed_node_count": len(result["diagram_annotation"]["nodes"]),
        "ports_created": 0,
        "edges_created": 0,
        "reviewer_authentication": "NOT_AUTHENTICATED_BY_LOCAL_TOOL",
        "training_authorized": False,
        "gold_authorized": False,
        "output_written": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
