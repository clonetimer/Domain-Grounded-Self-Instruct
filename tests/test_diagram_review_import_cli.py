from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_diagram_text_review.py"


def sha(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


class DiagramReviewImportCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = {
            "schema_version": "dgsi.diagram-text-regions.v1",
            "source_id": "SYNTHETIC_TEST_ONLY-SRC",
            "source_sha256": "a" * 64, "asset_id": "IMG0001",
            "asset_sha256": "b" * 64, "ocr_record_sha256": "c" * 64,
            "generation_recipe": "isolated-lines-plus-pair-hypotheses-v2",
            "candidates": [{
                "candidate_id": "OCR-" + "d" * 20, "candidate_type": "SINGLE_LINE",
                "label_text": "SYNTHETIC_TEST_ONLY ADCS", "ocr_line_ids": ["L1"],
                "bbox_px": {"left": 10, "top": 20, "width": 50, "height": 12},
                "evidence_locators": ["asset:IMG0001@sha256:" + "b"*64 + "#ocr-line:L1#bbox-px:10,20,50,12"],
                "object_type": "UNKNOWN", "interpretation": "UNRESOLVED_OCR_TEXT",
                "review_status": "MANUAL_REVIEW_REQUIRED",
            }],
            "review_status": "REVIEW_REQUIRED", "not_for_sft": True,
            "training_authorized": False, "gold_authorized": False,
        }
        self.receipt = {
            "schema_version": "dgsi.diagram-text-review.v1", "review_id": "R1",
            "source_sha256": "a"*64, "asset_id": "IMG0001", "asset_sha256": "b"*64,
            "candidate_record_sha256": sha(self.candidate), "reviewer_ref": "local-alias",
            "reviewer_authentication": "NOT_AUTHENTICATED_BY_LOCAL_TOOL",
            "reviewed_at": "2026-11-17T02:00:00Z",
            "decisions": [{
                "candidate_id": "OCR-"+"d"*20, "decision": "ACCEPT_AS_LABEL",
                "object_type": "SUBSYSTEM",
                "evidence_locator": self.candidate["candidates"][0]["evidence_locators"][0],
            }],
            "review_status": "REVIEW_REQUIRED", "training_authorized": False, "gold_authorized": False,
        }

    def run_cli(self, output):
        cp=self.root/"candidate.json"; rp=self.root/"receipt.json"
        cp.write_text(json.dumps(self.candidate),encoding="utf-8")
        rp.write_text(json.dumps(self.receipt),encoding="utf-8")
        return subprocess.run(
            [sys.executable,str(SCRIPT),"--candidate-record",str(cp),
             "--review-receipt",str(rp),"--output",str(output)],
            cwd=ROOT,capture_output=True,text=True,check=False,
        )

    def test_cli_writes_proposed_graph_without_echoing_source_text(self):
        output=self.root/"review"/"graph.json"
        result=self.run_cli(output)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertNotIn("SYNTHETIC_TEST_ONLY ADCS",result.stdout)
        data=json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(data["diagram_annotation"]["nodes"][0]["review_status"],"AI_PROPOSED")
        self.assertEqual(data["diagram_annotation"]["edges"],[])
        self.assertEqual(data["conversion_receipt"]["reviewer_authentication"],"NOT_AUTHENTICATED_BY_LOCAL_TOOL")

    def test_cli_refuses_overwrite(self):
        output=self.root/"graph.json"; output.write_text("KEEP",encoding="utf-8")
        result=self.run_cli(output)
        self.assertEqual(result.returncode,2)
        self.assertIn("DIAGRAM_REVIEW_IMPORT_OUTPUT_ALREADY_EXISTS",result.stdout)
        self.assertEqual(output.read_text(encoding="utf-8"),"KEEP")

    def test_cli_rejects_mutated_candidate(self):
        self.candidate["candidates"][0]["label_text"]="ALTERED"
        output=self.root/"graph.json"
        result=self.run_cli(output)
        self.assertEqual(result.returncode,2)
        self.assertIn("DIAGRAM_REVIEW_CANDIDATE_RECORD_HASH_MISMATCH",result.stdout)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
