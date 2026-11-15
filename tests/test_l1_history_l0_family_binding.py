"""SYNTHETIC_TEST_ONLY: L1 historical-source family anti-laundering tests.

All fixtures are public literature-derived scenarios or invented identifiers.
These tests do not authenticate real history, certify Gold or authorize splits.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import (
    L1TaskPacketError,
    validate_l1_task_packet,
    validate_l1_task_packet_collection,
)

ROOT = Path(__file__).resolve().parents[1]
CASSINI = "LIT-CASSINI-RWA-DRAG-007"
FUSE = "LIT-FUSE-RWA-KAPTON-001"
TROPICS = "LIT-TROPICS-PATHFINDER-CROSSSHORT-004"


def _fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(
            encoding="utf-8"
        )
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(
            encoding="utf-8"
        )
    )["cards"]
    return collection, cards


def _fuse_packet(collection):
    return copy.deepcopy(next(
        packet for packet in collection["packets"]
        if packet["task_id"] == "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012"
    ))


def _history_lineage(packet):
    return next(
        item for item in packet["synthetic_provenance"]["generated_fields"]
        if item["field_path"] == "case.input.historical_cases"
    )


class L1HistoryL0FamilyBindingTests(unittest.TestCase):
    def test_existing_fifteen_packets_keep_their_source_family_bindings(self):
        collection, cards = _fixtures()
        out = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(out["gold_eligible_count"], 0)
        self.assertFalse(out["training_authorized"])

    def test_distinct_cassini_history_card_passes_without_gold_promotion(self):
        collection, cards = _fixtures()
        packet = _fuse_packet(collection)
        self.assertEqual(packet["history_context"]["items"][0]["source_refs"], [CASSINI])
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertEqual(result["history_item_count"], 1)
        self.assertFalse(result["gold_eligible"])

    def test_unrelated_public_card_cannot_certify_claimed_cassini_family(self):
        collection, cards = _fixtures()
        packet = _fuse_packet(collection)
        packet["history_context"]["items"][0]["source_refs"] = [TROPICS]
        _history_lineage(packet)["source_fact_refs"] = [TROPICS]
        with self.assertRaisesRegex(
            L1TaskPacketError, "HISTORY_HIT_L0_SOURCE_FAMILY_MISMATCH"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_extra_wrong_public_card_cannot_hide_behind_correct_history_card(self):
        collection, cards = _fixtures()
        packet = _fuse_packet(collection)
        packet["history_context"]["items"][0]["source_refs"] = [CASSINI, TROPICS]
        _history_lineage(packet)["source_fact_refs"] = [CASSINI, TROPICS]
        with self.assertRaisesRegex(
            L1TaskPacketError, "HISTORY_HIT_L0_SOURCE_FAMILY_MISMATCH"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_current_event_ref_cannot_be_repackaged_as_independent_history(self):
        collection, cards = _fixtures()
        packet = _fuse_packet(collection)
        current_family = next(c["event_family_id"] for c in cards if c["case_id"] == FUSE)
        hit = packet["history_context"]["items"][0]
        hit["event_family_id"] = current_family
        hit["hit_metadata"]["source_group_id"] = current_family
        hit["source_refs"] = [FUSE]
        _history_lineage(packet)["source_fact_refs"] = [FUSE]
        with self.assertRaisesRegex(
            L1TaskPacketError, "CURRENT_L0_EVENT_FAMILY_CANNOT_BE_HISTORY"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_self_consistent_but_false_history_metadata_cannot_relabel_l0(self):
        collection, cards = _fixtures()
        packet = _fuse_packet(collection)
        hit = packet["history_context"]["items"][0]
        hit["event_family_id"] = "SYNTHETIC-INVENTED-DIFFERENT-FAMILY"
        hit["hit_metadata"]["source_group_id"] = hit["event_family_id"]
        with self.assertRaisesRegex(
            L1TaskPacketError, "HISTORY_HIT_L0_SOURCE_FAMILY_MISMATCH"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_explicitly_synthetic_rejected_prior_is_not_mistaken_for_public_l0(self):
        collection, cards = _fixtures()
        packet = copy.deepcopy(next(
            p for p in collection["packets"]
            if p["task_id"] == "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003"
        ))
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertEqual(result["history_item_count"], 1)
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
