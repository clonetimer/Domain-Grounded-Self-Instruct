"""SYNTHETIC_TEST_ONLY: adversarial SADA metadata-only claim-map checks.

No private source documents, real telemetry, ML outputs or expert signoffs.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from dgsi.p5c_sada_claim_map import SadaClaimMapError, audit_sada_claim_map

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "p5c_sada_claim_evidence_map_2026-11-17.json"


def fixture():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


class SadaClaimMapTests(unittest.TestCase):
    def assert_blocked(self, item, code):
        with self.assertRaises(SadaClaimMapError) as err:
            audit_sada_claim_map(item)
        self.assertEqual(str(err.exception), code)

    def test_existing_map_is_only_a_blocked_candidate(self):
        result = audit_sada_claim_map(fixture())
        self.assertEqual(result["decision"], "BLOCKED_PENDING_REAL_EVIDENCE")
        self.assertEqual(result["source_attributed_claims"], 5)
        self.assertEqual(result["private_curator_prompt_refs"], 3)
        self.assertEqual(result["received_case_specific_evidence"], 0)
        self.assertFalse(result["sft_eligible"])
        self.assertFalse(result["training_authorized"])
        self.assertNotIn("SOURCE_CAUSE_LOCALIZATION", repr(result))
        self.assertNotIn("181", repr(result))

    def test_old_public_inline_curator_prompt_list_is_forbidden(self):
        item = fixture()
        item["excluded_internal_review_prompts"] = ["not for export"]
        self.assert_blocked(item, "SADA_MAP_STRUCTURE_INVALID")

    def test_internal_review_can_never_be_model_visible(self):
        item = fixture()
        item["internal_review"]["not_for_sft"] = False
        self.assert_blocked(item, "SADA_MAP_INTERNAL_REVIEW_INVALID")

    def test_curator_question_must_not_be_stored_inline(self):
        item = fixture()
        item["internal_review"]["curator_prompt_refs"] = ["why is it failing?"]
        self.assert_blocked(item, "SADA_MAP_INTERNAL_REVIEW_INVALID")

    def test_target_inside_candidate_is_forbidden(self):
        item = fixture()
        item["formal_target"] = {"fault_source": "confirmed"}
        self.assert_blocked(item, "SADA_MAP_STRUCTURE_INVALID")

    def test_internal_review_cannot_be_nested_inside_claim(self):
        item = fixture()
        item["formal_source_claims"][0]["internal_review"] = {"not_for_sft": True}
        self.assert_blocked(item, "SADA_MAP_CLAIM_STRUCTURE_INVALID")

    def test_source_root_cause_cannot_be_promoted_to_confirmed(self):
        item = fixture()
        item["formal_source_claims"][3]["source_certainty"] = "CONFIRMED"
        self.assert_blocked(item, "SADA_MAP_CERTAINTY_ESCALATION")

    def test_original_claim_cannot_be_silently_rewritten(self):
        item = fixture()
        item["formal_source_claims"][0]["source_text"] = "fabricated timestamp joins"
        self.assert_blocked(item, "SADA_MAP_SOURCE_CLAIM_DRIFT")

    def test_no_case_specific_evidence_can_be_invented(self):
        item = fixture()
        item["formal_source_claims"][0]["current_evidence_status"] = "VERIFIED"
        self.assert_blocked(item, "SADA_MAP_UNVERIFIED_EVIDENCE")

    def test_actual_ml_input_cannot_be_claimed_without_receipt(self):
        item = fixture()
        item["required_dgsi_inputs"]["upstream_ml_result"]["status"] = "RECEIVED"
        self.assert_blocked(item, "SADA_MAP_UNVERIFIED_EVIDENCE")

    def test_disposal_execution_is_not_inferred(self):
        item = fixture()
        item["formal_source_claims"][4]["execution_status"] = "EXECUTED"
        self.assert_blocked(item, "SADA_MAP_DISPOSAL_ESCALATION")

    def test_source_rights_remain_pending(self):
        item = fixture()
        item["source"]["rights_and_training_use"] = "APPROVED"
        self.assert_blocked(item, "SADA_MAP_SOURCE_INVALID")

    def test_history_is_context_not_direct_support(self):
        item = fixture()
        item["required_dgsi_inputs"]["history_context"]["rule"] = "DIRECT_ROOT_CAUSE_EVIDENCE"
        self.assert_blocked(item, "SADA_MAP_HISTORY_ESCALATION")

    def test_counter_boolean_cannot_imply_reviewer_approval(self):
        item = fixture()
        item["target_admission"]["independent_reviews_complete"] = False
        self.assert_blocked(item, "SADA_MAP_UNAUTHORIZED_PROMOTION")

    def test_no_gold_split_or_training_escalation(self):
        for field in ("real_gold_admitted", "official_split_assigned", "sft_export_authorized", "training_authorized"):
            item = fixture()
            item["target_admission"][field] = True
            with self.subTest(field=field):
                self.assert_blocked(item, "SADA_MAP_UNAUTHORIZED_PROMOTION")

    def test_duplicate_claim_identity_is_rejected(self):
        item = fixture()
        item["formal_source_claims"][4] = copy.deepcopy(item["formal_source_claims"][3])
        self.assert_blocked(item, "SADA_MAP_CLAIMS_INVALID")

    def test_cli_only_reports_aggregate_blocked_state(self):
        done = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit_p5c_sada_claim_map.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(done.returncode, 0, done.stderr)
        result = json.loads(done.stdout)
        self.assertFalse(result["training_authorized"])
        self.assertNotIn("SADA-C", done.stdout)
        self.assertNotIn("error voltage", done.stdout)
        self.assertNotIn("USER-", done.stdout)


if __name__ == "__main__":
    unittest.main()
