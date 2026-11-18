#!/usr/bin/env python3
"""Validate one DGSI blinded cross-AI evaluation record; aggregate-only output."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.cross_ai_evaluation import CrossAIEvaluationError, validate_cross_ai_evaluation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True)
    args = parser.parse_args()
    try:
        path = Path(args.record)
        if path.is_symlink() or not path.is_file() or path.stat().st_size > 1024 * 1024:
            raise CrossAIEvaluationError("CROSS_AI_RECORD_UNAVAILABLE")
        record = json.loads(path.read_text(encoding="utf-8"))
        report = validate_cross_ai_evaluation(record)
    except CrossAIEvaluationError as exc:
        print(json.dumps({"decision": "BLOCKED", "error_code": str(exc), "training_authorized": False}))
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError):
        print(json.dumps({"decision": "BLOCKED", "error_code": "CROSS_AI_RECORD_INVALID", "training_authorized": False}))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
