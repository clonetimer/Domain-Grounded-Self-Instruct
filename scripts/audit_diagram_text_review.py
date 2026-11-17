#!/usr/bin/env python3
"""Audit a local text-region review receipt against its exact candidate record."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.diagram_text_review import DiagramTextReviewError, validate_diagram_text_review


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise DiagramTextReviewError("DIAGRAM_REVIEW_INPUT_JSON_INVALID") from None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-record", required=True, type=Path)
    parser.add_argument("--review-receipt", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = validate_diagram_text_review(
            read_json(args.candidate_record),
            read_json(args.review_receipt),
        )
    except DiagramTextReviewError as error:
        print(json.dumps({
            "decision": "BLOCKED",
            "error_code": str(error),
            "training_authorized": False,
            "gold_authorized": False,
        }))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
