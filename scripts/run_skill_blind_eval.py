#!/usr/bin/env python3
"""Run an opt-in blind baseline-vs-Skill evaluation using OpenAI Responses API."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

from dgsi.skill_eval import run_live_evaluation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-live", action="store_true", help="Make paid API calls. Omitted by default.")
    parser.add_argument("--limit", type=int, default=0, help="Explicit maximum case count; required for live runs.")
    parser.add_argument("--seed", type=int, default=20261114, help="Deterministic blind-order seed.")
    parser.add_argument("--output", type=Path, help="Local JSONL output path; never committed by default.")
    args = parser.parse_args(argv)

    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / "resources" / "skill_pressure_cases.json").read_text(encoding="utf-8"))["cases"]
    selected_count = min(args.limit, len(cases)) if args.limit > 0 else len(cases)

    if not args.execute_live:
        print(json.dumps({
            "mode": "DRY_RUN",
            "network_calls": 0,
            "cases_available": len(cases),
            "cases_selected": selected_count,
            "generator_model_configured": bool(os.environ.get("DGSI_GENERATOR_MODEL")),
            "judge_model_configured": bool(os.environ.get("DGSI_JUDGE_MODEL")),
            "generator_family_configured": bool(os.environ.get("DGSI_GENERATOR_FAMILY")),
            "judge_family_configured": bool(os.environ.get("DGSI_JUDGE_FAMILY")),
            "api_key_configured": bool(os.environ.get("OPENAI_API_KEY")),
            "responses_store": False,
            "next_step": "Set local environment variables and pass --execute-live --limit N to make an explicit bounded run.",
        }, ensure_ascii=False, indent=2))
        return 0

    if args.limit <= 0:
        parser.error("live runs require an explicit positive --limit to control API cost")
    generator_model = os.environ.get("DGSI_GENERATOR_MODEL", "").strip()
    judge_model = os.environ.get("DGSI_JUDGE_MODEL", "").strip()
    generator_family = os.environ.get("DGSI_GENERATOR_FAMILY", "").strip()
    judge_family = os.environ.get("DGSI_JUDGE_FAMILY", "").strip()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    independence_note = os.environ.get("DGSI_JUDGE_INDEPENDENCE_NOTE", "").strip()
    output = args.output or (
        root / "reports" / "skill_blind_eval" /
        f"skill-eval-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.jsonl"
    )

    result = run_live_evaluation(
        root=root,
        output_path=output,
        generator_model=generator_model,
        judge_model=judge_model,
        generator_family=generator_family,
        judge_family=judge_family,
        api_key=api_key,
        independence_note=independence_note,
        seed=args.seed,
        limit=min(args.limit, len(cases)),
    )
    print(json.dumps({
        "mode": "LIVE",
        "summary": result["summary"],
        "output_path": result["output_path"],
        "responses_store": False,
        "note": "Judge condition labels were hidden until after scoring. Verify the independence note and review critical failures before interpreting the result.",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
