#!/usr/bin/env python3
"""Local-only input SHA-256 verification; prints fixed codes/counts, never paths."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from dgsi.local_handoff_integrity import assess_local_input_sha256
from dgsi.real_case_handoff import RealCaseHandoffError, load_handoff_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit explicit local input files against handoff-declared SHA-256; no uploads.",
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--input-directory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        manifest = load_handoff_manifest(args.manifest.read_text(encoding="utf-8"))
        report = assess_local_input_sha256(manifest, args.input_directory)
    except (OSError, UnicodeError):
        print(json.dumps({"status": "REJECTED", "error_code": "LOCAL_INPUT_AUDIT_READ_ERROR"}))
        return 2
    except RealCaseHandoffError:
        # Do not leak JSON fragments or local file paths in exception text.
        print(json.dumps({"status": "REJECTED", "error_code": "LOCAL_INPUT_AUDIT_INVALID_MANIFEST"}))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0 if report["input_file_sha256_matched"] else 2


if __name__ == "__main__":
    sys.exit(main())
