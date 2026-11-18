#!/usr/bin/env python3
"""Audit a privately edited C2 rights worksheet against its BLANK reference."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_c2_rights_intake_audit import (
    C2SourceRightsIntakeError,
    audit_c2_source_rights_intake,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blank", type=Path, required=True,
                        help="Original fingerprint-bound coordinator rights queue")
    parser.add_argument("--submission", type=Path, required=True,
                        help="Edited private worksheet from the same C2 collection")
    args = parser.parse_args(argv)
    try:
        blank = json.loads(args.blank.read_text(encoding="utf-8"))
        submitted = json.loads(args.submission.read_text(encoding="utf-8"))
        result = audit_c2_source_rights_intake(blank, submitted)
    except C2SourceRightsIntakeError as exc:
        print(json.dumps({
            "decision": "REJECTED", "error_code": str(exc),
            "source_rights_verified": False, "training_authorized": False,
            "sft_records_emitted": 0,
        }))
        return 2
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(json.dumps({
            "decision": "REJECTED", "error_code": "C2_RIGHTS_INTAKE_READ_OR_SHAPE_INVALID",
            "source_rights_verified": False, "training_authorized": False,
            "sft_records_emitted": 0,
        }))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
