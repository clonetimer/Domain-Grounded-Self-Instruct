from __future__ import annotations

import copy
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.diagram_provenance import DiagramProvenanceError, validate_diagram_asset_provenance


class DiagramProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.payload = b"synthetic diagram image bytes"
        digest = hashlib.sha256(self.payload).hexdigest()
        self.document = {
            "schema_version": "dgsi.document-ingestion.v1",
            "source_id": "SYNTHETIC_TEST_ONLY-SRC",
            "filename": "synthetic.docx",
            "media_type": "DOCX",
            "sha256": "a" * 64,
            "size_bytes": 123,
            "extraction_status": "PARTIAL_REVIEW_REQUIRED",
            "pages": [{"locator": "DOCX logical page 1", "blocks": []}],
            "assets": [{
                "asset_id": "SYNTHETIC_TEST_ONLY-IMG",
                "asset_type": "IMAGE",
                "locator": "DOCX paragraph 1; word/media/image1.png",
                "extraction_status": "EXTRACTED",
                "sha256": digest,
                "size_bytes": len(self.payload),
                "stored_path": "IMG0001.png",
            }],
            "warnings": [],
            "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
        }
        self.ocr = {
            "schema_version": "dgsi.ocr-candidates.v1",
            "asset_id": "SYNTHETIC_TEST_ONLY-IMG",
            "asset_sha256": digest,
            "image_width": 100,
            "image_height": 80,
            "ocr_engine": {"name": "Tesseract", "version": "5.4.0", "page_segmentation_mode": 6},
            "language": "eng",
            "lines": [{
                "line_id": "L00001",
                "text": "SYNTHETIC TEST",
                "confidence": 90.0,
                "bbox_px": {"left": 10, "top": 10, "width": 40, "height": 12},
                "words": [{
                    "text": "SYNTHETIC",
                    "confidence": 90.0,
                    "bbox_px": {"left": 10, "top": 10, "width": 25, "height": 12},
                }],
                "review_status": "MANUAL_REVIEW_REQUIRED",
            }],
            "warnings": ["SYNTHETIC_TEST_ONLY"],
            "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
        }

    def run_valid(self, document=None, ocr=None):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "image.png"
            path.write_bytes(self.payload)
            return validate_diagram_asset_provenance(
                document or self.document, ocr or self.ocr, path
            )

    def test_exact_document_asset_and_ocr_hashes_bind(self):
        result = self.run_valid()
        self.assertEqual(result["decision"], "PROVENANCE_CONSISTENT_REVIEW_REQUIRED")
        self.assertEqual(result["ocr_line_count"], 1)
        self.assertEqual(result["ocr_word_count"], 1)
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["gold_authorized"])
        self.assertNotIn("SYNTHETIC TEST", str(result))

    def test_ocr_asset_hash_mismatch_rejected(self):
        record = copy.deepcopy(self.ocr)
        record["asset_sha256"] = "c" * 64
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_ASSET_HASH_MISMATCH$"):
            self.run_valid(ocr=record)

    def test_manifest_asset_hash_mismatch_rejected(self):
        record = copy.deepcopy(self.document)
        record["assets"][0]["sha256"] = "d" * 64
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_ASSET_HASH_MISMATCH$"):
            self.run_valid(document=record)

    def test_non_extracted_reference_only_asset_rejected(self):
        record = copy.deepcopy(self.document)
        record["assets"][0]["extraction_status"] = "REFERENCE_ONLY"
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_ASSET_BYTES_NOT_EXTRACTED$"):
            self.run_valid(document=record)

    def test_duplicate_asset_id_in_source_rejected(self):
        record = copy.deepcopy(self.document)
        record["assets"].append(copy.deepcopy(record["assets"][0]))
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_ASSET_ID_NOT_UNIQUE_IN_SOURCE$"):
            self.run_valid(document=record)

    def test_out_of_bounds_line_box_rejected(self):
        record = copy.deepcopy(self.ocr)
        record["lines"][0]["bbox_px"]["left"] = 90
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_OCR_BOX_OUT_OF_BOUNDS$"):
            self.run_valid(ocr=record)

    def test_empty_word_box_rejected(self):
        record = copy.deepcopy(self.ocr)
        record["lines"][0]["words"][0]["bbox_px"]["width"] = 0
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_OCR_BOX_EMPTY$"):
            self.run_valid(ocr=record)

    def test_duplicate_line_ids_rejected(self):
        record = copy.deepcopy(self.ocr)
        record["lines"].append(copy.deepcopy(record["lines"][0]))
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_OCR_LINE_ID_DUPLICATE$"):
            self.run_valid(ocr=record)

    def test_asset_size_mismatch_rejected(self):
        record = copy.deepcopy(self.document)
        record["assets"][0]["size_bytes"] += 1
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_ASSET_SIZE_MISMATCH$"):
            self.run_valid(document=record)


    def test_empty_ocr_line_id_rejected(self):
        record = copy.deepcopy(self.ocr)
        record["lines"][0]["line_id"] = " "
        with self.assertRaisesRegex(DiagramProvenanceError, "^DIAGRAM_OCR_LINE_ID_EMPTY$"):
            self.run_valid(ocr=record)

    def test_ocr_word_boxes_must_fit_inside_parent_line(self):
        # Both boxes remain inside the overall image. The mismatch must
        # still be rejected rather than silently treated as valid OCR.
        for axis, value in (("left", 35), ("top", 15)):
            with self.subTest(axis=axis):
                record = copy.deepcopy(self.ocr)
                record["lines"][0]["words"][0]["bbox_px"][axis] = value
                with self.assertRaisesRegex(
                    DiagramProvenanceError, "^DIAGRAM_OCR_WORD_OUTSIDE_LINE$"
                ):
                    self.run_valid(ocr=record)


if __name__ == "__main__":
    unittest.main()
