#!/usr/bin/env python3
"""Audit returned C2 A/B expert forms against the current L1 collection and L0 sources."""
import argparse
import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from dgsi.l1_c2_expert_intake import C2ExpertIntakeError, audit_c2_expert_intake_against_current_sources


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise C2ExpertIntakeError("C2_EXPERT_ARGUMENTS_INVALID")


def _unique_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise C2ExpertIntakeError("C2_EXPERT_JSON_DUPLICATE_KEY")
        obj[key] = value
    return obj


def _invalid_constant(value):
    raise C2ExpertIntakeError("C2_EXPERT_JSON_INVALID")


def _read(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_keys,
                      parse_constant=_invalid_constant)


def _publish(path, report):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".dgsi-expert-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(report, handle, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.link(name, path)
    finally:
        os.unlink(name)


def main(argv=None):
    parser = _ArgumentParser(description=__doc__)
    for flag in ("reviewer-a", "reviewer-b", "current-collection", "current-l0-facts"):
        parser.add_argument("--" + flag, required=True, type=Path)
    parser.add_argument("--output-file", type=Path)
    try:
        args = parser.parse_args(argv)
        sources = _read(args.current_l0_facts)
        cards = sources.get("cards") if isinstance(sources, dict) else sources
        report = audit_c2_expert_intake_against_current_sources(
            _read(args.reviewer_a), _read(args.reviewer_b), _read(args.current_collection), cards)
        if args.output_file is not None:
            _publish(args.output_file, report)
    except C2ExpertIntakeError as exc:
        code = str(exc)
    except FileExistsError:
        code = "C2_EXPERT_OUTPUT_ALREADY_EXISTS"
    except (OSError, ValueError, RecursionError):
        code = "C2_EXPERT_INPUT_OR_OUTPUT_INVALID"
    else:
        print(json.dumps({key: value for key, value in report.items() if key != "task_queue"}, sort_keys=True))
        return 0
    print(json.dumps({"decision": "REJECTED", "error_code": code,
                      "training_authorized": False, "sft_records_emitted": 0}, sort_keys=True))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
