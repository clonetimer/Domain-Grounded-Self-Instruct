from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dgsi.sota_construction_scorecard import ScorecardError, scorecard_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate independently reviewed DGSI/SOTA construction attempts without model calls")
    parser.add_argument("--input", required=True, type=Path, help="Private local trial JSON")
    parser.add_argument("--output", required=True, type=Path, help="New aggregate-only JSON report")
    args = parser.parse_args()
    try:
        scorecard_file(args.input, args.output)
    except (ScorecardError, ValueError, OSError) as exc:
        print(f"comparison unavailable: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(f"wrote aggregate-only report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
