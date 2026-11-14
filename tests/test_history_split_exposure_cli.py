"""SYNTHETIC-only subprocess tests for local-only history audit CLI."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/audit_history_split_exposure.py"
BASE = json.loads(
    (ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8")
)


def make_case(tag):
    case = copy.deepcopy(BASE)
    case["case_id"] = "SYNTH-CLI-" + tag
    case["provenance"]["source_group"] = "SYNTH-CLI-EPISODE-" + tag
    return case


class HistorySplitCliTests(unittest.TestCase):
    def run_manifest(self, root, rows, output=None):
        manifest_path = Path(root) / "manifest.json"
        manifest_path.write_text(json.dumps({"entries": rows}), encoding="utf-8")
        cmd = [sys.executable, str(SCRIPT), "--manifest", str(manifest_path)]
        if output is not None:
            cmd.extend(["--output", str(output)])
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        return subprocess.run(cmd, text=True, capture_output=True, cwd=ROOT, env=env, check=False)

    def save(self, root, case, name):
        path = Path(root) / (name + ".json")
        path.write_text(json.dumps(case), encoding="utf-8")
        return str(path)

    def test_single_case_emits_aggregate_only_and_creates_output(self):
        with tempfile.TemporaryDirectory() as root:
            path = self.save(root, make_case("ONE"), "one")
            output = Path(root) / "aggregate.json"
            completed = self.run_manifest(root, [{"split": "train", "case_path": path}], output)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertEqual(json.loads(output.read_text())["case_packet_count"], 1)
            self.assertNotIn("SYNTH-CLI-ONE", completed.stdout)
            self.assertNotIn(str(root), completed.stdout)
            self.assertNotIn("tracking error", completed.stdout)

    def test_shared_external_history_exit_code_is_manual_review(self):
        with tempfile.TemporaryDirectory() as root:
            a, b = make_case("ONE"), make_case("TWO")
            rows = [
                {"split": "train", "case_path": self.save(root, a, "a")},
                {"split": "test", "case_path": self.save(root, b, "b")},
            ]
            completed = self.run_manifest(root, rows)
            self.assertEqual(completed.returncode, 2, completed.stderr)
            self.assertEqual(json.loads(completed.stdout)["decision"], "MANUAL_HISTORY_REFERENCE_REVIEW")

    def test_heldout_case_exposure_fails_without_identifiers(self):
        with tempfile.TemporaryDirectory() as root:
            a, b = make_case("ONE"), make_case("TWO")
            a["input"]["historical_cases"][0]["case_ref"] = b["case_id"]
            a["provenance"]["historical_case_refs"] = [b["case_id"]]
            a["expected_output"]["historical_experience_relevance"][0]["case_ref"] = b["case_id"]
            rows = [
                {"split": "train", "case_path": self.save(root, a, "a")},
                {"split": "test", "case_path": self.save(root, b, "b")},
            ]
            completed = self.run_manifest(root, rows)
            self.assertEqual(completed.returncode, 1)
            self.assertIn("CROSS_SPLIT_HISTORY_CASE_REFERENCE", completed.stderr)
            self.assertNotIn(b["case_id"], completed.stderr)
            self.assertNotIn(str(root), completed.stderr)

    def test_existing_output_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as root:
            path = self.save(root, make_case("ONE"), "one")
            output = Path(root) / "aggregate.json"
            output.write_text("SYNTHETIC ORIGINAL - PRESERVE", encoding="utf-8")
            completed = self.run_manifest(root, [{"split": "train", "case_path": path}], output)
            self.assertEqual(completed.returncode, 1)
            self.assertIn("LOCAL_WRITE_FAILED", completed.stderr)
            self.assertEqual(output.read_text(encoding="utf-8"), "SYNTHETIC ORIGINAL - PRESERVE")

    def test_duplicate_json_keys_are_rejected_without_echo(self):
        with tempfile.TemporaryDirectory() as root:
            manifest = Path(root) / "manifest.json"
            manifest.write_text('{"entries": [], "entries": ["SYNTH-ONLY"]}', encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "--manifest", str(manifest)],
                text=True, capture_output=True, cwd=ROOT, env=env, check=False,
            )
            self.assertEqual(completed.returncode, 1)
            self.assertIn("DUPLICATE_JSON_KEY", completed.stderr)
            self.assertNotIn(str(root), completed.stderr)


if __name__ == "__main__":
    unittest.main()
