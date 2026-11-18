"""SYNTHETIC_TEST_ONLY: C2 review ZIPs are complete, separate, immutable."""
from __future__ import annotations

from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from create_l1_c2_complete_review_kit import build_review_kit

COLLECTION_PATH = ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
SOURCE_PATH = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
SCRIPT = ROOT / "scripts/create_l1_c2_complete_review_kit.py"
COLLECTION = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
CARDS = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))["cards"]


def _command(output: Path) -> list[str]:
    return [
        sys.executable, str(SCRIPT),
        "--collection", str(COLLECTION_PATH),
        "--source-facts", str(SOURCE_PATH),
        "--output-file", str(output),
    ]


class C2CompleteReviewKitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.archive, cls.manifest = build_review_kit(COLLECTION, CARDS)

    def test_full_15_task_nine_family_cohort_is_not_authorized(self):
        manifest = self.manifest
        self.assertEqual(manifest["packet_count"], 15)
        self.assertEqual(manifest["event_family_count"], 9)
        self.assertEqual(
            manifest["collection_projection_sha256"],
            "2d752d898cb6ef8988f5d7829b040bf129f8bf29c154f976af428be26797f0c3",
        )
        self.assertEqual(manifest["reviewer_forms"], "BLANK_UNAUTHENTICATED")
        self.assertTrue(manifest["not_for_sft"])
        self.assertFalse(manifest["gold_eligible"])
        self.assertFalse(manifest["source_rights_verified"])
        self.assertFalse(manifest["training_authorized"])
        self.assertEqual(manifest["sft_records_emitted"], 0)

    def test_separate_reviewer_archives_have_full_dossier_and_empty_scorecards(self):
        with ZipFile(BytesIO(self.archive)) as outer:
            self.assertEqual(set(outer.namelist()), {
                "reviewer_A.zip", "reviewer_B.zip",
                "COORDINATOR_REVIEW_ONLY_MANIFEST.json",
                "C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json",
                "README_REVIEW_ONLY.txt", "SHA256SUMS.txt",
            })
            coordinator = json.loads(outer.read("COORDINATOR_REVIEW_ONLY_MANIFEST.json"))
            self.assertEqual(coordinator, self.manifest)
            rights = json.loads(outer.read("C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json"))
            self.assertEqual(rights["distinct_source_document_count"], 7)
            self.assertEqual(rights["bound_l0_fact_count"], 12)
            self.assertEqual(rights["task_count"], 15)
            self.assertFalse(rights["source_rights_verified"])
            self.assertFalse(rights["training_authorized"])
            self.assertEqual(rights["collection_projection_sha256"],
                             coordinator["collection_projection_sha256"])
            self.assertEqual(
                sha256(outer.read("C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json")).hexdigest(),
                coordinator["source_rights_queue_sha256"],
            )
            self.assertEqual(coordinator["source_rights_document_count"], 7)
            self.assertEqual(coordinator["source_rights_bound_l0_fact_count"], 12)
            dossiers = []
            forms = []
            for slot in ("A", "B"):
                name = f"reviewer_{slot}.zip"
                content = outer.read(name)
                self.assertEqual(sha256(content).hexdigest(),
                                 coordinator["reviewer_archives_sha256"][name])
                with ZipFile(BytesIO(content)) as inner:
                    self.assertEqual(len(inner.namelist()), 5)
                    form = json.loads(inner.read(f"C2_reviewer_{slot}_BLANK.json"))
                    dossier = json.loads(inner.read("C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.json"))
                    html = inner.read("C2_SYNTHETIC_SCIENTIFIC_REVIEW_ONLY.html").decode("utf-8")
                    docx = inner.read(f"C2_reviewer_{slot}_BLANK.docx")
                    self.assertEqual(form["reviewer_slot"], slot)
                    self.assertEqual(len(form["tasks"]), 15)
                    self.assertEqual(len(dossier["items"]), 15)
                    self.assertEqual(
                        sum(dossier["l0_domain_review_status_counts"].values()),
                        dossier["l0_bound_fact_card_count"],
                    )
                    self.assertIn("SYNTHETIC", html)
                    self.assertIn("L0 领域审核状态", html)
                    self.assertNotIn("<script", html)
                    self.assertTrue(docx.startswith(b"PK"))
                    self.assertNotIn('"internal_review"', json.dumps(dossier))
                    self.assertTrue(dossier["not_for_sft"])
                    for task in form["tasks"]:
                        self.assertIsNone(task["scorecard"]["reviewer_token"])
                        self.assertIsNone(task["scorecard"]["decision"])
                        self.assertTrue(all(value is None for value in
                                            task["scorecard"]["scores"].values()))
                    forms.append(form)
                    dossiers.append(dossier)
            self.assertEqual(dossiers[0], dossiers[1])
            self.assertEqual(forms[0]["collection_projection_sha256"],
                             forms[1]["collection_projection_sha256"])
            self.assertEqual(forms[0]["collection_projection_sha256"],
                             dossiers[0]["collection_projection_sha256"])

    def test_deterministic_unchanged_inputs(self):
        another, manifest = build_review_kit(COLLECTION, CARDS)
        self.assertEqual(sha256(another).hexdigest(), sha256(self.archive).hexdigest())
        self.assertEqual(manifest, self.manifest)

    def test_cli_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "complete-review.zip"
            first = subprocess.run(_command(destination), capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            original = destination.read_bytes()
            self.assertEqual(original, self.archive)
            again = subprocess.run(_command(destination), capture_output=True, text=True)
            self.assertEqual(again.returncode, 2, again.stdout + again.stderr)
            self.assertEqual(json.loads(again.stdout)["error_code"],
                             "OUTPUT_EXISTS_NO_OVERWRITE")
            self.assertEqual(destination.read_bytes(), original)

    def test_cli_dangling_symlink_cannot_be_used_as_destination(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "linked.zip"
            victim = Path(td) / "uncreated-victim.zip"
            os.symlink(victim, destination)
            result = subprocess.run(_command(destination), capture_output=True, text=True)
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertTrue(destination.is_symlink())
            self.assertFalse(victim.exists())

    def test_two_concurrent_cli_writers_publish_exactly_one(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "concurrent.zip"
            p1 = subprocess.Popen(_command(destination), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
            p2 = subprocess.Popen(_command(destination), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
            out1, err1 = p1.communicate(timeout=60)
            out2, err2 = p2.communicate(timeout=60)
            self.assertEqual(sorted([p1.returncode, p2.returncode]), [0, 2],
                             out1 + err1 + out2 + err2)
            self.assertEqual(destination.read_bytes(), self.archive)

    def test_invalid_input_never_creates_output(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "rejected.zip"
            bogus = Path(td) / "bogus.json"
            bogus.write_text('{"cards": []}', encoding="utf-8")
            cmd = _command(destination)
            cmd[cmd.index(str(SOURCE_PATH))] = str(bogus)
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(destination.exists())
            self.assertEqual(json.loads(result.stdout)["sft_records_emitted"], 0)


if __name__ == "__main__":
    unittest.main()
