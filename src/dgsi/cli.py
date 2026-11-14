"""Offline preflight for individual seed JSON files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from .quality import load_registry, report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dgsi", description="Preflight ADCS Self-Instruct seed candidate (not a fact verifier)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="Validate a single seed JSON file")
    validate.add_argument("file", type=Path)
    validate.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        registry = load_registry(args.root)
        seed = json.loads(args.file.read_text(encoding="utf-8"))
        result = report(seed, registry)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(json.dumps({"decision": "INVALID_INPUT", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["decision"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
