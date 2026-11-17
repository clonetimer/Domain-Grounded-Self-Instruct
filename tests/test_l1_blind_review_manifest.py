"""SYNTHETIC_TEST_ONLY: metadata-only double-blind receipt fingerprint regression."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_blind_review_manifest import (
    L1BlindReviewManifestError,
    build_l1_blind_review_manifest,
    check_blind_review_pair,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
CARDS = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


def _receipts(entry):
    return [
        {
            "task_id": entry["task_id"],
            "packet_sha256": entry["packet_sha256"],
            "source_public_sha256": entry["source_public_sha256"],
            "reviewer_token": "SYNTHETIC_TEST_REVIEWER_A",
            "recommendation": "ACCEPT",
        },
        {
            "task_id": entry["task_id"],
            "packet_sha256": entry["packet_sha256"],
            "source_public_sha256": entry["source_public_sha256"],
            "reviewer_token": "SYNTHETIC_TEST_REVIEWER_B",
            "recommendation": "REVISE",
        },
    ]


class BlindReviewFingerprintManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_l1_blind_review_manifest(
            COLLECTION, source_fact_cards=CARDS
        )
        cls.entry = cls.manifest["review_packets"][0]

    def test_all_current_candidate_packets_bound_without_admission(self):
        m = self.manifest
        self.assertEqual(m["packet_count"], 15)
        self.assertEqual(m["event_family_count"], 9)
        self.assertEqual(m["expert_adjudicated_count"], 0)
        self.assertEqual(m["rights_cleared_event_family_count"], 0)
        self.assertEqual(m["sft_records_emitted"], 0)
        self.assertFalse(m["official_splits_assigned"])
        self.assertFalse(m["gold_eligible"])
        self.assertFalse(m["training_authorized"])
        self.assertEqual(len({x["task_id"] for x in m["review_packets"]}), 15)
        for row in m["review_packets"]:
            self.assertEqual(len(row["packet_sha256"]), 64)
            self.assertEqual(len(row["source_public_sha256"]), 64)
            self.assertTrue(row["source_fact_bindings"])
            self.assertEqual(row["reviewer_slots"], ["A_UNASSIGNED", "B_UNASSIGNED"])
            self.assertEqual(row["review_status"], "PENDING_TWO_INDEPENDENT_EXPERTS")

    def test_manifest_is_deterministic_and_contains_no_model_or_private_material(self):
        self.assertEqual(
            self.manifest,
            build_l1_blind_review_manifest(
                COLLECTION, source_fact_cards=CARDS
            ),
        )
        rendered = json.dumps(self.manifest, ensure_ascii=False)
        for forbidden in (
            "formal_target", "internal_review", "curator_prompts",
            "diagnostic_logs", "reviewer_questions", "reviewer_token",
            "report_text", "machine_diagnosis",
        ):
            self.assertNotIn(forbidden, rendered)

    def test_historical_l0_source_refs_also_bound_to_packet_review(self):
        cards = {card["case_id"] for card in CARDS}
        by_task = {row["task_id"]: row for row in self.manifest["review_packets"]}
        for packet in COLLECTION["packets"]:
            expected = set(packet["source_fact_refs"])
            for hit in packet["history_context"]["items"]:
                expected.update(ref for ref in hit["source_refs"] if ref in cards)
            bound = {
                item["source_fact_ref"]
                for item in by_task[packet["task_id"]]["source_fact_bindings"]
            }
            self.assertEqual(bound, expected)

    def test_two_distinct_receipts_are_not_expert_verification(self):
        result = check_blind_review_pair(self.entry, _receipts(self.entry))
        self.assertFalse(result["recommendations_agree"])
        self.assertFalse(result["expert_adjudicated"])
        self.assertFalse(result["source_rights_verified"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn("reviewer_token", result)

    def test_stale_packet_fingerprint_rejected(self):
        rows = _receipts(self.entry)
        rows[0]["packet_sha256"] = "0" * 64
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPT_STALE_PACKET"):
            check_blind_review_pair(self.entry, rows)

    def test_stale_public_source_fingerprint_rejected(self):
        rows = _receipts(self.entry)
        rows[1]["source_public_sha256"] = "0" * 64
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPT_STALE_SOURCE"):
            check_blind_review_pair(self.entry, rows)

    def test_same_reviewer_token_rejected(self):
        rows = _receipts(self.entry)
        rows[1]["reviewer_token"] = rows[0]["reviewer_token"]
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPT_REVIEWER_NOT_INDEPENDENT"):
            check_blind_review_pair(self.entry, rows)

    def test_whitespace_alias_of_same_review_token_rejected(self):
        rows = _receipts(self.entry)
        rows[1]["reviewer_token"] = "  " + rows[0]["reviewer_token"] + " "
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPT_REVIEWER_NOT_INDEPENDENT"):
            check_blind_review_pair(self.entry, rows)

    def test_insufficient_receipts_and_unknown_status_rejected(self):
        rows = _receipts(self.entry)
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPTS_REQUIRE_TWO"):
            check_blind_review_pair(self.entry, rows[:1])
        rows[0]["recommendation"] = "GOLD"
        with self.assertRaisesRegex(L1BlindReviewManifestError, "REVIEW_RECEIPT_STATUS_INVALID"):
            check_blind_review_pair(self.entry, rows)


if __name__ == "__main__":
    unittest.main()
