"""SYNTHETIC-only subprocess checks for the minimal run-lineage audit CLI."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_handoff_run_lineage import synthetic

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_handoff_run_lineage.py"


class RunLineageCliSyntheticTests(unittest.TestCase):
    def invoke(self, records, splits=None, lineage_text_override=None):
        with tempfile.TemporaryDirectory() as td:
            params = []
            for i, record in enumerate(records):
                manifest = Path(td) / f"confidential_manifest_{i}.json"
                lineage = Path(td) / f"confidential_lineage_{i}.json"
                manifest.write_text(json.dumps(record["manifest"]), encoding="utf-8")
                text = (lineage_text_override if i == 0 and lineage_text_override is not None
                        else json.dumps(record["lineage"]))
                lineage.write_text(text, encoding="utf-8")
                params += ["--pair", str(manifest), str(lineage)]
            for split in splits or []:
                params += ["--existing-split", split]
            env = dict(os.environ)
            env["PYTHONPATH"] = str(ROOT / "src")
            p = subprocess.run(
                [sys.executable, str(SCRIPT), *params],
                cwd=ROOT, env=env, capture_output=True,
                text=True, check=False, timeout=20,
            )
            return p, json.loads(p.stdout)

    def test_one_synthetic_never_training(self):
        p, report = self.invoke([synthetic()])
        self.assertEqual(p.returncode, 0)
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(report["training_eligible"])

    def test_cross_split_alias_blocks_without_identifier_leak(self):
        records = [
            synthetic("PRIVATE-A", "PRIVATE-FAM-A"),
            synthetic("PRIVATE-B", "PRIVATE-FAM-B"),
        ]
        p, report = self.invoke(records, ["train", "test"])
        self.assertEqual(p.returncode, 2)
        self.assertIn("CROSS_SPLIT_DECLARED_DIAGNOSIS_RUN", report["blocker_codes"])
        for fragment in ("PRIVATE-A", "PRIVATE-FAM", "confidential_manifest",
                         "synthetic://ml-run/001"):
            self.assertNotIn(fragment, p.stdout)

    def test_split_count_mismatch_is_fixed_code(self):
        p, report = self.invoke([synthetic(), synthetic("PRIVATE-B", "FAM-B")],
                                ["train"])
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "EXISTING_SPLIT_COUNT_MISMATCH")

    def test_duplicate_json_key_in_lineage_is_rejected(self):
        p, report = self.invoke(
            [synthetic()],
            lineage_text_override='{"case_id":"A","case_id":"B"}',
        )
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "DUPLICATE_LINEAGE_JSON_KEY")

    def test_forbidden_extra_expert_target_field_rejected(self):
        a = synthetic()
        a["lineage"]["expert_target"] = "not permissible"
        p, report = self.invoke([a])
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "INVALID_RUN_LINEAGE_SHAPE")
        self.assertNotIn("not permissible", p.stdout)

    def test_bad_lineage_json_rejected_without_values(self):
        p, report = self.invoke([synthetic()], lineage_text_override='{"lineage":')
        self.assertEqual(p.returncode, 2)
        self.assertEqual(report["error_code"], "INVALID_LINEAGE_JSON")


if __name__ == "__main__":
    unittest.main()
