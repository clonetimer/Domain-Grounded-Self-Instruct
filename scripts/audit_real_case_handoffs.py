#!/usr/bin/env python3
"""Read explicit local case_manifest.json files and print only aggregate triage.

Does not recurse through source folders, read diagnosis/log/target files,
publish anything, assign splits, or approve Gold/training.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from dgsi.real_case_handoff import (
    RealCaseHandoffError, audit_handoff_cohort, load_handoff_manifest,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Metadata-only real case handoff audit (no source upload).",
    )
    parser.add_argument(
        "manifests", metavar="case_manifest.json", nargs="+", type=Path,
        help="Explicit local manifest paths; no directories or source packet scans.",
    )
    args = parser.parse_args(argv)
    try:
        manifests = [
            load_handoff_manifest(path.read_text(encoding="utf-8"))
            for path in args.manifests
        ]
        result = audit_handoff_cohort(manifests)
    except RealCaseHandoffError as exc:
        # Exception codes never contain untrusted source text or case identities.
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}))
        return 2
    except (OSError, UnicodeError):
        # OS error messages can contain restricted local file paths.
        print(json.dumps({"status": "REJECTED", "error_code": "MANIFEST_READ_ERROR"}))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
