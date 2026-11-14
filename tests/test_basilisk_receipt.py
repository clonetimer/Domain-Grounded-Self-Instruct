import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from dgsi.basilisk_receipt import ReceiptError, validate_r84r3_package


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample(index: int):
    t = index * 0.2
    return {
        "time_s": t,
        "imu.raw_gyro_rad_s_x": 0.001 * index,
        "imu.raw_gyro_rad_s_y": 0.002 * index,
        "imu.raw_gyro_rad_s_z": -0.001 * index,
        "sensor.adcs.rw.speed_rad_s_0": 100.0 + index,
        "sensor.adcs.rw.speed_rad_s_1": 200.0 + index,
        "sensor.adcs.rw.speed_rad_s_2": 300.0 + index,
        "command.adcs.rw.motor_torque_nm_0": 0.001 * index,
        "command.adcs.rw.motor_torque_nm_1": 0.002 * index,
        "command.adcs.rw.motor_torque_nm_2": 0.003 * index,
        "estimate.adcs.pointing_error_deg": 0.01 * index,
    }


class BasiliskReceiptTests(unittest.TestCase):
    def build_package(self, root: Path):
        arm_specs = [
            (reference, capacity, noise)
            for reference in ("zero", "pulse09")
            for capacity in ("healthy", "loss50", "loss75")
            for noise in (0.0, 0.0001)
        ]
        cases = []
        telemetry = []
        imu = []
        qa = []
        base_rows = [sample(i) for i in range(31)]
        qa_rows = [{"time_s": row["time_s"], "qa_value": float(i)} for i, row in enumerate(base_rows)]

        for index, (reference, capacity, noise) in enumerate(arm_specs, 1):
            record_id = f"r84r3_{index:02d}"
            reference_index = 0 if reference == "zero" else 1
            capacity_index = {"healthy": 0, "loss50": 1, "loss75": 2}[capacity]
            noise_index = 0 if noise == 0.0 else 1
            seed = 50_000_000 + reference_index * 100_000 + capacity_index * 10_000 + noise_index * 1_000 + 331
            case_id = f"case_{record_id}"
            cases.append({
                "record_id": record_id, "case_id": case_id,
                "reference_mode": reference, "capacity_mode_QA_ONLY": capacity,
                "gyro_noise_std_rad_s": noise, "rng_seed": seed,
            })
            telemetry.append({"record_id": record_id, "rows": json.loads(json.dumps(base_rows))})
            imu.append({"record_id": record_id, "rows": [
                {"time_s": row["time_s"], **{key: row[key] for key in (
                    "imu.raw_gyro_rad_s_x", "imu.raw_gyro_rad_s_y", "imu.raw_gyro_rad_s_z"
                )}} for row in base_rows
            ]})
            qa.append({
                "record_id": record_id, "qa_rows": json.loads(json.dumps(qa_rows)),
                "max_abs_physics_delta": 0.0,
            })

        replay_target = "r84r3_12"
        replay_id = "r84r3_seeded_replay"
        target_case = next(row for row in cases if row["record_id"] == replay_target)
        cases.append({
            **target_case, "record_id": replay_id,
            "repeatability_control": True, "replay_of_record_id": replay_target,
        })
        telemetry.append({"record_id": replay_id, "rows": json.loads(json.dumps(base_rows))})
        imu.append({"record_id": replay_id, "rows": json.loads(json.dumps(imu[-1]["rows"]))})
        qa.append({
            "record_id": replay_id, "qa_rows": json.loads(json.dumps(qa_rows)),
            "max_abs_physics_delta": 0.0, "repeatability_control": True,
            "replay_of_record_id": replay_target,
        })

        for name, rows in (
            ("r84r3_multichannel_telemetry.jsonl", telemetry),
            ("r84r3_imu_sensor_observations.jsonl", imu),
            ("r84r3_case_manifest.jsonl", cases),
            ("r84r3_physics_qa.jsonl", qa),
        ):
            write_jsonl(root / name, rows)

        source_files = {
            "source/r83m-original.zip": b"fixture-r83m",
            "source/r84r0-reference.zip": b"fixture-r84r0",
            "source/r84r1-reference.zip": b"fixture-r84r1",
        }
        for name, payload in source_files.items():
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes(payload)

        write_json(root / "compat_payload_review.json", {
            "status": "PASS",
            "results": [{
                "payload_bytes_unchanged": True,
                "payload_file_count": 880,
                "source_sha256": "d51fe1ffa1b0b03dc415034b210497b28a2504428d4d8e71b481542a08c08a0a",
            }],
        })

        noise_checks = [{
            "reference_mode": reference,
            "capacity_mode_QA_ONLY": capacity,
            "non_imu_channels_unchanged": True,
            "max_abs_non_imu_delta": 0.0,
            "max_abs_imu_noise_on_off_delta": 0.0001,
        } for reference in ("zero", "pulse09") for capacity in ("healthy", "loss50", "loss75")]

        tracked = [
            "r84r3_multichannel_telemetry.jsonl",
            "r84r3_imu_sensor_observations.jsonl",
            "r84r3_case_manifest.jsonl",
            "r84r3_physics_qa.jsonl",
            *source_files,
        ]
        manifest = {
            "schema_version": "sat-sim.r84r3.multichannel-pilot-summary.v1",
            "status": "PASS",
            "unique_arm_count": 12,
            "native_execution_count_including_replay": 13,
            "recorder_samples_per_execution": 31,
            "physical_baseline_comparisons": 12,
            "seeded_replay": {"passed": True},
            "model_trained": False,
            "formal_training_or_test_eligible": False,
            "flight_or_hardware_safety_qualified": False,
            "stable_release_eligible": False,
            "noise_on_off_checks": noise_checks,
            "artifact_sha256": {name: digest(root / name) for name in tracked},
            "source_sha256": {
                "r83m_original_sha256": digest(root / "source/r83m-original.zip"),
                "r84r0_reference_sha256": digest(root / "source/r84r0-reference.zip"),
                "r84r1_reference_sha256": digest(root / "source/r84r1-reference.zip"),
            },
        }
        write_json(root / "r84r3_execution_manifest.json", manifest)
        return manifest

    def refresh_hash(self, root: Path, manifest: dict, artifact: str):
        manifest["artifact_sha256"][artifact] = digest(root / artifact)
        if artifact.startswith("source/"):
            key = {
                "source/r83m-original.zip": "r83m_original_sha256",
                "source/r84r0-reference.zip": "r84r0_reference_sha256",
                "source/r84r1-reference.zip": "r84r1_reference_sha256",
            }[artifact]
            manifest["source_sha256"][key] = digest(root / artifact)
        write_json(root / "r84r3_execution_manifest.json", manifest)

    def test_valid_package_requires_human_review_and_is_not_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_package(root)
            result = validate_r84r3_package(root)
            self.assertEqual(result["decision"], "REVIEW_REQUIRED")
            self.assertEqual(result["admission_status"], "NOT_ADMITTED")
            self.assertEqual(result["telemetry_sample_count"], 13 * 31)
            self.assertEqual(result["basilisk_native_payload_file_count"], 880)

    def test_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_package(root)
            with (root / "r84r3_multichannel_telemetry.jsonl").open("a") as stream:
                stream.write("{}\n")
            with self.assertRaisesRegex(ReceiptError, "SHA-256 mismatch"):
                validate_r84r3_package(root)

    def test_truth_leakage_in_model_facing_telemetry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            file = root / "r84r3_multichannel_telemetry.jsonl"
            rows = [json.loads(line) for line in file.read_text().splitlines()]
            rows[0]["rows"][0]["label.fault_active"] = True
            write_jsonl(file, rows)
            self.refresh_hash(root, manifest, file.name)
            with self.assertRaisesRegex(ReceiptError, "exact channel whitelist"):
                validate_r84r3_package(root)

    def test_training_eligibility_flag_must_remain_false(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            manifest["formal_training_or_test_eligible"] = True
            write_json(root / "r84r3_execution_manifest.json", manifest)
            with self.assertRaisesRegex(ReceiptError, "must explicitly keep"):
                validate_r84r3_package(root)

    def test_artifact_path_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            target = root / "r84r3_multichannel_telemetry.jsonl"
            target.unlink()
            outside = root.parent / (root.name + "_outside.jsonl")
            outside.write_text("{}\n")
            target.symlink_to(outside)
            with self.assertRaises(ReceiptError):
                validate_r84r3_package(root)

    def test_replay_must_match_referenced_arm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            file = root / "r84r3_multichannel_telemetry.jsonl"
            rows = [json.loads(line) for line in file.read_text().splitlines()]
            rows[-1]["rows"][0]["sensor.adcs.rw.speed_rad_s_0"] += 0.5
            write_jsonl(file, rows)
            self.refresh_hash(root, manifest, file.name)
            with self.assertRaisesRegex(ReceiptError, "replay is not exact"):
                validate_r84r3_package(root)

    def test_stream_time_axis_must_align(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            file = root / "r84r3_imu_sensor_observations.jsonl"
            rows = [json.loads(line) for line in file.read_text().splitlines()]
            rows[0]["rows"][3]["time_s"] += 0.01
            write_jsonl(file, rows)
            self.refresh_hash(root, manifest, file.name)
            with self.assertRaisesRegex(ReceiptError, "time grid"):
                validate_r84r3_package(root)

    def test_nonfinite_telemetry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            file = root / "r84r3_multichannel_telemetry.jsonl"
            rows = [json.loads(line) for line in file.read_text().splitlines()]
            rows[0]["rows"][2]["imu.raw_gyro_rad_s_x"] = float("nan")
            write_jsonl(file, rows)
            self.refresh_hash(root, manifest, file.name)
            with self.assertRaisesRegex(ReceiptError, "non-finite"):
                validate_r84r3_package(root)

    def test_source_archive_hash_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            with (root / "source/r83m-original.zip").open("ab") as stream:
                stream.write(b"tamper")
            with self.assertRaisesRegex(ReceiptError, "SHA-256 mismatch"):
                validate_r84r3_package(root)

    def test_noise_matrix_must_cover_all_six_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            manifest["noise_on_off_checks"].pop()
            write_json(root / "r84r3_execution_manifest.json", manifest)
            with self.assertRaisesRegex(ReceiptError, "six IMU noise-isolation"):
                validate_r84r3_package(root)

    def test_unregistered_extra_telemetry_channel_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = self.build_package(root)
            file = root / "r84r3_multichannel_telemetry.jsonl"
            rows = [json.loads(line) for line in file.read_text().splitlines()]
            rows[0]["rows"][0]["debug_internal_truth"] = 1.0
            write_jsonl(file, rows)
            self.refresh_hash(root, manifest, file.name)
            with self.assertRaisesRegex(ReceiptError, "exact channel whitelist"):
                validate_r84r3_package(root)


if __name__ == "__main__":
    unittest.main()
