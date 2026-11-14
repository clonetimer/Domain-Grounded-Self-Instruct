import unittest

from dgsi.astrograph_adapter import (
    UpstreamDiagnosisAdapterError,
    normalize_astrograph_diagnosis_result,
)


class AstroGraphDiagnosisAdapterTests(unittest.TestCase):
    def test_legacy_unverified_candidate_remains_a_candidate(self):
        result = normalize_astrograph_diagnosis_result({
            "schema_version": "external-diagnosis-result.v1",
            "case_id": "SYNTH-ADCS-001",
            "subsystem": "ADCS",
            "candidate_fault_id": "ADCS_RW_FRICTION_INCREASE",
            "diagnostic_summary": "上游模型提示反作用轮摩擦增大，尚未经物理故障确认。",
            "review_status": "UNVERIFIED",
        })
        self.assertEqual(result["status"], "FAULT_CANDIDATE")
        self.assertEqual(result["findings"][0]["result"], "ADCS_RW_FRICTION_INCREASE")
        self.assertEqual(result["findings"][0]["score"], None)
        self.assertIn("not a confirmed root cause", result["findings"][0]["limitations"][-1])

    def test_legacy_normal_without_candidate_stays_normal(self):
        result = normalize_astrograph_diagnosis_result({
            "case_id": "SYNTH-NONE-005",
            "status": "NORMAL",
            "diagnostic_summary": "上游此时间窗未产生明确故障候选。",
        })
        self.assertEqual(result["status"], "NORMAL")
        self.assertEqual(result["findings"], [])

    def test_unified_score_keeps_non_probability_semantics(self):
        result = normalize_astrograph_diagnosis_result({
            "schema_version": "astrograph-unified-diagnosis.v1",
            "case_id": "CASE-01",
            "status": "DIAGNOSED",
            "backend": "unified",
            "primary_subsystem": "ADCS",
            "primary_component": "reaction_wheel_2",
            "primary_effect_id": "ADCS_RW_FRICTION_INCREASE",
            "resolution_basis": "candidate screening",
            "candidates": [{
                "effect_id": "ADCS_RW_FRICTION_INCREASE",
                "screening_score": 0.81,
                "support_engines": ["residual"],
                "contradicting_engines": [],
                "evidence_summary": ["command response residual"],
            }],
            "diagnostic_evidence": [{
                "evidence_id": "E-01",
                "field": "rw_speed_residual",
                "statistic": "median",
                "interpretation": "residual elevated",
            }],
            "labels_used": False,
            "truth_used": False,
            "claim_boundary": "screening score is not calibrated probability",
        })
        self.assertEqual(result["status"], "FAULT_CANDIDATE")
        self.assertEqual(result["findings"][0]["score"], 0.81)
        self.assertIn("not a calibrated probability", result["findings"][0]["score_semantics"])
        self.assertEqual(result["findings"][0]["target"], "reaction_wheel_2")

    def test_truth_or_label_assisted_result_is_rejected(self):
        for field in ("truth_used", "labels_used"):
            with self.subTest(field=field):
                with self.assertRaises(UpstreamDiagnosisAdapterError):
                    normalize_astrograph_diagnosis_result({
                        "schema_version": "astrograph-unified-diagnosis.v1",
                        "status": "DIAGNOSED",
                        field: True,
                    })


if __name__ == "__main__":
    unittest.main()
