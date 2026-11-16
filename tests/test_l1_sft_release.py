"""SYNTHETIC_TEST_ONLY: L1 release is blocked even after metadata preflight.

No live flight record, verified ML run or authenticated expert is used.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from dgsi.l1_global_lineage import L1GlobalLineageError
from dgsi.l1_sft_release import (
    L1SftReleaseError, preflight_l1_sft_release, require_l1_sft_release,
)


ROOT = Path(__file__).resolve().parents[1]


def _batches():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json")
        .read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json")
        .read_text(encoding="utf-8")
    )["cards"]
    return [{"collection": collection, "source_fact_cards": cards}]


class L1SftReleasePreflightTests(unittest.TestCase):
    def test_current_15_synthetic_packets_remain_blocked(self):
        report = preflight_l1_sft_release(_batches())
        self.assertEqual(report["task_count"], 15)
        self.assertEqual(report["decision"], "BLOCKED_PENDING_EXTERNAL_ADMISSION")
        self.assertEqual(report["receipt_missing_packet_count"], 15)
        self.assertEqual(report["official_split_missing_packet_count"], 15)
        self.assertEqual(report["sft_records_emitted"], 0)
        self.assertEqual(report["gold_eligible_count"], 0)
        self.assertFalse(report["training_authorized"])
        self.assertEqual(
            report["track_task_counts"], {"LITERATURE_DERIVED_SYNTHETIC": 15}
        )

    def test_report_is_metadata_only_and_never_echoes_diagnostic_material(self):
        batches = _batches()
        result = json.dumps(preflight_l1_sft_release(batches), ensure_ascii=False)
        first = batches[0]["collection"]["packets"][0]
        self.assertNotIn(first["task_id"], result)
        self.assertNotIn(first["case"]["case_id"], result)
        for secret in ("formal_target", "internal_review", "historical_cases",
                       "machine_diagnosis", "source_fact_refs"):
            self.assertNotIn(secret, result)

    def test_future_serializer_guard_never_serializes_unapproved_samples(self):
        with self.assertRaisesRegex(
            L1SftReleaseError, "^L1_SFT_RELEASE_NOT_AUTHORIZED$"
        ):
            require_l1_sft_release(_batches())

    def test_unsigned_receipt_like_metadata_cannot_grant_release(self):
        batches = _batches()
        cid = batches[0]["collection"]["collection_id"]
        receipts = {cid: [{"task_id": p["task_id"], "receipt": {}}
                          for p in batches[0]["collection"]["packets"]]}
        # Even if a future receipt validator returns success, the external
        # reviewer-identity/IP/privacy/consent authority remains absent.
        with patch("dgsi.l1_sft_release.audit_l1_review_receipt_batch",
                   return_value={"decision": "RECEIPTS_BOUND"}):
            report = preflight_l1_sft_release(batches, receipt_batches=receipts)
            self.assertEqual(report["receipt_bound_packet_count"], 15)
            self.assertEqual(report["decision"], "BLOCKED_PENDING_EXTERNAL_ADMISSION")
            with self.assertRaisesRegex(
                L1SftReleaseError, "L1_SFT_RELEASE_NOT_AUTHORIZED"
            ):
                require_l1_sft_release(batches, receipt_batches=receipts)

    def test_unknown_receipt_collection_rejected(self):
        with self.assertRaisesRegex(
            L1SftReleaseError, "^L1_SFT_UNKNOWN_RECEIPT_COLLECTION$"
        ):
            preflight_l1_sft_release(_batches(), receipt_batches={"UNKNOWN": []})

    def test_malformed_receipt_mapping_rejected(self):
        with self.assertRaisesRegex(
            L1SftReleaseError, "^L1_SFT_RECEIPT_BATCHES_INVALID$"
        ):
            preflight_l1_sft_release(_batches(), receipt_batches={"x": "not a list"})

    def test_invalid_global_lineage_is_not_downgraded_to_advisory(self):
        batches = _batches()
        second = copy.deepcopy(batches[0])
        second["collection"]["collection_id"] = "DUPLICATE-TASKS"
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_DUPLICATE_TASK_ID"
        ):
            preflight_l1_sft_release([batches[0], second])


if __name__ == "__main__":
    unittest.main()
