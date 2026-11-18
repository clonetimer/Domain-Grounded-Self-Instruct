"""SYNTHETIC-only tests: AstroGraph history hits are not current truth or Gold."""
from __future__ import annotations

import copy
import unittest

from dgsi.history_temporal_gate import HistoryTemporalGateError, screen_historical_memory_hit


def fixture():
    return {
        "case_id": "SYNTHETIC-PRIOR-01",
        "source_group_id": "SYNTHETIC-OTHER-EPISODE",
        "verified_fault_id": "FAULT-TEST-A",
        "proposed_fault_id": "FAULT-TEST-A",
        "truth_source_ref": "synthetic://audit/reference",
        "reviewer": "synthetic-independent-reviewer",
        "equipment_scope": "SYNTHETIC-MOCK-RW",
        "snapshot": 3,
        "status": "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH",
        "diagnostic_vote_allowed": False,
        "relation_status": "CONSISTENT_HISTORICAL_CASE",
    }


def screen(hit):
    return screen_historical_memory_hit(
        hit,
        analysis_cutoff="2026-05-02T08:00:00Z",
        current_source_group_id="SYNTHETIC-CURRENT-EPISODE",
        equipment_scope="SYNTHETIC-MOCK-RW",
    )


class HistoryTemporalGateSyntheticTests(unittest.TestCase):
    def test_unmodified_current_astrograph_hit_lacks_asof_metadata(self):
        result = screen(fixture())
        self.assertEqual(result["decision"], "BLOCKED")
        self.assertIn("HISTORY_AS_OF_AVAILABILITY_NOT_VERIFIED", result["blockers"])
        self.assertIn("HISTORY_INDEPENDENT_VERIFICATION_TIME_NOT_VERIFIED", result["blockers"])
        self.assertFalse(result["current_root_cause_confirmed"])

    def test_future_availability_is_postdecision_leak(self):
        hit = fixture()
        hit.update(verified_at="2026-05-02T09:00:00Z", available_at="2026-05-02T09:00:00Z")
        result = screen(hit)
        self.assertIn("HISTORY_AVAILABLE_AFTER_ANALYSIS_CUTOFF", result["blockers"])
        self.assertIn("HISTORY_VERIFIED_AFTER_ANALYSIS_CUTOFF", result["blockers"])

    def test_availability_before_verification_blocks(self):
        hit = fixture()
        hit.update(verified_at="2026-05-02T07:59:00Z", available_at="2026-05-02T07:00:00Z")
        self.assertIn("HISTORY_AVAILABLE_BEFORE_VERIFICATION", screen(hit)["blockers"])

    def test_naive_asof_times_block(self):
        hit = fixture()
        hit.update(verified_at="2026-05-01T12:00:00", available_at="2026-05-01T12:05:00")
        self.assertIn("HISTORY_AS_OF_AVAILABILITY_NOT_VERIFIED", screen(hit)["blockers"])

    def test_same_incident_family_reuse_blocks(self):
        hit = fixture()
        hit["source_group_id"] = "SYNTHETIC-CURRENT-EPISODE"
        self.assertIn("SAME_INCIDENT_FAMILY_REUSE", screen(hit)["blockers"])

    def test_cross_equipment_reuse_blocks(self):
        hit = fixture()
        hit["equipment_scope"] = "SYNTHETIC-OTHER-SATELLITE"
        self.assertIn("EQUIPMENT_SCOPE_MISMATCH", screen(hit)["blockers"])

    def test_historical_vote_is_never_allowed(self):
        hit = fixture()
        hit["diagnostic_vote_allowed"] = True
        self.assertIn("HISTORICAL_CASE_CANNOT_VOTE_CURRENT_TRUTH", screen(hit)["blockers"])

    def test_missing_truth_source_reference_blocks(self):
        hit = fixture()
        hit["truth_source_ref"] = ""
        self.assertIn("HISTORY_TRUTH_SOURCE_REF_MISSING", screen(hit)["blockers"])

    def test_unsupported_review_status_blocks(self):
        hit = fixture()
        hit["status"] = "PENDING"
        self.assertIn("HISTORICAL_CONFIRMATION_NOT_ESTABLISHED", screen(hit)["blockers"])

    def test_misclassification_relation_must_remain_explicit(self):
        hit = fixture()
        hit["verified_fault_id"] = "FAULT-TEST-B"
        self.assertIn("HISTORY_RELATION_STATUS_MISMATCH", screen(hit)["blockers"])
        hit["relation_status"] = "PRIOR_UPSTREAM_MISCLASSIFICATION"
        self.assertNotIn("HISTORY_RELATION_STATUS_MISMATCH", screen(hit)["blockers"])

    def test_review_snapshot_needs_valid_integer(self):
        hit = fixture()
        hit["snapshot"] = True
        self.assertIn("HISTORY_SNAPSHOT_UNVERIFIED", screen(hit)["blockers"])

    def test_valid_synthetic_temporal_metadata_never_means_gold(self):
        # A fabricated timeline can pass metadata comparison, not source
        # authentication. The gate intentionally does not emit case material.
        hit = fixture()
        hit.update(verified_at="2026-04-30T05:00:00Z", available_at="2026-04-30T06:00:00Z")
        report = screen(hit)
        self.assertEqual(report["decision"], "PASS_TEMPORAL_METADATA_ONLY")
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["current_root_cause_confirmed"])
        self.assertTrue(report["requires_authenticated_source_and_independent_review"])
        self.assertNotIn("case_id", report)
        self.assertNotIn("truth_source_ref", report)

    def test_utc_offset_comparison_not_string_comparison(self):
        hit = fixture()
        hit.update(verified_at="2026-05-02T08:15:00+09:00", available_at="2026-05-02T08:30:00+09:00")
        self.assertEqual(screen(hit)["decision"], "PASS_TEMPORAL_METADATA_ONLY")

    def test_invalid_cutoff_rejected_without_echo(self):
        with self.assertRaisesRegex(HistoryTemporalGateError, "^INVALID_ANALYSIS_CUTOFF$"):
            screen_historical_memory_hit(
                fixture(),
                analysis_cutoff="no date",
                current_source_group_id="SYNTHETIC-CURRENT-EPISODE",
                equipment_scope="SYNTHETIC-MOCK-RW",
            )

    def test_unbound_equipment_scope_rejected(self):
        with self.assertRaisesRegex(HistoryTemporalGateError, "^EQUIPMENT_SCOPE_REQUIRED$"):
            screen_historical_memory_hit(
                fixture(),
                analysis_cutoff="2026-05-02T08:00:00Z",
                current_source_group_id="SYNTHETIC-CURRENT-EPISODE",
                equipment_scope="UNKNOWN",
            )

    def test_malformed_hit_rejected(self):
        with self.assertRaisesRegex(HistoryTemporalGateError, "^INVALID_HISTORY_HIT$"):
            screen_historical_memory_hit(
                [], analysis_cutoff="2026-05-02T08:00:00Z",
                current_source_group_id="SYNTHETIC-CURRENT-EPISODE",
                equipment_scope="SYNTHETIC-MOCK-RW",
            )


if __name__ == "__main__":
    unittest.main()
