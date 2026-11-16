"""SYNTHETIC_TEST_ONLY: count current L1 target families, not spare L0 cards."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

from dgsi.l1_global_lineage import audit_l1_cross_collection_lineage
from tests.test_l1_global_lineage import CASSINI, FUSE, TROPICS_A, TROPICS_B, _fixtures

ROOT = Path(__file__).resolve().parents[1]
L0 = ROOT / "examples" / "l0_public_literature_fact_cards_2026-11-15.json"
L1 = ROOT / "examples" / "l1_literature_synthetic_task_packets_v0.1.json"


class GlobalTargetFamilyCountTests(unittest.TestCase):
    def test_complete_unassigned_literature_pilot_counts_nine_target_families(self):
        collection = json.loads(L1.read_text(encoding="utf-8"))
        cards = json.loads(L0.read_text(encoding="utf-8"))["cards"]
        self.assertGreater(len({c["event_family_id"] for c in cards}), 9)
        report = audit_l1_cross_collection_lineage(
            [{"collection": collection, "source_fact_cards": cards}]
        )
        self.assertEqual(report["task_count"], 15)
        self.assertEqual(report["source_card_count"], 13)
        self.assertEqual(report["canonical_target_family_count"], 9)
        self.assertEqual(report["track_family_counts"]["LITERATURE_DERIVED_SYNTHETIC"], 9)
        self.assertFalse(report["training_authorized"])

    def test_two_synthetic_variants_of_one_event_count_one_target_family(self):
        report = audit_l1_cross_collection_lineage(_fixtures(TROPICS_A, TROPICS_B))
        self.assertEqual(report["canonical_target_family_count"], 1)
        self.assertEqual(report["task_count"], 2)

    def test_two_independent_target_events_count_two_families(self):
        report = audit_l1_cross_collection_lineage(_fixtures(FUSE, CASSINI))
        self.assertEqual(report["canonical_target_family_count"], 2)
        self.assertFalse(report["training_authorized"])

    def test_hypothetical_same_split_preserves_target_count_without_approval(self):
        batches = _fixtures(FUSE, CASSINI)
        splits = {
            batch["collection"]["collection_id"]: {
                batch["collection"]["packets"][0]["task_id"]: "train"
            }
            for batch in batches
        }
        report = audit_l1_cross_collection_lineage(
            batches, hypothetical_splits=splits
        )
        self.assertEqual(report["canonical_target_family_count"], 2)
        self.assertEqual(report["split_check_mode"], "HYPOTHETICAL_TEST_ONLY")
        self.assertFalse(report["training_authorized"])


if __name__ == "__main__":
    unittest.main()
