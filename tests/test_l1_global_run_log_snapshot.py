"""SYNTHETIC_TEST_ONLY: one upstream diagnosis run cannot silently change logs.

Uses invented run references and synthetic L1 fixtures. Neither synthetic logs
nor test results are real operations records, ML executions or expert approval.
"""
from __future__ import annotations

import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)
from tests.test_l1_global_run_result_fingerprint import same_run_batches
from tests.test_l1_global_case_run_family import (
    TROPICS_A, TROPICS_B, batches, case,
)


class GlobalRunLogSnapshotTests(unittest.TestCase):
    def test_same_run_and_same_log_snapshot_is_allowed(self):
        items = same_run_batches()
        self.assertNotEqual(case(items[0])["case_id"], case(items[1])["case_id"])
        report = audit_l1_cross_collection_lineage(items)
        self.assertEqual(report["task_count"], 2)
        self.assertFalse(report["training_authorized"])

    def test_same_run_different_log_content_blocked_with_distinct_cases(self):
        items = same_run_batches()
        case(items[1])["input"]["diagnostic_logs"][0]["content"] = (
            "SYNTHETIC_TEST_ONLY: conflicting log content under the same run."
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "^GLOBAL_DIAGNOSIS_RUN_LOG_SNAPSHOT_CONFLICT$"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_reversed_order_also_blocks_conflicting_log(self):
        items = same_run_batches()
        case(items[0])["input"]["diagnostic_logs"][0]["content"] = (
            "SYNTHETIC_TEST_ONLY: alternate log before the other task."
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "^GLOBAL_DIAGNOSIS_RUN_LOG_SNAPSHOT_CONFLICT$"
        ):
            audit_l1_cross_collection_lineage(list(reversed(items)))

    def test_different_run_refs_allow_distinct_log_snapshots(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["input"]["diagnostic_logs"][0]["content"] = (
            "SYNTHETIC_TEST_ONLY: a different upstream run has different logs."
        )
        report = audit_l1_cross_collection_lineage(items)
        self.assertEqual(report["task_count"], 2)
        self.assertEqual(report["decision"], "STRUCTURAL_PREFLIGHT_ONLY")
        self.assertFalse(report["training_authorized"])

    def test_same_run_changed_log_does_not_require_split_to_block(self):
        items = same_run_batches()
        for batch in items:
            self.assertEqual(batch["collection"]["split_assignments"], [])
        case(items[1])["input"]["diagnostic_logs"][0]["content"] = (
            "SYNTHETIC_TEST_ONLY: stale run ID paired with a new log snapshot."
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "^GLOBAL_DIAGNOSIS_RUN_LOG_SNAPSHOT_CONFLICT$"
        ):
            audit_l1_cross_collection_lineage(items)


if __name__ == "__main__":
    unittest.main()
