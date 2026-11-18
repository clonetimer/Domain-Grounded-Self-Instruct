"""Regression checks for the pre-SFT evaluation/tooling handoff only.

These are documentation and manifest integrity checks; they confer no Gold,
rights clearance, expert approval, split assignment or training authorization.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "examples" / "dgsi_evaluation_suite_manifest_2026-11-18.json"
CORRECTION = ROOT / "docs" / "AAS_RUN03F_INTEGRATION_FIELD_MAPPING_CORRECTION_2026-11-18.md"
COMPARISON = ROOT / "docs" / "DGSI_SOTA_DATA_CONSTRUCTION_COMPARISON.md"
CLOSEOUT = ROOT / "docs" / "PRODUCT_CLOSEOUT_PLAN.md"
README = ROOT / "README.md"


class CloseoutConsistencyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.correction = CORRECTION.read_text(encoding="utf-8")
        cls.comparison = COMPARISON.read_text(encoding="utf-8")
        cls.closeout = CLOSEOUT.read_text(encoding="utf-8")
        cls.readme = README.read_text(encoding="utf-8")

    def test_manifest_binds_corrected_aas_score_artifact(self):
        items = [x for x in self.manifest["suite_components"] if x["id"] == "AAS-RUN03F-001"]
        self.assertEqual(len(items), 1)
        fixture = items[0]
        self.assertEqual(fixture["track"], "SYNTHETIC_TEST_ONLY")
        self.assertEqual(
            fixture["artifact_file"],
            "DGSI_AAS_RUN03F_score_only_integration_demo_corrected_20261118.zip",
        )
        self.assertEqual(
            fixture["artifact_sha256"],
            "ef0ca966d5b9f762945bd20502f35971f1ae87ec48a69bc3ccd4e7bdb10c5c44",
        )
        self.assertIn(fixture["artifact_file"], self.correction)
        self.assertIn(fixture["artifact_sha256"], self.correction)
        self.assertNotEqual(fixture["artifact_file"], fixture["supersedes_artifact_file"])

    def test_evaluation_suite_never_claims_training_admission(self):
        admission = self.manifest["current_admission_state"]
        self.assertIs(admission["training_authorized"], False)
        for k in ("human_expert_adjudicated", "official_splits", "gold_examples", "authorized_sft_rows"):
            self.assertEqual(admission[k], 0)
        self.assertEqual(admission["rights_cleared_publications"], 0)
        for component in self.manifest["suite_components"]:
            self.assertNotIn("AUTHORIZED_FOR_TRAINING", component["classification"])

    def test_method_table_has_distinct_auto_instruct_arm(self):
        for arm in ("M0", "M1", "M2", "M3", "M4", "M5"):
            self.assertIn("| " + arm + " ", self.comparison)
        self.assertIn("2023.findings-emnlp.659", self.comparison)
        self.assertIn("NOT APPLICABLE", self.comparison)
        self.assertIn("not a fabricated training arm", self.comparison)

    def test_tooling_handoff_is_not_product_goal_completion(self):
        self.assertIn("single product goal", self.closeout)
        self.assertIn("not DGSI's product completion", self.closeout)
        self.assertIn("block declaring the product goal achieved", self.closeout)
        self.assertIn("separately classified and evaluated", self.closeout)
        self.assertIn("single spacecraft fault-diagnosis SFT dataset product goal", self.readme)
        self.assertNotIn("Skill product is being closed out separately", self.readme)
        self.assertIn("Auto-Instruct-style ranking", self.closeout)


if __name__ == "__main__":
    unittest.main()
