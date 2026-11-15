"""SYNTHETIC_TEST_ONLY provenance boundary tests; not flight or Gold data.

Ensure retrieved historical source material cannot be represented as evidence
for the current event's synthetic ML/log/configuration input. Conversely, a
synthetic history field must cite at least one actual retrieved-history source.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import (
    L1TaskPacketError, validate_l1_task_packet,
    validate_l1_task_packet_collection,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json"
FACTS = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
CASSINI = "LIT-CASSINI-RWA-DRAG-007"
FUSE = "LIT-FUSE-RWA-KAPTON-001"
TROPICS = "LIT-TROPICS-PATHFINDER-CROSSSHORT-004"
SYNTHETIC_PRIOR = "SYNTHETIC-HISTORY-REVIEW-REF-001"


def fixtures():
    collection = json.loads(COLLECTION.read_text(encoding="utf-8"))
    facts = json.loads(FACTS.read_text(encoding="utf-8"))["cards"]
    return collection, facts


def find_packet(collection, fragment):
    return next(p for p in collection["packets"] if fragment in p["task_id"])


def field(packet, root):
    return next(
        item for item in packet["synthetic_provenance"]["generated_fields"]
        if item["field_path"] == "case.input." + root
    )


class L1HistoricalInputSourceBoundaryTests(unittest.TestCase):
    def test_all_fifteen_public_synthetic_scenarios_remain_review_required(self):
        collection, cards = fixtures()
        result = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(result["packet_count"], 15)
        self.assertFalse(result["training_authorized"])

    def test_current_ml_cannot_cite_cassini_history_only_source(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "FUSE-RWA-HISTORY-REUSE")
        field(packet, "machine_diagnosis")["source_fact_refs"] = [CASSINI]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_CURRENT_FIELD_CITES_HISTORY_ONLY_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_mixed_current_and_historical_log_sources_are_rejected(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "FUSE-RWA-HISTORY-REUSE")
        field(packet, "diagnostic_logs")["source_fact_refs"] = [FUSE, CASSINI]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_CURRENT_FIELD_CITES_HISTORY_ONLY_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_current_spacecraft_configuration_cannot_cite_history_only_source(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "FUSE-RWA-HISTORY-REUSE")
        field(packet, "spacecraft_context")["source_fact_refs"] = [CASSINI]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_CURRENT_FIELD_CITES_HISTORY_ONLY_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_current_operational_context_cannot_cite_synthetic_history_source(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003")
        field(packet, "operational_context")["source_fact_refs"] = [SYNTHETIC_PRIOR]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_CURRENT_FIELD_CITES_HISTORY_ONLY_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_cassini_history_input_must_not_only_cite_current_fuse_event(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "FUSE-RWA-HISTORY-REUSE")
        field(packet, "historical_cases")["source_fact_refs"] = [FUSE]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_HISTORY_FIELD_NOT_BOUND_TO_HIT_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_synthetic_rejected_history_requires_its_declared_source(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003")
        field(packet, "historical_cases")["source_fact_refs"] = [TROPICS]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_HISTORY_FIELD_NOT_BOUND_TO_HIT_SOURCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_history_can_cite_current_and_historical_sources_when_both_declared(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "FUSE-RWA-HISTORY-REUSE")
        field(packet, "historical_cases")["source_fact_refs"] = [FUSE, CASSINI]
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertFalse(result["gold_eligible"])

    def test_valid_synthetic_history_only_source_is_not_a_real_event_proof(self):
        collection, cards = fixtures()
        packet = find_packet(collection, "TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003")
        self.assertEqual(field(packet, "historical_cases")["source_fact_refs"], [SYNTHETIC_PRIOR])
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
