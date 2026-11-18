#!/usr/bin/env python3
"""Privacy-safe combined C2 scientific + rights current-source audit; no SFT."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_c2_joint_review_preflight import (
    C2JointReviewError, audit_c2_joint_review_against_current_sources,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rights-blank", type=Path, required=True)
    parser.add_argument("--rights-submission", type=Path, required=True)
    parser.add_argument("--science-manifest", type=Path, required=True)
    parser.add_argument("--science-submissions", type=Path, required=True)
    parser.add_argument("--current-collection", type=Path, required=True)
    parser.add_argument("--current-l0-facts", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        rights_blank = json.loads(args.rights_blank.read_text(encoding="utf-8"))
        rights_submission = json.loads(args.rights_submission.read_text(encoding="utf-8"))
        science_manifest = json.loads(args.science_manifest.read_text(encoding="utf-8"))
        science_submissions = json.loads(args.science_submissions.read_text(encoding="utf-8"))
        current_collection = json.loads(args.current_collection.read_text(encoding="utf-8"))
        source_document = json.loads(args.current_l0_facts.read_text(encoding="utf-8"))
        current_sources = (
            source_document["cards"] if isinstance(source_document, dict)
            else source_document
        )
        report = audit_c2_joint_review_against_current_sources(
            rights_blank, rights_submission,
            science_manifest, science_submissions,
            current_collection, current_sources,
        )
    except C2JointReviewError as exc:
        report = {
            "decision": "REJECTED",
            "error_code": str(exc),
            "not_for_sft": True,
            "source_rights_verified": False,
            "training_authorized": False,
            "sft_records_emitted": 0,
        }
        print(json.dumps(report, sort_keys=True))
        return 2
    except (OSError, UnicodeError, TypeError, ValueError, KeyError):
        report = {
            "decision": "REJECTED",
            "error_code": "C2_JOINT_REVIEW_READ_OR_SHAPE_INVALID",
            "not_for_sft": True,
            "source_rights_verified": False,
            "training_authorized": False,
            "sft_records_emitted": 0,
        }
        print(json.dumps(report, sort_keys=True))
        return 2

    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
