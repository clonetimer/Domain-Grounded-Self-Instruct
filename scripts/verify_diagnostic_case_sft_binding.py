#!/usr/bin/env python3
"""Read-only local case/SFT binding preflight; never emits input content.

Usage: PYTHONPATH=src python scripts/verify_diagnostic_case_sft_binding.py \\
    --case <local-case.json> --sft <local-sft.json>
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from dgsi.case_sft_binding import CaseSftBindingError, verify_case_sft_binding


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--sft", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        case = json.loads(args.case.read_text(encoding="utf-8-sig"))
        example = json.loads(args.sft.read_text(encoding="utf-8-sig"))
        report = verify_case_sft_binding(case, example)
    except CaseSftBindingError as exc:
        print(json.dumps({"decision": "REJECTED", "error_code": str(exc), "gold_eligible": False}))
        return 2
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"decision": "REJECTED", "error_code": "INVALID_OR_UNREADABLE_INPUT", "gold_eligible": False}))
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
