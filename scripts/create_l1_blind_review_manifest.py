#!/usr/bin/env python3
"""Create metadata-only L1 blind-review manifest JSON; no SFT or expert approval."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dgsi.l1_blind_review_manifest import (
    L1BlindReviewManifestError, build_l1_blind_review_manifest,
)
from dgsi.l1_model_projection_audit import L1ProjectionAuditError


def _reject(code: str, stage: str) -> int:
    print(json.dumps({
        "decision": "REJECTED", "error_code": code, "stage": stage,
        "sft_records_emitted": 0, "training_authorized": False,
    }))
    return 2


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--source-facts", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    stage = "READ_COLLECTION"
    try:
        collection = json.loads(args.collection.read_text(encoding="utf-8"))
        stage = "READ_SOURCE_FACTS"
        sources = json.loads(args.source_facts.read_text(encoding="utf-8"))
        if not isinstance(sources, dict) or not isinstance(sources.get("cards"), list):
            return _reject("SOURCE_FACTS_SCHEMA_INVALID", stage)
        stage = "BUILD_REVIEW_MANIFEST"
        manifest = build_l1_blind_review_manifest(
            collection, source_fact_cards=sources["cards"]
        )
        stage = "WRITE_REVIEW_MANIFEST"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        # "x" enforces atomic exclusive creation on Ubuntu and Windows.
        # Checking Path.exists() and then writing is a TOCTOU race; it also
        # misses dangling symlinks and could overwrite their targets.
        with args.output.open("x", encoding="utf-8", newline="\n") as output:
            output.write(
                json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False)
                + "\n"
            )
    except (L1BlindReviewManifestError, L1ProjectionAuditError) as exc:
        return _reject(str(exc), stage)
    except FileExistsError:
        return _reject("OUTPUT_ALREADY_EXISTS", stage)
    except FileNotFoundError:
        return _reject("INPUT_FILE_NOT_FOUND", stage)
    except PermissionError:
        return _reject("INPUT_OR_OUTPUT_PERMISSION_DENIED", stage)
    except json.JSONDecodeError:
        return _reject("INPUT_JSON_INVALID", stage)
    except (KeyError, TypeError, ValueError, OSError, UnicodeError):
        return _reject("INPUT_OR_OUTPUT_INVALID", stage)
    print(json.dumps({
        "decision": manifest["decision"],
        "packet_count": manifest["packet_count"],
        "event_family_count": manifest["event_family_count"],
        "expert_adjudicated_count": 0,
        "rights_cleared_event_family_count": 0,
        "sft_records_emitted": 0,
        "training_authorized": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
