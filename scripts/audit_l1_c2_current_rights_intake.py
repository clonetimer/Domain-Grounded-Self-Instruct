#!/usr/bin/env python3
"""Review-only rights intake audited against current versioned L0/L1 artifacts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_c2_current_rights_preflight import (
    audit_c2_rights_intake_against_current_sources,
)
from dgsi.l1_c2_rights_intake_audit import C2SourceRightsIntakeError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blank", type=Path, required=True,
                        help="Unedited trusted rights queue from coordinator kit")
    parser.add_argument("--submission", type=Path, required=True,
                        help="Privately edited rights worksheet")
    parser.add_argument("--current-collection", type=Path, required=True,
                        help="Independent current local L1 collection JSON")
    parser.add_argument("--current-l0-facts", type=Path, required=True,
                        help="Independent current local L0 fact cards JSON")
    args = parser.parse_args(argv)

    try:
        blank = json.loads(args.blank.read_text(encoding="utf-8"))
        submission = json.loads(args.submission.read_text(encoding="utf-8"))
        collection = json.loads(args.current_collection.read_text(encoding="utf-8"))
        sources_doc = json.loads(args.current_l0_facts.read_text(encoding="utf-8"))
        sources = sources_doc["cards"] if isinstance(sources_doc, dict) else sources_doc
        report = audit_c2_rights_intake_against_current_sources(
            blank, submission, collection, sources
        )
    except C2SourceRightsIntakeError as exc:
        report = {
            "decision": "REJECTED", "error_code": str(exc),
            "source_rights_verified": False, "training_authorized": False,
            "sft_records_emitted": 0,
        }
        print(json.dumps(report, sort_keys=True))
        return 2
    except (OSError, UnicodeError, ValueError, TypeError, KeyError):
        print(json.dumps({
            "decision": "REJECTED",
            "error_code": "C2_RIGHTS_CURRENT_INTAKE_READ_OR_SHAPE_INVALID",
            "source_rights_verified": False, "training_authorized": False,
            "sft_records_emitted": 0,
        }, sort_keys=True))
        return 2

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
