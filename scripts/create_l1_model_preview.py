#!/usr/bin/env python3
"""Create a synthetic three-message preview; never emits SFT-authorized rows."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Make the portable ZIP self-contained when invoked from its extracted root.
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if SRC.is_dir() and str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from dgsi.l1_model_projection_preview import build_collection_preview
from dgsi.l1_model_projection_audit import L1ProjectionAuditError


def _reject(code: str, stage: str, detail: str | None = None) -> int:
    payload = {
        "decision": "REJECTED",
        "error_code": code,
        "stage": stage,
        "sft_records_emitted": 0,
    }
    if detail:
        payload["detail"] = detail
    print(json.dumps(payload, ensure_ascii=False))
    return 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--collection", required=True, type=Path)
    parser.add_argument("--source-facts", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)

    stage = "READ_COLLECTION"
    try:
        collection = json.loads(args.collection.read_text(encoding="utf-8"))
        stage = "READ_SOURCE_FACTS"
        source_payload = json.loads(args.source_facts.read_text(encoding="utf-8"))
        if not isinstance(source_payload, dict) or not isinstance(source_payload.get("cards"), list):
            return _reject("SOURCE_FACTS_SCHEMA_INVALID", stage)
        cards = source_payload["cards"]

        stage = "BUILD_PREVIEW"
        result = build_collection_preview(collection, source_fact_cards=cards)

        stage = "CHECK_OUTPUT"
        if args.output.exists():
            return _reject("OUTPUT_ALREADY_EXISTS", stage)
        stage = "WRITE_PREVIEW"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except L1ProjectionAuditError as exc:
        return _reject(str(exc), stage)
    except FileNotFoundError:
        return _reject("INPUT_FILE_NOT_FOUND", stage)
    except PermissionError:
        return _reject("INPUT_OR_OUTPUT_PERMISSION_DENIED", stage)
    except json.JSONDecodeError as exc:
        return _reject("INPUT_JSON_INVALID", stage, f"line={exc.lineno}; column={exc.colno}")
    except KeyError as exc:
        # A missing schema key is safe to identify; never print source payloads.
        return _reject("REQUIRED_FIELD_MISSING", stage, str(exc)[:120])
    except TypeError:
        return _reject("INPUT_SCHEMA_TYPE_INVALID", stage)
    except (OSError, ValueError, UnicodeError):
        return _reject("INPUT_OR_OUTPUT_INVALID", stage)

    print(json.dumps({
        "decision": result["decision"],
        "packet_count": result["packet_count"],
        "event_family_count": result["event_family_count"],
        "sft_records_emitted": 0,
        "training_authorized": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
