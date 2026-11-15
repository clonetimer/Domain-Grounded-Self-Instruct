"""Read-only local review of source-documented disposal; aggregate codes only.

Usage:
  PYTHONPATH=src python scripts/audit_disposal_source_review.py \
      --case /authorized/diagnostic_case.json \
      --review /authorized/private_disposal_review.json

Never upload the source Case, attestation packet, original logs, or expert
excerpts to this public repository. The JSON output is not Gold approval.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dgsi.disposal_source_review import (
    DisposalSourceReviewError,
    audit_disposal_source_review,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Local disposal review, aggregate-only")
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    try:
        case = json.loads(args.case.read_text(encoding="utf-8"))
        review = json.loads(args.review.read_text(encoding="utf-8"))
        summary = audit_disposal_source_review(case, review)
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"status": "BLOCKED", "error_code": "LOCAL_INPUT_READ_FAILED"}))
        return 2
    except DisposalSourceReviewError as exc:
        # Fixed validator codes only; never print paths, source content or IDs.
        print(json.dumps({"status": "BLOCKED", "error_code": str(exc)}))
        return 1
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
