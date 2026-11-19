import json
import unittest
from pathlib import Path


class DGSI2x2PreregistrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.data = json.loads((root / "evaluation" / "refinement_20261120" / "factorial_preregistration.json").read_text(encoding="utf-8"))

    def test_exact_factorial_and_two_ablations(self):
        arms = {row["id"]: row for row in self.data["arms"]}
        self.assertEqual(set(arms), {"A", "B", "C", "D"})
        self.assertEqual((arms["A"]["evolution"], arms["A"]["selection"]), (False, False))
        self.assertEqual((arms["B"]["evolution"], arms["B"]["selection"]), (False, True))
        self.assertEqual((arms["C"]["evolution"], arms["C"]["selection"]), (True, False))
        self.assertEqual((arms["D"]["evolution"], arms["D"]["selection"]), (True, True))
        self.assertEqual(arms["B"]["role"], "selection_only_ablation")
        self.assertEqual(arms["C"]["role"], "evolution_only_ablation")

    def test_holdout_is_shared_and_prior_dev_bundle_is_excluded(self):
        holdout = self.data["holdout"]
        self.assertTrue(holdout["same_case_manifest_all_arms"])
        self.assertTrue(holdout["freeze_case_ids_source_document_clusters_input_hashes_before_generation"])
        self.assertTrue(holdout["require_new_untouched_source_document_clusters"])
        self.assertFalse(holdout["prior_2026_11_19_four_case_bundle_eligible"])
        self.assertEqual(holdout["if_insufficient_independent_clusters"], "DO_NOT_RUN")

    def test_no_evaluation_tuning_or_training_authority(self):
        self.assertEqual(self.data["status"], "PREREGISTERED_DESIGN_ONLY_NOT_RUN")
        self.assertEqual(self.data["controls"]["retries"], 0)
        self.assertEqual(self.data["controls"]["regeneration"], 0)
        self.assertEqual(self.data["controls"]["posthoc_repairs"], 0)
        self.assertFalse(self.data["run_started"])
        self.assertFalse(self.data["model_calls_authorized"])
        self.assertFalse(self.data["training_authorized"])
        self.assertFalse(self.data["gold_eligible"])
        self.assertFalse(self.data["official_splits_assigned"])


if __name__ == "__main__":
    unittest.main()
