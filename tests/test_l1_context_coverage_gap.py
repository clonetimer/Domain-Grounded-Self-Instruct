"""SYNTHETIC_TEST_ONLY: metadata coverage is not review or SFT approval."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_context_coverage_gap import (
    L1ContextCoverageError, _packet_variants, audit_l1_context_coverage,
)

ROOT = Path(__file__).resolve().parents[1]
COLLECTION = ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json"
CARDS = ROOT / "examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json"


def fixture():
    return (
        json.loads(COLLECTION.read_text(encoding="utf-8")),
        json.loads(CARDS.read_text(encoding="utf-8"))["cards"],
    )


class L1ContextCoverageGapTests(unittest.TestCase):
    def test_current_21_cohort_exposes_real_history_scenario_gaps(self):
        cohort, cards = fixture()
        report = audit_l1_context_coverage(cohort, source_fact_cards=cards)
        self.assertEqual(report["packet_count"], 21)
        self.assertEqual(report["event_family_count"], 9)
        self.assertEqual(report["no_hit_packet_count"], 18)
        self.assertEqual(report["history_hit_packet_count"], 3)
        self.assertEqual(report["history_hit_item_count"], 3)
        counts = report["variant_packet_counts"]
        self.assertEqual(counts["NO_HIT"], 18)
        self.assertEqual(counts["REJECTED_PRESERVED"], 2)
        self.assertEqual(counts["PARTIALLY_CONFIRMED_PRESERVED"], 1)
        self.assertEqual(counts["HARDWARE_UNKNOWN"], 3)
        self.assertEqual(counts["CONFIRMED_APPLICABLE"], 0)
        self.assertEqual(counts["MULTIPLE_HITS"], 0)
        self.assertIn("CONFIRMED_APPLICABLE", report["missing_positive_variants"])
        self.assertEqual(report["review_pending_packet_count"], 21)

    def test_metadata_scenarios_do_not_authorize_sft(self):
        cohort, cards = fixture()
        report = audit_l1_context_coverage(cohort, source_fact_cards=cards)
        self.assertEqual(report["decision"], "REVIEW_REQUIRED_NOT_TRAINING_ADMISSION")
        self.assertEqual(report["sft_records_emitted"], 0)
        self.assertEqual(report["gold_eligible_count"], 0)
        self.assertFalse(report["training_authorized"])
        self.assertEqual(report["official_split_count"], 0)

    def test_negative_control_cases_are_never_positive_sft_examples(self):
        cohort, cards = fixture()
        report = audit_l1_context_coverage(cohort, source_fact_cards=cards)
        controls = report["negative_validator_controls_not_positive_sft"]
        self.assertIn("HISTORY_AVAILABLE_AFTER_CUTOFF", controls)
        self.assertIn("CURRENT_EVENT_FAMILY_AS_HISTORY", controls)
        self.assertNotIn("HISTORY_AVAILABLE_AFTER_CUTOFF", report["variant_packet_counts"])
        self.assertIn("CURRENT_LOGS_CONTRADICT_HISTORY", report["unassessable_from_metadata"])

    def test_report_never_echoes_ids_logs_targets_or_curator_review(self):
        cohort, cards = fixture()
        report = json.dumps(audit_l1_context_coverage(cohort, source_fact_cards=cards))
        first = cohort["packets"][0]
        for secret in (
            first["task_id"], first["case"]["case_id"],
            first["case"]["instruction"], "formal_target",
            "internal_review", "machine_diagnosis", "diagnostic_logs",
        ):
            self.assertNotIn(secret, report)

    def test_multi_hit_metadata_is_nonexclusive_and_preserves_mixed_status(self):
        packet = {"history_context": {"retrieval_status": "HIT", "items": [
            {"outcome_status": "CONFIRMED", "hardware_compatibility": "COMPATIBLE"},
            {"outcome_status": "REJECTED", "hardware_compatibility": "INCOMPATIBLE"},
        ]}}
        labels = _packet_variants(packet)
        self.assertIn("CONFIRMED_APPLICABLE", labels)
        self.assertIn("REJECTED_PRESERVED", labels)
        self.assertIn("HARDWARE_INCOMPATIBLE", labels)
        self.assertIn("MULTIPLE_HITS", labels)
        self.assertIn("MIXED_OUTCOME_HITS", labels)

    def test_no_hit_cannot_be_counted_as_a_historical_success(self):
        packet = {"history_context": {"retrieval_status": "NO_HIT", "items": []}}
        self.assertEqual(_packet_variants(packet), {"NO_HIT"})

    def test_tampered_packet_count_is_blocked_before_coverage(self):
        cohort, cards = fixture()
        cohort["packet_count"] -= 1
        with self.assertRaisesRegex(
            L1ContextCoverageError, "^CONTEXT_COVERAGE_COLLECTION_NOT_VALIDATED$"
        ):
            audit_l1_context_coverage(cohort, source_fact_cards=cards)

    def test_forged_real_track_is_blocked(self):
        cohort, cards = fixture()
        cohort["track"] = "REAL_CASE_CANDIDATE"
        with self.assertRaisesRegex(
            L1ContextCoverageError, "^CONTEXT_COVERAGE_SYNTHETIC_TRACK_ONLY$"
        ):
            audit_l1_context_coverage(cohort, source_fact_cards=cards)

    def test_future_history_is_rejected_by_existing_l1_validator(self):
        cohort, cards = fixture()
        hit = next(p for p in cohort["packets"]
                   if p["history_context"]["retrieval_status"] == "HIT")
        hit["history_context"]["items"][0]["hit_metadata"]["available_at"] = (
            "2099-01-01T00:00:00Z"
        )
        with self.assertRaisesRegex(
            L1ContextCoverageError, "^CONTEXT_COVERAGE_COLLECTION_NOT_VALIDATED$"
        ):
            audit_l1_context_coverage(cohort, source_fact_cards=cards)


if __name__ == "__main__":
    unittest.main()
