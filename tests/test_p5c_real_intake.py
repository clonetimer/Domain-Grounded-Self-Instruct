"""SYNTHETIC_TEST_ONLY: incomplete REAL candidate preflight regressions.

Tests mutate a checked-in *metadata-only* fixture; no private narratives,
manufactured ML outputs, operational logs or expert approvals are required.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from dgsi.p5c_real_intake import RealCandidateIntakeError, audit_real_candidate_intake

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "p5c_real_case_candidate_intake_2026-11-17.json"


def fixture():
    return json.loads(SOURCE.read_text(encoding="utf-8"))


class RealCandidateIntakeTests(unittest.TestCase):
    def assert_blocked(self, payload, code):
        with self.assertRaises(RealCandidateIntakeError) as context:
            audit_real_candidate_intake(payload)
        self.assertEqual(str(context.exception), code)

    def test_existing_five_cases_are_blocked_pending_evidence(self):
        report = audit_real_candidate_intake(fixture())
        self.assertEqual(report["decision"], "BLOCKED_PENDING_REAL_EVIDENCE")
        self.assertEqual(report["real_case_candidates"], 5)
        self.assertEqual(report["domains"], {"ADCS": 2, "COMM": 2, "PROPULSION": 1})
        self.assertEqual(report["independently_approved"], 0)
        self.assertFalse(report["training_authorized"])
        self.assertNotIn("USER-ADCS-SADA-001", repr(report))
        self.assertNotIn("故障案例参考.docx", repr(report))

    def test_case_count_drift_is_blocked(self):
        doc = fixture()
        doc["case_count"] = 6
        self.assert_blocked(doc, "REAL_INTAKE_CASE_COUNT_DRIFT")

    def test_boolean_forged_as_integer_count_is_blocked(self):
        doc = fixture()
        doc["aggregate"]["real_gold_admitted"] = False
        self.assert_blocked(doc, "REAL_INTAKE_AGGREGATE_ESCALATION")

    def test_duplicate_case_cannot_masquerade_as_independent(self):
        doc = fixture()
        doc["cases"][1] = copy.deepcopy(doc["cases"][0])
        self.assert_blocked(doc, "REAL_INTAKE_CASE_ID_DRIFT")

    def test_case_id_substitution_is_blocked(self):
        doc = fixture()
        doc["cases"][0]["case_id"] = "USER-ADCS-SADA-FAKE"
        self.assert_blocked(doc, "REAL_INTAKE_CASE_ID_DRIFT")

    def test_domain_and_disposal_meaning_cannot_drift(self):
        doc = fixture()
        doc["cases"][2]["disposal_record_type"] = "SOURCE_RECORDS_MEASURE"
        self.assert_blocked(doc, "REAL_INTAKE_CASE_SEMANTIC_DRIFT")

    def test_conditional_procedure_cannot_claim_execution(self):
        doc = fixture()
        doc["cases"][2]["disposal_execution_and_effectiveness"] = "EXECUTED"
        self.assert_blocked(doc, "REAL_INTAKE_UNVERIFIED_EVIDENCE")

    def test_upstream_result_cannot_be_filled_by_editing_register(self):
        doc = fixture()
        doc["cases"][0]["upstream_ml_result"] = "made_up_run_101"
        self.assert_blocked(doc, "REAL_INTAKE_UNVERIFIED_EVIDENCE")

    def test_extra_payload_field_cannot_smuggle_sft_target(self):
        doc = fixture()
        doc["cases"][0]["formal_target"] = {"fault_source": "invented"}
        self.assert_blocked(doc, "REAL_INTAKE_CASE_STRUCTURE_INVALID")

    def test_top_level_training_artifact_is_blocked(self):
        doc = fixture()
        doc["sft_records"] = [{"messages": ["private"]}]
        self.assert_blocked(doc, "REAL_INTAKE_STRUCTURE_INVALID")

    def test_invented_independent_approval_cannot_promote_case(self):
        doc = fixture()
        doc["cases"][0]["independent_case_review"] = "APPROVED"
        self.assert_blocked(doc, "REAL_INTAKE_UNAUTHORIZED_PROMOTION")

    def test_track_cannot_be_renamed_gold(self):
        doc = fixture()
        doc["track"] = "REAL_GOLD_TRACK"
        self.assert_blocked(doc, "REAL_INTAKE_TRACK_ESCALATION")

    def test_context_cannot_be_declared_direct_evidence(self):
        doc = fixture()
        doc["policy"]["historical_experience_role"] = "CONFIRMS_ROOT_CAUSE"
        self.assert_blocked(doc, "REAL_INTAKE_POLICY_INVALID")

    def test_cli_emits_only_counts_and_never_source_payload(self):
        run = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit_p5c_real_intake.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["real_case_candidates"], 5)
        self.assertNotIn("USER-", run.stdout)
        self.assertNotIn("故障案例参考", run.stdout)
        self.assertNotIn("notes", run.stdout)


if __name__ == "__main__":
    unittest.main()
