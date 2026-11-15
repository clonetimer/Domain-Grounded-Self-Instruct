#!/usr/bin/env python3
"""Read-only, local Case/history as-of audit. Never prints case content or paths."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.case_history_asof import CaseHistoryAsOfError, audit_case_history_asof  # noqa: E402

_MAX_BYTES = 8 * 1024 * 1024


class LocalInputError(ValueError):
    pass


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise LocalInputError("DUPLICATE_LOCAL_JSON_KEY")
        result[key] = value
    return result


def _nonfinite(_value):
    raise LocalInputError("NONFINITE_LOCAL_JSON_NUMBER")


def _read(path_value):
    path = Path(path_value)
    try:
        if path.is_symlink() or not path.is_file():
            raise LocalInputError("INVALID_LOCAL_FILE")
        if path.stat().st_size > _MAX_BYTES:
            raise LocalInputError("LOCAL_FILE_TOO_LARGE")
        payload = path.read_text(encoding="utf-8")
        return json.loads(payload, object_pairs_hook=_object, parse_constant=_nonfinite)
    except LocalInputError:
        raise
    except (OSError, UnicodeError, ValueError):
        raise LocalInputError("INVALID_OR_UNREADABLE_LOCAL_JSON") from None


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Local aggregate-only historical as-of audit; never exports source files"
    )
    parser.add_argument("--case", required=True, help="Explicit authorized diagnostic Case JSON path")
    parser.add_argument("--history-hits", required=True, help="Explicit local history-hit metadata JSON list")
    parser.add_argument("--equipment-scope", required=True, help="Case-configured component ID")
    args = parser.parse_args(argv)
    try:
        case, hits = _read(args.case), _read(args.history_hits)
        result = audit_case_history_asof(case, hits, equipment_scope=args.equipment_scope)
        success = result["decision"] in {"PASS_ASOF_METADATA_ONLY", "NO_HISTORY_REFERENCES"}
    except (CaseHistoryAsOfError, LocalInputError) as exc:
        result = {
            "schema_version": "dgsi-case-history-asof-binding.v1",
            "decision": "BLOCKED",
            "error_code": str(exc),
            "gold_eligible": False,
            "training_authorized": False,
        }
        success = False
    except Exception:
        # No exception messages or tracebacks: they can include restricted
        # source text, paths or identifiers.
        result = {
            "schema_version": "dgsi-case-history-asof-binding.v1",
            "decision": "BLOCKED",
            "error_code": "LOCAL_HISTORY_AUDIT_FAILED",
            "gold_eligible": False,
            "training_authorized": False,
        }
        success = False
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if success else 2


if __name__ == "__main__":
    sys.exit(main())
