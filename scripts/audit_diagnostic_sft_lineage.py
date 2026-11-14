#!/usr/bin/env python3
"""Offline, read-only SFT structural lineage and leakage audit.

No source document, prompt, diagnostic report, case ID, hash or file path is
printed. This tool does not publish artifacts or confer Gold approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from dgsi.diagnostic_context import DiagnosticContextValidationError
from dgsi.sft_lineage import SftLineageAuditError, audit_sft_lineage


def _read_examples(path: Path) -> list[dict[str, Any]]:
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8-sig") as stream:
            return [json.loads(line) for line in stream if line.strip()]
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(payload, dict):
        return [payload]
    if not isinstance(payload, list):
        raise ValueError("INVALID_INPUT_TYPE")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="local JSON/JSONL SFT examples")
    args = parser.parse_args(argv)
    try:
        examples = _read_examples(args.input)
        report = audit_sft_lineage(examples)
    except SftLineageAuditError as exc:
        print(json.dumps({"decision": "REJECTED", "error_code": str(exc), "gold_eligible": False}))
        return 2
    except (DiagnosticContextValidationError, OSError, ValueError, TypeError):
        # Do not echo parse failures or paths; errors can contain restricted text.
        print(json.dumps({"decision": "REJECTED", "error_code": "INVALID_OR_UNREADABLE_INPUT", "gold_eligible": False}))
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
