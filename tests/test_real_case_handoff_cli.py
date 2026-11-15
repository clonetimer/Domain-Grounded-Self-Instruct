"""SYNTHETIC-ONLY CLI safety checks; never access an actual diagnostic packet."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_real_case_handoffs.py"


def fixture(case_id: str, family_id: str) -> dict:
    return {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": case_id,
        "event_family_id": family_id,
        "source_class": "SYNTHETIC_FIXTURE",
        "permission_status": "UNKNOWN",
        "analysis_cutoff": "2026-11-14T04:00:00Z",
        "timestamp_policy": "ORIGINAL_TIMEZONE_AWARE",
        "redaction": {
            "personal_identifiers_removed": True,
            "sensitive_ids_pseudonymized": True,
            "time_shifted": False,
            "redacted_fields": [],
        },
    }


class RealCaseHandoffCliSyntheticTests(unittest.TestCase):
    def run_cli(self, paths: list[Path]):
        env = dict(os.environ)
        env["PYTHONPATH"] = str(ROOT / "src")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, paths)],
            cwd=ROOT, env=env, capture_output=True, text=True,
            check=False, timeout=20,
        )
        return proc, json.loads(proc.stdout)

    def test_aggregate_output_omits_case_identifiers_and_disables_split(self):
        with tempfile.TemporaryDirectory() as dirname:
            paths = [Path(dirname) / "one.json", Path(dirname) / "two.json"]
            paths[0].write_text(json.dumps(fixture("SYNTHETIC-SECRET-1", "SYNTHETIC-FAMILY-1")), encoding="utf-8")
            paths[1].write_text(json.dumps(fixture("SYNTHETIC-SECRET-2", "SYNTHETIC-FAMILY-1")), encoding="utf-8")
            proc, report = self.run_cli(paths)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(report["case_count"], 2)
        self.assertEqual(report["repeated_event_family_count"], 1)
        self.assertEqual(report["decision_counts"]["SYNTHETIC_TEST_ONLY"], 2)
        self.assertFalse(report["split_assignment_allowed"])
        self.assertNotIn("SYNTHETIC-SECRET", proc.stdout)
        self.assertNotIn("SYNTHETIC-FAMILY-1", proc.stdout)

    def test_missing_file_error_does_not_echo_path(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "PRIVATE_SOURCE_FILENAME.json"
            proc, report = self.run_cli([path])
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(report["error_code"], "MANIFEST_READ_ERROR")
        self.assertNotIn("PRIVATE_SOURCE_FILENAME", proc.stdout)

    def test_duplicate_json_key_error_does_not_echo_values(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "case_manifest.json"
            path.write_text('{"case_id":"SECRET-1","case_id":"SECRET-2"}', encoding="utf-8")
            proc, report = self.run_cli([path])
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(report["error_code"], "DUPLICATE_MANIFEST_JSON_KEY")
        self.assertNotIn("SECRET-", proc.stdout)

    def test_unexpected_raw_telemetry_key_fails_closed(self):
        with tempfile.TemporaryDirectory() as dirname:
            path = Path(dirname) / "case_manifest.json"
            manifest = fixture("SYNTHETIC-3", "SYNTHETIC-FAMILY-3")
            manifest["raw_telemetry"] = [[1, 2, 3]]
            path.write_text(json.dumps(manifest), encoding="utf-8")
            proc, report = self.run_cli([path])
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(report["error_code"], "HANDOFF_SCHEMA_ADDITIONALPROPERTIES")


if __name__ == "__main__":
    unittest.main()
