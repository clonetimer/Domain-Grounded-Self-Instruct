"""SYNTHETIC_TEST_ONLY: a holdout target must not be a prior in another split.

These are literature-derived/invented fixtures, not independently reviewed SFT,
real operational records, Gold evidence, or authorization to assign pilot splits.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import (
    L1TaskPacketError,
    validate_l1_task_packet_collection,
)

ROOT = Path(__file__).resolve().parents[1]
FUSE_TASK = "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012"
FUSE_CARD = "LIT-FUSE-RWA-KAPTON-001"
CASSINI_CARD = "LIT-CASSINI-RWA-DRAG-007"
SEASAT_CARD = "LIT-SEASAT-SLIPRING-001"


def _fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json")
        .read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json")
        .read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


def _assign_all(collection, cards, *, family_overrides=None):
    by_id = {card["case_id"]: card for card in cards}
    overrides = family_overrides or {}
    return [
        {
            "task_id": packet["task_id"],
            "split": overrides.get(
                by_id[packet["source_fact_refs"][0]]["event_family_id"], "train"
            ),
        }
        for packet in collection["packets"]
    ]


def _family(cards, ref):
    return next(card["event_family_id"] for card in cards if card["case_id"] == ref)


class HistoryCrossSplitTargetGateTests(unittest.TestCase):
    def test_existing_unassigned_fifteen_packets_remain_review_required(self):
        collection, cards = _fixtures()
        audit = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(audit["packet_count"], 15)
        self.assertFalse(audit["split_audit_performed"])
        self.assertFalse(audit["training_authorized"])

    def test_other_split_cassini_target_cannot_be_fuse_history(self):
        collection, cards = _fixtures()
        self.assertTrue(any(p["task_id"] == FUSE_TASK for p in collection["packets"]))
        collection["split_assignments"] = _assign_all(
            collection, cards,
            family_overrides={_family(cards, FUSE_CARD): "validation"},
        )
        # Cassini current-event packets remain in train. The FUSE validation
        # prompt must not obtain a train-target Cassini conclusion as history.
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_HISTORY_CONTEXT_REFERENCES_OTHER_SPLIT_TARGET"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_other_split_fuse_prompt_cannot_consume_cassini_target(self):
        collection, cards = _fixtures()
        collection["split_assignments"] = _assign_all(
            collection, cards,
            family_overrides={_family(cards, CASSINI_CARD): "test"},
        )
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_HISTORY_CONTEXT_REFERENCES_OTHER_SPLIT_TARGET"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_same_split_history_does_not_bypass_review_requirement(self):
        collection, cards = _fixtures()
        collection["split_assignments"] = _assign_all(collection, cards)
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_SPLIT_BEFORE_INDEPENDENT_REVIEW"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_unrelated_family_split_does_not_trigger_false_history_leakage(self):
        collection, cards = _fixtures()
        collection["split_assignments"] = _assign_all(
            collection, cards,
            family_overrides={_family(cards, SEASAT_CARD): "test"},
        )
        # Invented rejected history fixtures cannot be promoted into a
        # fabricated event-family relationship merely by split assignment.
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_SPLIT_BEFORE_INDEPENDENT_REVIEW"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_incomplete_assignment_retains_existing_error_priority(self):
        collection, cards = _fixtures()
        collection["split_assignments"] = _assign_all(collection, cards)[:-1]
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_SPLIT_ASSIGNMENTS_INCOMPLETE"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)

    def test_same_family_cross_split_still_rejected_by_original_gate(self):
        collection, cards = _fixtures()
        collection["split_assignments"] = _assign_all(collection, cards)
        grouped = {}
        for packet in collection["packets"]:
            group = packet["case"]["provenance"]["source_group"]
            grouped.setdefault(group, []).append(packet["task_id"])
        pair = next(values[:2] for values in grouped.values() if len(values) >= 2)
        for assignment in collection["split_assignments"]:
            if assignment["task_id"] == pair[1]:
                assignment["split"] = "validation"
        with self.assertRaisesRegex(
            L1TaskPacketError, "L1_EVENT_FAMILY_CROSSES_DATASET_SPLITS"
        ):
            validate_l1_task_packet_collection(collection, source_fact_cards=cards)


if __name__ == "__main__":
    unittest.main()
