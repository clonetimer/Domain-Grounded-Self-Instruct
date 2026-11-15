"""SYNTHETIC_TEST_ONLY: global L1 event-family and Context holdout preflight.

All split plans below are invented adversarial assignments. None are official
dataset splits or independent expert approval, and no input is real ML output.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)

ROOT = Path(__file__).resolve().parents[1]
FUSE = "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012"
CASSINI = "L1-CASSINI-RWA-DRAG-SYNTH-008"
TROPICS_A = "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003"
TROPICS_B = "L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013"


def _fixtures(task_a=FUSE, task_b=CASSINI):
    raw = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
    cards = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))["cards"]
    batches = []
    for n, task_id in enumerate((task_a, task_b)):
        item = copy.deepcopy(raw)
        item["collection_id"] = "SYNTHETIC-GLOBAL-BATCH-" + str(n)
        item["packets"] = [p for p in item["packets"] if p["task_id"] == task_id]
        assert len(item["packets"]) == 1
        item["packet_count"] = 1
        item["split_assignments"] = []
        batches.append({"collection": item, "source_fact_cards": copy.deepcopy(cards)})
    return batches


def _plans(batches, first="validation", second="train"):
    return {
        batches[0]["collection"]["collection_id"]: {
            batches[0]["collection"]["packets"][0]["task_id"]: first
        },
        batches[1]["collection"]["collection_id"]: {
            batches[1]["collection"]["packets"][0]["task_id"]: second
        },
    }


class GlobalL1HoldoutTests(unittest.TestCase):
    def test_unassigned_pilot_remains_nontraining(self):
        batches = _fixtures()
        result = audit_l1_cross_collection_lineage(batches)
        self.assertEqual(result["collection_count"], 2)
        self.assertEqual(result["task_count"], 2)
        self.assertEqual(result["gold_eligible_count"], 0)
        self.assertFalse(result["training_authorized"])

    def test_fuse_cassini_other_split_history_is_blocked(self):
        batches = _fixtures()
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_HISTORY_EXPOSES_OTHER_SPLIT_TARGET"):
            audit_l1_cross_collection_lineage(
                batches, hypothetical_splits=_plans(batches)
            )

    def test_fuse_cassini_same_split_is_still_not_training_approved(self):
        batches = _fixtures()
        result = audit_l1_cross_collection_lineage(
            batches, hypothetical_splits=_plans(batches, "train", "train")
        )
        self.assertEqual(result["split_check_mode"], "HYPOTHETICAL_TEST_ONLY")
        self.assertFalse(result["training_authorized"])

    def test_same_target_family_in_two_collections_cannot_cross_splits(self):
        batches = _fixtures(TROPICS_A, TROPICS_B)
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_EVENT_FAMILY_CROSSES_SPLITS"):
            audit_l1_cross_collection_lineage(
                batches, hypothetical_splits=_plans(batches)
            )

    def test_partial_simulated_collection_map_is_rejected(self):
        batches = _fixtures()
        plan = _plans(batches)
        del plan[batches[1]["collection"]["collection_id"]]
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_HYPOTHETICAL_COLLECTION_COVERAGE_INCOMPLETE"):
            audit_l1_cross_collection_lineage(batches, hypothetical_splits=plan)

    def test_empty_hypothetical_task_map_fails_closed(self):
        batches = _fixtures()
        plan = _plans(batches)
        plan[batches[1]["collection"]["collection_id"]] = {}
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_SPLIT_MAP_INCOMPLETE"):
            audit_l1_cross_collection_lineage(batches, hypothetical_splits=plan)

    def test_task_identifier_reuse_across_collections_is_blocked(self):
        batches = _fixtures(FUSE, FUSE)
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_DUPLICATE_TASK_ID"):
            audit_l1_cross_collection_lineage(batches)

    def test_conflicting_version_of_same_source_card_fails_closed(self):
        batches = _fixtures()
        # Fictional metadata edit; the historical source is not amended.
        batches[1]["source_fact_cards"][0]["internal_review"]["quality_flags"].append(
            "SYNTHETIC_TEST_ONLY_MUTATION"
        )
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_SOURCE_CARD_VERSION_CONFLICT"):
            audit_l1_cross_collection_lineage(batches)

    def test_review_label_without_two_family_evidence_cannot_bind_alias(self):
        batches = _fixtures()
        f = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-FUSE-RWA-KAPTON-001")
        c = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-CASSINI-RWA-DRAG-007")
        invented_alias = {
            "alias_family_id": f["event_family_id"],
            "canonical_family_id": c["event_family_id"],
            "source_fact_refs": [f["case_id"]],
            "review_status": "DOMAIN_EXPERT_CONFIRMED",
        }
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_ALIAS_SOURCE_EVIDENCE_INCOMPLETE"):
            audit_l1_cross_collection_lineage(
                batches, reviewed_aliases=[invented_alias]
            )

    def test_explicit_false_alias_does_not_create_independent_history(self):
        batches = _fixtures()
        f = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-FUSE-RWA-KAPTON-001")
        c = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-CASSINI-RWA-DRAG-007")
        # Deliberately FALSE alias assertion for adversarial testing, not a
        # claim that the real FUSE and Cassini events share an identity.
        invented_alias = {
            "alias_family_id": c["event_family_id"],
            "canonical_family_id": f["event_family_id"],
            "source_fact_refs": [f["case_id"], c["case_id"]],
            "review_status": "DOMAIN_EXPERT_CONFIRMED",
        }
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_ALIAS_HISTORY_IS_CURRENT_EVENT"):
            audit_l1_cross_collection_lineage(
                batches, reviewed_aliases=[invented_alias]
            )

    def test_undecided_alias_is_not_considered_verified(self):
        batches = _fixtures()
        f = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-FUSE-RWA-KAPTON-001")
        c = next(c for c in batches[0]["source_fact_cards"] if c["case_id"] == "LIT-CASSINI-RWA-DRAG-007")
        alias = {
            "alias_family_id": c["event_family_id"],
            "canonical_family_id": f["event_family_id"],
            "source_fact_refs": [f["case_id"], c["case_id"]],
            "review_status": "REVIEW_REQUIRED",
        }
        with self.assertRaisesRegex(L1GlobalLineageError, "GLOBAL_ALIAS_NOT_DOMAIN_REVIEWED"):
            audit_l1_cross_collection_lineage(
                batches, reviewed_aliases=[alias]
            )


if __name__ == "__main__":
    unittest.main()
