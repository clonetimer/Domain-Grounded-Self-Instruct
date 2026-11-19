"""Synthetic counterfactuals and read-only REV1 structure regression for P5-C16."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_model_visible_source_holdout import (
    audit_l1_model_visible_source_holdout,
)
from dgsi.l1_source_document_holdout import L1DocumentHoldoutError

ROOT = Path(__file__).resolve().parents[1]


def fixtures():
    collection = json.loads(
        (ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json")
        .read_text(encoding="utf-8")
    )
    cards = json.loads(
        (ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json")
        .read_text(encoding="utf-8")
    )["cards"]
    return collection, cards


def find_task(collection, suffix):
    return next(p for p in collection["packets"] if p["task_id"].endswith(suffix))


class VisibleHoldoutTests(unittest.TestCase):
    def test_rev1_history_connects_fuse_and_cassini_documents(self):
        collection, cards = fixtures()
        result = audit_l1_model_visible_source_holdout(collection, cards)
        self.assertEqual(result["task_count"], 21)
        self.assertEqual(result["primary_document_count"], 7)
        self.assertEqual(result["primary_document_cluster_count"], 7)
        self.assertEqual(result["model_visible_document_cluster_count"], 6)
        self.assertEqual(result["history_exposed_public_source_ids"], ["NASA-LLIS-1416"])
        cluster = next(
            c for c in result["model_visible_holdout_clusters"]
            if "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012" in c["task_ids"]
        )
        self.assertIn("L1-CASSINI-RWA-DRAG-SYNTH-008", cluster["task_ids"])
        self.assertIn("NASA-LLIS-1416", cluster["visible_source_ids"])
        self.assertIn("FUSE-SPIE-2002-RWA", cluster["visible_source_ids"])
        self.assertFalse(result["historical_asof_certified"])
        self.assertFalse(result["training_authorized"])

    def test_same_history_case_stays_in_single_group(self):
        collection, cards = fixtures()
        result = audit_l1_model_visible_source_holdout(collection, cards)
        cluster = next(c for c in result["model_visible_holdout_clusters"]
                       if "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003" in c["task_ids"])
        self.assertIn("L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013", cluster["task_ids"])

    def test_fuse_training_and_cassini_test_conflict(self):
        collection, cards = fixtures()
        plan = {p["task_id"]: "train" for p in collection["packets"]}
        plan["L1-CASSINI-RWA-DRAG-SYNTH-008"] = "test"
        with self.assertRaisesRegex(L1DocumentHoldoutError, "CROSS_SPLIT_EXPOSURE"):
            audit_l1_model_visible_source_holdout(collection, cards, hypothetical_splits=plan)

    def test_hypothetical_safe_assignment_is_never_authorized(self):
        collection, cards = fixtures()
        plan = {p["task_id"]: "train" for p in collection["packets"]}
        outcome = audit_l1_model_visible_source_holdout(collection, cards, hypothetical_splits=plan)
        self.assertEqual(outcome["decision"], "HYPOTHETICAL_VISIBLE_SOURCE_SAFE")
        self.assertFalse(outcome["official_splits_assigned"])
        self.assertFalse(outcome["training_authorized"])

    def test_without_fuse_history_or_cassini_evidence_original_seven_groups_return(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        fuse = find_task(collection, "-012")
        fuse["history_context"]["items"] = []
        fuse["history_context"]["retrieval_status"] = "NO_HIT"
        fuse["case"]["input"]["historical_cases"] = []
        fuse["case"]["input"]["knowledge_evidence"] = [
            e for e in fuse["case"]["input"]["knowledge_evidence"]
            if e["source_id"] != "NASA-LLIS-1416"
        ]
        outcome = audit_l1_model_visible_source_holdout(collection, cards)
        self.assertEqual(outcome["model_visible_document_cluster_count"], 7)

    def test_unknown_public_evidence_fails_closed(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        find_task(collection, "-012")["case"]["input"]["knowledge_evidence"][1]["source_id"] = "UNKNOWN-DOC"
        with self.assertRaisesRegex(L1DocumentHoldoutError, "UNRESOLVED_PUBLIC_DOCUMENT"):
            audit_l1_model_visible_source_holdout(collection, cards)

    def test_unknown_history_source_does_not_guess_document(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        find_task(collection, "-012")["history_context"]["items"][0]["source_refs"] = ["UNKNOWN-REAL-DOCUMENT"]
        with self.assertRaisesRegex(L1DocumentHoldoutError, "HISTORY_SOURCE_UNRESOLVED"):
            audit_l1_model_visible_source_holdout(collection, cards)

    def test_history_case_prompt_cannot_silently_disagree_with_manifest(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        find_task(collection, "-012")["case"]["input"]["historical_cases"] = []
        with self.assertRaisesRegex(L1DocumentHoldoutError, "HISTORY_PROMPT_MISMATCH"):
            audit_l1_model_visible_source_holdout(collection, cards)

    def test_shared_explicit_synthetic_history_ref_also_connects_groups(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        target = find_task(collection, "-001")
        donor = find_task(collection, "-003")
        target["history_context"]["items"] = copy.deepcopy(donor["history_context"]["items"])
        target["case"]["input"]["historical_cases"] = copy.deepcopy(donor["case"]["input"]["historical_cases"])
        result = audit_l1_model_visible_source_holdout(collection, cards)
        self.assertEqual(result["model_visible_document_cluster_count"], 5)

    def test_missing_historical_source_metadata_fails_closed(self):
        collection, cards = fixtures()
        collection = copy.deepcopy(collection)
        find_task(collection, "-012")["history_context"]["items"][0]["source_refs"] = []
        with self.assertRaisesRegex(L1DocumentHoldoutError, "HISTORY_SOURCE_MISSING"):
            audit_l1_model_visible_source_holdout(collection, cards)


if __name__ == "__main__":
    unittest.main()
