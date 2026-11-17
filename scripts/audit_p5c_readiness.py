#!/usr/bin/env python3
"""Read-only, payload-free P5-C0 inventory audit of bundled public fixtures."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dgsi.p5c_readiness import P5CReadinessError, audit_p5c_sft_readiness  # noqa: E402


def main() -> int:
    try:
        names = (
            "p5c_sft_readiness_baseline_2026-11-17.json",
            "l1_literature_synthetic_task_packets_v0.1.json",
            "l0_public_literature_fact_cards_2026-11-15.json",
        )
        docs = [json.loads((ROOT / "examples" / n).read_text(encoding="utf-8")) for n in names]
        result = audit_p5c_sft_readiness(*docs)
    except P5CReadinessError as exc:
        result = {"decision": "BLOCKED", "code": str(exc), "training_authorized": False}
        print(json.dumps(result, ensure_ascii=True, sort_keys=True))
        return 2
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({"decision": "BLOCKED", "code": "P5C_INPUT_UNREADABLE", "training_authorized": False}))
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
