"""Adversarial, source-grounded contract tests. These are not efficacy claims."""
import copy
import json
from pathlib import Path
import unittest

from dgsi.quality import load_registry, report, validate_seed


ROOT = Path(__file__).resolve().parents[1]


class QualityGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(ROOT)
        cls.example = json.loads((ROOT / "examples/illustrative_gyro_abstain.json").read_text(encoding="utf-8"))

    def codes(self, record):
        return {f.code for f in validate_seed(record, self.registry)}

    def test_illustrative_abstention_can_remain_candidate(self):
        result = report(self.example, self.registry)
        self.assertEqual(result["decision"], "CANDIDATE_CHECKS_PASSED")
        self.assertEqual(result["findings"], [])
        self.assertFalse(result["gold_eligible"])

    def test_unknown_term_id_rejected(self):
        case = copy.deepcopy(self.example)
        case["term_ids"].append("姿态量子裂解")
        self.assertIn("UNKNOWN_TERM", self.codes(case))

    def test_forbidden_coinage_detected_in_answer(self):
        case = copy.deepcopy(self.example)
        case["answer"]["summary"] += " 已发生姿态量子解耦故障。"
        self.assertIn("FORBIDDEN_PHRASE", self.codes(case))

    def test_unknown_source_cannot_ground_evidence(self):
        case = copy.deepcopy(self.example)
        case["evidence"][0]["source_id"] = "INVENTED_STANDARD_2099"
        self.assertIn("UNKNOWN_SOURCE", self.codes(case))

    def test_claim_cannot_reference_missing_evidence(self):
        case = copy.deepcopy(self.example)
        case["claims"][0]["evidence_ids"] = ["NOT_IN_RECORD"]
        self.assertIn("UNKNOWN_EVIDENCE", self.codes(case))

    def test_unknown_telemetry_channel_is_rejected(self):
        case = copy.deepcopy(self.example)
        case["input"]["observations"][0]["channel_id"] = "adcs.imaginary.magic"
        self.assertIn("UNKNOWN_CHANNEL", self.codes(case))

    def test_causal_claim_needs_human_review_and_domain_source(self):
        case = copy.deepcopy(self.example)
        case["claims"][0].update({"claim_type":"CAUSAL","text":"陀螺异常必然导致飞轮卡死","source_ids":["AAS_CHANNEL_CATALOG"],"causal_review":"MACHINE_VALIDATED"})
        issues = self.codes(case)
        self.assertIn("UNREVIEWED_CAUSAL_CLAIM", issues)
        self.assertIn("CAUSAL_SOURCE_NOT_ADMITTED", issues)

    def test_causal_language_is_flagged_when_claim_marked_observation(self):
        case = copy.deepcopy(self.example)
        case["claims"][0]["text"] = "该测量波动直接导致飞轮失效"
        self.assertIn("CAUSAL_LANGUAGE_MISMATCH", self.codes(case))

    def test_unsubstantiated_self_attestation_flagged(self):
        case = copy.deepcopy(self.example)
        case["answer"]["summary"] += " 已经过权威验证，完全证明故障源。"
        self.assertIn("SELF_ATTESTATION", self.codes(case))

    def test_training_input_truth_leakage_rejected(self):
        case = copy.deepcopy(self.example)
        case["input"]["fault_id"] = "gyro_axis_dropout"
        self.assertIn("INPUT_TRUTH_LEAKAGE", self.codes(case))

    def test_invented_diagnosis_from_hypothetical_observation_blocked(self):
        case = copy.deepcopy(self.example)
        case["answer"].update({"status":"DIAGNOSED", "effect_id":"gyro_axis_dropout"})
        self.assertIn("DIAGNOSIS_NEEDS_ADMITTED_RUN", self.codes(case))

    def test_gold_state_without_human_receipt_is_rejected(self):
        case = copy.deepcopy(self.example)
        case["review"]["status"] = "HUMAN_REVIEWED"
        self.assertIn("GOLD_REVIEW_RECEIPT_MISSING", self.codes(case))
        self.assertFalse(report(case, self.registry)["gold_eligible"])

    def test_gold_state_cannot_be_promoted_by_generator_metadata(self):
        case = copy.deepcopy(self.example)
        case["review"].update({"status":"HUMAN_REVIEWED","reviewer_id":"gpt-model","reviewed_at":"2026-11-14T00:00:00Z","decision":"APPROVE","review_mode":"MODEL"})
        self.assertIn("GOLD_REVIEW_RECEIPT_MISSING", self.codes(case))

    def test_non_doc_claim_requires_valid_domain_source(self):
        case = copy.deepcopy(self.example)
        case["claims"][0].update({"claim_type":"MECHANISM","source_ids":["AAS_CHANNEL_CATALOG"]})
        self.assertIn("MECHANISM_SOURCE_NOT_ADMITTED", self.codes(case))

    def test_causal_claim_hidden_in_answer_is_blocked(self):
        case = copy.deepcopy(self.example)
        case["answer"]["summary"] += " 这一测量偏离直接导致飞轮卡死。"
        self.assertIn("UNDECLARED_CAUSAL_CONCLUSION", self.codes(case))

    def test_document_excerpt_requires_real_document_source(self):
        case = copy.deepcopy(self.example)
        case["evidence"][0].update({"origin":"DOCUMENT_EXCERPT", "locator":"page 1"})
        self.assertIn("DOCUMENT_SOURCE_NOT_ADMITTED", self.codes(case))

    def test_mechanism_claim_needs_precise_source_locator(self):
        case = copy.deepcopy(self.example)
        case["claims"][0].update({"claim_type":"MECHANISM", "source_ids":["NASA_SMALLSAT_GNC"]})
        self.assertIn("CLAIM_SOURCE_LOCATOR_MISSING", self.codes(case))

    def test_admitted_run_must_match_diagnosed_effect(self):
        case = copy.deepcopy(self.example)
        case["input"]["kind"] = "TRACE"
        case["answer"].update({"status":"DIAGNOSED", "effect_id":"gyro_axis_dropout"})
        case["evidence"][0]["origin"] = "MEASURED"
        case["provenance"]["trace_used"] = True
        case["provenance"]["run_id"] = "SIM-VERIFIED-EXAMPLE"
        registry = copy.deepcopy(self.registry)
        registry["runs"]["SIM-VERIFIED-EXAMPLE"] = {
            "run_id": "SIM-VERIFIED-EXAMPLE", "effect_id":"star_tracker_dropout", "trace_verified": True,
            "event_window_reviewed": True, "physical_effect_verified": True, "split_admitted": True,
        }
        issues = {f.code for f in validate_seed(case, registry)}
        self.assertIn("RUN_EFFECT_MISMATCH", issues)

    def test_registry_has_no_admitted_runs(self):
        self.assertEqual(self.registry["simulation_truth"]["runs"], [])


if __name__ == "__main__":
    unittest.main()
