"""SYNTHETIC_TEST_ONLY CLI privacy and filesystem tests."""
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_l1_c2_expert_intake import forms
from test_l1_c2_scored_review import COLLECTION, CARDS, ROOT


class ExpertIntakeCliTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder = Path(temp.name)
        self.args = [sys.executable, str(ROOT / "scripts/audit_l1_c2_current_expert_intake.py")]
        for flag, value in zip(("reviewer-a", "reviewer-b", "current-collection", "current-l0-facts"),
                               [*forms(), COLLECTION, {"cards": CARDS}]):
            path = self.folder / flag
            path.write_text(json.dumps(value), encoding="utf-8")
            self.args.extend(["--" + flag, str(path)])
        self.output = self.folder / "PRIVATE-output.json"
        self.args.extend(["--output-file", str(self.output)])

    def invoke(self):
        return subprocess.run(self.args, capture_output=True, text=True, timeout=45)

    def test_racing_writers_publish_only_one_complete_private_file(self):
        with concurrent.futures.ThreadPoolExecutor(2) as pool:
            results = list(pool.map(lambda _: self.invoke(), range(2)))
        self.assertEqual(sorted(r.returncode for r in results), [0, 2])
        for result in results:
            self.assertEqual(result.stderr, "")
            self.assertNotIn("task_queue", result.stdout)
            self.assertNotIn("PRIVATE", result.stdout)
        winner = next(r for r in results if r.returncode == 0)
        private = json.loads(self.output.read_text(encoding="utf-8"))
        self.assertEqual(len(private.pop("task_queue")), 15)
        self.assertEqual(json.loads(winner.stdout), private)
        self.assertEqual(len(list(self.folder.iterdir())), 5)

    def test_missing_output_parent_is_never_created(self):
        missing_dir = self.folder / "PRIVATE-missing"
        self.args[-1] = str(missing_dir / "report.json")
        result = self.invoke()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["decision"], "REJECTED")
        self.assertEqual(result.stderr, "")
        self.assertNotIn("PRIVATE", result.stdout)
        self.assertFalse(missing_dir.exists())

    def test_existing_output_and_symlink_preserved(self):
        self.output.write_text("PRIVATE", encoding="utf-8")
        result = self.invoke()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["error_code"], "C2_EXPERT_OUTPUT_ALREADY_EXISTS")
        self.assertEqual(self.output.read_text(encoding="utf-8"), "PRIVATE")
        self.output.unlink()
        target = self.folder / "PRIVATE-target"
        try:
            self.output.symlink_to(target)
        except OSError:
            self.skipTest("Symlinks unavailable")
        self.assertEqual(self.invoke().returncode, 2)
        self.assertTrue(self.output.is_symlink())
        self.assertFalse(target.exists())

    def test_invalid_duplicate_and_missing_inputs_have_only_fixed_errors(self):
        path = self.folder / "reviewer-a"
        original = path.read_text(encoding="utf-8")
        duplicate = '{"notice":"PRIVATE",' + original[1:]
        for content in ("[PRIVATE", duplicate, None):
            if content is None:
                path.unlink()
            else:
                path.write_text(content, encoding="utf-8")
            result = self.invoke()
            self.assertEqual(result.returncode, 2)
            self.assertEqual(result.stderr, "")
            self.assertEqual(json.loads(result.stdout)["decision"], "REJECTED")
            self.assertNotIn("PRIVATE", result.stdout)
            self.assertFalse(self.output.exists())
