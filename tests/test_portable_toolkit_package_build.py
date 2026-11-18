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
                # The extracted projection validator loads this collection schema
                # from resources/ at runtime; file presence alone is not enough,
                # so the clean-room preview smoke below exercises the import path.
                self.assertIn("resources/l1_task_packet_collection.schema.json", names)
                self.assertIn(
                    "scripts/create_l1_model_preview.py",
                    names,
                )
                self.assertIn(
                    "tests/test_l1_model_projection_preview.py",
                    names,
                )
                self.assertIn("scripts/create_l1_blind_review_manifest.py", names)
                self.assertIn("tests/test_l1_blind_review_manifest.py", names)
                self.assertIn("tests/test_l1_blind_review_manifest_cli.py", names)
                self.assertIn("scripts/create_l1_c2_complete_review_kit.py", names)
                self.assertIn("scripts/create_l1_c2_expert_review_handoff.py", names)
                self.assertIn("scripts/create_l1_c2_scientific_dossier.py", names)
                self.assertIn("tests/test_l1_c2_complete_review_kit.py", names)
                self.assertIn("tests/test_l1_c2_source_rights_queue.py", names)
                self.assertIn("tests/test_l1_model_preview_cli_no_clobber.py", names)
                self.assertIn("docs/P5C2_COMPLETE_TWO_REVIEWER_KIT_2026-11-18.md", names)
                self.assertIn("docs/P5C2_SOURCE_RIGHTS_DEDUPLICATED_QUEUE_2026-11-18.md", names)
                self.assertIn(
                    "skills/dgsi-simulation-to-sft/references/BLIND_EXPERT_REVIEW.md",
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
                    review_help = subprocess.run(
                        [sys.executable, str(extracted_root / "scripts/create_l1_blind_review_manifest.py"), "--help"],
                        cwd=extracted_root, env=clean_env, capture_output=True, text=True, timeout=30, check=False,
                    )
                    self.assertEqual(0, review_help.returncode, review_help.stderr[:500])
                    self.assertIn("--source-facts", review_help.stdout)
                    kit_help = subprocess.run(
                        [sys.executable, str(extracted_root / "scripts/create_l1_c2_complete_review_kit.py"), "--help"],
                        cwd=extracted_root, env=clean_env, capture_output=True, text=True, timeout=30, check=False,
                    )
                    self.assertEqual(0, kit_help.returncode, kit_help.stderr[:500])
                    self.assertIn("--output-file", kit_help.stdout)
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
                    self.assertEqual(0, smoke.returncode, f"stdout={smoke.stdout[:1000]!r}; stderr={smoke.stderr[:1000]!r}")
                    preview_result = json.loads(preview_output.read_text(encoding="utf-8"))
                    self.assertEqual(15, preview_result["packet_count"])
                    self.assertEqual(9, preview_result["event_family_count"])
                    self.assertEqual(0, preview_result["sft_records_emitted"])
                    self.assertFalse(preview_result["training_authorized"])
                    review_output = extracted_root / "blind-review-manifest.json"
                    review_smoke = subprocess.run(
                        [
                            sys.executable,
                            str(extracted_root / "scripts/create_l1_blind_review_manifest.py"),
                            "--collection",
                            str(ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"),
                            "--source-facts",
                            str(ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"),
                            "--output",
                            str(review_output),
                        ],
                        cwd=extracted_root,
                        env=clean_env,
                        capture_output=True,
                        text=True,
                        timeout=60,
                        check=False,
                    )
                    self.assertEqual(0, review_smoke.returncode, f"stdout={review_smoke.stdout[:1000]!r}; stderr={review_smoke.stderr[:1000]!r}")
                    review_result = json.loads(review_output.read_text(encoding="utf-8"))
                    self.assertEqual(15, review_result["packet_count"])
                    self.assertEqual(9, review_result["event_family_count"])
                    self.assertEqual(15, len(review_result["review_packets"]))
                    self.assertEqual(0, review_result["sft_records_emitted"])
                    self.assertFalse(review_result["training_authorized"])
                    self.assertFalse(review_result["gold_eligible"])
                    self.assertTrue(all(row["collection_projection_sha256"] == review_result["collection_projection_sha256"] for row in review_result["review_packets"]))
                    kit_output = extracted_root / "c2-two-reviewer-kit.zip"
                    kit_smoke = subprocess.run(
                        [
                            sys.executable,
                            str(extracted_root / "scripts/create_l1_c2_complete_review_kit.py"),
                            "--collection",
                            str(ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"),
                            "--source-facts",
                            str(ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"),
                            "--output-file",
                            str(kit_output),
                        ],
                        cwd=extracted_root,
                        env=clean_env,
                        capture_output=True,
                        text=True,
                        timeout=90,
                        check=False,
                    )
                    self.assertEqual(0, kit_smoke.returncode, f"stdout={kit_smoke.stdout[:1000]!r}; stderr={kit_smoke.stderr[:1000]!r}")
                    self.assertTrue(kit_output.is_file())
                    with zipfile.ZipFile(kit_output) as kit:
                        kit_names = kit.namelist()
                        self.assertIn("reviewer_A.zip", kit_names)
                        self.assertIn("reviewer_B.zip", kit_names)
                        self.assertIn("C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json", kit_names)
                        kit_manifest = json.loads(kit.read("COORDINATOR_REVIEW_ONLY_MANIFEST.json"))
                        self.assertEqual(15, kit_manifest["packet_count"])
                        self.assertEqual(9, kit_manifest["event_family_count"])
                        self.assertFalse(kit_manifest["source_rights_verified"])
                        self.assertFalse(kit_manifest["expert_review_complete"])
                        self.assertFalse(kit_manifest["training_authorized"])
                        self.assertEqual(0, kit_manifest["sft_records_emitted"])
                for item in manifest["files"]:
                    content = archive.read(item["path"])
                    self.assertEqual(len(content), item["size_bytes"])
                    self.assertEqual(
                        hashlib.sha256(content).hexdigest(),
                        item["sha256"],
                    )


if __name__ == "__main__":
    unittest.main()
