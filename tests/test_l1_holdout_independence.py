"""SYNTHETIC_TEST_ONLY: prospective holdout structural leakage checks.

No official split is assigned; all task labels in these tests are hypothetical.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_holdout_independence import (
    L1HoldoutIndependenceError,
    audit_l1_holdout_independence,
    check_hypothetical_holdout_partition,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json"
).read_text(encoding="utf-8"))
CARDS = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json"
).read_text(encoding="utf-8"))["cards"]


def _hypothetical_all_train():
    return {p["task_id"]: "train" for p in COLLECTION["packets"]}


class DocumentConnectedHoldoutTests(unittest.TestCase):
    def test_current_twenty_one_have_only_six_independent_groups(self):
        result = audit_l1_holdout_independence(
            copy.deepcopy(COLLECTION), source_fact_cards=copy.deepcopy(CARDS)
        )
        self.assertEqual(result["task_count"], 21)
        self.assertEqual(result["event_family_count"], 9)
        self.assertEqual(result["distinct_bound_source_document_count"], 7)
        self.assertEqual(result["independent_connected_group_count"], 6)
        self.assertEqual(result["group_task_sizes"], [1, 2, 3, 4, 5, 6])
        self.assertEqual(result["group_event_family_sizes"], [1, 1, 1, 1, 2, 3])
        self.assertFalse(result["official_splits_assigned"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn("SEASAT", json.dumps(result))

    def test_three_tropics_event_families_share_one_publication(self):
        assignments = _hypothetical_all_train()
        packet = next(p for p in COLLECTION["packets"] if
                      p["case"]["provenance"]["source_group"] ==
                      "LITERATURE-DERIVED:TROPICS-SLIPRING-QUALIFICATION")
        assignments[packet["task_id"]] = "test"
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError,
            "HOLDOUT_CONNECTED_GROUP_CROSSES_SPLITS",
        ):
            check_hypothetical_holdout_partition(
                COLLECTION, source_fact_cards=CARDS,
                hypothetical_task_splits=assignments,
            )

    def test_history_cassini_source_connects_fuse_target(self):
        assignments = _hypothetical_all_train()
        packet = next(p for p in COLLECTION["packets"] if
                      p["case"]["task_type"] == "historical_case_reuse")
        assignments[packet["task_id"]] = "test"
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError,
            "HOLDOUT_CONNECTED_GROUP_CROSSES_SPLITS",
        ):
            check_hypothetical_holdout_partition(
                COLLECTION, source_fact_cards=CARDS,
                hypothetical_task_splits=assignments,
            )

    def test_same_family_multiple_episodes_cannot_be_separated(self):
        assignments = _hypothetical_all_train()
        lunar = [p for p in COLLECTION["packets"] if
                 "LUNAR-ORBITER-III" in p["case"]["provenance"]["source_group"]]
        self.assertGreaterEqual(len(lunar), 2)
        assignments[lunar[0]["task_id"]] = "validation"
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError,
            "HOLDOUT_CONNECTED_GROUP_CROSSES_SPLITS",
        ):
            check_hypothetical_holdout_partition(
                COLLECTION, source_fact_cards=CARDS,
                hypothetical_task_splits=assignments,
            )

    def test_incomplete_or_unknown_hypothetical_assignment_rejected(self):
        assignments = _hypothetical_all_train()
        del assignments[next(iter(assignments))]
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError,
            "HOLDOUT_PARTITION_INCOMPLETE_OR_UNKNOWN_TASK",
        ):
            check_hypothetical_holdout_partition(
                COLLECTION, source_fact_cards=CARDS,
                hypothetical_task_splits=assignments,
            )

    def test_one_group_label_pass_does_not_authorize_training(self):
        report = check_hypothetical_holdout_partition(
            COLLECTION, source_fact_cards=CARDS,
            hypothetical_task_splits=_hypothetical_all_train(),
        )
        self.assertEqual(report["decision"], "HYPOTHETICAL_STRUCTURAL_CHECK_ONLY")
        self.assertFalse(report["training_authorized"])
        self.assertFalse(report["official_splits_assigned"])

    def test_source_document_identity_collision_is_rejected(self):
        cards = copy.deepcopy(CARDS)
        changed = next(c for c in cards if
                       c["source_reference"]["source_id"] ==
                       "MITLL-TROPICS-LESSONS-2025")
        changed["source_reference"]["source_title"] += " SYNTHETIC_TEST_ONLY"
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError, "HOLDOUT_SOURCE_DOCUMENT_ID_COLLISION",
        ):
            audit_l1_holdout_independence(
                COLLECTION, source_fact_cards=cards,
            )

    def test_invalid_proposed_label_rejected(self):
        assignments = _hypothetical_all_train()
        assignments[next(iter(assignments))] = "gold_holdout"
        with self.assertRaisesRegex(
            L1HoldoutIndependenceError, "HOLDOUT_PARTITION_INVALID_LABEL",
        ):
            check_hypothetical_holdout_partition(
                COLLECTION, source_fact_cards=CARDS,
                hypothetical_task_splits=assignments,
            )



    def test_six_new_task_variants_not_independent_holdout_events(self):
        # 016-021 are deliberately new *tasks*, not new source families.
        # Check each against the rest of the 21-task candidate.
        for suffix in ("016", "017", "018", "019", "020", "021"):
            with self.subTest(task_suffix=suffix):
                packet = next(p for p in COLLECTION["packets"]
                              if p["task_id"].endswith("-" + suffix))
                proposal = _hypothetical_all_train()
                proposal[packet["task_id"]] = "test"
                with self.assertRaisesRegex(
                    L1HoldoutIndependenceError,
                    "HOLDOUT_CONNECTED_GROUP_CROSSES_SPLITS",
                ):
                    check_hypothetical_holdout_partition(
                        COLLECTION, source_fact_cards=CARDS,
                        hypothetical_task_splits=proposal,
                    )

    def test_new_task_types_remain_unadmitted_synthetic(self):
        self.assertEqual(len(COLLECTION["packets"]), 21)
        self.assertEqual(COLLECTION["track"], "LITERATURE_DERIVED_SYNTHETIC")
        types = [p["case"]["task_type"] for p in COLLECTION["packets"]]
        self.assertEqual(types.count("conflict_reconciliation"), 2)
        self.assertEqual(types.count("evidence_sufficiency"), 5)
        for packet in COLLECTION["packets"]:
            self.assertEqual(packet["track"], "LITERATURE_DERIVED_SYNTHETIC")
        result = audit_l1_holdout_independence(COLLECTION, source_fact_cards=CARDS)
        self.assertFalse(result["official_splits_assigned"])
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])

if __name__ == "__main__":
    unittest.main()
