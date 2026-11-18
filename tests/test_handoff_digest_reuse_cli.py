"""SYNTHETIC-only CLI regressions; no real material accessed."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_handoff_digest_reuse.py"


def synthetic(cid: str, fid: str, digest: str = "a" * 64) -> dict:
    return {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": cid,
        "event_family_id": fid,
        "source_class": "SYNTHETIC_FIXTURE",
        "permission_status": "UNKNOWN",
        "analysis_cutoff": "2026-10-01T00:00:00Z",
        "timestamp_policy": "ORIGINAL_TIMEZONE_AWARE",
        "redaction": {
            "personal_identifiers_removed": True,
            "sensitive_ids_pseudonymized": True,
            "time_shifted": False,
            "redacted_fields": [],
        },
        "available_files": [
            "diagnosis_result.json", "diagnostic_logs.jsonl",
        ],
        "input_file_sha256": {
            "diagnosis_result.json": digest,
            "diagnostic_logs.jsonl": ("b" if cid.endswith("1") else "c") * 64,
        },
    }


class SyntheticDigestReuseCliTests(unittest.TestCase):
    def call(self, manifest_objs: list[dict], splits: list[str] | None = None):
        with tempfile.TemporaryDirectory() as name:
            paths = []
            for i, obj in enumerate(manifest_objs):
                path = Path(name) / f"secret_{i}.json"
                path.write_text(json.dumps(obj), encoding="utf-8")
                paths.append(str(path))
            options = []
            for split in splits or []:
                options += ["--existing-split", split]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), *options, *paths],
                env=env, cwd=ROOT, capture_output=True, text=True, timeout=20,
                check=False,
            )
            return proc, json.loads(proc.stdout)

    def test_synthetic_cohort_does_not_leak_identifiers(self):
        p, report = self.call([
            synthetic("SECRET-1", "PRIVATE-FAMILY-1"),
            synthetic("SECRET-2", "PRIVATE-FAMILY-2", "d" * 64),
        ])
        self.assertEqual(p.returncode, 0)
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(report["gold_eligible"])
        for token in ("PRIVATE-FAMILY", "SECRET-1", "secret_0.json", "a" * 64):
            self.assertNotIn(token, p.stdout)

    def test_cross_split_shared_digest_blocks(self):
        p, report = self.call([
            synthetic("SECRET-1", "PRIVATE-FAMILY-1"),
            synthetic("SECRET-2", "PRIVATE-FAMILY-2"),
        ], ["train", "test"])
        self.assertEqual(p.returncode, 2)
        self.assertIn("CROSS_SPLIT_DECLARED_EVENT_SOURCE_DIGEST", report["blocker_codes"])

    def test_wrong_split_count_is_rejected_without_paths(self):
        p, report = self.call([
            synthetic("SECRET-1", "PRIVATE-FAMILY-1"),
            synthetic("SECRET-2", "PRIVATE-FAMILY-2"),
        ], ["train"])
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "EXISTING_SPLIT_COUNT_MISMATCH")
        self.assertNotIn("secret_", p.stdout)

    def test_invalid_manifest_rejected_before_audit(self):
        invalid = synthetic("SECRET-1", "PRIVATE-FAMILY-1")
        invalid["raw_telemetry"] = [0.1]
        p, report = self.call([invalid])
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "INVALID_HANDOFF_MANIFEST")
        self.assertNotIn("SECRET-1", p.stdout)


if __name__ == "__main__":
    unittest.main()
