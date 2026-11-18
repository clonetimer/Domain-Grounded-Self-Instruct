"""SYNTHETIC_TEST_ONLY: exercise the real portable ZIP builder end to end."""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]


class PortableToolkitPackageBuildTests(unittest.TestCase):
    def test_builder_is_byte_reproducible_when_clock_changes(self):
        # Control the external clock; execute the real CLI and compare its ZIPs.
        build_with_clock = textwrap.dedent("""\
            import runpy
            import sys
            import time
            from unittest.mock import patch

            script, output, year = sys.argv[1:]
            sys.argv = [script, "--output", output]
            clock = time.struct_time((int(year), 1, 2, 3, 4, 6, 0, 0, -1))
            with patch("zipfile.time.localtime", return_value=clock):
                runpy.run_path(script, run_name="__main__")
        """)
        with tempfile.TemporaryDirectory() as directory:
            packages = []
            for year in (2020, 2030):
                output = Path(directory) / f"toolkit-{year}.zip"
                result = subprocess.run(
                    [sys.executable, "-c", build_with_clock,
                     str(ROOT / "scripts/package_dgsi_simulation_to_sft.py"),
                     str(output), str(year)],
                    cwd=ROOT, capture_output=True, text=True, timeout=90,
                    check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr[:1000])
                packages.append(output.read_bytes())
                with zipfile.ZipFile(output) as archive:
                    self.assertTrue(all(
                        item.compress_type == zipfile.ZIP_DEFLATED
                        for item in archive.infolist()
                    ))
            self.assertEqual(packages[0], packages[1])

    def test_builder_uses_repository_version_from_external_working_directory(self):
        version = (ROOT / "skills/dgsi-simulation-to-sft/VERSION").read_text(
            encoding="utf-8"
        ).strip()
        with (tempfile.TemporaryDirectory() as directory,
              tempfile.TemporaryDirectory(dir=ROOT) as output_directory):
            caller = Path(directory) / "caller"
            caller.mkdir()
            for shadow_version in (False, True):
                with self.subTest(shadow_version=shadow_version):
                    if shadow_version:
                        shadow = caller / "skills/dgsi-simulation-to-sft/VERSION"
                        shadow.parent.mkdir(parents=True)
                        shadow.write_text("UNRELATED-CALLER-VERSION\n", encoding="utf-8")
                    output = Path(output_directory) / f"toolkit-{shadow_version}.zip"
                    # Relative outputs, like absolute ones, must work from elsewhere.
                    argument = os.path.relpath(output, ROOT) if shadow_version else str(output)
                    result = subprocess.run(
                        [sys.executable,
                         str(ROOT / "scripts/package_dgsi_simulation_to_sft.py"),
                         "--output", argument],
                        cwd=caller, capture_output=True, text=True, timeout=90,
                        check=False,
                    )
                    self.assertEqual(0, result.returncode, result.stderr[:1000])
                    with zipfile.ZipFile(output) as archive:
                        manifest = json.loads(archive.read("PACKAGE_SHA256_MANIFEST.json"))
                        self.assertEqual(version, manifest["version"])

    def test_workflow_writes_standard_sha256sums(self):
        workflow = (ROOT / ".github/workflows/package-p5c2.yml").read_text(
            encoding="utf-8"
        )
        # Execute the actual workflow Python block without a YAML dependency.
        match = re.search(r"(?m)^ +python - <<'PY'\n(.*?)^ +PY$", workflow, re.DOTALL)
        self.assertIsNotNone(match, "workflow package verification block is missing")
        code = textwrap.dedent(match.group(1))
        # Synthetic versions ensure workflow paths cannot silently pin a release.
        for version, host_newline in (("0.0.0-test.1", "\n"), ("0.0.0-test.2", "\r\n")):
            with self.subTest(version=version, host_newline=host_newline), tempfile.TemporaryDirectory() as directory:
                version_file = Path(directory) / "skills/dgsi-simulation-to-sft/VERSION"
                version_file.parent.mkdir(parents=True)
                version_file.write_text(version + "\n", encoding="utf-8")
                output = Path(directory) / "dist" / f"dgsi-simulation-to-sft-toolkit-{version}.zip"
                output.parent.mkdir()
                payload = b"SYNTHETIC_TEST_ONLY\n"
                manifest = {
                    "version": version,
                    "training_authorized": False,
                    "gold_authorized": False,
                    "sft_export_authorized": False,
                    "files": [{"path": "fixture.txt", "size_bytes": len(payload),
                               "sha256": hashlib.sha256(payload).hexdigest()}],
                }
                with zipfile.ZipFile(output, "w") as archive:
                    archive.writestr("fixture.txt", payload)
                    archive.writestr("PACKAGE_SHA256_MANIFEST.json", json.dumps(manifest))
                # Emulate LF/CRLF host defaults while retaining real file writes.
                code_with_host_newline = (
                    "import pathlib\nfrom functools import partialmethod\n"
                    "pathlib.Path.write_text = partialmethod(pathlib.Path.write_text, "
                    f"newline={host_newline!r})\n" + code
                )
                result = subprocess.run(
                    [sys.executable, "-c", code_with_host_newline], cwd=directory,
                    capture_output=True, text=True, timeout=30, check=False,
                )
                self.assertEqual(0, result.returncode, result.stderr[:1000])
                expected = f"{hashlib.sha256(output.read_bytes()).hexdigest()}  {output.name}\n"
                self.assertEqual(expected.encode("ascii"),
                                 (output.parent / "SHA256SUMS.txt").read_bytes())

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
                for required in (
                    "scripts/audit_l1_c2_current_expert_intake.py",
                    "tests/test_l1_c2_expert_intake.py",
                    "tests/test_l1_c2_expert_intake_cli.py",
                    "docs/P5C2_CURRENT_EXPERT_INTAKE_20261118.md",
                    "scripts/audit_l1_c2_current_rights_intake.py",
                    "scripts/audit_l1_c2_source_rights_intake.py",
                    "tests/test_l1_c2_current_rights_preflight.py",
                    "tests/test_l1_c2_rights_intake_audit.py",
                    "docs/P5C2_CURRENT_SOURCE_RIGHTS_PREFLIGHT_20261118.md",
                    "docs/P5C2_OFFLINE_SOURCE_RIGHTS_INTAKE_20261118.md",
                    "docs/P5C2_SOURCE_DOCUMENT_IDENTITY_GUARD_20261118.md",
                ):
                    self.assertIn(required, names)
                self.assertIn("docs/P5C2_COMPLETE_TWO_REVIEWER_KIT_2026-11-18.md", names)
                self.assertIn("docs/P5C2_SOURCE_RIGHTS_DEDUPLICATED_QUEUE_2026-11-18.md", names)
                self.assertIn("docs/P5C2_PACKAGE_DELIVERY_2026-11-18.md", names)
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
                        blank_queue = extracted_root / "rights-queue-blank.json"
                        blank_queue.write_bytes(kit.read("C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json"))
                        reviewer_forms = {}
                        for slot in ("A", "B"):
                            with zipfile.ZipFile(io.BytesIO(kit.read(f"reviewer_{slot}.zip"))) as reviewer_zip:
                                form_path = extracted_root / f"reviewer_{slot}_blank.json"
                                form_path.write_bytes(reviewer_zip.read(f"C2_reviewer_{slot}_BLANK.json"))
                                reviewer_forms[slot] = form_path
                    # The actual blank handoffs must round-trip through the
                    # extracted intake CLI without any invented expert scores.
                    expert_queue = extracted_root / "expert-intake-pending.json"
                    expert_smoke = subprocess.run(
                        [sys.executable,
                         str(extracted_root / "scripts/audit_l1_c2_current_expert_intake.py"),
                         "--reviewer-a", str(reviewer_forms["A"]),
                         "--reviewer-b", str(reviewer_forms["B"]),
                         "--current-collection",
                         str(ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"),
                         "--current-l0-facts",
                         str(ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"),
                         "--output-file", str(expert_queue)],
                        cwd=extracted_root, env=clean_env,
                        capture_output=True, text=True, timeout=90, check=False,
                    )
                    self.assertEqual(0, expert_smoke.returncode, expert_smoke.stdout[:1000] + expert_smoke.stderr[:1000])
                    expert_summary = json.loads(expert_smoke.stdout)
                    self.assertEqual(15, expert_summary["packet_count"])
                    self.assertEqual(30, expert_summary["incomplete_scorecard_count"])
                    self.assertEqual(0, expert_summary["complete_scorecard_count"])
                    self.assertEqual(0, expert_summary["paired_review_count"])
                    self.assertEqual(15, expert_summary["pending_completion_count"])
                    self.assertNotIn("task_queue", expert_summary)
                    expert_report = json.loads(expert_queue.read_text(encoding="utf-8"))
                    self.assertEqual(15, len(expert_report["task_queue"]))
                    self.assertIs(True, expert_report["current_public_source_snapshot_matched"])
                    self.assertIs(False, expert_report["training_authorized"])
                    self.assertEqual(0, expert_report["sft_records_emitted"])
                    # Exercise both shipped rights CLIs using the real kit's blank
                    # queue. A structural/current-source match grants no clearance.
                    for script_name, extra_args in (
                        ("audit_l1_c2_source_rights_intake.py", []),
                        ("audit_l1_c2_current_rights_intake.py", [
                            "--current-collection",
                            str(ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"),
                            "--current-l0-facts",
                            str(ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"),
                        ]),
                    ):
                        with self.subTest(rights_cli=script_name):
                            rights_smoke = subprocess.run(
                                [sys.executable, str(extracted_root / "scripts" / script_name),
                                 "--blank", str(blank_queue),
                                 "--submission", str(blank_queue), *extra_args],
                                cwd=extracted_root, env=clean_env,
                                capture_output=True, text=True, timeout=60, check=False,
                            )
                            self.assertEqual(0, rights_smoke.returncode, rights_smoke.stderr[:1000])
                            rights_report = json.loads(rights_smoke.stdout)
                            self.assertEqual(7, rights_report["distinct_source_document_count"])
                            self.assertEqual(0, rights_report["rights_cleared_document_count"])
                            self.assertEqual(0, rights_report["sft_records_emitted"])
                            for flag in ("source_rights_verified", "expert_review_complete",
                                         "gold_eligible", "official_splits_assigned", "training_authorized"):
                                self.assertIs(False, rights_report[flag])
                            if extra_args:
                                self.assertIs(True, rights_report["current_public_source_snapshot_matched"])
                for item in manifest["files"]:
                    content = archive.read(item["path"])
                    self.assertEqual(len(content), item["size_bytes"])
                    self.assertEqual(
                        hashlib.sha256(content).hexdigest(),
                        item["sha256"],
                    )


if __name__ == "__main__":
    unittest.main()
