"""SYNTHETIC_TEST_ONLY: adversarial design-derived intake checks."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.design_derived_intake import (
    DesignDerivedIntakeError,
    validate_design_derived_batch,
)


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "examples" / "design_report_0918_pilot"


class DesignDerivedIntakeBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pilot = json.loads(
            (PILOT / "design_derived_candidates.json").read_text(encoding="utf-8")
        )
        cls.inventory = json.loads(
            (PILOT / "source_inventory.json").read_text(encoding="utf-8")
        )

    def _blocked(self, mutate, code):
        data = copy.deepcopy(self.pilot)
        mutate(data)
        with self.assertRaisesRegex(DesignDerivedIntakeError, "^" + code + "$"):
            validate_design_derived_batch(data)

    def test_pilot_remains_non_sft_and_fingerprint_bound(self):
        report = validate_design_derived_batch(
            self.pilot,
            expected_source_sha256=self.inventory["sha256"],
        )
        self.assertEqual("NON_SFT_INTAKE_ONLY", report["decision"])
        self.assertEqual(20, report["source_fact_count"])
        self.assertEqual(6, report["hypothetical_candidate_count"])
        self.assertEqual(0, report["sft_records_emitted"])
        self.assertFalse(report["training_authorized"])
        self.assertNotIn("cases", report)
        self.assertNotIn("source", report)

    def test_skill_and_pilot_schema_are_byte_identical(self):
        skill = (
            ROOT / "skills" / "dgsi-simulation-to-sft" / "schemas"
            / "design_derived_batch.schema.json"
        ).read_bytes()
        example = (PILOT / "design_derived_batch.schema.json").read_bytes()
        self.assertEqual(skill, example)

    def test_reject_missing_model_visible_hypothetical_notice(self):
        self._blocked(
            lambda b: b["candidates"][0]["model_visible_input"].pop("evidence_status"),
            "DESIGN_INTAKE_SCHEMA_INVALID",
        )

    def test_reject_improper_real_ml_run_claim_inside_input(self):
        self._blocked(
            lambda b: b["candidates"][0]["model_visible_input"].update(
                diagnosis_run_ref="actual-on-orbit-run-123"
            ),
            "DESIGN_INTAKE_SCHEMA_INVALID",
        )

    def test_reject_hidden_truth_or_internal_review_in_input(self):
        for key in ("hidden_truth", "internal_review", "qa_label"):
            with self.subTest(key=key):
                self._blocked(
                    lambda b, k=key: b["candidates"][0]["model_visible_input"].update(
                        {k: {"answer": "fault-source"}}
                    ),
                    "DESIGN_INTAKE_SCHEMA_INVALID",
                )

    def test_reject_premature_source_localization(self):
        self._blocked(
            lambda b: b["candidates"][0]["target"].update(
                fault_source_candidate="confirmed wheel failure"
            ),
            "DESIGN_INTAKE_SCHEMA_INVALID",
        )

    def test_reject_unapproved_gold_or_training(self):
        for key, value in (("training_authorized", True), ("review_status", "APPROVED")):
            self._blocked(
                lambda b, k=key, v=value: b.__setitem__(k, v),
                "DESIGN_INTAKE_SCHEMA_INVALID",
            )
        self._blocked(
            lambda b: b["counts"].__setitem__("gold", 1),
            "DESIGN_INTAKE_SCHEMA_INVALID",
        )

    def test_reject_claimed_simulation_or_ml_evidence(self):
        for key in ("observed_fault_events", "simulation_runs", "upstream_ml_bundles"):
            self._blocked(
                lambda b, k=key: b["counts"].__setitem__(k, 1),
                "DESIGN_INTAKE_SCHEMA_INVALID",
            )

    def test_reject_duplicate_fact_and_candidate_ids(self):
        self._blocked(
            lambda b: b["source_facts"][1].__setitem__(
                "fact_id", b["source_facts"][0]["fact_id"]
            ),
            "DESIGN_INTAKE_DUPLICATE_FACT_ID",
        )
        self._blocked(
            lambda b: b["candidates"][1].__setitem__(
                "case_id", b["candidates"][0]["case_id"]
            ),
            "DESIGN_INTAKE_DUPLICATE_CANDIDATE_ID",
        )

    def test_reject_count_mismatch(self):
        self._blocked(
            lambda b: b["counts"].__setitem__("source_facts", 21),
            "DESIGN_INTAKE_COUNT_MISMATCH",
        )

    def test_reject_unbound_source_reference(self):
        self._blocked(
            lambda b: b["candidates"][0]["source_fact_refs"].append("NO-SUCH-FACT"),
            "DESIGN_INTAKE_UNBOUND_SOURCE_FACT",
        )
        self._blocked(
            lambda b: b["candidates"][0]["model_visible_input"][
                "available_evidence_ids"
            ].append("DF-020"),
            "DESIGN_INTAKE_UNBOUND_SOURCE_FACT",
        )

    def test_reject_source_receipt_mismatch_without_echo(self):
        with self.assertRaisesRegex(
            DesignDerivedIntakeError, "^DESIGN_INTAKE_SOURCE_FINGERPRINT_MISMATCH$"
        ):
            validate_design_derived_batch(
                self.pilot, expected_source_sha256="0" * 64
            )


if __name__ == "__main__":
    unittest.main()
