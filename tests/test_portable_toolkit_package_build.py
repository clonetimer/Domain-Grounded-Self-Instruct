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
                # Collection validation in the extracted toolkit requires this schema.
                self.assertIn("resources/l1_task_packet_collection.schema.json", names)
                self.assertIn(
                    "scripts/create_l1_model_preview.py",
                    names,
                )
                self.assertIn(
                    "tests/test_l1_model_projection_preview.py",
                    names,
                )
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
                skill_text = archive.read("skills/dgsi-simulation-to-sft/SKILL.md").decode("utf-8")
                self.assertIn("P5-C2 integrated production workflow", skill_text)
                self.assertIn("co-equal deliverables", skill_text)
                manifest_contract = json.loads(
                    archive.read("skills/dgsi-simulation-to-sft/TOOLKIT_MANIFEST.json")
                )
                version = (ROOT / "skills/dgsi-simulation-to-sft/VERSION").read_text(encoding="utf-8").strip()
                self.assertEqual(version, manifest_contract["version"])
                self.assertEqual(manifest_contract["version"], "0.2.0-rc.1")
                self.assertTrue(manifest_contract["dataset_and_skill_are_coequal_deliverables"])
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
                skill_manifest = json.loads(
                    (ROOT / "skills/dgsi-simulation-to-sft/TOOLKIT_MANIFEST.json").read_text(encoding="utf-8")
                )
                version = (ROOT / "skills/dgsi-simulation-to-sft/VERSION").read_text(encoding="utf-8").strip()
                self.assertEqual(version, skill_manifest["version"])
                self.assertEqual(version, manifest["version"])
                self.assertEqual(version, manifest_contract["version"])
                for flag in (
                    "training_authorized",
                    "gold_authorized",
                    "sft_export_authorized",
                ):
                    self.assertIs(False, manifest[flag])
                # Verify the extracted preview CLI starts in a clean environment
                # without repository checkout or PYTHONPATH.
                with tempfile.TemporaryDirectory() as extracted_dir:
                    archive.extractall(extracted_dir)
                    extracted_root = Path(extracted_dir)
                    clean_env = {k: v for k, v in __import__("os").environ.items() if k != "PYTHONPATH"}
                    help_result = subprocess.run(
                        [sys.executable, str(extracted_root / "scripts/create_l1_model_preview.py"), "--help"],
                        cwd=extracted_root, env=clean_env, capture_output=True, text=True, timeout=30, check=False,
                    )
                    self.assertEqual(0, help_result.returncode, help_result.stderr[:500])
                    self.assertIn("--collection", help_result.stdout)
                    # Run a real 15-packet preview from the extracted toolkit,
                    # while keeping the candidate dataset external to the ZIP.
                    preview_output = extracted_root / "preview-output.json"
                    smoke = subprocess.run(
                        [
                            sys.executable,
                            str(extracted_root / "scripts/create_l1_model_preview.py"),
                            "--collection",
                            str(ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"),
                            "--source-facts",
                            str(ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"),
                            "--output",
                            str(preview_output),
                        ],
                        cwd=extracted_root,
                        env=clean_env,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )
                    self.assertEqual(0, smoke.returncode, smoke.stderr[:1000])
                    preview_result = json.loads(preview_output.read_text(encoding="utf-8"))
                    self.assertEqual(15, preview_result["packet_count"])
                    self.assertEqual(9, preview_result["event_family_count"])
                    self.assertEqual(0, preview_result["sft_records_emitted"])
                    self.assertFalse(preview_result["training_authorized"])
                for item in manifest["files"]:
                    content = archive.read(item["path"])
                    self.assertEqual(len(content), item["size_bytes"])
                    self.assertEqual(
                        hashlib.sha256(content).hexdigest(),
                        item["sha256"],
                    )


if __name__ == "__main__":
    unittest.main()
