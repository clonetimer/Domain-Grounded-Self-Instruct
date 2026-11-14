import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from dgsi.basilisk_receipt import ReceiptError, validate_r84r3_package


def write_json(path: Path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sample():
    return {
        "time_s": 0.0,
        "imu.raw_gyro_rad_s_x": 0.0,
        "imu.raw_gyro_rad_s_y": 0.0,
        "imu.raw_gyro_rad_s_z": 0.0,
        "sensor.adcs.rw.speed_rad_s_0": 0.0,
        "sensor.adcs.rw.speed_rad_s_1": 0.0,
        "sensor.adcs.rw.speed_rad_s_2": 0.0,
        "command.adcs.rw.motor_torque_nm_0": 0.0,
        "command.adcs.rw.motor_torque_nm_1": 0.0,
        "command.adcs.rw.motor_torque_nm_2": 0.0,
        "estimate.adcs.pointing_error_deg": 0.0,
    }


class BasiliskReceiptTests(unittest.TestCase):
    def build_package(self, root: Path):
        ids = [f"r84r3_{i:02d}" for i in range(12)] + ["r84r3_replay"]
        telemetry = [{"record_id": item, "rows": [sample() for _ in range(31)]} for item in ids]
        imu = [{"record_id": item, "rows": [{"time_s": 0.0} for _ in range(31)]} for item in ids]
        qa = [{"record_id": item, "qa_rows": [{"time_s": 0.0} for _ in range(31)]} for item in ids]
        cases = [{"record_id": item} for item in ids[:-1]] + [{
            "record_id": ids[-1], "repeatability_control": True, "replay_of_record_id": ids[-2]
        }]
        for name, rows in (
            ("r84r3_multichannel_telemetry.jsonl", telemetry),
            ("r84r3_imu_sensor_observations.jsonl", imu),
            ("r84r3_case_manifest.jsonl", cases),
            ("r84r3_physics_qa.jsonl", qa),
        ):
            write_jsonl(root / name, rows)
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
            "noise_on_off_checks": [{"non_imu_channels_unchanged": True} for _ in range(6)],
            "artifact_sha256": {
                name: digest(root / name) for name in (
                    "r84r3_multichannel_telemetry.jsonl",
                    "r84r3_imu_sensor_observations.jsonl",
                    "r84r3_case_manifest.jsonl",
                    "r84r3_physics_qa.jsonl",
                )
            },
        }
        write_json(root / "r84r3_execution_manifest.json", manifest)
        return manifest

    def test_valid_package_requires_human_review_and_is_not_admitted(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.build_package(root)
            result = validate_r84r3_package(root)
            self.assertEqual(result["decision"], "REVIEW_REQUIRED")
            self.assertEqual(result["admission_status"], "NOT_ADMITTED")
            self.assertEqual(result["telemetry_sample_count"], 13 * 31)

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
            rows = json.loads((root / "r84r3_multichannel_telemetry.jsonl").read_text().splitlines()[0])
            rows["rows"][0]["label.fault_active"] = True
            write_jsonl(root / "r84r3_multichannel_telemetry.jsonl", [rows] + [
                json.loads(line) for line in (root / "r84r3_multichannel_telemetry.jsonl").read_text().splitlines()[1:]
            ])
            manifest["artifact_sha256"]["r84r3_multichannel_telemetry.jsonl"] = digest(root / "r84r3_multichannel_telemetry.jsonl")
            write_json(root / "r84r3_execution_manifest.json", manifest)
            with self.assertRaisesRegex(ReceiptError, "truth/QA field leaked"):
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
            self.build_package(root)
            manifest = _ = json.loads((root / "r84r3_execution_manifest.json").read_text())
            manifest["artifact_sha256"]["r84r3_multichannel_telemetry.jsonl"] = digest(root / "r84r3_multichannel_telemetry.jsonl")
            # Required artifact lookup is rooted in the package; symlinks cannot escape it.
            (root / "r84r3_multichannel_telemetry.jsonl").unlink()
            outside = root.parent / (root.name + "_outside.jsonl")
            outside.write_text("{}\n")
            (root / "r84r3_multichannel_telemetry.jsonl").symlink_to(outside)
            write_json(root / "r84r3_execution_manifest.json", manifest)
            with self.assertRaises(ReceiptError):
                validate_r84r3_package(root)


if __name__ == "__main__":
    unittest.main()
