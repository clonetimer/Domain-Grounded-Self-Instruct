#!/usr/bin/env python3
"""Local-only CLI; no network, no payload echoes, no SFT emission."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from dgsi.simulation_run_receipt import (MAX_RECEIPT_BYTES, SimulationReceiptError,
                                       load_receipt_text, validate_simulation_run_receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", required=True)
    parser.add_argument("--artifact-root", required=True)
    args = parser.parse_args()
    try:
        path = Path(args.receipt)
        if path.is_symlink():
            raise SimulationReceiptError("SIM_SYMLINK_FORBIDDEN")
        if not path.is_file() or path.stat().st_size > MAX_RECEIPT_BYTES:
            raise SimulationReceiptError("SIM_RECEIPT_SIZE_OR_TYPE_INVALID")
        with path.open("rb") as stream:
            data = stream.read(MAX_RECEIPT_BYTES + 1)
        if len(data) > MAX_RECEIPT_BYTES:
            raise SimulationReceiptError("SIM_RECEIPT_SIZE_OR_TYPE_INVALID")
        receipt = load_receipt_text(data.decode("utf-8-sig"))
        report = validate_simulation_run_receipt(receipt, artifact_root=args.artifact_root)
    except SimulationReceiptError as exc:
        print(json.dumps({"decision": "BLOCKED", "error_code": str(exc), "sft_records_emitted": 0, "training_authorized": False}))
        return 2
    except (OSError, UnicodeError):
        print(json.dumps({"decision": "BLOCKED", "error_code": "SIM_RECEIPT_NOT_READABLE", "sft_records_emitted": 0, "training_authorized": False}))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
