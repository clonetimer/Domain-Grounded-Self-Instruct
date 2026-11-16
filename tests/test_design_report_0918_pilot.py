from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "examples" / "design_report_0918_pilot"


class DesignReport0918PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.inventory = json.loads((PILOT / "source_inventory.json").read_text(encoding="utf-8"))
        cls.facts = json.loads((PILOT / "source_facts.json").read_text(encoding="utf-8"))
        cls.batch = json.loads((PILOT / "design_derived_candidates.json").read_text(encoding="utf-8"))
        cls.schema = json.loads((PILOT / "design_derived_batch.schema.json").read_text(encoding="utf-8"))

    def test_batch_matches_dedicated_design_derived_schema(self):
        errors = sorted(Draft202012Validator(self.schema).iter_errors(self.batch), key=lambda e: list(e.path))
        self.assertEqual([], [f"{list(e.path)}: {e.message}" for e in errors])

    def test_source_fingerprint_and_identity_are_consistent(self):
        self.assertEqual(self.inventory["sha256"], self.batch["source"]["sha256"])
        self.assertEqual(self.inventory["source_id"], self.batch["source"]["source_id"])
        self.assertEqual(64, len(self.inventory["sha256"]))

    def test_fact_ids_are_unique_and_located(self):
        ids = [fact["fact_id"] for fact in self.facts]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(20, len(self.facts))
        for fact in self.facts:
            self.assertTrue(fact["locator"].strip())
            self.assertEqual("DESIGN_DECLARATION", fact["certainty"])
            self.assertTrue(fact["boundary"].strip())

    def test_candidate_references_resolve_and_are_explicitly_hypothetical(self):
        fact_ids = {fact["fact_id"] for fact in self.facts}
        self.assertEqual(6, len(self.batch["candidates"]))
        candidate_ids = [candidate["case_id"] for candidate in self.batch["candidates"]]
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        for candidate in self.batch["candidates"]:
            self.assertEqual("DESIGN_DERIVED_HYPOTHETICAL", candidate["track"])
            self.assertEqual("HYPOTHETICAL_NOT_OBSERVED", candidate["scenario_status"])
            self.assertTrue(candidate["scenario_assumption"].strip())
            self.assertTrue(set(candidate["source_fact_refs"]).issubset(fact_ids))
            self.assertEqual("INCOMPLETE_EVIDENCE", candidate["target"]["decision"])
            self.assertIsNone(candidate["target"].get("fault_source_candidate"))

    def test_no_runtime_or_upstream_evidence_is_claimed(self):
        counts = self.batch["counts"]
        for key in ("observed_fault_events", "simulation_runs", "test_reports", "upstream_ml_bundles", "gold", "sft_export_authorized"):
            self.assertEqual(0, counts[key], key)
        self.assertFalse(self.batch["training_authorized"])
        self.assertEqual("REVIEW_REQUIRED", self.batch["review_status"])

    def test_out_of_scope_and_unverified_regions_are_quarantined(self):
        locators = {entry["locator"] for entry in self.batch["quarantine"]}
        self.assertIn("PDF pp.55-57", locators)
        self.assertIn("PDF pp.58-59", locators)

    def test_skill_distinguishes_simulation_receipt_from_formal_l1_admission(self):
        skill_root = ROOT / "skills" / "dgsi-simulation-to-sft"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("schemas/design_derived_batch.schema.json", skill)
        self.assertIn("SIMULATION_CASE_CANDIDATE", skill)
        self.assertIn("schemas/simulation_run_receipt.schema.json", skill)
        self.assertIn("local run-evidence intake only", skill)
        self.assertIn("not an L1 task packet", skill)
        self.assertIn("formal L1 simulation task representation", skill)
        self.assertTrue((skill_root / "schemas" / "simulation_run_receipt.schema.json").is_file())
        receipt_guide = (skill_root / "references" / "SIMULATION_RUN_RECEIPT.md").read_text(encoding="utf-8")
        self.assertIn("LOCAL_ARTIFACT_BYTES", receipt_guide)
        self.assertIn("SYNTHETIC_TEST_ONLY", receipt_guide)


if __name__ == "__main__":
    unittest.main()
