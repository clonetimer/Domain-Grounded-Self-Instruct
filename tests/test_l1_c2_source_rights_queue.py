"""SYNTHETIC_TEST_ONLY: source rights remain unverified across duplicate L0 uses."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import sys
import unittest

from dgsi.l1_c2_scientific_dossier import build_c2_scientific_dossier
from dgsi.l1_c2_source_rights_queue import (
    C2SourceRightsQueueError, build_c2_source_rights_queue,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = json.loads((
    ROOT / "examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json"
).read_text(encoding="utf-8"))
SOURCES = json.loads((
    ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
).read_text(encoding="utf-8"))["cards"]


class C2SourceRightsQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = build_c2_scientific_dossier(
            COLLECTION, source_fact_cards=SOURCES
        )
        cls.queue = build_c2_source_rights_queue(cls.dossier)

    def test_15_tasks_reuse_12_bound_facts_across_only_seven_documents(self):
        queue = self.queue
        self.assertEqual(queue["task_count"], 15)
        self.assertEqual(queue["bound_l0_fact_count"], 12)
        self.assertEqual(queue["distinct_source_document_count"], 7)
        self.assertEqual(queue["collection_projection_sha256"],
                         self.dossier["collection_projection_sha256"])
        self.assertEqual(
            sum(len(d["bound_l0_fact_bindings"]) for d in queue["source_documents"]),
            12,
        )
        # The ISEE expert-system L0 is in the inventory but not in this C2
        # candidate cohort; rights queue must not inflate source coverage.
        bound = {
            b["case_id"] for d in queue["source_documents"]
            for b in d["bound_l0_fact_bindings"]
        }
        self.assertNotIn("LIT-ISEE-HPS-EXPERT-SYSTEM-008", bound)

    def test_shared_publication_is_not_four_distinct_licenses(self):
        docs = {r["source_id"]: r for r in self.queue["source_documents"]}
        tropics = docs["MITLL-TROPICS-LESSONS-2025"]
        self.assertEqual(len(tropics["bound_l0_fact_bindings"]), 4)
        self.assertIn("PUBLIC_FLIGHT_REPORT", tropics["source_classes"])
        self.assertIn("PUBLIC_GROUND_TEST_REPORT", tropics["source_classes"])
        lunar = docs["NASA-CR-66461"]
        self.assertEqual(len(lunar["bound_l0_fact_bindings"]), 2)

    def test_no_legal_or_training_approval_inferred(self):
        queue = self.queue
        for key in ("source_rights_verified", "gold_eligible",
                    "official_splits_assigned", "training_authorized"):
            self.assertIs(queue[key], False)
        self.assertTrue(queue["not_for_sft"])
        self.assertEqual(queue["rights_cleared_document_count"], 0)
        self.assertEqual(queue["sft_records_emitted"], 0)
        for row in queue["source_documents"]:
            self.assertEqual(row["rights_review_status"],
                             "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW")
            self.assertIsNone(row["rights_decision"])
            self.assertIsNone(row["license_or_permission_evidence_ref"])
            self.assertIsNone(row["permitted_reuse_scope"])
            self.assertFalse(row["rights_cleared"])
        serialized = json.dumps(queue, ensure_ascii=False)
        self.assertNotIn('"internal_review"', serialized)
        self.assertNotIn('"reviewer_token"', serialized)
        self.assertNotIn('"curator_prompts"', serialized)

    def test_source_fact_change_invalidates_cohort_fingerprint(self):
        modified = copy.deepcopy(SOURCES)
        modified[0]["phenomenon_analysis"] += " (review-only correction)"
        changed = build_c2_scientific_dossier(COLLECTION, source_fact_cards=modified)
        result = build_c2_source_rights_queue(changed)
        self.assertNotEqual(result["collection_projection_sha256"],
                            self.queue["collection_projection_sha256"])

    def test_same_source_id_with_inconsistent_title_rejected(self):
        changed = copy.deepcopy(self.dossier)
        for item in changed["items"]:
            for fact in item["l0_public_source_context"]:
                if fact["case_id"] == "LIT-TROPICS-FLIGHT-CRC-003-B":
                    fact["source_reference"]["source_title"] += " WRONG EDITION"
        with self.assertRaisesRegex(C2SourceRightsQueueError,
                                    "C2_RIGHTS_DOCUMENT_ID_COLLISION"):
            build_c2_source_rights_queue(changed)

    def test_missing_or_duplicate_l0_source_binding_rejected(self):
        changed = copy.deepcopy(self.dossier)
        changed["items"][0]["source_fact_bindings"].pop()
        with self.assertRaises(C2SourceRightsQueueError):
            build_c2_source_rights_queue(changed)
        changed = copy.deepcopy(self.dossier)
        changed["items"].append(copy.deepcopy(changed["items"][0]))
        with self.assertRaisesRegex(C2SourceRightsQueueError,
                                    "C2_RIGHTS_DUPLICATE_OR_INVALID_TASK"):
            build_c2_source_rights_queue(changed)

    def _tamper_second_occurrence(self, edit):
        """Change one repeated L0 reference without changing its bound digest."""
        from collections import Counter

        changed = copy.deepcopy(self.dossier)
        counts = Counter(
            fact["case_id"] for item in changed["items"]
            for fact in item["l0_public_source_context"]
        )
        repeated = next(case_id for case_id, count in counts.items() if count > 1)
        occurrences = 0
        for item in changed["items"]:
            for fact in item["l0_public_source_context"]:
                if fact["case_id"] == repeated:
                    occurrences += 1
                    if occurrences == 2:
                        edit(fact)
                        return changed
        self.fail("Synthetic fixture must contain a reused L0 case")

    def test_repeated_l0_cannot_change_publication_without_hash_change(self):
        changed = self._tamper_second_occurrence(
            lambda fact: fact["source_reference"].update({
                "source_id": "FORGED-SYNTHETIC-DOCUMENT",
                "source_title": "Wrong publication for same L0 digest",
            })
        )
        with self.assertRaisesRegex(
            C2SourceRightsQueueError, "C2_RIGHTS_L0_IDENTITY_DRIFT"
        ):
            build_c2_source_rights_queue(changed)

    def test_repeated_l0_cannot_change_event_family_without_hash_change(self):
        changed = self._tamper_second_occurrence(
            lambda fact: fact.update({"event_family_id": "FORGED-FAMILY"})
        )
        with self.assertRaisesRegex(
            C2SourceRightsQueueError, "C2_RIGHTS_L0_IDENTITY_DRIFT"
        ):
            build_c2_source_rights_queue(changed)

    def test_repeated_l0_cannot_change_source_locator_without_hash_change(self):
        changed = self._tamper_second_occurrence(
            lambda fact: fact["source_reference"].update({
                "source_locator": "FORGED-PAGE-999"
            })
        )
        with self.assertRaisesRegex(
            C2SourceRightsQueueError, "C2_RIGHTS_L0_IDENTITY_DRIFT"
        ):
            build_c2_source_rights_queue(changed)

    def test_repeated_l0_cannot_change_source_class_without_hash_change(self):
        changed = self._tamper_second_occurrence(
            lambda fact: fact.update({"source_class": "FORGED_SOURCE_CLASS"})
        )
        with self.assertRaisesRegex(
            C2SourceRightsQueueError, "C2_RIGHTS_L0_IDENTITY_DRIFT"
        ):
            build_c2_source_rights_queue(changed)

    def test_cannot_launder_training_approval_into_rights_queue(self):
        changed = copy.deepcopy(self.dossier)
        changed["training_authorized"] = True
        with self.assertRaisesRegex(C2SourceRightsQueueError,
                                    "C2_RIGHTS_DOSSIER_NOT_REVIEW_ONLY"):
            build_c2_source_rights_queue(changed)


if __name__ == "__main__":
    unittest.main()
