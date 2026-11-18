"""SYNTHETIC_TEST_ONLY: real 15-task cohort, BLANK reviewer handoffs."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from xml.etree import ElementTree
from zipfile import ZipFile

from dgsi.l1_c2_expert_handoff import build_c2_expert_handoff
from dgsi.l1_coverage_review import REVIEW_DIMENSIONS

ROOT = Path(__file__).resolve().parents[1]
COLLECTION_PATH = ROOT / (
    "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
)
SOURCE_PATH = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
COLLECTION = json.loads(COLLECTION_PATH.read_text(encoding="utf-8"))
SOURCES = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))["cards"]
SCRIPT = ROOT / "scripts/create_l1_c2_expert_review_handoff.py"


class C2ExpertHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = build_c2_expert_handoff(COLLECTION, source_fact_cards=SOURCES, reviewer_slot="A")
        cls.b = build_c2_expert_handoff(COLLECTION, source_fact_cards=SOURCES, reviewer_slot="B")

    def test_real_cohort_is_bound_but_not_approved(self):
        a = self.a
        self.assertEqual(a["packet_count"], 15)
        self.assertEqual(a["event_family_count"], 9)
        self.assertEqual(len(a["tasks"]), 15)
        self.assertEqual(len({p["task_id"] for p in a["tasks"]}), 15)
        self.assertEqual(len(a["collection_projection_sha256"]), 64)
        # Frozen C2 cohort digest independently recomputed from the 15
        # packets and all current/historical L0 public-source bytes.
        self.assertEqual(
            a["collection_projection_sha256"],
            "2d752d898cb6ef8988f5d7829b040bf129f8bf29c154f976af428be26797f0c3",
        )
        self.assertFalse(a["training_authorized"])
        self.assertFalse(a["gold_eligible"])
        self.assertFalse(a["source_rights_verified"])
        self.assertEqual(a["expert_adjudicated_count"], 0)
        self.assertEqual(a["sft_records_emitted"], 0)
        for p in a["tasks"]:
            self.assertEqual(p["collection_projection_sha256"], a["collection_projection_sha256"])
            self.assertEqual(p["blinded_packet_ref"], "sha256:" + p["packet_sha256"])
            self.assertTrue(p["source_fact_bindings"])
            self.assertEqual(len(p["source_public_sha256"]), 64)

    def test_separate_unfilled_reviewers_and_ten_dimensions(self):
        self.assertEqual(self.a["reviewer_slot"], "A")
        self.assertEqual(self.b["reviewer_slot"], "B")
        for pa, pb in zip(self.a["tasks"], self.b["tasks"]):
            self.assertEqual(pa["packet_sha256"], pb["packet_sha256"])
            self.assertEqual(pa["source_public_sha256"], pb["source_public_sha256"])
            self.assertNotEqual(pa["reviewer_slot"], pb["reviewer_slot"])
            for p in (pa, pb):
                self.assertIsNone(p["scorecard"]["reviewer_token"])
                self.assertIsNone(p["scorecard"]["decision"])
                self.assertEqual(p["scorecard"]["finding_codes"], [])
                self.assertEqual(
                    set(p["scorecard"]["scores"]), set(REVIEW_DIMENSIONS)
                )
                self.assertTrue(all(s is None for s in p["scorecard"]["scores"].values()))

    def test_no_model_target_or_private_curator_content_in_forms(self):
        for form in (self.a, self.b):
            text = json.dumps(form, ensure_ascii=False)
            for forbidden in (
                '"formal_target"', '"internal_review"', '"diagnostic_logs"',
                '"machine_diagnosis"', '"follow_up_actions"', '"report_text"',
            ):
                self.assertNotIn(forbidden, text)
            self.assertNotIn("SYNTHETIC_TEST_ONLY_A", text)

    def test_l0_public_fact_change_invalidates_review_fingerprint(self):
        sources = copy.deepcopy(SOURCES)
        sources[0]["source_fact_testing_nonce"] = "SYNTHETIC_TEST_ONLY_change"
        # A new field may violate the domain fact-card schema. The builder
        # must either fail validation or derive a different public digest.
        try:
            altered = build_c2_expert_handoff(
                COLLECTION, source_fact_cards=sources, reviewer_slot="A"
            )
        except (ValueError, KeyError, TypeError):
            return
        self.assertNotEqual(
            self.a["collection_projection_sha256"],
            altered["collection_projection_sha256"],
        )

    def test_invalid_slot_rejected_without_form(self):
        with self.assertRaisesRegex(ValueError, "C2_HANDOFF_REVIEWER_SLOT_INVALID"):
            build_c2_expert_handoff(
                COLLECTION, source_fact_cards=SOURCES, reviewer_slot="UNVERIFIED"
            )

    def test_cli_word_json_are_separate_valid_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "expert_review_forms"
            cmd = [
                sys.executable, str(SCRIPT),
                "--collection", str(COLLECTION_PATH),
                "--source-facts", str(SOURCE_PATH),
                "--output-dir", str(out),
            ]
            first = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
            response = json.loads(first.stdout)
            self.assertEqual(response["files_created"], 4)
            self.assertFalse(response["training_authorized"])
            self.assertEqual(len(list(out.iterdir())), 4)
            for slot in ("A", "B"):
                form = json.loads(
                    (out / f"C2_reviewer_{slot}_BLANK.json").read_text(encoding="utf-8")
                )
                self.assertEqual(form["reviewer_slot"], slot)
                docx = out / f"C2_reviewer_{slot}_BLANK.docx"
                with ZipFile(docx) as archive:
                    self.assertIn("word/document.xml", archive.namelist())
                    self.assertIn("word/styles.xml", archive.namelist())
                    self.assertIn("word/_rels/document.xml.rels", archive.namelist())
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
                    styles = ElementTree.fromstring(archive.read("word/styles.xml"))
                    style_ids = {
                        element.get("{" + ns["w"] + "}styleId")
                        for element in styles.findall("w:style", ns)
                    }
                    self.assertTrue({"Normal", "Title", "Heading1"} <= style_ids)
                    self.assertIn(b'Noto Sans CJK SC', archive.read("word/styles.xml"))
                    self.assertIn(b'Target="styles.xml"', archive.read("word/_rels/document.xml.rels"))
                    self.assertIn(b'/word/styles.xml', archive.read("[Content_Types].xml"))
                    xml = archive.read("word/document.xml")
                    document = ElementTree.fromstring(xml)
                    self.assertEqual(len(document.findall(".//w:pageBreakBefore", ns)), form["packet_count"] - 1)
                    self.assertIn(b'w:val="Title"', xml)
                    self.assertIn(b"sha-256", xml.lower())
                    self.assertNotIn(b"formal_target", xml)
            before = (out / "C2_reviewer_A_BLANK.json").read_bytes()
            second = subprocess.run(cmd, capture_output=True, text=True, check=False)
            self.assertEqual(second.returncode, 2)
            self.assertEqual(json.loads(second.stdout)["error_code"], "OUTPUT_DIRECTORY_EXISTS")
            self.assertEqual(
                (out / "C2_reviewer_A_BLANK.json").read_bytes(), before
            )


if __name__ == "__main__":
    unittest.main()
