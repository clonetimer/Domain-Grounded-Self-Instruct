#!/usr/bin/env python3
"""Read-only local aggregate audit; no source file scans and no uploads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from dgsi.real_review_queue_preflight import (
    ReviewQueuePreflightError, audit_review_queue, load_review_queue,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Metadata-only DGSI REAL review queue audit")
    parser.add_argument("queue", type=Path, help="One explicit local v0.5 evidence-request queue")
    args = parser.parse_args(argv)
    try:
        report = audit_review_queue(load_review_queue(args.queue.read_text(encoding="utf-8")))
    except ReviewQueuePreflightError as exc:
        print(json.dumps({"status": "BLOCKED", "error_code": str(exc)}))
        return 2
    except (OSError, UnicodeError):
        print(json.dumps({"status": "BLOCKED", "error_code": "QUEUE_READ_ERROR"}))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
