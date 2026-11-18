"""TC01–TC09 AstroGraph adapter contract tests; SYNTHETIC, never Gold."""
import json
import unittest
from pathlib import Path

from dgsi.astrograph_adapter import (
    UpstreamDiagnosisAdapterError,
    normalize_astrograph_diagnosis_result,
)

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads(
    (ROOT / "resources/astrograph_tc_synthetic_adapter_matrix.json").read_text(encoding="utf-8")
)


class AstrographSyntheticAcceptanceMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {record["tc"]: record for record in MATRIX["cases"]}

    def test_all_nine_are_explicitly_synthetic_and_not_training_eligible(self):
        self.assertEqual(MATRIX["classification"], "SYNTHETIC")
        self.assertFalse(MATRIX["training_eligible"])
        self.assertFalse(MATRIX["gold_eligible"])
        self.assertEqual(set(self.cases), {f"TC{x:02d}" for x in range(1, 10)})
        for record in self.cases.values():
            self.assertEqual(record["classification"], "SYNTHETIC")
            self.assertFalse(record["gold_eligible"])
            self.assertFalse(record["training_eligible"])
            self.assertIn("platform_acceptance_cases_v1/", record["source_path"])

    def test_eight_existing_synthetic_results_normalize_without_inventing_truth(self):
        for tc in (f"TC{x:02d}" for x in range(1, 9)):
            with self.subTest(tc=tc):
                record = self.cases[tc]
                upstream = record["upstream_diagnosis"]
                self.assertTrue(upstream["case_id"].startswith("SYNTH-"))
                normalized = normalize_astrograph_diagnosis_result(upstream)
                self.assertEqual(normalized["status"], record["expected_status"])
                self.assertEqual(
                    [finding["result"] for finding in normalized["findings"]],
                    record["expected_candidate_fault_ids"],
                )
                self.assertEqual(normalized["producer"]["version"], "NOT_RECORDED")
                self.assertTrue(all(finding["score"] is None for finding in normalized["findings"]))
                self.assertTrue(
                    all("not a confirmed root cause" in " ".join(finding["limitations"])
                        for finding in normalized["findings"])
                )

    def test_tc03_missing_corroboration_is_not_confirmation(self):
        candidate = normalize_astrograph_diagnosis_result(self.cases["TC03"]["upstream_diagnosis"])
        self.assertEqual(candidate["status"], "FAULT_CANDIDATE")
        self.assertEqual(candidate["findings"][0]["supporting_evidence_ids"], [])

    def test_tc04_unknown_code_is_not_replaced_by_guessed_fault(self):
        normalized = normalize_astrograph_diagnosis_result(self.cases["TC04"]["upstream_diagnosis"])
        self.assertEqual(normalized["findings"][0]["result"], "PROP_VALVE_LEAK_UNDOCUMENTED")
        self.assertEqual(normalized["status"], "FAULT_CANDIDATE")

    def test_tc05_log_only_alarm_cannot_create_machine_fault(self):
        normalized = normalize_astrograph_diagnosis_result(self.cases["TC05"]["upstream_diagnosis"])
        self.assertEqual(normalized["status"], "NORMAL")
        self.assertEqual(normalized["findings"], [])

    def test_tc06_preserves_two_distinct_candidates(self):
        normalized = normalize_astrograph_diagnosis_result(self.cases["TC06"]["upstream_diagnosis"])
        self.assertEqual(normalized["status"], "MULTIPLE_CANDIDATES")
        self.assertEqual(len(normalized["findings"]), 2)

    def test_tc07_missing_reference_fails_preflight_not_fabricated(self):
        r = self.cases["TC07"]
        self.assertTrue(r["has_log_artifact"])
        self.assertFalse(r["has_reference_artifact"])
        self.assertEqual(r["intake_gate"], "BLOCKED_MISSING_REFERENCE")
        self.assertFalse(r["gold_eligible"])

    def test_tc08_untrusted_reference_requires_manual_safety_review(self):
        r = self.cases["TC08"]
        self.assertTrue(r["untrusted_reference"])
        self.assertEqual(r["intake_gate"], "REVIEW_REQUIRED_UNTRUSTED_REFERENCE")
        self.assertFalse(r["training_eligible"])

    def test_tc09_has_no_diagnosis_result_and_is_out_of_sft_scope(self):
        r = self.cases["TC09"]
        self.assertIsNone(r["upstream_diagnosis"])
        self.assertEqual(r["intake_gate"], "OUT_OF_SCOPE_GRAPH_BUILD")
        with self.assertRaises(UpstreamDiagnosisAdapterError):
            normalize_astrograph_diagnosis_result(r["upstream_diagnosis"])


if __name__ == "__main__":
    unittest.main()
