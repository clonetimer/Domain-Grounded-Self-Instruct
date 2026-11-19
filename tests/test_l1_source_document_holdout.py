"""Synthetic-only tests of source-document holdout independence."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_source_document_holdout import (
    L1DocumentHoldoutError, audit_l1_source_document_holdout,
)

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json")
        .read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json")
        .read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


class DocumentHoldoutTests(unittest.TestCase):
    def test_rev1_reports_seven_documents_not_nine_independent_sources(self):
        collection, cards = fixtures()
        outcome = audit_l1_source_document_holdout(collection, cards)
        self.assertEqual((outcome["task_count"], outcome["event_family_count"],
                          outcome["source_document_count"]), (21, 9, 7))
        self.assertFalse(outcome["official_splits_assigned"])
        self.assertFalse(outcome["training_authorized"])
        tropics = next(g for g in outcome["source_document_groups"]
                       if g["source_id"] == "MITLL-TROPICS-LESSONS-2025")
        self.assertEqual(len(tropics["task_ids"]), 6)
        self.assertEqual(len(tropics["event_family_ids"]), 3)

    def test_different_tropics_families_may_not_cross_splits(self):
        collection, cards = fixtures()
        plan = {p["task_id"]: "train" for p in collection["packets"]}
        plan["L1-TROPICS-TVAC-SLIPRING-SYNTH-004"] = "test"
        with self.assertRaisesRegex(
            L1DocumentHoldoutError, "L1_HOLDOUT_SHARED_DOCUMENT_OR_FAMILY_CROSS_SPLIT"
        ):
            audit_l1_source_document_holdout(collection, cards, hypothetical_splits=plan)

    def test_hypothetical_safe_plan_does_not_authorize_training(self):
        collection, cards = fixtures()
        plan = {p["task_id"]: "train" for p in collection["packets"]}
        outcome = audit_l1_source_document_holdout(
            collection, cards, hypothetical_splits=plan
        )
        self.assertEqual(outcome["decision"], "HYPOTHETICAL_DOCUMENT_HOLDOUT_SAFE")
        self.assertFalse(outcome["official_splits_assigned"])
        self.assertFalse(outcome["training_authorized"])

    def test_incomplete_plan_is_rejected(self):
        collection, cards = fixtures()
        with self.assertRaisesRegex(
            L1DocumentHoldoutError, "L1_HOLDOUT_HYPOTHETICAL_PLAN_INCOMPLETE"
        ):
            audit_l1_source_document_holdout(
                collection, cards, hypothetical_splits={collection["packets"][0]["task_id"]: "test"}
            )

    def test_missing_source_metadata_rejected_without_guessing(self):
        collection, cards = fixtures()
        cards = copy.deepcopy(cards)
        cards[0]["source_reference"]["source_id"] = None
        with self.assertRaisesRegex(
            L1DocumentHoldoutError, "L1_HOLDOUT_DOCUMENT_ID_MISSING"
        ):
            audit_l1_source_document_holdout(collection, cards)

    def test_multiple_source_refs_connect_document_clusters(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        first = collection["packets"][0]
        first["source_fact_refs"].append("LIT-LUNAR-ORBITER-POWER-MONITOR-006")
        result = audit_l1_source_document_holdout(collection, cards)
        self.assertEqual(result["independent_source_document_cluster_count"], 6)

    def test_real_track_is_not_silently_grouped_with_synthetic(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        collection["track"] = "REAL_GOLD_TRACK"
        with self.assertRaisesRegex(
            L1DocumentHoldoutError, "L1_HOLDOUT_TRACK_UNSUPPORTED"
        ):
            audit_l1_source_document_holdout(collection, cards)


if __name__ == "__main__":
    unittest.main()
