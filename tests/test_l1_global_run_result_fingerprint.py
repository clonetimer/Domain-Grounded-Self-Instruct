"""SYNTHETIC_TEST_ONLY: globally bind reused run refs to one ML result.

All examples are constructed from public, explicitly synthetic task fixtures.
No real diagnosis runs, telemetry, flight logs, or expert approvals are used.
"""
from __future__ import annotations

import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)
from tests.test_l1_global_case_run_family import (
    TROPICS_A,
    TROPICS_B,
    batches,
    case,
)


def same_run_batches():
    items = batches(TROPICS_A, TROPICS_B)
    case(items[1])["provenance"]["diagnosis_run_refs"] = list(
        case(items[0])["provenance"]["diagnosis_run_refs"]
    )
    return items


class GlobalRunResultFingerprintTests(unittest.TestCase):
    def test_same_family_same_run_and_identical_ml_result_is_allowed(self):
        report = audit_l1_cross_collection_lineage(same_run_batches())
        self.assertEqual(report["task_count"], 2)
        self.assertEqual(report["decision"], "STRUCTURAL_PREFLIGHT_ONLY")
        self.assertFalse(report["training_authorized"])

    def test_same_run_with_changed_ml_summary_is_rejected_without_splits(self):
        items = same_run_batches()
        case(items[1])["input"]["machine_diagnosis"]["machine_summary"] = (
            "SYNTHETIC_TEST_ONLY alternate upstream model result"
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_same_run_with_changed_candidate_score_is_rejected(self):
        items = same_run_batches()
        case(items[1])["input"]["machine_diagnosis"]["findings"][0]["score"] = 0.64
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_different_run_ids_can_have_different_ml_results_same_family(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["input"]["machine_diagnosis"]["machine_summary"] = (
            "SYNTHETIC_TEST_ONLY separate candidate run"
        )
        report = audit_l1_cross_collection_lineage(items)
        self.assertEqual(report["track_family_counts"]["LITERATURE_DERIVED_SYNTHETIC"], 1)
        self.assertFalse(report["training_authorized"])

    def test_reversed_order_still_blocks_conflicting_run_result(self):
        items = same_run_batches()
        case(items[0])["input"]["machine_diagnosis"]["machine_summary"] = (
            "SYNTHETIC_TEST_ONLY conflicting earlier record"
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(list(reversed(items)))


if __name__ == "__main__":
    unittest.main()
