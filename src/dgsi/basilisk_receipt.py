"""Conservative intake checks for native Basilisk R84-R3 evidence packages.

Validates immutable provenance, aligned native observations and truth boundaries.
A successful check is review-only: it never admits data or certifies science.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

MANIFEST_NAME = "r84r3_execution_manifest.json"
COMPAT_REPORT = "compat_payload_review.json"
REQUIRED_ARTIFACTS = {
    "r84r3_multichannel_telemetry.jsonl",
    "r84r3_imu_sensor_observations.jsonl",
    "r84r3_case_manifest.jsonl",
    "r84r3_physics_qa.jsonl",
    "source/r83m-original.zip",
    "source/r84r0-reference.zip",
    "source/r84r1-reference.zip",
}
SOURCE_HASH_FIELDS = {
    "source/r83m-original.zip": "r83m_original_sha256",
    "source/r84r0-reference.zip": "r84r0_reference_sha256",
    "source/r84r1-reference.zip": "r84r1_reference_sha256",
}
IMU_FIELDS = (
    "imu.raw_gyro_rad_s_x",
    "imu.raw_gyro_rad_s_y",
    "imu.raw_gyro_rad_s_z",
)
TELEMETRY_FIELDS = (
    *IMU_FIELDS,
    "sensor.adcs.rw.speed_rad_s_0",
    "sensor.adcs.rw.speed_rad_s_1",
    "sensor.adcs.rw.speed_rad_s_2",
    "command.adcs.rw.motor_torque_nm_0",
    "command.adcs.rw.motor_torque_nm_1",
    "command.adcs.rw.motor_torque_nm_2",
    "estimate.adcs.pointing_error_deg",
)
TELEMETRY_FORBIDDEN_TOKENS = ("QA_ONLY", "label.", "fault_", "hub.", "capacity_mode")
EXPECTED_REFERENCES = {"zero", "pulse09"}
EXPECTED_CAPACITIES = {"healthy", "loss50", "loss75"}
EXPECTED_NOISES = {0.0, 0.0001}
EXPECTED_NOISE_PAIRS = {
    (reference, capacity)
    for reference in EXPECTED_REFERENCES
    for capacity in EXPECTED_CAPACITIES
}


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


def _records_by_id(records: list[dict[str, Any]], stream_name: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in records:
        record_id = row.get("record_id")
        if not isinstance(record_id, str) or not record_id:
            raise ReceiptError(f"{stream_name} record_id must be a non-empty string")
        if record_id in result:
            raise ReceiptError(f"duplicate {stream_name} record_id: {record_id}")
        result[record_id] = row
    return result


def _numeric(value: Any, context: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ReceiptError(f"non-numeric value in {context}")
    number = float(value)
    if not math.isfinite(number):
        raise ReceiptError(f"non-finite value in {context}")
    return number


def _validate_rows(
    rows: Any,
    required_fields: tuple[str, ...],
    context: str,
    *,
    exact_fields: bool = False,
) -> list[dict[str, Any]]:
    if not isinstance(rows, list) or len(rows) != 31:
        raise ReceiptError(f"{context} must contain exactly 31 samples")
    validated: list[dict[str, Any]] = []
    previous_time: float | None = None
    expected_fields = set(required_fields)
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ReceiptError(f"{context} sample {index} must be an object")
        fields = set(row)
        missing = expected_fields - fields
        if missing:
            raise ReceiptError(f"{context} sample {index} missing fields: {sorted(missing)}")
        if exact_fields and fields != expected_fields:
            raise ReceiptError(f"{context} sample {index} violates exact channel whitelist")
        time_s = _numeric(row["time_s"], f"{context}[{index}].time_s")
        expected_time = index * 0.2
        if abs(time_s - expected_time) > 1e-12:
            raise ReceiptError(f"{context} sample {index} has an unexpected time grid")
        if previous_time is not None and time_s <= previous_time:
            raise ReceiptError(f"{context} time axis is not strictly increasing")
        previous_time = time_s
        for field in fields:
            _numeric(row[field], f"{context}[{index}].{field}")
        validated.append(row)
    return validated


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
    replay_summary = manifest.get("seeded_replay")
    if not isinstance(replay_summary, dict) or replay_summary.get("passed") is not True:
        raise ReceiptError("exact seeded replay did not pass")

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
    observed_noise_pairs = set()
    for item in noise_checks:
        if not isinstance(item, dict):
            raise ReceiptError("malformed IMU noise-isolation record")
        pair = (item.get("reference_mode"), item.get("capacity_mode_QA_ONLY"))
        if pair in observed_noise_pairs:
            raise ReceiptError("duplicate IMU noise-isolation pair")
        observed_noise_pairs.add(pair)
        if item.get("non_imu_channels_unchanged") is not True:
            raise ReceiptError("IMU observer noise changed non-IMU channels")
        if _numeric(item.get("max_abs_non_imu_delta"), "noise check non-IMU delta") > 1e-12:
            raise ReceiptError("non-IMU channel changed under observer-noise intervention")
        if _numeric(item.get("max_abs_imu_noise_on_off_delta"), "noise check IMU delta") <= 0:
            raise ReceiptError("IMU noise intervention produced no IMU-channel change")
    if observed_noise_pairs != EXPECTED_NOISE_PAIRS:
        raise ReceiptError("IMU noise-isolation matrix does not cover the frozen 2x3 design")

    artifact_hashes = manifest.get("artifact_sha256")
    source_hashes = manifest.get("source_sha256")
    if not isinstance(artifact_hashes, dict) or not isinstance(source_hashes, dict):
        raise ReceiptError("artifact/source SHA-256 maps are missing")
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
        source_field = SOURCE_HASH_FIELDS.get(relative)
        if source_field and source_hashes.get(source_field) != actual:
            raise ReceiptError(f"source archive SHA-256 mismatch: {relative}")

    compat = _read_json(_safe_artifact(root, COMPAT_REPORT))
    results = compat.get("results")
    if compat.get("status") != "PASS" or not isinstance(results, list) or len(results) != 1:
        raise ReceiptError("Basilisk compatibility payload review is not PASS")
    compat_result = results[0]
    if compat_result.get("payload_bytes_unchanged") is not True or compat_result.get("payload_file_count") != 880:
        raise ReceiptError("Basilisk native payload was not proven byte-identical")
    if compat_result.get("source_sha256") != "d51fe1ffa1b0b03dc415034b210497b28a2504428d4d8e71b481542a08c08a0a":
        raise ReceiptError("unexpected upstream Basilisk wheel SHA-256")

    telemetry = _read_jsonl(_safe_artifact(root, "r84r3_multichannel_telemetry.jsonl"))
    case_manifest = _read_jsonl(_safe_artifact(root, "r84r3_case_manifest.jsonl"))
    qa_records = _read_jsonl(_safe_artifact(root, "r84r3_physics_qa.jsonl"))
    imu_records = _read_jsonl(_safe_artifact(root, "r84r3_imu_sensor_observations.jsonl"))
    if not (len(telemetry) == len(case_manifest) == len(qa_records) == len(imu_records) == 13):
        raise ReceiptError("all four record streams must contain 13 aligned executions")

    case_by_id = _records_by_id(case_manifest, "case manifest")
    telemetry_by_id = _records_by_id(telemetry, "telemetry")
    imu_by_id = _records_by_id(imu_records, "IMU")
    qa_by_id = _records_by_id(qa_records, "physics QA")
    expected_ids = set(case_by_id)
    for stream_name, records in (
        ("telemetry", telemetry_by_id),
        ("IMU", imu_by_id),
        ("physics QA", qa_by_id),
    ):
        if set(records) != expected_ids:
            raise ReceiptError(f"{stream_name} record IDs do not match case manifest")

    replay_rows = [row for row in case_manifest if row.get("repeatability_control") is True]
    if len(replay_rows) != 1:
        raise ReceiptError("exactly one replay control record is required")
    replay_id = replay_rows[0]["record_id"]
    replay_target = replay_rows[0].get("replay_of_record_id")
    if replay_target not in case_by_id or replay_target == replay_id:
        raise ReceiptError("replay must reference one of the 12 unique native arms")
    arm_ids = expected_ids - {replay_id}
    if len(arm_ids) != 12 or any(case_by_id[item].get("repeatability_control") is True for item in arm_ids):
        raise ReceiptError("case manifest must contain exactly 12 unique arms and one replay")

    observed_arms = set()
    for record_id in arm_ids:
        case = case_by_id[record_id]
        reference = case.get("reference_mode")
        capacity = case.get("capacity_mode_QA_ONLY")
        noise = case.get("gyro_noise_std_rad_s")
        if reference not in EXPECTED_REFERENCES or capacity not in EXPECTED_CAPACITIES or noise not in EXPECTED_NOISES:
            raise ReceiptError(f"unregistered R84-R3 arm design: {record_id}")
        arm = (reference, capacity, noise)
        if arm in observed_arms:
            raise ReceiptError(f"duplicate R84-R3 arm design: {arm}")
        observed_arms.add(arm)
        reference_index = 0 if reference == "zero" else 1
        capacity_index = {"healthy": 0, "loss50": 1, "loss75": 2}[capacity]
        noise_index = 0 if noise == 0.0 else 1
        expected_seed = 50_000_000 + reference_index * 100_000 + capacity_index * 10_000 + noise_index * 1_000 + 331
        if case.get("rng_seed") != expected_seed:
            raise ReceiptError(f"R84-R3 frozen seed mismatch: {record_id}")
    if observed_arms != {
        (reference, capacity, noise)
        for reference in EXPECTED_REFERENCES
        for capacity in EXPECTED_CAPACITIES
        for noise in EXPECTED_NOISES
    }:
        raise ReceiptError("R84-R3 arm matrix is incomplete")
    replay_case = case_by_id[replay_id]
    target_case = case_by_id[replay_target]
    if any(replay_case.get(field) != target_case.get(field) for field in (
        "case_id", "reference_mode", "capacity_mode_QA_ONLY", "gyro_noise_std_rad_s", "rng_seed"
    )):
        raise ReceiptError("replay metadata does not match its source arm")

    total_samples = 0
    for record_id in expected_ids:
        telemetry_rows = _validate_rows(
            telemetry_by_id[record_id].get("rows"),
            ("time_s", *TELEMETRY_FIELDS),
            f"telemetry:{record_id}",
            exact_fields=True,
        )
        imu_rows = _validate_rows(
            imu_by_id[record_id].get("rows"),
            ("time_s", *IMU_FIELDS),
            f"imu:{record_id}",
            exact_fields=True,
        )
        qa_payload = qa_by_id[record_id].get("qa_rows")
        if not isinstance(qa_payload, list) or len(qa_payload) != 31:
            raise ReceiptError(f"physics QA:{record_id} must contain exactly 31 samples")
        qa_rows = _validate_rows(qa_payload, ("time_s",), f"physics-qa:{record_id}")
        total_samples += len(telemetry_rows)

        for index, (telemetry_row, imu_row, qa_row) in enumerate(zip(telemetry_rows, imu_rows, qa_rows)):
            for key in telemetry_row:
                if any(token in key for token in TELEMETRY_FORBIDDEN_TOKENS):
                    raise ReceiptError(f"truth/QA field leaked into model-facing telemetry: {key}")
            if abs(telemetry_row["time_s"] - imu_row["time_s"]) > 1e-12:
                raise ReceiptError(f"telemetry/IMU time mismatch: {record_id}:{index}")
            if abs(telemetry_row["time_s"] - qa_row["time_s"]) > 1e-12:
                raise ReceiptError(f"telemetry/QA time mismatch: {record_id}:{index}")
            for field in IMU_FIELDS:
                if abs(telemetry_row[field] - imu_row[field]) > 1e-12:
                    raise ReceiptError(f"IMU channel mismatch between streams: {record_id}:{index}:{field}")

    for record_id in arm_ids:
        qa_record = qa_by_id[record_id]
        if _numeric(qa_record.get("max_abs_physics_delta"), "physics baseline delta") > 1e-8:
            raise ReceiptError(f"physical baseline comparison exceeded tolerance: {record_id}")
    replay_qa = qa_by_id[replay_id]
    if _numeric(replay_qa.get("max_abs_physics_delta"), "replay physics delta") > 1e-12:
        raise ReceiptError("replay physics delta is not exact")

    # The replay must be sample-exact across telemetry, IMU and physics QA.
    for stream_name, records, row_key, fields in (
        ("telemetry", telemetry_by_id, "rows", ("time_s", *TELEMETRY_FIELDS)),
        ("IMU", imu_by_id, "rows", ("time_s", *IMU_FIELDS)),
        ("physics QA", qa_by_id, "qa_rows", None),
    ):
        replay_values = records[replay_id].get(row_key)
        target_values = records[replay_target].get(row_key)
        if not isinstance(replay_values, list) or not isinstance(target_values, list) or len(replay_values) != 31 or len(target_values) != 31:
            raise ReceiptError(f"{stream_name} replay rows are malformed")
        if fields is None:
            fields = tuple(sorted(set(replay_values[0]) | set(target_values[0])))
        for index, (replay_sample, target_sample) in enumerate(zip(replay_values, target_values)):
            if any(field not in replay_sample or field not in target_sample for field in fields):
                raise ReceiptError(f"{stream_name} replay field mismatch")
            if any(_numeric(replay_sample[field], field) != _numeric(target_sample[field], field) for field in fields):
                raise ReceiptError(f"{stream_name} replay is not exact: sample {index}")

    return {
        "schema_version": "dgsi.basilisk-intake-check.v1",
        "decision": "REVIEW_REQUIRED",
        "admission_status": "NOT_ADMITTED",
        "dataset_eligibility": "INELIGIBLE_PENDING_SEPARATE_RESEARCH_REVIEW",
        "source_manifest_sha256": _sha256(manifest_path),
        "artifact_sha256_verified": verified_hashes,
        "source_archive_sha256_verified": {path: verified_hashes[path] for path in SOURCE_HASH_FIELDS},
        "upstream_basilisk_wheel_sha256": compat_result["source_sha256"],
        "basilisk_native_payload_file_count": compat_result["payload_file_count"],
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
