"""SYNTHETIC ONLY: test declared run-reference reuse; no real material."""
from __future__ import annotations

import copy
import json
import unittest

from dgsi.handoff_run_lineage import RunLineageAuditError, audit_handoff_run_lineage


def synthetic(case_id="SYNTHETIC-CASE-A", family="SYNTHETIC-FAMILY-A",
              run_ref="synthetic://ml-run/001", source_class="SYNTHETIC_FIXTURE"):
    manifest = {
        "schema_version": "dgsi-real-case-handoff.v1",
        "case_id": case_id, "event_family_id": family,
        "source_class": source_class,
        "permission_status": "AUTHORIZED_FOR_REVIEW",
        "source_owner": "SYNTHETIC-TEST-OWNER",
        "analysis_cutoff": "2026-11-15T03:00:00Z",
        "timestamp_policy": "ORIGINAL_TIMEZONE_AWARE",
        "redaction": {
            "personal_identifiers_removed": True,
            "sensitive_ids_pseudonymized": True,
            "time_shifted": False,
            "redacted_fields": [],
        },
        "available_files": [
            "diagnosis_result.json", "diagnostic_logs.jsonl",
            "spacecraft_context.json", "operational_context.json", "expert_target.json",
        ],
        "outcome_status": "UNKNOWN",
    }
    lineage = {
        "case_id": case_id,
        "source_group": family,
        "diagnosis_run_refs": [run_ref] if run_ref is not None else [],
        "generation_method": "SYNTHETIC test record",
    }
    return {"manifest": manifest, "lineage": lineage, "split": None}


class RunLineageSyntheticTests(unittest.TestCase):
    def test_synthetic_only_cannot_become_gold(self):
        result = audit_handoff_run_lineage([synthetic()])
        self.assertEqual(result["decision"], "SYNTHETIC_TEST_ONLY")
        for key in ("source_authenticity_verified", "run_identity_authenticated",
                    "split_assignment_allowed", "expert_review_verified",
                    "gold_eligible", "training_eligible"):
            self.assertFalse(result[key])

    def test_reused_run_across_alias_families_signals_review(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B")
        result = audit_handoff_run_lineage([a, b])
        self.assertEqual(result["cross_family_run_reuse_signature_count"], 1)
        self.assertIn("DECLARED_DIAGNOSIS_RUN_REUSED_ACROSS_FAMILIES",
                      result["manual_review_codes"])

    def test_cross_split_same_run_blocked_without_digest_match(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B")
        a["split"], b["split"] = "train", "test"
        report = audit_handoff_run_lineage([a, b])
        self.assertEqual(report["decision"], "BLOCKED_RUN_LINEAGE")
        self.assertIn("CROSS_SPLIT_DECLARED_DIAGNOSIS_RUN", report["blocker_codes"])
        self.assertEqual(report["cross_split_run_reuse_signature_count"], 1)
        self.assertEqual(report["existing_split_counts"]["test"], 1)

    def test_cross_split_validation_also_blocked(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B")
        a["split"], b["split"] = "validation", "train"
        self.assertIn("CROSS_SPLIT_DECLARED_DIAGNOSIS_RUN",
                      audit_handoff_run_lineage([a, b])["blocker_codes"])

    def test_no_duplicate_run_without_collision(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B",
                      "synthetic://ml-run/002")
        report = audit_handoff_run_lineage([a, b])
        self.assertEqual(report["cross_family_run_reuse_signature_count"], 0)
        self.assertEqual(report["declared_run_signature_count"], 2)

    def test_same_family_run_is_not_cross_family_reuse(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-A")
        report = audit_handoff_run_lineage([a, b])
        self.assertEqual(report["repeated_incident_family_count"], 1)
        self.assertEqual(report["cross_family_run_reuse_signature_count"], 0)

    def test_cross_split_same_family_even_different_runs_rejected(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-A",
                      "synthetic://ml-run/002")
        a["split"], b["split"] = "train", "validation"
        with self.assertRaisesRegex(RunLineageAuditError, "^CROSS_SPLIT_INCIDENT_FAMILY$"):
            audit_handoff_run_lineage([a, b])

    def test_mixed_source_same_run_blocks_synthetic_laundering(self):
        a = synthetic()
        b = synthetic("PSEUDONYM-B", "FAMILY-B", source_class="ENGINEERING_TEST")
        b["lineage"]["generation_method"] = "captured adapter"  # unverified claim
        report = audit_handoff_run_lineage([a, b])
        self.assertIn("SYNTHETIC_REAL_RUN_LINEAGE_ALIAS", report["blocker_codes"])
        self.assertIn("SYNTHETIC_RUN_LINEAGE_MISDECLARED_REAL", report["blocker_codes"])

    def test_synthetic_marker_cannot_claim_real_without_duplicate_run(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A",
                      "synthetic://another-run", "REAL_GROUND_TEST")
        a["lineage"]["generation_method"] = None
        report = audit_handoff_run_lineage([a])
        self.assertEqual(report["decision"], "BLOCKED_RUN_LINEAGE")
        self.assertIn("SYNTHETIC_RUN_LINEAGE_MISDECLARED_REAL", report["blocker_codes"])

    def test_real_claim_unverified_is_never_gold(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A", "custodian-run-001",
                      "REAL_GROUND_TEST")
        a["lineage"]["generation_method"] = None
        report = audit_handoff_run_lineage([a])
        self.assertEqual(report["decision"], "PASS_UNTRUSTED_RUN_CLAIMS_ONLY")
        self.assertFalse(report["gold_eligible"])
        self.assertFalse(report["training_eligible"])

    def test_missing_run_refs_requires_review_not_pass(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A", None, "ENGINEERING_TEST")
        a["lineage"]["generation_method"] = None
        report = audit_handoff_run_lineage([a])
        self.assertEqual(report["decision"], "MANUAL_RUN_LINEAGE_REVIEW")
        self.assertEqual(report["missing_run_reference_case_count"], 1)

    def test_nonready_manifest_is_not_clean(self):
        a = synthetic("PSEUDONYM-A", "FAMILY-A", "custodian-run-001",
                      "REAL_GROUND_TEST")
        a["lineage"]["generation_method"] = None
        a["manifest"]["permission_status"] = "RESTRICTED_REVIEW_ONLY"
        result = audit_handoff_run_lineage([a])
        self.assertEqual(result["decision"], "MANUAL_RUN_LINEAGE_REVIEW")
        self.assertEqual(result["handoff_not_ready_case_count"], 1)

    def test_missing_or_extra_lineage_keys_rejected(self):
        a = synthetic()
        del a["lineage"]["diagnosis_run_refs"]
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_RUN_LINEAGE_SHAPE$"):
            audit_handoff_run_lineage([a])
        b = synthetic()
        b["lineage"]["expert_target"] = {"root_cause": "NOT AUTHORIZED"}
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_RUN_LINEAGE_SHAPE$"):
            audit_handoff_run_lineage([b])

    def test_case_and_family_binding_required(self):
        a = synthetic()
        a["lineage"]["case_id"] = "DIFFERENT"
        with self.assertRaisesRegex(RunLineageAuditError, "^RUN_LINEAGE_MANIFEST_BINDING_MISMATCH$"):
            audit_handoff_run_lineage([a])
        b = synthetic()
        b["lineage"]["source_group"] = "OTHER"
        with self.assertRaisesRegex(RunLineageAuditError, "^RUN_LINEAGE_MANIFEST_BINDING_MISMATCH$"):
            audit_handoff_run_lineage([b])

    def test_repeated_refs_in_one_case_not_allowed(self):
        a = synthetic()
        a["lineage"]["diagnosis_run_refs"] *= 2
        with self.assertRaisesRegex(RunLineageAuditError, "^DUPLICATE_DIAGNOSIS_RUN_REFERENCE$"):
            audit_handoff_run_lineage([a])

    def test_whitespace_and_bad_run_id_rejected(self):
        for ref in ("", " ", " shared-run ", 7, None):
            with self.subTest(ref=ref):
                a = synthetic()
                a["lineage"]["diagnosis_run_refs"] = [ref]
                with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_DIAGNOSIS_RUN_REFERENCES$"):
                    audit_handoff_run_lineage([a])

    def test_partial_and_invalid_preexisting_splits_fail_closed(self):
        a = synthetic()
        b = synthetic("SYNTHETIC-CASE-B", "SYNTHETIC-FAMILY-B",
                      "synthetic://ml-run/002")
        a["split"] = "train"
        with self.assertRaisesRegex(RunLineageAuditError, "^PARTIALLY_ASSIGNED_SPLIT_COHORT$"):
            audit_handoff_run_lineage([a, b])
        a["split"] = "gold"
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_PREEXISTING_SPLIT$"):
            audit_handoff_run_lineage([a])

    def test_duplicate_case_identifier_rejected(self):
        a = synthetic()
        b = synthetic(family="SYNTHETIC-FAMILY-B")
        with self.assertRaisesRegex(RunLineageAuditError, "^DUPLICATE_HANDOFF_CASE_ID$"):
            audit_handoff_run_lineage([a, b])

    def test_reject_nonmanifest_fields_before_reporting(self):
        a = synthetic()
        a["manifest"]["raw_telemetry"] = [[1.0, 2.0]]
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_HANDOFF_MANIFEST$"):
            audit_handoff_run_lineage([a])

    def test_report_is_aggregate_and_does_not_emit_identifiers(self):
        a = synthetic("SECRET-CASE-A", "SECRET-FAMILY-A")
        b = synthetic("SECRET-CASE-B", "SECRET-FAMILY-B")
        report = audit_handoff_run_lineage([a, b])
        text = json.dumps(report, ensure_ascii=False)
        for word in ("SECRET-", "synthetic://ml-run/001", "SYNTHETIC-TEST-OWNER"):
            self.assertNotIn(word, text)

    def test_invalid_batch_entry_and_method_types(self):
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_RUN_LINEAGE_BATCH$"):
            audit_handoff_run_lineage(None)
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_RUN_LINEAGE_ENTRY$"):
            audit_handoff_run_lineage([{"manifest": {}, "lineage": {}}])
        a = synthetic()
        a["lineage"]["generation_method"] = []
        with self.assertRaisesRegex(RunLineageAuditError, "^INVALID_RUN_LINEAGE_GENERATION_METHOD$"):
            audit_handoff_run_lineage([a])


if __name__ == "__main__":
    unittest.main()
