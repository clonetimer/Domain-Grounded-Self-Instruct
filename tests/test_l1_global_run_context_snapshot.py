"""SYNTHETIC_TEST_ONLY: reused ML run ID binds one physical/mission context.

All spacecraft IDs, run refs and diagnostic records are illustrative fixtures.
No real operation, ML execution or expert conclusion is represented here.
"""
from __future__ import annotations

import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)
from tests.test_l1_global_run_result_fingerprint import same_run_batches
from tests.test_l1_global_case_run_family import (
    TROPICS_A,
    TROPICS_B,
    batches,
    case,
)


class GlobalRunContextSnapshotTests(unittest.TestCase):
    def test_same_run_and_identical_context_accepted(self):
        items = same_run_batches()
        self.assertNotEqual(case(items[0])["case_id"], case(items[1])["case_id"])
        result = audit_l1_cross_collection_lineage(items)
        self.assertEqual(result["task_count"], 2)
        self.assertFalse(result["training_authorized"])

    def test_same_run_with_different_spacecraft_configuration_rejected(self):
        items = same_run_batches()
        case(items[1])["input"]["spacecraft_context"]["configuration"]["interface_scope"] = (
            "SYNTHETIC_TEST_ONLY-ALTERNATE-INTERFACE"
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError,
            "^GLOBAL_DIAGNOSIS_RUN_CONTEXT_SNAPSHOT_CONFLICT$",
        ):
            audit_l1_cross_collection_lineage(items)

    def test_same_run_with_different_mission_operations_rejected(self):
        items = same_run_batches()
        case(items[1])["input"]["operational_context"]["recent_operations"] = [
            "SYNTHETIC_TEST_ONLY: changed operating history under reused ML run ID."
        ]
        with self.assertRaisesRegex(
            L1GlobalLineageError,
            "^GLOBAL_DIAGNOSIS_RUN_CONTEXT_SNAPSHOT_CONFLICT$",
        ):
            audit_l1_cross_collection_lineage(items)

    def test_reversed_batch_order_also_rejects_changed_context(self):
        items = same_run_batches()
        case(items[0])["input"]["spacecraft_context"]["spacecraft_id"] = (
            "SYNTHETIC_TEST_ONLY-OTHER-SPACECRAFT"
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError,
            "^GLOBAL_DIAGNOSIS_RUN_CONTEXT_SNAPSHOT_CONFLICT$",
        ):
            audit_l1_cross_collection_lineage(list(reversed(items)))

    def test_different_run_refs_allow_different_operational_contexts(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["input"]["operational_context"]["recent_operations"] = [
            "SYNTHETIC_TEST_ONLY: separate upstream run and mission scenario."
        ]
        result = audit_l1_cross_collection_lineage(items)
        self.assertEqual(result["decision"], "STRUCTURAL_PREFLIGHT_ONLY")
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
