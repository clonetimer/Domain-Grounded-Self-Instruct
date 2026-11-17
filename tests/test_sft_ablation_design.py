"""SYNTHETIC_TEST_ONLY: no real case, model result or expert review here."""
from __future__ import annotations

import copy
import unittest

from dgsi.sft_ablation_design import (
    ARMS, METRICS, TRAINING_SOURCES, SFTAblationDesignError,
    audit_sft_ablation_design,
)


def _plan():
    return {
        "schema_version": "dgsi-sft-ablation-design.v1",
        "arm_specs": [
            {"arm": a, "training_source": TRAINING_SOURCES[a],
             "context_mode": "AS_OF_RETRIEVED" if a == "DGSI_WITH_RETRIEVED_HISTORY" else "NONE",
             "run_status": "NOT_RUN"}
            for a in ARMS
        ],
        "evaluation_metrics": list(METRICS),
        "candidate_training_families": [],
        "candidate_holdout_families": [],
        "holdout_policy": {"provisional_only": True, "unit": "EVENT_FAMILY", "same_across_arms": True},
        "history_policy": {"retrieval_mode": "USER_CONTEXT_ONLY", "analysis_cutoff_enforced": True,
                           "timestamp_required": True, "source_status_preserved": True,
                           "same_family_excluded": True, "hardware_scope_required": True},
        "gold_eligible": False,
        "training_authorized": False,
        "evaluation_executed": False,
    }


class SFTAblationDesignTests(unittest.TestCase):
    def assertBlocked(self, plan, code):
        with self.assertRaisesRegex(SFTAblationDesignError, '^' + code + '$'):
            audit_sft_ablation_design(plan)

    def test_empty_preregistration_is_nonexecuting(self):
        out = audit_sft_ablation_design(_plan())
        self.assertEqual(out["arm_count"], 5)
        self.assertEqual(out["candidate_holdout_family_count"], 0)
        self.assertFalse(out["training_authorized"])
        self.assertFalse(out["formal_split_assigned"])
        self.assertEqual(out["candidate_holdout_family_count_by_track"]["REAL_GOLD"], 0)

    def test_duplicate_arm_is_blocked(self):
        p = _plan()
        p["arm_specs"][4] = copy.deepcopy(p["arm_specs"][0])
        self.assertBlocked(p, "ABLATION_ARM_UNKNOWN_OR_DUPLICATE")

    def test_missing_arm_is_blocked(self):
        p = _plan(); p["arm_specs"].pop()
        self.assertBlocked(p, "ABLATION_ARMS_INCOMPLETE")

    def test_history_context_must_only_change_in_e_arm(self):
        p = _plan(); p["arm_specs"][0]["context_mode"] = "AS_OF_RETRIEVED"
        self.assertBlocked(p, "ABLATION_CONTEXT_CONFOUND")

    def test_history_and_synthetic_training_source_cannot_be_swapped(self):
        p = _plan(); p["arm_specs"][4]["training_source"] = "REAL_GOLD"
        self.assertBlocked(p, "ABLATION_TRAINING_SOURCE_MISMATCH")

    def test_unverified_run_or_training_authorization_blocked(self):
        p = _plan(); p["arm_specs"][0]["run_status"] = "PASS"
        self.assertBlocked(p, "ABLATION_UNVERIFIED_RUN_CLAIM")
        p = _plan(); p["training_authorized"] = True
        self.assertBlocked(p, "ABLATION_UNAUTHORIZED_PROMOTION")

    def test_metric_omission_blocked(self):
        p = _plan(); p["evaluation_metrics"].remove("disposal_fidelity")
        self.assertBlocked(p, "ABLATION_METRIC_SET_INCOMPLETE")

    def test_family_exposure_blocked_even_under_different_tracks(self):
        p = _plan()
        p["candidate_training_families"] = [{"family_ref": "SYNTHETIC-FAMILY-A", "track": "LITERATURE_DERIVED_SYNTHETIC", "fact_card_sha256": "a" * 64}]
        p["candidate_holdout_families"] = [{"family_ref": "SYNTHETIC-FAMILY-A", "track": "REAL_GOLD", "fact_card_sha256": "b" * 64}]
        self.assertBlocked(p, "ABLATION_EVENT_FAMILY_EXPOSURE")

    def test_unequal_family_refs_do_not_grant_review_or_split(self):
        p = _plan()
        p["candidate_training_families"] = [{"family_ref": "SYNTHETIC-A", "track": "LITERATURE_DERIVED_SYNTHETIC", "fact_card_sha256": "a" * 64}]
        p["candidate_holdout_families"] = [{"family_ref": "SYNTHETIC-B", "track": "REAL_GOLD", "fact_card_sha256": "b" * 64}]
        out = audit_sft_ablation_design(p)
        self.assertEqual(out["candidate_training_family_count"], 1)
        self.assertEqual(out["candidate_holdout_family_count"], 1)
        self.assertNotIn("SYNTHETIC-A", repr(out))
        self.assertFalse(out["training_authorized"])

    def test_cross_holdout_source_digest_alias_is_blocked(self):
        p = _plan()
        p["candidate_training_families"] = [{"family_ref": "SYNTHETIC-A", "track": "LITERATURE_DERIVED_SYNTHETIC", "fact_card_sha256": "a" * 64}]
        p["candidate_holdout_families"] = [{"family_ref": "SYNTHETIC-ALIAS", "track": "REAL_GOLD", "fact_card_sha256": "a" * 64}]
        self.assertBlocked(p, "ABLATION_SOURCE_FACT_DIGEST_EXPOSURE")

    def test_case_variant_training_holdout_alias_is_blocked(self):
        p = _plan()
        p["candidate_training_families"] = [
            {"family_ref": "FUSE-RW-2000", "track": "LITERATURE_DERIVED_SYNTHETIC",
             "fact_card_sha256": "a" * 64}]
        p["candidate_holdout_families"] = [
            {"family_ref": "fuse-rw-2000", "track": "REAL_GOLD",
             "fact_card_sha256": "b" * 64}]
        self.assertBlocked(p, "ABLATION_EVENT_FAMILY_EXPOSURE")

    def test_case_variant_alias_within_training_is_blocked(self):
        p = _plan()
        p["candidate_training_families"] = [
            {"family_ref": "EPISODE-A", "track": "LITERATURE_DERIVED_SYNTHETIC",
             "fact_card_sha256": "a" * 64},
            {"family_ref": "episode-a", "track": "LITERATURE_DERIVED_SYNTHETIC",
             "fact_card_sha256": "b" * 64}]
        self.assertBlocked(p, "ABLATION_DUPLICATE_FAMILY")

    def test_noncanonical_event_family_identifiers_fail_closed(self):
        for alias in ("FAMILY A", "FAMILY\nA", "ＦＡＭＩＬＹ", "FAMILY\u200bA", " A", "A "):
            with self.subTest(alias=repr(alias)):
                p = _plan()
                p["candidate_training_families"] = [
                    {"family_ref": alias, "track": "LITERATURE_DERIVED_SYNTHETIC",
                     "fact_card_sha256": "a" * 64}]
                self.assertBlocked(p, "INVALID_TRAINING_FAMILY_PROPOSAL")

    def test_distinct_canonical_ids_stay_provisional(self):
        p = _plan()
        p["candidate_training_families"] = [
            {"family_ref": "NASA:TWTA/EPISODE-1", "track": "LITERATURE_DERIVED_SYNTHETIC",
             "fact_card_sha256": "a" * 64}]
        p["candidate_holdout_families"] = [
            {"family_ref": "NASA:TWTA/EPISODE-2", "track": "REAL_GOLD",
             "fact_card_sha256": "b" * 64}]
        out = audit_sft_ablation_design(p)
        self.assertEqual(out["candidate_training_family_count"], 1)
        self.assertEqual(out["candidate_holdout_family_count"], 1)
        self.assertFalse(out["formal_split_assigned"])

    def test_unhashable_track_is_fixed_error_not_typeerror(self):
        p = _plan()
        p["candidate_holdout_families"] = [{"family_ref": "SYNTHETIC-A", "track": [], "fact_card_sha256": "a" * 64}]
        self.assertBlocked(p, "INVALID_HOLDOUT_FAMILY_PROPOSAL")

    def test_history_unsafe_if_cutoff_or_status_not_enforced(self):
        for key in ("analysis_cutoff_enforced", "source_status_preserved", "hardware_scope_required", "timestamp_required", "same_family_excluded"):
            with self.subTest(key=key):
                p = _plan(); p["history_policy"][key] = False
                self.assertBlocked(p, "ABLATION_HISTORY_POLICY_UNSAFE")

    def test_nonprovisional_or_different_holdouts_blocked(self):
        for key in ("provisional_only", "same_across_arms"):
            p = _plan(); p["holdout_policy"][key] = False
            self.assertBlocked(p, "ABLATION_HOLDOUT_POLICY_UNSAFE")

    def test_extra_payload_and_untrusted_claims_blocked(self):
        p = _plan(); p["private_diagnostic_log"] = "DO-NOT-INCLUDE"
        self.assertBlocked(p, "INVALID_ABLATION_ENVELOPE")
        p = _plan(); p["evaluation_executed"] = True
        self.assertBlocked(p, "ABLATION_UNAUTHORIZED_PROMOTION")


if __name__ == "__main__":
    unittest.main()
