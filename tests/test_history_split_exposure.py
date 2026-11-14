"""SYNTHETIC-only adversarial tests for historical reuse and split exposure."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.history_split_exposure import (
    HistorySplitExposureError,
    audit_history_split_exposure,
)

_BASE = json.loads(
    (Path(__file__).resolve().parents[1] /
     "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8")
)


def case_for(tag: str) -> dict:
    result = copy.deepcopy(_BASE)
    result["case_id"] = "SYNTH-CASE-" + tag
    result["provenance"]["source_group"] = "SYNTH-EPISODE-" + tag
    result["input"]["historical_cases"] = []
    result["provenance"]["historical_case_refs"] = []
    result["expected_output"]["historical_experience_relevance"] = []
    return result


def add_history(case: dict, ref: str) -> None:
    case["input"]["historical_cases"].append({
        "case_ref": ref,
        "similarity_basis": ["SYNTHETIC: analogous fault category"],
        "prior_conclusion": "SYNTHETIC: unresolved historical candidate",
        "outcome_status": "UNRESOLVED",
        "applicability_limitations": ["SYNTHETIC: no expert-confirmed root cause"],
    })
    case["provenance"]["historical_case_refs"].append(ref)


def record(case: dict, split: str) -> dict:
    return {"case": case, "split": split}


class HistorySplitExposureSyntheticTests(unittest.TestCase):
    def assert_blocked(self, records, code):
        with self.assertRaisesRegex(HistorySplitExposureError, "^" + code + "$"):
            audit_history_split_exposure(records)

    def test_disjoint_cases_without_history_pass_structural_only(self):
        result = audit_history_split_exposure([
            record(case_for("train"), "train"),
            record(case_for("test"), "test"),
        ])
        self.assertEqual(result["decision"], "PASS_STRUCTURAL_ONLY")
        self.assertEqual(result["distinct_case_count"], 2)
        self.assertEqual(result["history_reference_count"], 0)
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])

    def test_train_prompt_cannot_reference_heldout_case(self):
        training, heldout = case_for("train"), case_for("heldout")
        add_history(training, heldout["case_id"])
        self.assert_blocked([
            record(training, "train"), record(heldout, "test")
        ], "CROSS_SPLIT_HISTORY_CASE_REFERENCE")

    def test_validation_prompt_cannot_reference_train_case(self):
        training, validation = case_for("train"), case_for("val")
        add_history(validation, training["case_id"])
        self.assert_blocked([
            record(training, "train"), record(validation, "validation")
        ], "CROSS_SPLIT_HISTORY_CASE_REFERENCE")

    def test_cross_split_episode_alias_is_detected(self):
        training, heldout = case_for("train"), case_for("heldout")
        add_history(training, heldout["provenance"]["source_group"])
        self.assert_blocked([
            record(training, "train"), record(heldout, "test")
        ], "CROSS_SPLIT_HISTORY_EPISODE_REFERENCE")

    def test_self_historical_case_is_not_independent_evidence(self):
        item = case_for("same")
        add_history(item, item["case_id"])
        self.assert_blocked([record(item, "train")], "SELF_REFERENTIAL_HISTORICAL_CASE")

    def test_same_episode_group_alias_is_not_historical_evidence(self):
        item = case_for("same")
        add_history(item, item["provenance"]["source_group"])
        self.assert_blocked([record(item, "train")], "SELF_REFERENTIAL_HISTORICAL_CASE")

    def test_reusing_unknown_external_history_across_splits_requires_review(self):
        a, b = case_for("train"), case_for("heldout")
        add_history(a, "SYNTH-EXTERNAL-MEMORY-001")
        add_history(b, "SYNTH-EXTERNAL-MEMORY-001")
        result = audit_history_split_exposure([
            record(a, "train"), record(b, "test")
        ])
        self.assertEqual(result["decision"], "MANUAL_HISTORY_REFERENCE_REVIEW")
        self.assertEqual(result["shared_history_reference_across_split_count"], 1)
        self.assertTrue(result["history_asof_and_identity_review_required"])
        self.assertNotIn("SYNTH-EXTERNAL-MEMORY-001", str(result))
        self.assertFalse(result["gold_eligible"])

    def test_same_known_history_within_one_split_is_not_a_cross_split_leak(self):
        a, b = case_for("one"), case_for("two")
        add_history(a, "SYNTH-EXTERNAL-MEMORY-001")
        add_history(b, "SYNTH-EXTERNAL-MEMORY-001")
        result = audit_history_split_exposure([
            record(a, "train"), record(b, "train")
        ])
        self.assertEqual(result["decision"], "PASS_STRUCTURAL_ONLY")
        self.assertTrue(result["history_asof_and_identity_review_required"])
        self.assertEqual(result["history_reference_count"], 2)

    def test_known_history_in_same_split_still_needs_temporal_audit(self):
        previous, current = case_for("old"), case_for("current")
        add_history(current, previous["case_id"])
        result = audit_history_split_exposure([
            record(previous, "train"), record(current, "train")
        ])
        self.assertEqual(result["decision"], "PASS_STRUCTURAL_ONLY")
        self.assertTrue(result["history_asof_and_identity_review_required"])

    def test_duplicated_case_id_across_splits_is_blocked(self):
        a, b = case_for("one"), case_for("one")
        self.assert_blocked([
            record(a, "train"), record(b, "test")
        ], "CROSS_SPLIT_CASE_ID")

    def test_duplicated_episode_family_across_splits_is_blocked(self):
        a, b = case_for("one"), case_for("two")
        b["provenance"]["source_group"] = a["provenance"]["source_group"]
        self.assert_blocked([
            record(a, "train"), record(b, "validation")
        ], "CROSS_SPLIT_INCIDENT_FAMILY")

    def test_case_id_must_not_change_episode_identity(self):
        a, b = case_for("one"), case_for("one")
        b["provenance"]["source_group"] = "SYNTH-UNRELATED-EPISODE"
        self.assert_blocked([
            record(a, "train"), record(b, "train")
        ], "CASE_INCIDENT_FAMILY_CHANGED")

    def test_invalid_case_does_not_echo_private_payload(self):
        item = case_for("bad")
        item["input"]["raw_telemetry"] = [{"secret": "SYNTH-PRIVATE-PLACEHOLDER"}]
        self.assert_blocked([record(item, "train")], "INVALID_DIAGNOSTIC_CASE")

    def test_unexpected_manifest_field_is_rejected(self):
        self.assert_blocked([
            {"case": case_for("one"), "split": "train", "unredacted": "SYNTH-ONLY"}
        ], "INVALID_CASE_BATCH_ENTRY")

    def test_invalid_split_is_rejected(self):
        self.assert_blocked([record(case_for("one"), "gold")], "INVALID_SPLIT")

    def test_empty_batch_is_auditable_but_not_training_ready(self):
        result = audit_history_split_exposure([])
        self.assertEqual(result["case_packet_count"], 0)
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])


if __name__ == "__main__":
    unittest.main()
