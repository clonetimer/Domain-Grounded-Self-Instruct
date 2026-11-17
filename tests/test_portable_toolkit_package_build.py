"""SYNTHETIC_TEST_ONLY: exercise the real portable ZIP builder end to end."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class PortableToolkitPackageBuildTests(unittest.TestCase):
    def test_builder_emits_verified_source_only_archive(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "toolkit.zip"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "package_dgsi_simulation_to_sft.py"),
                    "--output",
                    str(output),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                timeout=90,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr[:500])
            self.assertTrue(output.is_file())
            self.assertIn("TRAINING_AUTHORIZED=false", result.stdout)
            with zipfile.ZipFile(output, "r") as archive:
                names = archive.namelist()
                self.assertEqual(len(names), len(set(names)))
                self.assertIn("PACKAGE_SHA256_MANIFEST.json", names)
                self.assertIn(
                    "src/dgsi/design_derived_intake.py",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/schemas/design_derived_batch.schema.json",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/references/P5C2_INTEGRATED_DATASET_PRODUCTION.md",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/references/OPERATOR_QUICKSTART.md",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/SKILL.md",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/references/P5C2_INTEGRATED_DATASET_PRODUCTION.md",
                    names,
                )
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/references/OPERATOR_QUICKSTART.md",
                    names,
                )
                self.assertFalse(
                    any(
                        name.startswith("examples/")
                        or name.endswith(".docx")
                        or name.endswith(".pdf")
                        or "hidden_truth" in name.lower()
                        for name in names
                    )
                )
                manifest = json.loads(
                    archive.read("PACKAGE_SHA256_MANIFEST.json").decode("utf-8")
                )
                for flag in (
                    "training_authorized",
                    "gold_authorized",
                    "sft_export_authorized",
                ):
                    self.assertIs(False, manifest[flag])
                for item in manifest["files"]:
                    content = archive.read(item["path"])
                    self.assertEqual(len(content), item["size_bytes"])
                    self.assertEqual(
                        hashlib.sha256(content).hexdigest(),
                        item["sha256"],
                    )


if __name__ == "__main__":
    unittest.main()
