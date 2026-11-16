"""SYNTHETIC_TEST_ONLY: cross-track L1 identities must never be reused.

All identities, source cards, and upstream diagnostics are test fixtures.
No real ML execution, operational log, engineer approval, or Gold claim.
"""
from __future__ import annotations

import copy
import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)
from tests.test_l1_task_packet import make_packet, source_card


def dual_track_batches():
    synthetic = make_packet(with_history=False)
    real = make_packet(track="REAL_CASE_CANDIDATE", with_history=False)
    public_card = source_card()
    user_card = source_card("USER_SUPPLIED_CASE")
    user_card["case_id"] = "L0-SYNTHETIC-TEST-ONLY-USER-SOURCE-001"
    user_card["event_status"] = "USER_REPORTED_CASE"
    real["source_fact_refs"] = [user_card["case_id"]]

    def collection(packet, suffix):
        return {
            "schema_version": "dgsi-l1-task-packet-collection.v1",
            "collection_id": "SYNTHETIC-TEST-ONLY-MIXED-TRACK-" + suffix,
            "track": packet["track"],
            "packet_count": 1,
            "data_status": "REVIEW_REQUIRED",
            "split_policy": "No official split before independent expert review.",
            "packets": [packet],
            "gold_eligible": False,
            "training_authorized": False,
        }

    return [
        {"collection": collection(synthetic, "PUBLIC"),
         "source_fact_cards": [public_card]},
        {"collection": collection(real, "USER"),
         "source_fact_cards": [user_card]},
    ]


def current_case(batch):
    return batch["collection"]["packets"][0]["case"]


class GlobalTrackIdentityIsolationTests(unittest.TestCase):
    def test_separate_real_candidate_and_synthetic_case_run_ids_are_allowed(self):
        result = audit_l1_cross_collection_lineage(dual_track_batches())
        self.assertEqual(result["task_count"], 2)
        self.assertEqual(result["track_task_counts"]["REAL_CASE_CANDIDATE"], 1)
        self.assertEqual(result["track_task_counts"]["LITERATURE_DERIVED_SYNTHETIC"], 1)
        self.assertEqual(result["gold_eligible_count"], 0)
        self.assertFalse(result["training_authorized"])

    def test_synthetic_case_id_cannot_be_reused_by_real_candidate(self):
        batches = dual_track_batches()
        current_case(batches[1])["case_id"] = current_case(batches[0])["case_id"]
        with self.assertRaisesRegex(L1GlobalLineageError, "^GLOBAL_CASE_ID_CROSSES_TRACKS$"):
            audit_l1_cross_collection_lineage(batches)

    def test_case_id_collision_rejected_in_reverse_order(self):
        batches = dual_track_batches()
        current_case(batches[0])["case_id"] = current_case(batches[1])["case_id"]
        with self.assertRaisesRegex(L1GlobalLineageError, "^GLOBAL_CASE_ID_CROSSES_TRACKS$"):
            audit_l1_cross_collection_lineage(list(reversed(batches)))

    def test_synthetic_diagnosis_run_cannot_be_reclassified_as_real(self):
        batches = dual_track_batches()
        current_case(batches[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            current_case(batches[0])["provenance"]["diagnosis_run_refs"]
        )
        with self.assertRaisesRegex(L1GlobalLineageError, "^GLOBAL_DIAGNOSIS_RUN_CROSSES_TRACKS$"):
            audit_l1_cross_collection_lineage(batches)

    def test_run_cross_track_collision_rejected_in_reverse_order(self):
        batches = dual_track_batches()
        current_case(batches[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            current_case(batches[0])["provenance"]["diagnosis_run_refs"]
        )
        with self.assertRaisesRegex(L1GlobalLineageError, "^GLOBAL_DIAGNOSIS_RUN_CROSSES_TRACKS$"):
            audit_l1_cross_collection_lineage(list(reversed(batches)))


if __name__ == "__main__":
    unittest.main()
