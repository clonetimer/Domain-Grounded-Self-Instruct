"""SYNTHETIC_TEST_ONLY: nonconfirmed historical as-of timestamp adversaries.

Fixtures are labeled literature-derived candidates. They are not verified
historical memory, real ML output, in-orbit logs, Gold, or training records.
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
TASKS = ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json"
FACTS = ROOT / "examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json"
TASK_ID = "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003"


def fixture():
    collection = json.loads(TASKS.read_text(encoding="utf-8"))
    cards = json.loads(FACTS.read_text(encoding="utf-8"))["cards"]
    packet = copy.deepcopy(next(
        p for p in collection["packets"] if p["task_id"] == TASK_ID
    ))
    assert packet["history_context"]["items"][0]["outcome_status"] == "REJECTED"
    return packet, cards, collection


def validate(packet, cards):
    return validate_l1_task_packet(packet, source_fact_cards=cards)


class NonconfirmedHistoricalVerificationOrderTests(unittest.TestCase):
    def test_current_21_task_candidate_is_still_review_only(self):
        _, cards, collection = fixture()
        report = validate_l1_task_packet_collection(
            collection, source_fact_cards=cards
        )
        self.assertEqual(report["packet_count"], 21)
        self.assertFalse(report["training_authorized"])

    def test_unverified_nonconfirmed_history_keeps_existing_policy(self):
        packet, cards, _ = fixture()
        self.assertNotIn(
            "verified_at", packet["history_context"]["items"][0]["hit_metadata"]
        )
        report = validate(packet, cards)
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["training_authorized"])

    def test_review_later_than_history_availability_blocks_retroactive_status(self):
        packet, cards, _ = fixture()
        packet["history_context"]["items"][0]["hit_metadata"]["verified_at"] = (
            "2026-04-10T08:01:00Z"
        )
        with self.assertRaisesRegex(
            L1TaskPacketError, "^HISTORY_AVAILABLE_BEFORE_VERIFICATION$"
        ):
            validate(packet, cards)

    def test_equal_time_does_not_claim_current_root_cause(self):
        packet, cards, _ = fixture()
        packet["history_context"]["items"][0]["hit_metadata"]["verified_at"] = (
            "2026-04-10T08:00:00Z"
        )
        report = validate(packet, cards)
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["training_authorized"])

    def test_earlier_review_cannot_promote_rejected_history(self):
        packet, cards, _ = fixture()
        packet["history_context"]["items"][0]["hit_metadata"]["verified_at"] = (
            "2026-04-10T07:59:00Z"
        )
        report = validate(packet, cards)
        self.assertEqual(packet["history_context"]["items"][0]["outcome_status"], "REJECTED")
        self.assertFalse(report["training_authorized"])

    def test_offset_aware_timestamp_is_compared_in_absolute_time(self):
        packet, cards, _ = fixture()
        packet["history_context"]["items"][0]["hit_metadata"]["verified_at"] = (
            "2026-04-10T17:01:00+09:00"
        )
        with self.assertRaisesRegex(
            L1TaskPacketError, "^HISTORY_AVAILABLE_BEFORE_VERIFICATION$"
        ):
            validate(packet, cards)

    def test_future_review_retains_existing_cutoff_guard(self):
        packet, cards, _ = fixture()
        packet["history_context"]["items"][0]["hit_metadata"]["verified_at"] = (
            "2026-04-13T00:00:00Z"
        )
        with self.assertRaisesRegex(
            L1TaskPacketError, "^HISTORY_VERIFICATION_TIME_INVALID_OR_FUTURE$"
        ):
            validate(packet, cards)


if __name__ == "__main__":
    unittest.main()
