from __future__ import annotations

import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.diagram_review_import import DiagramReviewImportError, import_reviewed_text_as_proposed_graph


def sha(value):
    return hashlib.sha256(json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


class DiagramReviewImportTests(unittest.TestCase):
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
            "candidate_record_sha256": sha(self.candidate),
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

    def convert(self, candidate=None, receipt=None):
        return import_reviewed_text_as_proposed_graph(
            self.candidate if candidate is None else candidate,
            self.receipt if receipt is None else receipt,
        )

    def test_accept_label_creates_only_ai_proposed_node(self):
        result = self.convert()
        graph = result["diagram_annotation"]
        audit = result["conversion_receipt"]
        self.assertEqual(len(graph["nodes"]), 1)
        self.assertEqual(graph["nodes"][0]["object_type"], "SUBSYSTEM")
        self.assertEqual(graph["nodes"][0]["review_status"], "AI_PROPOSED")
        self.assertEqual(graph["nodes"][0]["evidence_locator"], self.receipt["decisions"][0]["evidence_locator"])
        self.assertEqual(graph["ports"], [])
        self.assertEqual(graph["edges"], [])
        self.assertEqual(audit["node_status"], "AI_PROPOSED")
        self.assertEqual(audit["ports_created"], 0)
        self.assertEqual(audit["edges_created"], 0)
        self.assertEqual(audit["reviewer_authentication"], "NOT_AUTHENTICATED_BY_LOCAL_TOOL")
        self.assertFalse(graph["training_authorized"])
        self.assertFalse(audit["gold_authorized"])

    def test_rejected_and_unresolved_candidates_do_not_create_nodes(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"][0] = {
            "candidate_id": self.candidate["candidates"][0]["candidate_id"],
            "decision": "UNRESOLVED",
            "evidence_locator": self.candidate["candidates"][0]["evidence_locators"][0],
        }
        result = self.convert(receipt=receipt)
        self.assertEqual(result["diagram_annotation"]["nodes"], [])
        self.assertEqual(result["diagram_annotation"]["ports"], [])
        self.assertEqual(result["diagram_annotation"]["edges"], [])

    def test_candidate_mutation_fails_closed(self):
        candidate = copy.deepcopy(self.candidate)
        candidate["candidates"][0]["label_text"] = "ALTERED"
        with self.assertRaisesRegex(DiagramReviewImportError, "^DIAGRAM_REVIEW_CANDIDATE_RECORD_HASH_MISMATCH$"):
            self.convert(candidate=candidate)

    def test_import_never_promotes_to_human_confirmed(self):
        result = self.convert()
        self.assertTrue(all(n["review_status"] != "HUMAN_CONFIRMED" for n in result["diagram_annotation"]["nodes"]))
        self.assertTrue(all(c["certainty"] == "PROPOSED_INTERPRETATION" for c in result["diagram_annotation"]["claims"]))

    def test_receipt_without_accept_decision_creates_empty_review_graph(self):
        receipt = copy.deepcopy(self.receipt)
        receipt["decisions"][0]["decision"] = "REJECT_LABEL"
        receipt["decisions"][0].pop("object_type")
        result = self.convert(receipt=receipt)
        self.assertEqual(result["diagram_annotation"]["nodes"], [])
        self.assertEqual(result["conversion_receipt"]["accepted_candidate_ids"], [])


if __name__ == "__main__":
    unittest.main()
