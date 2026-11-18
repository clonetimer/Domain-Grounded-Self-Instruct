"""SYNTHETIC_TEST_ONLY adversarial coverage of per-hit historical provenance.

Fixtures are invented workflow tests, never real ML runs, flight logs, expert
testimony, Gold diagnoses, approved SFT records, or training authorization.
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
PACKETS = ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json"
FACTS = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
CURRENT = "LIT-TROPICS-PATHFINDER-CROSSSHORT-004"
FIRST = "SYNTHETIC-HISTORY-REVIEW-REF-001"
SECOND = "SYNTHETIC-HISTORY-REVIEW-REF-002"


def fixtures():
    collection = json.loads(PACKETS.read_text(encoding="utf-8"))
    cards = json.loads(FACTS.read_text(encoding="utf-8"))["cards"]
    packet = next(
        p for p in collection["packets"]
        if p["task_id"] == "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003"
    )
    return packet, cards, collection


def historical_lineage(packet):
    return next(
        entry for entry in packet["synthetic_provenance"]["generated_fields"]
        if entry["field_path"] == "case.input.historical_cases"
    )


def two_history_items(packet):
    """Add another independent, explicitly synthetic rejected history hit."""
    original = packet["history_context"]["items"][0]
    other = copy.deepcopy(original)
    other["case_ref"] = "SYNTHETIC-HISTORY-SEL-REJECTED-002"
    other["event_family_id"] = "SYNTHETIC-PRIOR-SEL-FAMILY-2"
    other["source_refs"] = [SECOND]
    other["hit_metadata"]["case_id"] = other["case_ref"]
    other["hit_metadata"]["source_group_id"] = other["event_family_id"]
    packet["history_context"]["items"].append(other)

    prior = copy.deepcopy(packet["case"]["input"]["historical_cases"][0])
    prior["case_ref"] = other["case_ref"]
    packet["case"]["input"]["historical_cases"].append(prior)

    transfer = copy.deepcopy(
        packet["case"]["expected_output"]["historical_experience_relevance"][0]
    )
    transfer["case_ref"] = other["case_ref"]
    packet["case"]["expected_output"]["historical_experience_relevance"].append(transfer)
    packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])


class HistoricalPerHitProvenanceTests(unittest.TestCase):
    def test_existing_fifteen_packets_remain_review_required(self):
        _, cards, collection = fixtures()
        result = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(result["packet_count"], 15)
        self.assertFalse(result["training_authorized"])

    def test_two_independent_history_hits_need_two_sources(self):
        packet, cards, _ = fixtures()
        two_history_items(packet)
        self.assertEqual(historical_lineage(packet)["source_fact_refs"], [FIRST])
        with self.assertRaisesRegex(
            L1TaskPacketError,
            "SYNTHETIC_HISTORY_HIT_SOURCE_COVERAGE_INCOMPLETE",
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_second_hit_source_alone_cannot_mask_first_hit(self):
        packet, cards, _ = fixtures()
        two_history_items(packet)
        historical_lineage(packet)["source_fact_refs"] = [SECOND]
        with self.assertRaisesRegex(
            L1TaskPacketError,
            "SYNTHETIC_HISTORY_HIT_SOURCE_COVERAGE_INCOMPLETE",
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_current_source_plus_one_history_ref_cannot_mask_other_hit(self):
        packet, cards, _ = fixtures()
        two_history_items(packet)
        historical_lineage(packet)["source_fact_refs"] = [CURRENT, FIRST]
        with self.assertRaisesRegex(
            L1TaskPacketError,
            "SYNTHETIC_HISTORY_HIT_SOURCE_COVERAGE_INCOMPLETE",
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_both_rejected_history_sources_can_be_covered_without_promotion(self):
        packet, cards, _ = fixtures()
        two_history_items(packet)
        historical_lineage(packet)["source_fact_refs"] = [FIRST, SECOND]
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertEqual(result["history_item_count"], 2)
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])

    def test_comparative_current_source_allowed_when_all_history_covered(self):
        packet, cards, _ = fixtures()
        two_history_items(packet)
        historical_lineage(packet)["source_fact_refs"] = [CURRENT, FIRST, SECOND]
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertEqual(result["history_item_count"], 2)
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
