#!/usr/bin/env python3
"""Fail-closed, current-source-bound ten-dimension review receipt preflight."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_blind_review_manifest import L1BlindReviewManifestError
from dgsi.l1_c2_current_scored_review_preflight import (
    audit_c2_scored_review_against_current_sources,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path,
                        help="Original unedited coordinator manifest")
    parser.add_argument("--submissions", required=True, type=Path,
                        help="Private JSON array of all task scorecard submissions")
    parser.add_argument("--current-collection", required=True, type=Path,
                        help="Independent version-controlled current L1 collection")
    parser.add_argument("--current-l0-facts", required=True, type=Path,
                        help="Independent version-controlled current L0 facts")
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        submissions = json.loads(args.submissions.read_text(encoding="utf-8"))
        collection = json.loads(args.current_collection.read_text(encoding="utf-8"))
        source_doc = json.loads(args.current_l0_facts.read_text(encoding="utf-8"))
        sources = source_doc["cards"] if isinstance(source_doc, dict) else source_doc
        report = audit_c2_scored_review_against_current_sources(
            manifest, submissions, collection, sources
        )
    except L1BlindReviewManifestError as exc:
        print(json.dumps({
            "decision": "REJECTED",
            "error_code": str(exc),
            "expert_review_complete": False,
            "training_authorized": False,
            "sft_records_emitted": 0,
        }, sort_keys=True))
        return 2
    except (OSError, UnicodeError, TypeError, KeyError, ValueError):
        print(json.dumps({
            "decision": "REJECTED",
            "error_code": "C2_SCORED_CURRENT_INTAKE_READ_OR_SHAPE_INVALID",
            "expert_review_complete": False,
            "training_authorized": False,
            "sft_records_emitted": 0,
        }, sort_keys=True))
        return 2

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
