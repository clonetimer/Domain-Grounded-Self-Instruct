#!/usr/bin/env python3
"""Read-only, aggregate-only audit of SADA first-case claim/evidence metadata."""
from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.p5c_sada_claim_map import (  # noqa: E402
    SadaClaimMapError,
    audit_sada_claim_map,
)


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("SADA_MAP_DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def main() -> int:
    try:
        item = json.loads(
            (ROOT / "examples" / "p5c_sada_claim_evidence_map_2026-11-17.json").read_text(
                encoding="utf-8"
            ),
            object_pairs_hook=_unique_keys,
        )
        result = audit_sada_claim_map(item)
    except SadaClaimMapError as exc:
        print(json.dumps({"decision": "BLOCKED", "code": str(exc), "training_authorized": False},
                         sort_keys=True))
        return 2
    except (OSError, TypeError, ValueError, KeyError):
        print(json.dumps({"decision": "BLOCKED", "code": "SADA_MAP_SOURCE_UNREADABLE",
                          "training_authorized": False}, sort_keys=True))
        return 2

    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
