"""SYNTHETIC-only subprocess checks; no private Case/log materials."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_case_history_asof import synthetic_case, synthetic_hit

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_case_history_asof.py"


class CaseHistoryAsOfCliSyntheticTests(unittest.TestCase):
    def invoke(self, case=None, hits=None, hit_text=None, scope="reaction_wheel_2"):
        with tempfile.TemporaryDirectory() as temporary:
            case_path = Path(temporary) / "restricted_case.json"
            hit_path = Path(temporary) / "restricted_hits.json"
            case_path.write_text(json.dumps(
                synthetic_case() if case is None else case), encoding="utf-8")
            hit_path.write_text(hit_text if hit_text is not None else json.dumps(
                [synthetic_hit()] if hits is None else hits), encoding="utf-8")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "--case", str(case_path),
                 "--history-hits", str(hit_path), "--equipment-scope", scope],
                cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
                capture_output=True, text=True, timeout=20, check=False,
            )
            return proc, json.loads(proc.stdout)

    def test_pass_is_metadata_only(self):
        proc, result = self.invoke()
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(result["decision"], "PASS_ASOF_METADATA_ONLY")
        self.assertFalse(result["gold_eligible"])

    def test_missing_history_hit_is_nonzero_without_content(self):
        proc, result = self.invoke(hits=[])
        self.assertEqual(proc.returncode, 2)
        self.assertIn("CONFIRMED_HISTORY_HIT_MISSING", result["blocker_codes"])
        self.assertNotIn("HIST-ADCS-017", proc.stdout)
        self.assertNotIn("restricted_case.json", proc.stdout)

    def test_duplicate_json_keys_rejected_without_values(self):
        proc, result = self.invoke(hit_text='{"secret":"SYNTHETIC-PRIVATE", "secret":"SYNTHETIC-PRIVATE"}')
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result["error_code"], "DUPLICATE_LOCAL_JSON_KEY")
        self.assertNotIn("SYNTHETIC-PRIVATE", proc.stdout)

    def test_unresolved_prior_history_requires_manual_review(self):
        proc, result = self.invoke(case=synthetic_case(confirmed=False), hits=[])
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result["decision"], "MANUAL_HISTORY_REVIEW")
        self.assertFalse(result["training_authorized"])

    def test_unbound_scope_rejected(self):
        proc, result = self.invoke(scope="unconfigured_component")
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result["error_code"], "EQUIPMENT_SCOPE_NOT_BOUND_TO_CASE")

    def test_nonfinite_json_is_blocked(self):
        proc, result = self.invoke(hit_text='[NaN]')
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(result["error_code"], "NONFINITE_LOCAL_JSON_NUMBER")


if __name__ == "__main__":
    unittest.main()
