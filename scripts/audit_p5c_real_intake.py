#!/usr/bin/env python3
"""Read-only, aggregate-only preflight of the P5-C1 REAL candidate register."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.p5c_real_intake import (  # noqa: E402
    RealCandidateIntakeError,
    audit_real_candidate_intake,
)


def _no_duplicate_json_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("REAL_INTAKE_JSON_DUPLICATE_KEY")
        result[key] = value
    return result


def main() -> int:
    try:
        with (ROOT / "examples" / "p5c_real_case_candidate_intake_2026-11-17.json").open(
            encoding="utf-8"
        ) as handle:
            item = json.load(handle, object_pairs_hook=_no_duplicate_json_keys)
        result = audit_real_candidate_intake(item)
    except RealCandidateIntakeError as exc:
        print(json.dumps({
            "decision": "BLOCKED", "code": str(exc), "training_authorized": False,
        }, sort_keys=True))
        return 2
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({
            "decision": "BLOCKED", "code": "REAL_INTAKE_SOURCE_UNREADABLE",
            "training_authorized": False,
        }, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
