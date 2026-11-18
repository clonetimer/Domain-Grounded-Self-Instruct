"""SYNTHETIC_TEST_ONLY adversarial tests for L1 generated-field provenance.

These fixtures are not flight logs, true ML runs, Gold or approved SFT.
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
COLLECTION_FILE = ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json"
CARDS_FILE = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"


def _fixtures():
    collection = json.loads(COLLECTION_FILE.read_text(encoding="utf-8"))
    cards = json.loads(CARDS_FILE.read_text(encoding="utf-8"))["cards"]
    return collection, cards


def _generated(packet):
    return packet["synthetic_provenance"]["generated_fields"]


class L1SyntheticFieldLineageTests(unittest.TestCase):
    def test_existing_fifteen_synthetic_packets_still_pass(self):
        collection, cards = _fixtures()
        result = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(result["packet_count"], 15)
        self.assertFalse(result["training_authorized"])

    def test_duplicate_field_path_does_not_hide_second_origin(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet).append(copy.deepcopy(_generated(packet)[0]))
        with self.assertRaisesRegex(
            L1TaskPacketError, "DUPLICATE_SYNTHETIC_FIELD_PROVENANCE"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_unknown_path_does_not_count_as_lineage(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet).append({
            **copy.deepcopy(_generated(packet)[0]),
            "field_path": "case.input.imaginary_source",
        })
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_FIELD_PATH_NOT_INPUT"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_curator_review_cannot_be_a_generated_input(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet).append({
            **copy.deepcopy(_generated(packet)[0]),
            "field_path": "case.internal_review",
        })
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_FIELD_PATH_NOT_INPUT"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_formal_target_cannot_be_a_generated_input(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet).append({
            **copy.deepcopy(_generated(packet)[0]),
            "field_path": "formal_target",
        })
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_FIELD_PATH_NOT_INPUT"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_hit_requires_historical_case_generation_lineage(self):
        collection, cards = _fixtures()
        packet = next(p for p in collection["packets"]
                      if p["history_context"]["retrieval_status"] == "HIT")
        packet["synthetic_provenance"]["generated_fields"] = [
            f for f in _generated(packet)
            if f["field_path"] != "case.input.historical_cases"
        ]
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_HISTORY_FIELD_LINEAGE_MISMATCH"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_no_hit_cannot_claim_synthetic_history_was_present(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet).append({
            **copy.deepcopy(_generated(packet)[0]),
            "field_path": "case.input.historical_cases",
        })
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_HISTORY_FIELD_LINEAGE_MISMATCH"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_generated_field_must_name_its_source_fact(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet)[0]["source_fact_refs"] = []
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_FIELD_REQUIRES_SOURCE_FACT_REF"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_synthetic_ml_cannot_be_labeled_as_literal_source_fact(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet)[0]["origin"] = "DERIVED_FROM_SOURCE_FACT"
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_ML_OR_LOG_CLAIMED_AS_SOURCE_FACT"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_synthetic_log_cannot_be_labeled_as_literal_source_fact(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet)[1]["origin"] = "DERIVED_FROM_SOURCE_FACT"
        with self.assertRaisesRegex(
            L1TaskPacketError, "SYNTHETIC_ML_OR_LOG_CLAIMED_AS_SOURCE_FACT"
        ):
            validate_l1_task_packet(packet, source_fact_cards=cards)

    def test_source_grounded_context_is_not_falsely_banned(self):
        collection, cards = _fixtures()
        packet = collection["packets"][0]
        _generated(packet)[2]["origin"] = "DERIVED_FROM_SOURCE_FACT"
        result = validate_l1_task_packet(packet, source_fact_cards=cards)
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
