#!/usr/bin/env python3
"""Offline declaration-only duplicate-source audit; no source file access."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from dgsi.handoff_digest_reuse import (
    HandoffDigestReuseError, audit_handoff_digest_reuse,
)
from dgsi.real_case_handoff import RealCaseHandoffError, load_handoff_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit declared diagnosis/log digests; no bytes read or splits assigned."
    )
    parser.add_argument("manifests", nargs="+", type=Path)
    parser.add_argument(
        "--existing-split", action="append", choices=("train", "validation", "test"),
        help="Repeat once per manifest, in positional order, only for already assigned splits.",
    )
    args = parser.parse_args(argv)
    if args.existing_split and len(args.existing_split) != len(args.manifests):
        print(json.dumps({"status": "REJECTED", "error_code": "EXISTING_SPLIT_COUNT_MISMATCH"}))
        return 2
    try:
        manifests = [
            load_handoff_manifest(path.read_text(encoding="utf-8"))
            for path in args.manifests
        ]
        entries = [
            {"manifest": m, "split": args.existing_split[i] if args.existing_split else None}
            for i, m in enumerate(manifests)
        ]
        report = audit_handoff_digest_reuse(entries)
    except (HandoffDigestReuseError, RealCaseHandoffError) as exc:
        # Contract errors are fixed codes; never include manifest values.
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}))
        return 2
    except (OSError, UnicodeError):
        print(json.dumps({"status": "REJECTED", "error_code": "DIGEST_MANIFEST_READ_ERROR"}))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 2 if report["decision"] in {
        "BLOCKED_SOURCE_REUSE", "MANUAL_EVENT_FAMILY_REVIEW"
    } else 0


if __name__ == "__main__":
    sys.exit(main())
