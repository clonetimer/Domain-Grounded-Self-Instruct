#!/usr/bin/env python3
"""Offline pseudonymous run-lineage audit; no source/target file reads."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from dgsi.handoff_run_lineage import RunLineageAuditError, audit_handoff_run_lineage
from dgsi.real_case_handoff import RealCaseHandoffError, load_handoff_manifest


def _load_lineage(text: str) -> dict:
    """Reject duplicate keys and nonfinite numbers in minimal Case provenance."""
    def unique_pairs(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise RunLineageAuditError("DUPLICATE_LINEAGE_JSON_KEY")
            obj[key] = value
        return obj

    def reject_constant(_):
        raise RunLineageAuditError("NONFINITE_LINEAGE_JSON_NUMBER")

    try:
        value = json.loads(text, object_pairs_hook=unique_pairs,
                           parse_constant=reject_constant)
    except (ValueError, TypeError) as exc:
        if isinstance(exc, RunLineageAuditError):
            raise
        raise RunLineageAuditError("INVALID_LINEAGE_JSON") from None
    if not isinstance(value, dict):
        raise RunLineageAuditError("INVALID_RUN_LINEAGE_SHAPE")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Audit declared ML diagnosis-run reuse; no case/target files accessed."
    )
    parser.add_argument(
        "--pair", nargs=2, metavar=("MANIFEST", "LINEAGE"),
        type=Path, action="append", required=True,
        help="Explicit manifest and minimal pseudonymous Case-provenance JSON pair.",
    )
    parser.add_argument(
        "--existing-split", action="append", choices=("train", "validation", "test"),
        help="Repeat once per --pair, ONLY for pre-existing manual split labels.",
    )
    args = parser.parse_args(argv)
    if args.existing_split and len(args.existing_split) != len(args.pair):
        print(json.dumps({"status": "REJECTED", "error_code": "EXISTING_SPLIT_COUNT_MISMATCH"}))
        return 2

    try:
        entries = []
        for i, (manifest_path, lineage_path) in enumerate(args.pair):
            manifest = load_handoff_manifest(manifest_path.read_text(encoding="utf-8"))
            lineage = _load_lineage(lineage_path.read_text(encoding="utf-8"))
            entries.append({
                "manifest": manifest,
                "lineage": lineage,
                "split": args.existing_split[i] if args.existing_split else None,
            })
        report = audit_handoff_run_lineage(entries)
    except (RunLineageAuditError, RealCaseHandoffError) as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}))
        return 2
    except (OSError, UnicodeError):
        print(json.dumps({"status": "REJECTED", "error_code": "RUN_LINEAGE_FILE_READ_ERROR"}))
        return 2

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 2 if report["decision"] in {
        "BLOCKED_RUN_LINEAGE", "MANUAL_RUN_LINEAGE_REVIEW",
    } else 0


if __name__ == "__main__":
    sys.exit(main())
