"""SYNTHETIC_TEST_ONLY adversarial checks for P5-B4.2 text-region proposals."""
from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dgsi.diagram_text_regions import DiagramTextRegionError, propose_diagram_text_regions


class DiagramTextRegionTests(unittest.TestCase):
    def setUp(self):
        self.data = b"SYNTHETIC_TEST_ONLY image bytes"
        digest = hashlib.sha256(self.data).hexdigest()
        self.doc = {
            "schema_version": "dgsi.document-ingestion.v1",
            "source_id": "SYNTHETIC_TEST_ONLY-SRC",
            "filename": "synthetic.docx",
            "media_type": "DOCX",
            "sha256": "a" * 64,
            "size_bytes": 100,
            "extraction_status": "PARTIAL_REVIEW_REQUIRED",
            "pages": [{"locator": "DOCX paragraph 1", "blocks": []}],
            "assets": [{
                "asset_id": "IMG0001", "asset_type": "IMAGE",
                "locator": "DOCX paragraph 1",
                "extraction_status": "EXTRACTED",
                "sha256": digest, "size_bytes": len(self.data),
            }],
            "warnings": [],
            "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
        }
        self.ocr = {
            "schema_version": "dgsi.ocr-candidates.v1",
            "asset_id": "IMG0001",
            "asset_sha256": digest,
            "image_width": 200,
            "image_height": 120,
            "ocr_engine": {
                "name": "Tesseract", "version": "5.x", "page_segmentation_mode": 6,
            },
            "language": "eng",
            "lines": [
                self._line("L2", "Unverified OCR label B", 20, 70),
                self._line("L1", "Unverified OCR label A", 10, 10),
            ],
            "warnings": ["SYNTHETIC_TEST_ONLY"],
            "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
        }

    @staticmethod
    def _line(line_id, text, left, top):
        return {
            "line_id": line_id,
            "text": text,
            "confidence": 88,
            "bbox_px": {"left": left, "top": top, "width": 120, "height": 15},
            "words": [],
            "review_status": "MANUAL_REVIEW_REQUIRED",
        }

    def propose(self, doc=None, ocr=None):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "synthetic.png"
            path.write_bytes(self.data)
            return propose_diagram_text_regions(
                self.doc if doc is None else doc,
                self.ocr if ocr is None else ocr,
                path,
            )

    def test_candidates_are_exact_unresolved_ocr_text_only(self):
        result = self.propose()
        self.assertEqual(result["schema_version"], "dgsi.diagram-text-regions.v1")
        self.assertEqual(result["generation_recipe"], "isolated-ocr-line-v1")
        self.assertEqual(len(result["candidates"]), 2)
        self.assertEqual(
            [r["label_text"] for r in result["candidates"]],
            ["Unverified OCR label A", "Unverified OCR label B"],
        )
        self.assertEqual(
            result["candidates"][0]["evidence_locators"],
            [f"asset:IMG0001@sha256:{self.ocr['asset_sha256']}#ocr-line:L1#bbox-px:10,10,120,15"],
        )
        self.assertTrue(result["not_for_sft"])
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["gold_authorized"])
        self.assertEqual(result["candidates"][0]["object_type"], "UNKNOWN")
        self.assertEqual(result["candidates"][0]["interpretation"], "UNRESOLVED_OCR_TEXT")
        for forbidden in ("ports", "edges", "hierarchy", "fault_root", "disposal_measures"):
            self.assertNotIn(forbidden, str(result.keys()))

    def test_reordering_ocr_lines_keeps_candidate_ids_and_order(self):
        before = self.propose()
        changed = copy.deepcopy(self.ocr)
        changed["lines"].reverse()
        after = self.propose(ocr=changed)
        self.assertEqual(before["candidates"], after["candidates"])
        self.assertNotEqual(before["ocr_record_sha256"], after["ocr_record_sha256"])

    def test_changed_ocr_text_changes_candidate_identity(self):
        before = self.propose()
        changed = copy.deepcopy(self.ocr)
        changed["lines"][0]["text"] += " corrected"
        after = self.propose(ocr=changed)
        self.assertNotEqual(before["candidates"][1]["candidate_id"],
                            after["candidates"][1]["candidate_id"])

    def test_blank_ocr_line_text_is_not_silently_promoted(self):
        changed = copy.deepcopy(self.ocr)
        changed["lines"][0]["text"] = " \t"
        with self.assertRaisesRegex(
            DiagramTextRegionError, "^DIAGRAM_OCR_LINE_TEXT_EMPTY$"
        ):
            self.propose(ocr=changed)

    def test_unsafe_line_id_cannot_inject_locator_fragments(self):
        changed = copy.deepcopy(self.ocr)
        changed["lines"][0]["line_id"] = "L2#bbox-px:0,0,1,1"
        with self.assertRaisesRegex(
            DiagramTextRegionError, "^DIAGRAM_OCR_LINE_ID_UNSAFE_FOR_LOCATOR$"
        ):
            self.propose(ocr=changed)

    def test_unsafe_asset_id_cannot_inject_locator_fragments(self):
        doc = copy.deepcopy(self.doc)
        ocr = copy.deepcopy(self.ocr)
        doc["assets"][0]["asset_id"] = "IMG#other"
        ocr["asset_id"] = "IMG#other"
        with self.assertRaisesRegex(
            DiagramTextRegionError, "^DIAGRAM_ASSET_ID_UNSAFE_FOR_LOCATOR$"
        ):
            self.propose(doc=doc, ocr=ocr)

    def test_blocked_source_is_rejected_prior_to_label_proposal(self):
        doc = copy.deepcopy(self.doc)
        doc["extraction_status"] = "BLOCKED"
        with self.assertRaisesRegex(
            DiagramTextRegionError, "^DIAGRAM_DOCUMENT_EXTRACTION_BLOCKED$"
        ):
            self.propose(doc=doc)

    def test_no_ocr_text_remains_unreviewed_empty_candidates(self):
        ocr = copy.deepcopy(self.ocr)
        ocr["lines"] = []
        result = self.propose(ocr=ocr)
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["review_status"], "REVIEW_REQUIRED")
        self.assertFalse(result["training_authorized"])

    def test_ocr_geometry_failure_is_inherited_from_provenance_gate(self):
        ocr = copy.deepcopy(self.ocr)
        ocr["lines"][0]["bbox_px"]["width"] = 300
        with self.assertRaisesRegex(
            DiagramTextRegionError, "^DIAGRAM_OCR_BOX_OUT_OF_BOUNDS$"
        ):
            self.propose(ocr=ocr)

    def test_aligned_adjacent_lines_emit_additional_unresolved_pair_hypothesis(self):
        ocr = copy.deepcopy(self.ocr)
        ocr["lines"] = [
            self._line("L1", "Reaction", 20, 20),
            self._line("L2", "Wheel", 25, 40),
        ]
        result = self.propose(ocr=ocr)
        singles = [c for c in result["candidates"] if c["candidate_type"] == "SINGLE_LINE"]
        groups = [c for c in result["candidates"] if c["candidate_type"] == "MULTI_LINE_HYPOTHESIS"]
        self.assertEqual(len(singles), 2)
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["label_text"], "Reaction\\nWheel")
        self.assertEqual(groups[0]["ocr_line_ids"], ["L1", "L2"])
        self.assertEqual(groups[0]["object_type"], "UNKNOWN")
        self.assertEqual(groups[0]["interpretation"], "UNRESOLVED_OCR_TEXT")
        self.assertEqual(groups[0]["review_status"], "MANUAL_REVIEW_REQUIRED")
        self.assertIn("#ocr-lines:L1,L2#", groups[0]["evidence_locators"][0])
        self.assertTrue(result["not_for_sft"])
        self.assertFalse(result["training_authorized"])

    def test_distant_lines_do_not_create_pair_hypothesis(self):
        result = self.propose()
        self.assertFalse(any(
            c["candidate_type"] == "MULTI_LINE_HYPOTHESIS"
            for c in result["candidates"]
        ))

    def test_pair_hypothesis_is_order_independent(self):
        ocr = copy.deepcopy(self.ocr)
        ocr["lines"] = [
            self._line("L1", "Reaction", 20, 20),
            self._line("L2", "Wheel", 25, 40),
        ]
        first = self.propose(ocr=ocr)
        ocr["lines"].reverse()
        second = self.propose(ocr=ocr)
        self.assertEqual(first["candidates"], second["candidates"])
        self.assertNotEqual(first["ocr_record_sha256"], second["ocr_record_sha256"])

    def test_overlapping_lines_do_not_create_vertical_pair(self):
        ocr = copy.deepcopy(self.ocr)
        ocr["lines"] = [
            self._line("L1", "Left", 10, 20),
            self._line("L2", "Right", 30, 25),
        ]
        result = self.propose(ocr=ocr)
        self.assertFalse(any(
            c["candidate_type"] == "MULTI_LINE_HYPOTHESIS"
            for c in result["candidates"]
        ))


if __name__ == "__main__":
    unittest.main()
