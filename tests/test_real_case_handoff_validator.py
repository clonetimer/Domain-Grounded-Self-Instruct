"""SYNTHETIC-ONLY tests of safe handoff metadata admission; no real case data."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.real_case_handoff import (
    RealCaseHandoffError, assess_handoff_manifest, audit_handoff_cohort,
    load_handoff_manifest,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_manifest() -> dict:
    return {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": "SYNTHETIC-CASE-01",
        "source_class": "SYNTHETIC_FIXTURE",
        "permission_status": "AUTHORIZED_FOR_TRAINING",  # intentionally misleading; still synthetic
        "source_owner": "SYNTHETIC_TEST_OWNER",
        "event_family_id": "SYNTHETIC-FAMILY-1",
        "analysis_cutoff": "2026-11-14T09:00:00+09:00",
        "timestamp_policy": "CONSISTENTLY_SHIFTED",
        "redaction": {
            "personal_identifiers_removed": True,
            "sensitive_ids_pseudonymized": True,
            "time_shifted": True,
            "redacted_fields": [],
        },
        "available_files": [
            "diagnosis_result.json", "diagnostic_logs.jsonl", "spacecraft_context.json",
            "operational_context.json", "expert_target.json",
        ],
        "outcome_status": "CONFIRMED",
    }


class SyntheticHandoffValidatorTests(unittest.TestCase):
    def test_synthetic_never_promoted_by_permission_assertion(self):
        result = assess_handoff_manifest(synthetic_manifest())
        self.assertEqual(result["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_eligible"])
        self.assertFalse(result["authorization_verified_by_software"])
        self.assertNotIn("case_id", result)

    def test_real_claim_only_gates_to_manual_review_not_gold(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "ENGINEERING_TEST"  # claim intentionally unverified
        result = assess_handoff_manifest(manifest)
        self.assertEqual(result["decision"], "ACCEPT_FOR_EXPERT_REVIEW")
        self.assertFalse(result["training_eligible"])
        self.assertFalse(result["source_content_reviewed"])

    def test_missing_evidence_files_is_conditional(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_GROUND_TEST"
        manifest["available_files"].remove("diagnostic_logs.jsonl")
        result = assess_handoff_manifest(manifest)
        self.assertEqual(result["decision"], "CONDITIONAL_ACCEPT")
        self.assertIn("MISSING_DIAGNOSTIC_LOG_FILE_DECLARATION", result["blocker_codes"])

    def test_missing_expert_target_not_filled_by_generation(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["available_files"].remove("expert_target.json")
        self.assertIn("EXPERT_TARGET_NOT_DECLARED", assess_handoff_manifest(manifest)["blocker_codes"])

    def test_unknown_permission_rejected(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["permission_status"] = "UNKNOWN"
        self.assertEqual(assess_handoff_manifest(manifest)["decision"], "REJECT")

    def test_restricted_review_only_not_training_ready(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["permission_status"] = "RESTRICTED_REVIEW_ONLY"
        self.assertEqual(assess_handoff_manifest(manifest)["decision"], "CONDITIONAL_ACCEPT")
        self.assertFalse(assess_handoff_manifest(manifest)["training_eligible"])

    def test_unredacted_identifiers_rejected(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["redaction"]["sensitive_ids_pseudonymized"] = False
        self.assertEqual(assess_handoff_manifest(manifest)["decision"], "REJECT")

    def test_unknown_source_rejected(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "UNKNOWN"
        self.assertEqual(assess_handoff_manifest(manifest)["decision"], "REJECT")

    def test_time_shift_declaration_must_match_policy(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["redaction"]["time_shifted"] = False
        self.assertIn("INCONSISTENT_TIME_SHIFT_DECLARATION", assess_handoff_manifest(manifest)["blocker_codes"])

    def test_partial_unknown_time_not_accepted(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest["timestamp_policy"] = "PARTIALLY_UNKNOWN"
        manifest["redaction"]["time_shifted"] = False
        self.assertEqual(assess_handoff_manifest(manifest)["decision"], "CONDITIONAL_ACCEPT")
        self.assertIn("TIMESTAMP_PROVENANCE_INCOMPLETE", assess_handoff_manifest(manifest)["blocker_codes"])

    def test_naive_cutoff_fails_even_without_optional_format_dependency(self):
        manifest = synthetic_manifest()
        manifest["analysis_cutoff"] = "2026-11-14T09:00:00"
        with self.assertRaises(RealCaseHandoffError):
            assess_handoff_manifest(manifest)

    def test_unknown_field_rejected_by_real_json_schema(self):
        manifest = synthetic_manifest()
        manifest["raw_telemetry"] = [[0.1, 0.2]]
        with self.assertRaisesRegex(RealCaseHandoffError, "^HANDOFF_SCHEMA_ADDITIONALPROPERTIES$"):
            assess_handoff_manifest(manifest)

    def test_invalid_nested_flag_rejected_by_real_json_schema(self):
        manifest = synthetic_manifest()
        manifest["redaction"]["time_shifted"] = "true"
        with self.assertRaisesRegex(RealCaseHandoffError, "^HANDOFF_SCHEMA_TYPE$"):
            assess_handoff_manifest(manifest)

    def test_missing_timestamp_policy_is_conditional(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest.pop("timestamp_policy")
        manifest["redaction"]["time_shifted"] = False
        result = assess_handoff_manifest(manifest)
        self.assertEqual(result["decision"], "CONDITIONAL_ACCEPT")
        self.assertIn("TIMESTAMP_PROVENANCE_INCOMPLETE", result["blocker_codes"])

    def test_blank_pseudonym_rejected(self):
        manifest = synthetic_manifest()
        manifest["event_family_id"] = "  "
        with self.assertRaisesRegex(RealCaseHandoffError, "^INVALID_HANDOFF_PSEUDONYM$"):
            assess_handoff_manifest(manifest)

    def test_duplicate_file_entries_rejected(self):
        manifest = synthetic_manifest()
        manifest["available_files"].append("diagnosis_result.json")
        with self.assertRaisesRegex(RealCaseHandoffError, "^DUPLICATE_HANDOFF_FILE_ENTRY$"):
            assess_handoff_manifest(manifest)

    def test_duplicate_manifest_json_key_rejected(self):
        text = '{"case_id":"SYNTHETIC-1","case_id":"SYNTHETIC-2"}'
        with self.assertRaisesRegex(RealCaseHandoffError, "^DUPLICATE_MANIFEST_JSON_KEY$"):
            load_handoff_manifest(text)

    def test_nonfinite_json_number_rejected(self):
        with self.assertRaisesRegex(RealCaseHandoffError, "^NONFINITE_MANIFEST_JSON_NUMBER$"):
            load_handoff_manifest('{"any":NaN}')

    def test_batch_duplicate_id_rejected_without_echo(self):
        manifest = synthetic_manifest()
        with self.assertRaisesRegex(RealCaseHandoffError, "^DUPLICATE_HANDOFF_CASE_ID$"):
            audit_handoff_cohort([manifest, copy.deepcopy(manifest)])

    def test_batch_groups_same_incident_and_never_assigns_split(self):
        first, second = synthetic_manifest(), synthetic_manifest()
        second["case_id"] = "SYNTHETIC-CASE-02"
        result = audit_handoff_cohort([first, second])
        self.assertEqual(result["case_count"], 2)
        self.assertEqual(result["event_family_count"], 1)
        self.assertEqual(result["repeated_event_family_count"], 1)
        self.assertFalse(result["split_assignment_allowed"])
        self.assertEqual(result["gold_eligible_count"], 0)
        self.assertNotIn("SYNTHETIC-FAMILY-1", json.dumps(result))

    def test_batch_mixed_classes_only_aggregate(self):
        first = synthetic_manifest()
        second = synthetic_manifest()
        second["case_id"] = "SYNTHETIC-CASE-03"
        second["event_family_id"] = "SYNTHETIC-FAMILY-03"
        second["source_class"] = "ENGINEERING_TEST"  # unverified source claim
        result = audit_handoff_cohort([first, second])
        self.assertEqual(result["decision_counts"]["SYNTHETIC_TEST_ONLY"], 1)
        self.assertEqual(result["decision_counts"]["ACCEPT_FOR_EXPERT_REVIEW"], 1)
        self.assertNotIn("case_id", result)
        self.assertNotIn("event_family_id", result)

    def test_outcome_unknown_warns_not_fake_confirmed(self):
        manifest = synthetic_manifest()
        manifest["outcome_status"] = "UNKNOWN"
        result = assess_handoff_manifest(manifest)
        self.assertIn("OUTCOME_NOT_ADJUDICATED", result["warning_codes"])

    def test_no_source_owner_conditional(self):
        manifest = synthetic_manifest()
        manifest["source_class"] = "REAL_FLIGHT"
        manifest.pop("source_owner")
        result = assess_handoff_manifest(manifest)
        self.assertEqual(result["decision"], "CONDITIONAL_ACCEPT")
        self.assertIn("SOURCE_OWNER_NOT_DOCUMENTED", result["blocker_codes"])


if __name__ == "__main__":
    unittest.main()
