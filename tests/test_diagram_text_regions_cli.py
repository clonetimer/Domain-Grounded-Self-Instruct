from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "propose_diagram_text_regions.py"


class DiagramTextRegionsCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.asset = self.root / "image.png"
        self.asset.write_bytes(b"SYNTHETIC_TEST_ONLY image bytes")
        digest = hashlib.sha256(self.asset.read_bytes()).hexdigest()
        self.document = {
            "schema_version": "dgsi.document-ingestion.v1",
            "source_id": "SYNTHETIC_TEST_ONLY-SRC",
            "filename": "synthetic.docx",
            "media_type": "DOCX",
            "sha256": "a" * 64,
            "size_bytes": 100,
            "extraction_status": "PARTIAL_REVIEW_REQUIRED",
            "pages": [{"locator": "page 1", "blocks": []}],
            "assets": [{
                "asset_id": "IMG0001", "asset_type": "IMAGE",
                "locator": "page 1 figure 1", "extraction_status": "EXTRACTED",
                "sha256": digest, "size_bytes": self.asset.stat().st_size,
            }],
            "warnings": [], "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
        }
        self.ocr = {
            "schema_version": "dgsi.ocr-candidates.v1",
            "asset_id": "IMG0001", "asset_sha256": digest,
            "image_width": 100, "image_height": 80,
            "ocr_engine": {"name": "Tesseract", "version": "5.x", "page_segmentation_mode": 6},
            "language": "eng",
            "lines": [{
                "line_id": "L00001", "text": "SYNTHETIC_TEST_ONLY OCR label",
                "confidence": 90,
                "bbox_px": {"left": 10, "top": 10, "width": 40, "height": 12},
                "words": [], "review_status": "MANUAL_REVIEW_REQUIRED",
            }],
            "warnings": ["SYNTHETIC_TEST_ONLY"],
            "review_status": "REVIEW_REQUIRED", "training_authorized": False,
        }
        self.document_path = self.root / "manifest.json"
        self.ocr_path = self.root / "ocr.json"
        self.document_path.write_text(json.dumps(self.document), encoding="utf-8")
        self.ocr_path.write_text(json.dumps(self.ocr), encoding="utf-8")

    def run_cli(self, output):
        return subprocess.run(
            [
                sys.executable, str(SCRIPT),
                "--document-manifest", str(self.document_path),
                "--ocr-record", str(self.ocr_path),
                "--asset", str(self.asset),
                "--output", str(output),
            ],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )

    def test_writes_local_review_required_output_without_echoing_ocr_text(self):
        output = self.root / "authorized-local-review" / "regions.json"
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("SYNTHETIC_TEST_ONLY OCR label", result.stdout)
        record = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(record["candidates"][0]["label_text"], "SYNTHETIC_TEST_ONLY OCR label")
        self.assertTrue(record["not_for_sft"])
        self.assertFalse(record["training_authorized"])
        self.assertFalse(record["gold_authorized"])

    def test_refuses_to_overwrite_existing_output(self):
        output = self.root / "regions.json"
        output.write_text("KEEP", encoding="utf-8")
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("DIAGRAM_OUTPUT_ALREADY_EXISTS", result.stdout)
        self.assertEqual(output.read_text(encoding="utf-8"), "KEEP")
        self.assertNotIn("SYNTHETIC_TEST_ONLY OCR label", result.stdout)

    def test_blocked_source_emits_payload_free_error(self):
        self.document["extraction_status"] = "BLOCKED"
        self.document_path.write_text(json.dumps(self.document), encoding="utf-8")
        output = self.root / "regions.json"
        result = self.run_cli(output)
        self.assertEqual(result.returncode, 2)
        self.assertIn("DIAGRAM_DOCUMENT_EXTRACTION_BLOCKED", result.stdout)
        self.assertFalse(output.exists())
        self.assertNotIn("SYNTHETIC_TEST_ONLY OCR label", result.stdout)


if __name__ == "__main__":
    unittest.main()
