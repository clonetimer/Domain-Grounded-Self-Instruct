#!/usr/bin/env python3
"""Create labeled SYNTHETIC_TEST_ONLY fixtures, never simulator evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path


def build_fixture(destination: Path, case: str = "unknown-physics") -> dict:
    if case not in {"complete", "unknown-physics", "missed-detection", "no-execution"}:
        raise ValueError("FIXTURE_CASE_INVALID")
    # Refuse to overwrite a user directory or existing run artifacts.
    destination.mkdir(parents=True, exist_ok=False)
    (destination / "artifacts").mkdir()
    roles = ["CONFIGURATION", "EXECUTION_RECORD", "PHYSICS_QA", "DIAGNOSTIC_LOG", "ML_RESULT", "ML_EVALUATION", "SPACECRAFT_CONTEXT", "OPERATIONAL_CONTEXT"]
    stage_names = ["injection_configured", "injection_executed", "physical_effect_observed", "diagnostic_effect_observed", "upstream_ml_detected", "upstream_ml_localized"]
    statuses = ["YES"] * 6
    if case == "unknown-physics":
        statuses[2] = "UNKNOWN"
    elif case == "missed-detection":
        statuses[4:] = ["NO", "UNKNOWN"]
    elif case == "no-execution":
        statuses[1:] = ["NO", "NO", "NO", "UNKNOWN", "UNKNOWN"]
    artifacts = []
    for i, role in enumerate(roles):
        data = (json.dumps({"evidence_origin": "SYNTHETIC_TEST_ONLY", "record_id": f"FIXTURE-{i}", "reported_status": statuses[i] if i < 6 else "FIXTURE_CONTEXT", "notice": "Schema/IO test only; no spacecraft, simulator or ML run was executed."}, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        relative = f"artifacts/fixture_{i}.json"
        (destination / relative).write_bytes(data)
        artifacts.append({"artifact_id": f"A{i}", "run_id": "SYNTHETIC-RUN-1", "role": role, "visibility": "MODEL_VISIBLE" if i in (3, 4, 6, 7) else "QA_ONLY", "path": relative, "format": "json", "size_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "available_at": "2026-01-01T00:00:05Z"})
    receipt = {"schema_version": "dgsi-simulation-run-receipt.v1", "evidence_origin": "SYNTHETIC_TEST_ONLY", "candidate_class": "SIMULATION_CASE_CANDIDATE", "run_id": "SYNTHETIC-RUN-1", "event_family_id": "SYNTHETIC-FAMILY-1", "scenario_id": "SYNTHETIC-SCENARIO-1", "replay_of": None, "simulator": {"engine": "OTHER", "version": "fixture-only", "model_revision": "fixture-only", "configuration_sha256": artifacts[0]["sha256"], "random_seed": 1}, "started_at": "2026-01-01T00:00:00Z", "ended_at": "2026-01-01T00:00:10Z", "analysis_cutoff": "2026-01-01T00:00:06Z", "artifacts": artifacts, "model_visible_artifact_refs": ["A3", "A4", "A6", "A7"], "stages": {name: {"status": status, "evidence_refs": [] if status == "UNKNOWN" else [f"A{i}"]} for i, (name, status) in enumerate(zip(stage_names, statuses))}, "review_status": "REVIEW_REQUIRED", "training_authorized": False, "gold_authorized": False, "sft_export_authorized": False}
    (destination / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    parser.add_argument("--case", choices=["complete", "unknown-physics", "missed-detection", "no-execution"], default="unknown-physics")
    args = parser.parse_args()
    try:
        build_fixture(Path(args.output), args.case)
    except (OSError, ValueError):
        print(json.dumps({"decision": "BLOCKED", "error_code": "FIXTURE_DESTINATION_UNAVAILABLE"}))
        return 2
    print(json.dumps({"decision": "SYNTHETIC_TEST_ONLY", "artifact_count": 8, "simulator_executed": False, "training_authorized": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
