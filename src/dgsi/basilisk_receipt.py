"""Conservative intake checks for native Basilisk R84-R3 evidence packages.

This module validates provenance and separation boundaries only. It never
promotes a run to training eligibility or certifies scientific truth.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

MANIFEST_NAME = "r84r3_execution_manifest.json"
REQUIRED_ARTIFACTS = {
    "r84r3_multichannel_telemetry.jsonl",
    "r84r3_imu_sensor_observations.jsonl",
    "r84r3_case_manifest.jsonl",
    "r84r3_physics_qa.jsonl",
}
TELEMETRY_FORBIDDEN_TOKENS = ("QA_ONLY", "label.", "fault_", "hub.", "capacity_mode")


class ReceiptError(ValueError):
    """Raised when a run package violates the frozen intake contract."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ReceiptError(f"invalid JSON artifact: {path.name}") from exc
    if not isinstance(value, dict):
        raise ReceiptError(f"JSON root must be an object: {path.name}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ReceiptError(f"cannot read JSONL artifact: {path.name}") from exc
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ReceiptError(f"invalid JSONL at {path.name}:{number}") from exc
        if not isinstance(row, dict):
            raise ReceiptError(f"JSONL record must be an object: {path.name}:{number}")
        rows.append(row)
    if not rows:
        raise ReceiptError(f"empty evidence artifact: {path.name}")
    return rows


def _safe_artifact(root: Path, relative: str) -> Path:
    candidate = (root / relative).resolve()
    base = root.resolve()
    if candidate != base and base not in candidate.parents:
        raise ReceiptError(f"artifact path escapes package: {relative}")
    if not candidate.is_file():
        raise ReceiptError(f"required artifact missing: {relative}")
    return candidate


def validate_r84r3_package(package_dir: str | Path) -> dict[str, Any]:
    """Return REVIEW_REQUIRED for a structurally valid package; never ADMITTED."""
    root = Path(package_dir)
    manifest_path = _safe_artifact(root, MANIFEST_NAME)
    manifest = _read_json(manifest_path)

    if manifest.get("schema_version") != "sat-sim.r84r3.multichannel-pilot-summary.v1":
        raise ReceiptError("unsupported R84-R3 manifest schema")
    if manifest.get("status") != "PASS":
        raise ReceiptError("native execution manifest is not PASS")
    if manifest.get("unique_arm_count") != 12:
        raise ReceiptError("expected exactly 12 unique native arms")
    if manifest.get("native_execution_count_including_replay") != 13:
        raise ReceiptError("expected 12 native arms plus one exact replay")
    if manifest.get("recorder_samples_per_execution") != 31:
        raise ReceiptError("unexpected recorder sample count")
    if manifest.get("physical_baseline_comparisons") != 12:
        raise ReceiptError("all 12 physical baseline comparisons are required")
    if manifest.get("seeded_replay", {}).get("passed") is not True:
        raise ReceiptError("exact seeded replay did not pass")

    # R84-R3 is an observer/provenance pilot, not a diagnostic dataset.
    for field in (
        "model_trained",
        "formal_training_or_test_eligible",
        "flight_or_hardware_safety_qualified",
        "stable_release_eligible",
    ):
        if manifest.get(field) is not False:
            raise ReceiptError(f"R84-R3 must explicitly keep {field}=false")

    noise_checks = manifest.get("noise_on_off_checks")
    if not isinstance(noise_checks, list) or len(noise_checks) != 6:
        raise ReceiptError("six IMU noise-isolation checks are required")
    if any(item.get("non_imu_channels_unchanged") is not True for item in noise_checks):
        raise ReceiptError("IMU observer noise changed non-IMU channels")

    artifact_hashes = manifest.get("artifact_sha256")
    if not isinstance(artifact_hashes, dict):
        raise ReceiptError("artifact_sha256 map is missing")
    missing = REQUIRED_ARTIFACTS - set(artifact_hashes)
    if missing:
        raise ReceiptError(f"manifest omits artifact hashes: {sorted(missing)}")

    verified_hashes: dict[str, str] = {}
    for relative in sorted(REQUIRED_ARTIFACTS):
        path = _safe_artifact(root, relative)
        actual = _sha256(path)
        if artifact_hashes[relative] != actual:
            raise ReceiptError(f"artifact SHA-256 mismatch: {relative}")
        verified_hashes[relative] = actual

    telemetry = _read_jsonl(_safe_artifact(root, "r84r3_multichannel_telemetry.jsonl"))
    case_manifest = _read_jsonl(_safe_artifact(root, "r84r3_case_manifest.jsonl"))
    qa_records = _read_jsonl(_safe_artifact(root, "r84r3_physics_qa.jsonl"))
    imu_records = _read_jsonl(_safe_artifact(root, "r84r3_imu_sensor_observations.jsonl"))

    if not (len(telemetry) == len(case_manifest) == len(qa_records) == len(imu_records) == 13):
        raise ReceiptError("all four record streams must contain 13 aligned executions")
    expected_ids = [row.get("record_id") for row in case_manifest]
    if len(set(expected_ids)) != 13 or any(not isinstance(item, str) for item in expected_ids):
        raise ReceiptError("case record IDs must be 13 unique non-empty strings")
    for stream_name, records in (
        ("telemetry", telemetry),
        ("imu", imu_records),
        ("physics QA", qa_records),
    ):
        ids = [row.get("record_id") for row in records]
        if ids != expected_ids:
            raise ReceiptError(f"{stream_name} record order/IDs do not match case manifest")

    total_samples = 0
    for record in telemetry:
        rows = record.get("rows")
        if not isinstance(rows, list) or len(rows) != 31:
            raise ReceiptError("each telemetry execution must contain 31 samples")
        total_samples += len(rows)
        for sample in rows:
            if not isinstance(sample, dict):
                raise ReceiptError("telemetry sample must be an object")
            for key in sample:
                if any(token in key for token in TELEMETRY_FORBIDDEN_TOKENS):
                    raise ReceiptError(f"truth/QA field leaked into model-facing telemetry: {key}")
            if not {"time_s", "imu.raw_gyro_rad_s_x", "imu.raw_gyro_rad_s_y",
                    "imu.raw_gyro_rad_s_z", "sensor.adcs.rw.speed_rad_s_0",
                    "sensor.adcs.rw.speed_rad_s_1", "sensor.adcs.rw.speed_rad_s_2",
                    "command.adcs.rw.motor_torque_nm_0", "command.adcs.rw.motor_torque_nm_1",
                    "command.adcs.rw.motor_torque_nm_2", "estimate.adcs.pointing_error_deg"} <= set(sample):
                raise ReceiptError("telemetry sample is missing required native channels")

    # The replay is retained as an audit/control record, not a distinct scenario.
    replay_rows = [row for row in case_manifest if row.get("repeatability_control") is True]
    if len(replay_rows) != 1 or replay_rows[0].get("replay_of_record_id") not in expected_ids:
        raise ReceiptError("exactly one replay linked to a recorded arm is required")

    return {
        "schema_version": "dgsi.basilisk-intake-check.v1",
        "decision": "REVIEW_REQUIRED",
        "admission_status": "NOT_ADMITTED",
        "dataset_eligibility": "INELIGIBLE_PENDING_SEPARATE_RESEARCH_REVIEW",
        "source_manifest_sha256": _sha256(manifest_path),
        "artifact_sha256_verified": verified_hashes,
        "unique_arm_count": 12,
        "native_execution_count_including_replay": 13,
        "telemetry_sample_count": total_samples,
        "truth_boundary": "R84-R3 QA-only truth is not part of model-facing telemetry",
        "required_human_actions": [
            "verify immutable source archive hashes and simulator build provenance",
            "review event-to-observable mapping and channel units",
            "review fault injection truth separately from model-facing inputs",
            "define independent scenario/run/source split groups before any training use",
            "approve each intended task and label with a qualified ADCS reviewer",
        ],
        "limitations": [
            "structural and hash checks do not establish physical correctness",
            "native state-feedback wheel speed is an ideal upper-bound channel, not an encoder measurement",
            "R84-R3 pilot is not training, validation, test, flight, or hardware qualification evidence",
        ],
    }
