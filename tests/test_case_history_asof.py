"""SYNTHETIC ONLY: historical memory as-of binding adversarial contract tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.case_history_asof import CaseHistoryAsOfError, audit_case_history_asof

_BASE = json.loads(
    (Path(__file__).resolve().parents[1] /
     "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8")
)
_SCOPE = "reaction_wheel_2"


def synthetic_case(confirmed=True):
    case = copy.deepcopy(_BASE)
    if confirmed:
        case["input"]["historical_cases"][0]["outcome_status"] = "CONFIRMED"
    return case


def synthetic_hit():
    return {
        "case_id": "HIST-ADCS-017",
        "source_group_id": "SYNTHETIC-PRIOR-INCIDENT",
        "verified_fault_id": "SYNTHETIC-FAULT",
        "proposed_fault_id": "SYNTHETIC-FAULT",
        "truth_source_ref": "synthetic://independent-verification",
        "reviewer": "SYNTHETIC-REVIEWER",
        "equipment_scope": _SCOPE,
        "snapshot": 2,
        "status": "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH",
        "diagnostic_vote_allowed": False,
        "relation_status": "CONSISTENT_HISTORICAL_CASE",
        "verified_at": "2026-04-11T08:00:00Z",
        "available_at": "2026-04-11T09:00:00Z",
    }


class CaseHistoryAsOfSyntheticTests(unittest.TestCase):
    def assess(self, case=None, hits=None, scope=_SCOPE):
        return audit_case_history_asof(
            synthetic_case() if case is None else case,
            [synthetic_hit()] if hits is None else hits,
            equipment_scope=scope,
        )

    def test_verified_prior_history_is_metadata_only(self):
        result = self.assess()
        self.assertEqual(result["decision"], "PASS_ASOF_METADATA_ONLY")
        self.assertEqual(result["temporally_screened_count"], 1)
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertFalse(result["current_root_cause_confirmed"])
        self.assertFalse(result["source_authenticated"])

    def test_missing_availability_blocks_asof_replay(self):
        hit = synthetic_hit()
        hit.pop("available_at")
        self.assertIn("HISTORY_AS_OF_AVAILABILITY_NOT_VERIFIED",
                      self.assess(hits=[hit])["blocker_codes"])

    def test_post_cutoff_availability_blocks(self):
        hit = synthetic_hit()
        hit["available_at"] = "2026-04-12T18:11:00+09:00"
        self.assertIn("HISTORY_AVAILABLE_AFTER_ANALYSIS_CUTOFF",
                      self.assess(hits=[hit])["blocker_codes"])

    def test_future_independent_verification_blocks(self):
        hit = synthetic_hit()
        hit["verified_at"] = "2026-04-13T08:00:00Z"
        hit["available_at"] = "2026-04-13T09:00:00Z"
        self.assertIn("HISTORY_VERIFIED_AFTER_ANALYSIS_CUTOFF",
                      self.assess(hits=[hit])["blocker_codes"])

    def test_timezone_offsets_compare_instants(self):
        hit = synthetic_hit()
        hit["verified_at"] = "2026-04-11T17:00:00+09:00"
        hit["available_at"] = "2026-04-11T18:00:00+09:00"
        self.assertEqual(self.assess(hits=[hit])["decision"], "PASS_ASOF_METADATA_ONLY")

    def test_same_incident_family_is_not_history(self):
        hit = synthetic_hit()
        hit["source_group_id"] = synthetic_case()["provenance"]["source_group"]
        self.assertIn("SAME_INCIDENT_FAMILY_REUSE",
                      self.assess(hits=[hit])["blocker_codes"])

    def test_cross_equipment_claim_blocked(self):
        hit = synthetic_hit()
        hit["equipment_scope"] = "another_wheel"
        self.assertIn("EQUIPMENT_SCOPE_MISMATCH",
                      self.assess(hits=[hit])["blocker_codes"])

    def test_unbound_equipment_argument_rejected(self):
        with self.assertRaisesRegex(CaseHistoryAsOfError, "^EQUIPMENT_SCOPE_NOT_BOUND_TO_CASE$"):
            self.assess(scope="unknown_component")

    def test_missing_confirmed_hit_is_blocked(self):
        self.assertIn("CONFIRMED_HISTORY_HIT_MISSING",
                      self.assess(hits=[])["blocker_codes"])

    def test_extra_hit_is_blocked_not_used_as_evidence(self):
        hit = synthetic_hit()
        hit["case_id"] = "SYNTHETIC-UNREFERENCED-CASE"
        result = self.assess(hits=[synthetic_hit(), hit])
        self.assertIn("UNREFERENCED_HISTORY_HIT", result["blocker_codes"])

    def test_duplicate_hit_is_rejected(self):
        with self.assertRaisesRegex(CaseHistoryAsOfError, "^DUPLICATE_HISTORY_HIT_REFERENCE$"):
            self.assess(hits=[synthetic_hit(), synthetic_hit()])

    def test_unconfirmed_history_without_hit_requires_review(self):
        case = synthetic_case(confirmed=False)
        result = self.assess(case=case, hits=[])
        self.assertEqual(result["decision"], "MANUAL_HISTORY_REVIEW")
        self.assertEqual(result["temporally_screened_count"], 0)
        self.assertFalse(result["gold_eligible"])

    def test_unconfirmed_history_cannot_be_upgraded_by_memory_hit(self):
        case = synthetic_case(confirmed=False)
        result = self.assess(case=case)
        self.assertIn("UNCONFIRMED_HISTORY_CANNOT_BE_UPGRADED",
                      result["blocker_codes"])

    def test_no_history_and_no_hits_is_not_gold(self):
        case = synthetic_case()
        case["input"]["historical_cases"] = []
        case["provenance"]["historical_case_refs"] = []
        case["expected_output"]["historical_experience_relevance"] = []
        result = self.assess(case=case, hits=[])
        self.assertEqual(result["decision"], "NO_HISTORY_REFERENCES")
        self.assertFalse(result["training_authorized"])

    def test_raw_telemetry_hidden_in_case_is_rejected_without_echo(self):
        case = synthetic_case()
        case["input"]["raw_telemetry"] = "SYNTHETIC-PRIVATE-CANARY"
        with self.assertRaisesRegex(CaseHistoryAsOfError, "^INVALID_DIAGNOSTIC_CASE$"):
            self.assess(case=case)

    def test_extra_hit_payload_is_rejected_without_echo(self):
        hit = synthetic_hit()
        hit["raw_telemetry"] = "SYNTHETIC-PRIVATE-CANARY"
        with self.assertRaisesRegex(CaseHistoryAsOfError, "^INVALID_HISTORY_HIT_SHAPE$"):
            self.assess(hits=[hit])

    def test_results_do_not_contain_source_identifiers(self):
        output = json.dumps(self.assess())
        for token in ("HIST-ADCS-017", "synthetic://", "SYNTHETIC-REVIEWER"):
            self.assertNotIn(token, output)


if __name__ == "__main__":
    unittest.main()
