from __future__ import annotations

import copy
import hashlib
import json
import sys
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.diagram_text_review import DiagramTextReviewError, validate_diagram_text_review


def digest(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


class DiagramTextReviewTests(unittest.TestCase):
    def setUp(self):
        self.candidate = {
            "schema_version": "dgsi.diagram-text-regions.v1",
            "source_id": "SYNTHETIC_TEST_ONLY-SRC",
            "source_sha256": "a" * 64,
            "asset_id": "IMG0001",
            "asset_sha256": "b" * 64,
            "ocr_record_sha256": "c" * 64,
            "generation_recipe": "isolated-lines-plus-pair-hypotheses-v2",
            "candidates": [{
                "candidate_id": "OCR-" + "d" * 20,
                "candidate_type": "SINGLE_LINE",
                "label_text": "SYNTHETIC_TEST_ONLY ADCS",
                "ocr_line_ids": ["L00001"],
                "bbox_px": {"left": 10, "top": 20, "width": 80, "height": 12},
                "evidence_locators": [
                    "asset:IMG0001@sha256:" + "b" * 64 + "#ocr-line:L00001#bbox-px:10,20,80,12"
                ],
                "object_type": "UNKNOWN",
                "interpretation": "UNRESOLVED_OCR_TEXT",
                "review_status": "MANUAL_REVIEW_REQUIRED",
            }],
            "review_status": "REVIEW_REQUIRED",
            "not_for_sft": True,
            "training_authorized": False,
            "gold_authorized": False,
        }
        self.receipt = {
            "schema_version": "dgsi.diagram-text-review.v1",
            "review_id": "REVIEW-001",
            "source_sha256": self.candidate["source_sha256"],
            "asset_id": self.candidate["asset_id"],
            "asset_sha256": self.candidate["asset_sha256"],
            "candidate_record_sha256": digest(self.candidate),
            "reviewer_ref": "reviewer-local-alias-01",
            "reviewer_authentication": "NOT_AUTHENTICATED_BY_LOCAL_TOOL",
            "reviewed_at": "2026-11-17T02:00:00Z",
            "decisions": [{
                "candidate_id": self.candidate["candidates"][0]["candidate_id"],
                "decision": "ACCEPT_AS_LABEL",
                "object_type": "SUBSYSTEM",
                "evidence_locator": self.candidate["candidates"][0]["evidence_locators"][0],
            }],
            "review_status": "REVIEW_REQUIRED",
            "training_authorized": False,
            "gold_authorized": False,
        }

    def validate(self, candidate=None, receipt=None):
        return validate_diagram_text_review(
            self.candidate if candidate is None else candidate,
            self.receipt if receipt is None else receipt,
        )

    def test_valid_receipt_binds_candidate_and_returns_aggregate_only(self):
        result = self.validate()
        self.assertEqual(result["decision"], "REVIEW_RECEIPT_BOUND_NOT_AUTHENTICATED")
        self.assertEqual(result["accepted_label_count"], 1)
        self.assertEqual(result["reviewer_authentication"], "NOT_AUTHENTICATED_BY_LOCAL_TOOL")
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["gold_authorized"])
        self.assertNotIn("reviewer-local-alias-01", str(result))
        self.assertNotIn("SYNTHETIC_TEST_ONLY ADCS", str(result))

    def test_source_hash_mismatch_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["source_sha256"] = "e" * 64
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_SOURCE_HASH_MISMATCH$"):
            self.validate(receipt=receipt)

    def test_asset_hash_mismatch_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["asset_sha256"] = "f" * 64
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_ASSET_HASH_MISMATCH$"):
            self.validate(receipt=receipt)

    def test_candidate_record_mutation_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["candidates"][0]["label_text"] = "ALTERED"
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_CANDIDATE_RECORD_HASH_MISMATCH$"):
            self.validate(candidate=candidate)

    def test_unknown_candidate_reference_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"][0]["candidate_id"] = "OCR-" + "0" * 20
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_CANDIDATE_UNKNOWN$"):
            self.validate(receipt=receipt)

    def test_duplicate_decisions_rejected(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"].append(copy.deepcopy(receipt["decisions"][0]))
        receipt["candidate_record_sha256"] = digest(self.candidate)
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_DECISION_DUPLICATE$"):
            self.validate(receipt=receipt)

    def test_locator_must_match_exact_candidate_evidence(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"][0]["evidence_locator"] += "#forged"
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_REVIEW_EVIDENCE_LOCATOR_MISMATCH$"):
            self.validate(receipt=receipt)

    def test_review_receipt_cannot_claim_authenticated_reviewer(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["reviewer_authentication"] = "AUTHENTICATED"
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_TEXT_REVIEW_RECEIPT_INVALID$"):
            self.validate(receipt=receipt)

    def test_nonaccepted_decision_cannot_supply_object_type(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"][0]["decision"] = "UNRESOLVED"
        with self.assertRaisesRegex(DiagramTextReviewError, "^DIAGRAM_TEXT_REVIEW_RECEIPT_INVALID$"):
            self.validate(receipt=receipt)



class DiagramTextReviewCliTests(unittest.TestCase):
    def test_cli_emits_aggregate_only_summary(self):
        fixture = DiagramTextReviewTests()
        fixture.setUp()
        with tempfile.TemporaryDirectory() as temp:
            candidate_path = Path(temp) / "candidates.json"
            receipt_path = Path(temp) / "review.json"
            candidate_path.write_text(json.dumps(fixture.candidate), encoding="utf-8")
            receipt_path.write_text(json.dumps(fixture.receipt), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/audit_diagram_text_review.py"),
                 "--candidate-record", str(candidate_path),
                 "--review-receipt", str(receipt_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("REVIEW_RECEIPT_BOUND_NOT_AUTHENTICATED", result.stdout)
        self.assertNotIn("reviewer-local-alias-01", result.stdout)
        self.assertNotIn("SYNTHETIC_TEST_ONLY ADCS", result.stdout)

    def test_cli_rejects_invalid_receipt_without_echoing_values(self):
        fixture = DiagramTextReviewTests()
        fixture.setUp()
        fixture.receipt["reviewer_authentication"] = "AUTHENTICATED"
        with tempfile.TemporaryDirectory() as temp:
            candidate_path = Path(temp) / "candidates.json"
            receipt_path = Path(temp) / "review.json"
            candidate_path.write_text(json.dumps(fixture.candidate), encoding="utf-8")
            receipt_path.write_text(json.dumps(fixture.receipt), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts/audit_diagram_text_review.py"),
                 "--candidate-record", str(candidate_path),
                 "--review-receipt", str(receipt_path)],
                cwd=ROOT, capture_output=True, text=True, check=False,
            )
        self.assertEqual(result.returncode, 2)
        self.assertIn("DIAGRAM_TEXT_REVIEW_RECEIPT_INVALID", result.stdout)
        self.assertNotIn("AUTHENTICATED", result.stdout)


if __name__ == "__main__":
    unittest.main()
