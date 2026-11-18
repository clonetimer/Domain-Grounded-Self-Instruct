"""SYNTHETIC_TEST_ONLY: frozen REV1 cohort handoff, not SFT."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import create_l1_c2_rev1_review_kit as current


class Rev1ReviewKitTests(unittest.TestCase):
    def test_real_current_candidate_produces_only_blank_21_task_handoff(self):
        data, manifest = current.build_rev1_review_kit()
        self.assertEqual(21, manifest["packet_count"])
        self.assertEqual(current.EXPECTED_PROJECTION_SHA256,
                         manifest["collection_projection_sha256"])
        self.assertIn("REV1", manifest["collection_id"])
        self.assertEqual(9, manifest["event_family_count"])
        self.assertEqual(7, manifest["source_rights_document_count"])
        self.assertEqual(12, manifest["source_rights_bound_l0_fact_count"])
        self.assertFalse(manifest["training_authorized"])
        self.assertFalse(manifest["source_rights_verified"])
        self.assertFalse(manifest["expert_review_complete"])
        self.assertEqual(0, manifest["sft_records_emitted"])
        with ZipFile(BytesIO(data)) as outer:
            names = outer.namelist()
            self.assertIn("reviewer_A.zip", names)
            self.assertIn("reviewer_B.zip", names)
            rights = json.loads(outer.read("C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json"))
            self.assertEqual(7, rights["distinct_source_document_count"])
            for slot in ("A", "B"):
                blob = outer.read(f"reviewer_{slot}.zip")
                self.assertEqual(sha256(blob).hexdigest(),
                                 manifest["reviewer_archives_sha256"][f"reviewer_{slot}.zip"])
                with ZipFile(BytesIO(blob)) as inner:
                    form = json.loads(inner.read(f"C2_reviewer_{slot}_BLANK.json"))
                    self.assertEqual(21, form["packet_count"])
                    self.assertEqual(21, len(form["tasks"]))
                    for task in form["tasks"]:
                        self.assertIsNone(task["scorecard"]["reviewer_token"])
                        self.assertIsNone(task["scorecard"]["decision"])
                        self.assertTrue(all(v is None for v in task["scorecard"]["scores"].values()))
                    dossier = json.loads(inner.read("C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json"))
                    self.assertEqual(21, dossier["packet_count"])
                    self.assertNotIn("internal_review", json.dumps(dossier))

    def test_old_21_cohort_is_rejected_not_silently_reused(self):
        old_path = ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json"
        older = json.loads(old_path.read_text(encoding="utf-8"))
        source = current._read_frozen_json("source_facts")
        with self.assertRaisesRegex(current.Rev1ReviewKitError,
                                    "^REV1_21_COHORT_GATE_BLOCKED$"):
            current.assert_pending_rev1_21(older, source)

    def test_task_015_structured_target_does_not_assert_hydrogen_poisoning(self):
        candidate = current._read_frozen_json("collection")
        task = next(p for p in candidate["packets"]
                    if p["task_id"] == "L1-SPACEBORNE-TWTA-LNA-HANDOVER-SYNTH-015")
        actual = task["formal_target"]["cause_localization"]["candidates"][0]["fault_mode"]
        mirrored = task["case"]["expected_output"]["cause_localization"]["candidates"][0]["fault_mode"]
        self.assertEqual("linearizer_LNA_gain_degradation_candidate", actual)
        self.assertEqual(actual, mirrored)
        self.assertNotEqual("linearizer_LNA_hydrogen_poisoning", actual)
        self.assertEqual("REVIEW_REQUIRED", task["review"]["status"])

    def test_fail_closed_for_stale_or_fake_training_permissions(self):
        collection = current._read_frozen_json("collection")
        source = current._read_frozen_json("source_facts")
        current.assert_pending_rev1_21(collection, source)
        for key, value in (("packet_count", 20), ("training_authorized", True),
                           ("gold_eligible", True), ("data_status", "APPROVED")):
            with self.subTest(key=key):
                changed = deepcopy(collection)
                changed[key] = value
                with self.assertRaises(current.Rev1ReviewKitError):
                    current.assert_pending_rev1_21(changed, source)
        changed = deepcopy(source)
        changed["cards"][0]["domain_review_status"] = "DOMAIN_EXPERT_CONFIRMED"
        with self.assertRaises(current.Rev1ReviewKitError):
            current.assert_pending_rev1_21(collection, changed)

    def test_stale_snapshot_digest_is_rejected_before_generation(self):
        with patch.dict(current._SNAPSHOTS, {
            "collection": (current._SNAPSHOTS["collection"][0], "0" * 40),
        }):
            with self.assertRaisesRegex(current.Rev1ReviewKitError,
                                        "^REV1_21_SOURCE_SNAPSHOT_CHANGED$"):
                current.build_rev1_review_kit()

    def test_cli_off_repo_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "C2_21_review_only.zip"
            args = [sys.executable, str(ROOT / "scripts/create_l1_c2_rev1_review_kit.py"),
                    "--output-file", str(output)]
            first = subprocess.run(args, cwd=ROOT, text=True, capture_output=True,
                                   check=False, timeout=120)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr[:500])
            self.assertEqual(21, json.loads(first.stdout)["packet_count"])
            digest = sha256(output.read_bytes()).hexdigest()
            second = subprocess.run(args, cwd=ROOT, text=True, capture_output=True,
                                    check=False, timeout=120)
            self.assertEqual(2, second.returncode)
            self.assertEqual("OUTPUT_EXISTS_NO_OVERWRITE",
                             json.loads(second.stdout)["error_code"])
            self.assertEqual(digest, sha256(output.read_bytes()).hexdigest())

    def test_cli_rejects_repository_output_without_publishing(self):
        candidate = ROOT / "C2_REV1_21_REVIEW_SHOULD_NOT_EXIST.zip"
        self.assertFalse(candidate.exists())
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/create_l1_c2_rev1_review_kit.py"),
             "--output-file", str(candidate)],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=20,
        )
        self.assertEqual(2, result.returncode)
        self.assertEqual("REV1_21_REVIEW_KIT_REJECTED",
                         json.loads(result.stdout)["error_code"])
        self.assertFalse(candidate.exists())


if __name__ == "__main__":
    unittest.main()
