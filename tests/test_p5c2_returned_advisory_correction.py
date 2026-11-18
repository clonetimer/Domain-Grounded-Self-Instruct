"""SYNTHETIC_TEST_ONLY: verify the returned AI advisory correction is narrow and review-only."""
from __future__ import annotations
import copy, json
from pathlib import Path
import unittest
from dgsi.l1_task_packet import validate_l1_task_packet_collection
from dgsi.l1_model_projection_audit import audit_l1_synthetic_collection_projection

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json"
NEW = ROOT / "examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json"
L0 = ROOT / "examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json"
EXPECTED_PROJECTION = "3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a"
TASK = "L1-SPACEBORNE-TWTA-LNA-HANDOVER-SYNTH-015"

class C2ReturnedAdvisoryCorrectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.old = json.loads(OLD.read_text(encoding="utf-8"))
        cls.new = json.loads(NEW.read_text(encoding="utf-8"))
        cls.cards = json.loads(L0.read_text(encoding="utf-8"))["cards"]

    def test_only_task_015_structured_fault_mode_pair_and_collection_id_change(self):
        old = copy.deepcopy(self.old)
        new = copy.deepcopy(self.new)
        old_packet = next(p for p in old["packets"] if p["task_id"] == TASK)
        new_packet = next(p for p in new["packets"] if p["task_id"] == TASK)
        self.assertEqual(old_packet["formal_target"]["cause_localization"]["candidates"][0]["fault_mode"], "linearizer_LNA_hydrogen_poisoning")
        self.assertEqual(new_packet["formal_target"]["cause_localization"]["candidates"][0]["fault_mode"], "linearizer_LNA_gain_degradation_candidate")
        self.assertEqual(new_packet["case"]["expected_output"]["cause_localization"]["candidates"][0]["fault_mode"], "linearizer_LNA_gain_degradation_candidate")
        old_packet["formal_target"]["cause_localization"]["candidates"][0]["fault_mode"] = "linearizer_LNA_gain_degradation_candidate"
        old_packet["case"]["expected_output"]["cause_localization"]["candidates"][0]["fault_mode"] = "linearizer_LNA_gain_degradation_candidate"
        old["collection_id"] = new["collection_id"]
        self.assertEqual(old, new)

    def test_revised_collection_is_structurally_valid_and_review_only(self):
        report = validate_l1_task_packet_collection(self.new, source_fact_cards=self.cards)
        self.assertEqual(report["packet_count"], 21)
        self.assertEqual(self.new["track"], "LITERATURE_DERIVED_SYNTHETIC")
        self.assertFalse(report["training_authorized"])
        self.assertTrue(all(p["review"]["status"] == "REVIEW_REQUIRED" for p in self.new["packets"]))

    def test_projection_is_bound_to_new_cohort_and_matches_manifest(self):
        report = audit_l1_synthetic_collection_projection(self.new, source_fact_cards=self.cards)
        self.assertEqual(report["collection_projection_sha256"], EXPECTED_PROJECTION)
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["training_authorized"])

    def test_old_cohort_is_not_mutated(self):
        packet = next(p for p in self.old["packets"] if p["task_id"] == TASK)
        self.assertEqual(packet["formal_target"]["cause_localization"]["candidates"][0]["fault_mode"], "linearizer_LNA_hydrogen_poisoning")
        self.assertEqual(packet["review"]["status"], "REVIEW_REQUIRED")

if __name__ == "__main__":
    unittest.main()
