#!/usr/bin/env python3
"""Read-only local history/split audit. Never uploads source case packets.

Input: a local JSON manifest with entries [{"split": "train",
"case_path": "/restricted/local/case.json"}, ...]. Results contain aggregate
counts and fixed blocker codes only; paths, case IDs and content never print.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dgsi.history_split_exposure import (
    HistorySplitExposureError,
    audit_history_split_exposure,
)


class LocalAuditInputError(ValueError):
    pass


def _unique_object(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise LocalAuditInputError("DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj


def _read_json(path: Path):
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f, object_pairs_hook=_unique_object,
                             parse_constant=lambda _x: _invalid_number())
    except (OSError, UnicodeError):
        raise LocalAuditInputError("LOCAL_READ_FAILED") from None
    except json.JSONDecodeError:
        raise LocalAuditInputError("INVALID_JSON") from None


def _invalid_number():
    raise LocalAuditInputError("NONFINITE_JSON_NUMBER")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Local metadata-only historical split audit")
    parser.add_argument("--manifest", required=True, help="Restricted local manifest JSON")
    parser.add_argument("--output", help="Optional restricted local aggregate JSON output")
    args = parser.parse_args(argv)
    try:
        manifest = _read_json(Path(args.manifest))
        if not isinstance(manifest, dict) or set(manifest) != {"entries"}:
            raise LocalAuditInputError("INVALID_MANIFEST")
        rows = manifest["entries"]
        if not isinstance(rows, list):
            raise LocalAuditInputError("INVALID_MANIFEST")
        entries = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != {"split", "case_path"}:
                raise LocalAuditInputError("INVALID_MANIFEST_ENTRY")
            path = row["case_path"]
            if not isinstance(path, str) or not path.strip():
                raise LocalAuditInputError("INVALID_LOCAL_PATH")
            entries.append({"split": row["split"], "case": _read_json(Path(path))})
        report = audit_history_split_exposure(entries)
        text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        if args.output:
            try:
                Path(args.output).write_text(text + "\n", encoding="utf-8")
            except (OSError, UnicodeError):
                raise LocalAuditInputError("LOCAL_WRITE_FAILED") from None
        print(text)
        # Shared history in different splits always requires manual review.
        return 2 if report["decision"] == "MANUAL_HISTORY_REFERENCE_REVIEW" else 0
    except (LocalAuditInputError, HistorySplitExposureError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
