"""SYNTHETIC_TEST_ONLY: review manifest CLI output is metadata-only, no overwrite."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/create_l1_blind_review_manifest.py"
COL = ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
SRC = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"


class ReviewManifestCliTests(unittest.TestCase):
    def _run(self, output: Path):
        return subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--collection", str(COL),
                "--source-facts", str(SRC),
                "--output", str(output),
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_generates_frozen_review_metadata_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.json"
            result = self._run(output)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(payload["packet_count"], 15)
            self.assertEqual(payload["event_family_count"], 9)
            self.assertFalse(payload["training_authorized"])
            self.assertEqual(payload["sft_records_emitted"], 0)
            self.assertEqual(len(payload["review_packets"]), 15)
            rendered = output.read_text(encoding="utf-8")
            self.assertNotIn("internal_review", rendered)
            self.assertNotIn("formal_target", rendered)
            self.assertNotIn("reviewer_token", rendered)
            self.assertEqual(json.loads(result.stdout)["expert_adjudicated_count"], 0)

    def test_refuses_overwrite_without_mutating_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "manifest.json"
            output.write_text("USER_OWNED_FILE", encoding="utf-8")
            result = self._run(output)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(encoding="utf-8"), "USER_OWNED_FILE")
            self.assertEqual(json.loads(result.stdout)["error_code"], "OUTPUT_ALREADY_EXISTS")


if __name__ == "__main__":
    unittest.main()
