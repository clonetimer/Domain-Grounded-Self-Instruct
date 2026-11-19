import json
import unittest
from pathlib import Path


class AblationAttributionAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = Path(__file__).resolve().parents[1] / "evaluation" / "refinement_20261119" / "ablation_attribution.json"
        cls.data = json.loads(path.read_text(encoding="utf-8"))

    def test_frozen_holdout_and_source_snapshot_are_bound(self):
        self.assertEqual(self.data["source_commit"], "fed424e76e25df77e553c3be683f1ca3546090e2")
        self.assertEqual(self.data["frozen_input_sha256"], "d36cacfb898ca249cd199abd634fb23acad961d3ced946c8360abf6aaad10368")
        self.assertEqual(self.data["holdout"]["cases"], 4)
        self.assertEqual(self.data["holdout"]["connected_source_document_clusters"], 2)
        self.assertTrue(self.data["immutable_inputs"])
        self.assertFalse(self.data["evaluation_changes"])
        self.assertFalse(self.data["score_rule_changes"])

    def test_two_ablation_arms_and_combined_arm_are_preserved(self):
        arms = self.data["arms"]
        self.assertEqual(arms["M5"]["mean_score"], 19.875)
        self.assertEqual(arms["M6"]["mean_score"], 20.0)
        self.assertEqual(arms["M7"]["mean_score"], 19.625)
        self.assertEqual(arms["M5"]["paired_accepts"], 3)
        self.assertEqual(arms["M6"]["paired_accepts"], 4)
        self.assertEqual(arms["M7"]["paired_accepts"], 2)

    def test_exposed_development_scores_do_not_promote_a_recipe(self):
        doc = Path(__file__).resolve().parents[1] / "docs" / "DGSI_ABLATION_ATTRIBUTION_2026-11-20.md"
        text = doc.read_text(encoding="utf-8")
        self.assertIn("Do not designate a winning recipe", text)
        self.assertIn("baseline", text)
        self.assertIn("selector-specific causal benefit is unproven", text)

    def test_selection_effect_is_not_overclaimed(self):
        selector = self.data["selector_diagnostic"]
        self.assertEqual(selector["M6_selected_instruction_ids"], {"I1": 4})
        self.assertEqual(selector["M7_selected_instruction_ids"], {"I1": 4})
        self.assertFalse(selector["selector_specific_gain_demonstrated"])

    def test_confounding_and_small_sample_limits_are_explicit(self):
        gaps = " ".join(self.data["design_gaps"])
        self.assertIn("fully identified 2x2", gaps)
        self.assertIn("two connected source-document clusters", gaps)
        self.assertFalse(self.data["training_authorized"])
        self.assertFalse(self.data["gold_eligible"])
        self.assertFalse(self.data["official_splits_assigned"])


if ( __name__ == "__main__"):
    unittest.main()
