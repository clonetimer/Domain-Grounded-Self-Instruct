"""SYNTHETIC_TEST_ONLY: whole-collection projection is never an SFT exporter."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_model_projection_audit import (
    L1ProjectionAuditError,
    audit_l1_synthetic_collection_projection,
)

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json")
        .read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json")
        .read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


class L1CollectionProjectionPreflightTests(unittest.TestCase):
    def setUp(self):
        self.collection, self.cards = fixtures()

    def audit(self, collection=None, cards=None):
        return audit_l1_synthetic_collection_projection(
            self.collection if collection is None else collection,
            source_fact_cards=self.cards if cards is None else cards,
        )

    def test_existing_15_packet_collection_is_blocked_metadata_only(self):
        result = self.audit()
        self.assertEqual(result["decision"], "BLOCKED_PENDING_EXTERNAL_ADMISSION")
        self.assertEqual(result["packet_count"], 15)
        self.assertEqual(result["event_family_count"], 9)
        self.assertEqual(len(result["collection_projection_sha256"]), 64)
        self.assertEqual(result["sft_records_emitted"], 0)
        self.assertFalse(result["internal_review_exported"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn("packets", result)
        self.assertNotIn("input", result)
        self.assertNotIn("target", result)

    def test_reordering_packets_does_not_change_manifest_identity(self):
        baseline = self.audit()["collection_projection_sha256"]
        variant = copy.deepcopy(self.collection)
        variant["packets"].reverse()
        self.assertEqual(self.audit(variant)["collection_projection_sha256"], baseline)

    def test_input_change_changes_collection_digest_without_releasing_text(self):
        before = self.audit()["collection_projection_sha256"]
        variant = copy.deepcopy(self.collection)
        marker = "SYNTHETIC_TEST_ONLY_CHANGED_INPUT"
        variant["packets"][0]["case"]["input"]["machine_diagnosis"]["machine_summary"] += marker
        after = self.audit(variant)
        self.assertNotEqual(after["collection_projection_sha256"], before)
        self.assertNotIn(marker, json.dumps(after))

    def test_curator_only_note_change_is_excluded_from_collection_digest(self):
        before = self.audit()["collection_projection_sha256"]
        variant = copy.deepcopy(self.collection)
        variant["packets"][0]["case"]["internal_review"]["curator_prompts"].append(
            "SYNTHETIC_TEST_ONLY_PRIVATE_REVIEW_NOTE"
        )
        self.assertEqual(self.audit(variant)["collection_projection_sha256"], before)

    def test_duplicate_packet_identity_blocks_entire_collection(self):
        variant = copy.deepcopy(self.collection)
        variant["packets"].append(copy.deepcopy(variant["packets"][0]))
        variant["packet_count"] += 1
        with self.assertRaisesRegex(
            L1ProjectionAuditError, "^L1_PROJECTION_COLLECTION_NOT_VALIDATED$"
        ):
            self.audit(variant)

    def test_any_nested_curator_field_in_model_input_blocks_whole_batch(self):
        variant = copy.deepcopy(self.collection)
        variant["packets"][-1]["case"]["input"]["operational_context"][
            "reviewer_questions"
        ] = ["SYNTHETIC_TEST_ONLY_PRIVATE"]
        with self.assertRaisesRegex(
            L1ProjectionAuditError,
            "^L1_PROJECTION_CURATOR_FIELD_IN_MODEL_SURFACE$",
        ):
            self.audit(variant)

    def test_official_split_and_real_track_are_forbidden(self):
        variant = copy.deepcopy(self.collection)
        variant["split_assignments"] = [{"task_id": variant["packets"][0]["task_id"], "split": "train"}]
        with self.assertRaisesRegex(
            L1ProjectionAuditError, "^L1_PROJECTION_COLLECTION_SPLIT_NOT_AUTHORIZED$"
        ):
            self.audit(variant)
        variant = copy.deepcopy(self.collection)
        variant["track"] = "REAL_GOLD_TRACK"
        with self.assertRaisesRegex(
            L1ProjectionAuditError, "^L1_PROJECTION_COLLECTION_REAL_TRACK_NOT_AUTHORIZED$"
        ):
            self.audit(variant)

    def test_missing_l0_source_closure_blocks_batch(self):
        with self.assertRaisesRegex(
            L1ProjectionAuditError, "^L1_PROJECTION_COLLECTION_NOT_VALIDATED$"
        ):
            self.audit(cards=[])


if __name__ == "__main__":
    unittest.main()
