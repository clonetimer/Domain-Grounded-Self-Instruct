"""SYNTHETIC_TEST_ONLY complete L1 review-receipt batch audit tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_coverage_review import L1QualityGateError, REVIEW_DIMENSIONS
from dgsi.l1_review_receipts import (
    audit_l1_review_receipt_batch,
    fingerprint_l1_review_material,
)

ROOT = Path(__file__).resolve().parents[1]


def _fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


def _receipt(packet, cards, *, finding="NO_ISSUE"):
    fp = fingerprint_l1_review_material(packet, source_fact_cards=cards)
    return {
        "schema_version": "dgsi-l1-review-binding.v1",
        "packet_sha256": fp["packet_sha256"],
        "source_fact_cards_sha256": fp["source_fact_cards_sha256"],
        "blind_review": {
            "schema_version": "dgsi-l1-blind-review.v1",
            "blinded_packet_ref": "sha256:" + fp["packet_sha256"],
            "assessments": [
                {
                    "reviewer_token": token,
                    "scores": {dimension: 4 for dimension in REVIEW_DIMENSIONS},
                    "finding_codes": [finding],
                    "decision": "ACCEPT_L1",
                }
                for token in ("SYNTHETIC-REVIEWER-A", "SYNTHETIC-REVIEWER-B")
            ],
        },
        "adjudication_status": (
            "PENDING_SECURE_ADJUDICATION" if finding != "NO_ISSUE"
            else "PENDING_REVIEWER_AUTHENTICATION"
        ),
    }


class L1ReviewReceiptBatchTests(unittest.TestCase):
    def _all_receipts(self, collection, cards):
        return [
            {"task_id": packet["task_id"], "receipt": _receipt(packet, cards)}
            for packet in collection["packets"]
        ]

    def test_all_fifteen_packets_have_exactly_one_bound_receipt(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        result = audit_l1_review_receipt_batch(
            collection, source_fact_cards=cards, receipts=receipts
        )
        self.assertEqual(result["packet_count"], 15)
        self.assertEqual(result["receipt_count"], 15)
        self.assertEqual(result["packet_binding_valid_count"], 15)
        self.assertEqual(result["source_binding_valid_count"], 15)
        self.assertEqual(result["reviewer_authentication_pending_count"], 15)
        self.assertEqual(result["l1_experiment_approval_count"], 0)
        self.assertEqual(result["gold_eligible_count"], 0)
        self.assertEqual(
            result["source_fact_domain_review_status_counts"]
            ["AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION"],
            12,
        )
        self.assertFalse(result["training_authorized"])
        self.assertNotIn(collection["packets"][0]["task_id"], repr(result))

    def test_missing_task_receipt_fails_closed(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)[:-1]
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_RECEIPT_COVERAGE_INCOMPLETE"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=receipts)

    def test_duplicate_task_receipt_fails_closed(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        receipts.append(copy.deepcopy(receipts[0]))
        with self.assertRaisesRegex(L1QualityGateError, "DUPLICATE_L1_REVIEW_RECEIPT_TASK"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=receipts)

    def test_unknown_task_receipt_fails_closed(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        receipts[-1]["task_id"] = "UNKNOWN-SYNTHETIC-TASK"
        with self.assertRaisesRegex(L1QualityGateError, "UNKNOWN_L1_REVIEW_RECEIPT_TASK"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=receipts)

    def test_receipt_for_one_packet_cannot_be_reused_for_another(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        receipts[1]["receipt"] = copy.deepcopy(receipts[0]["receipt"])
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_PACKET_CHANGED_SINCE_REVIEW"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=receipts)

    def test_one_substantive_finding_requires_secure_adjudication(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        receipts[4]["receipt"] = _receipt(
            collection["packets"][4], cards, finding="SOURCE_FACT_OVERSTATEMENT"
        )
        result = audit_l1_review_receipt_batch(
            collection, source_fact_cards=cards, receipts=receipts
        )
        self.assertEqual(result["secure_adjudication_required_count"], 1)
        self.assertEqual(result["reviewer_authentication_pending_count"], 14)
        self.assertEqual(result["l1_experiment_approval_count"], 0)

    def test_receipt_source_facts_must_be_current(self):
        collection, cards = _fixtures()
        receipts = self._all_receipts(collection, cards)
        cards[0]["phenomenon_analysis"] += " SYNTHETIC_TEST_ONLY source mutation"
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_L0_FACTS_CHANGED_SINCE_REVIEW"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=receipts)

    def test_batch_rejects_non_list_receipts(self):
        collection, cards = _fixtures()
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_RECEIPT_BATCH_NOT_LIST"):
            audit_l1_review_receipt_batch(collection, source_fact_cards=cards, receipts=None)


if __name__ == "__main__":
    unittest.main()
