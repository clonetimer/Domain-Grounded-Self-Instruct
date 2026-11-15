"""SYNTHETIC_TEST_ONLY review receipt and evidence-binding adversarial tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_coverage_review import (
    L1QualityGateError, REVIEW_DIMENSIONS, validate_blind_l1_review,
)
from dgsi.l1_review_receipts import (
    fingerprint_l1_review_material, validate_l1_review_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


def _fixture():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text("utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text("utf-8")
    )["cards"]
    return collection["packets"][0], cards


def _receipt(packet, cards):
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
                    "scores": {k: 4 for k in REVIEW_DIMENSIONS},
                    "finding_codes": ["NO_ISSUE"],
                    "decision": "ACCEPT_L1",
                }
                for token in ("SYNTHETIC-REVIEWER-A", "SYNTHETIC-REVIEWER-B")
            ],
        },
        "adjudication_status": "PENDING_REVIEWER_AUTHENTICATION",
    }


class L1ReviewReceiptTests(unittest.TestCase):
    def test_receipt_binds_synthetic_packet_and_l0_without_approving_gold(self):
        packet, cards = _fixture()
        result = validate_l1_review_receipt(
            packet, source_fact_cards=cards, receipt=_receipt(packet, cards)
        )
        self.assertEqual(result["decision"], "AWAITING_INDEPENDENT_REVIEWER_AUTHENTICATION")
        self.assertTrue(result["packet_binding_valid"])
        self.assertTrue(result["source_fact_binding_valid"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn(packet["task_id"], repr(result))

    def test_packet_change_after_review_fails_closed(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        packet["task_id"] += "-ALTERED-SYNTHETIC"
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_PACKET_CHANGED_SINCE_REVIEW"):
            validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)

    def test_source_fact_change_after_review_fails_closed(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        cards[0]["phenomenon_analysis"] += " SYNTHETIC_TEST_ONLY mutation"
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_L0_FACTS_CHANGED_SINCE_REVIEW"):
            validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)

    def test_curator_only_notes_are_not_review_material(self):
        packet, cards = _fixture()
        baseline = fingerprint_l1_review_material(packet, source_fact_cards=cards)
        packet["case"]["internal_review"]["curator_prompts"].append(
            "SYNTHETIC_TEST_ONLY internal-only note"
        )
        altered = fingerprint_l1_review_material(packet, source_fact_cards=cards)
        self.assertEqual(baseline, altered)

    def test_mutated_blinded_reference_fails_closed(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        receipt["blind_review"]["blinded_packet_ref"] = "SYNTHETIC-UNBOUND"
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_BLIND_TOKEN_NOT_BOUND_TO_PACKET"):
            validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)

    def test_altered_hash_and_extra_fields_fail_closed(self):
        packet, cards = _fixture()
        for patch, code in [
            ({"packet_sha256": "0" * 64}, "L1_REVIEW_PACKET_CHANGED_SINCE_REVIEW"),
            ({"packet_sha256": "unknown"}, "INVALID_L1_REVIEW_FINGERPRINT"),
            ({"extra_private_notes": "DO NOT UPLOAD"}, "INVALID_L1_REVIEW_RECEIPT_ENVELOPE"),
        ]:
            receipt = _receipt(packet, cards)
            receipt.update(patch)
            with self.subTest(patch=list(patch)), self.assertRaisesRegex(L1QualityGateError, code):
                validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)

    def test_blocker_finding_requires_secure_adjudication_even_if_both_accept(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        receipt["blind_review"]["assessments"][1]["finding_codes"] = ["FAULT_SOURCE_UNSUPPORTED"]
        receipt["adjudication_status"] = "PENDING_SECURE_ADJUDICATION"
        result = validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)
        self.assertEqual(result["decision"], "NEEDS_SECURE_ADJUDICATION")
        self.assertFalse(result["training_authorized"])

    def test_adjudication_status_cannot_be_self_declared_resolved(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        receipt["adjudication_status"] = "SECURELY_RESOLVED"
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_ADJUDICATION_STATE_MISMATCH"):
            validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)

    def test_whitespace_alias_does_not_prove_distinct_reviewers(self):
        packet, cards = _fixture()
        form = _receipt(packet, cards)["blind_review"]
        form["assessments"][1]["reviewer_token"] = " " + form["assessments"][0]["reviewer_token"] + " "
        with self.assertRaisesRegex(L1QualityGateError, "REVIEWER_TOKENS_MUST_BE_DISTINCT"):
            validate_blind_l1_review(form)

    def test_no_issue_cannot_coexist_with_blocking_finding(self):
        packet, cards = _fixture()
        form = _receipt(packet, cards)["blind_review"]
        form["assessments"][1]["finding_codes"] = ["NO_ISSUE", "SOURCE_FACT_OVERSTATEMENT"]
        with self.assertRaisesRegex(L1QualityGateError, "NO_ISSUE_CONTRADICTS_REVIEW_FINDINGS"):
            validate_blind_l1_review(form)

    def test_no_issue_cannot_mask_unacceptable_score(self):
        packet, cards = _fixture()
        form = _receipt(packet, cards)["blind_review"]
        form["assessments"][0]["scores"]["fault_source"] = 1
        with self.assertRaisesRegex(L1QualityGateError, "NO_ISSUE_CONTRADICTS_REVIEW_FINDINGS"):
            validate_blind_l1_review(form)

    def test_l0_domain_review_state_change_invalidates_existing_l1_receipt(self):
        packet, cards = _fixture()
        receipt = _receipt(packet, cards)
        source_card = next(card for card in cards if card["case_id"] == packet["source_fact_refs"][0])
        source_card["domain_review_status"] = "DOMAIN_EXPERT_CONFIRMED"
        source_card["domain_review_evidence_sha256"] = "a" * 64
        with self.assertRaisesRegex(L1QualityGateError, "L1_REVIEW_L0_FACTS_CHANGED_SINCE_REVIEW"):
            validate_l1_review_receipt(packet, source_fact_cards=cards, receipt=receipt)


if __name__ == "__main__":
    unittest.main()
