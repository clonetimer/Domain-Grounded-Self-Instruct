"""Read-only local audit of five-arm input scenario assignments; no model calls."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.sota_construction_scorecard import ScorecardError
from dgsi.sota_scenario_manifest import audit_local_sota_scenarios


def _unique_pairs(pairs):
    result = {}
    for name, value in pairs:
        if name in result:
            raise ScorecardError("SOTA_LOCAL_DUPLICATE_JSON_KEY")
        result[name] = value
    return result


def main() -> int:
    p = argparse.ArgumentParser(description="Audit local, rights-controlled canonical SOTA input assignments")
    p.add_argument("--trials", required=True, type=Path, help="Private scorecard trial input")
    p.add_argument("--manifest", required=True, type=Path, help="Private canonical scenario manifest")
    p.add_argument("--output", required=True, type=Path, help="New metadata-only audit report")
    args = p.parse_args()
    try:
        output = args.output.resolve()
        if output in (args.trials.resolve(), args.manifest.resolve()):
            raise ScorecardError("SOTA_LOCAL_NO_INPUT_OVERWRITE")
        if args.output.exists():
            raise ScorecardError("SOTA_LOCAL_OUTPUT_EXISTS")
        trials = json.loads(args.trials.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"), object_pairs_hook=_unique_pairs)
        result = audit_local_sota_scenarios(trials, manifest)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except (ScorecardError, ValueError, OSError, TypeError):
        print("scenario comparison unavailable: local validation failed", file=sys.stderr)
        return 2
    print("metadata-only scenario audit created")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
