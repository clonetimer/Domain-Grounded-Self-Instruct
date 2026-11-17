#!/usr/bin/env python3
"""Audit explicitly authorized local REAL evidence-submission metadata only.

Never print local input paths, private case identifiers or evidence references.
No referenced evidence file is opened, and nothing is uploaded or written.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

from dgsi.real_review_queue_preflight import (
    ReviewQueuePreflightError, load_review_queue,
)
from dgsi.real_evidence_submission_preflight import (
    RealEvidenceSubmissionError, audit_evidence_submissions,
)


def main() -> int:
    if len(sys.argv) != 3:
        print("USAGE: audit_real_evidence_submissions.py LOCAL_QUEUE_JSON LOCAL_SUBMISSION_JSON")
        return 2
    try:
        queue = load_review_queue(Path(sys.argv[1]).read_text(encoding="utf-8"))
        manifest = load_review_queue(Path(sys.argv[2]).read_text(encoding="utf-8"))
        result = audit_evidence_submissions(queue, manifest)
    except (OSError, UnicodeError):
        print("LOCAL_EVIDENCE_INPUT_READ_FAILED", file=sys.stderr)
        return 2
    except (ReviewQueuePreflightError, RealEvidenceSubmissionError) as exc:
        # Both exception types guarantee stable, payload-free error codes.
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
