"""SYNTHETIC-only adversarial tests for local input-byte SHA-256 checks."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from dgsi.local_handoff_integrity import assess_local_input_sha256
from dgsi.real_case_handoff import RealCaseHandoffError

FILENAMES = (
    "diagnosis_result.json", "diagnostic_logs.jsonl",
    "spacecraft_context.json", "operational_context.json",
)


class SyntheticLocalInputIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.manifest = {
            "schema_version": "dgsi-real-case-handoff.v1",
            "case_id": "SYNTHETIC-TEST-01",
            "event_family_id": "SYNTHETIC-FAMILY-01",
            "source_class": "SYNTHETIC_FIXTURE",
            "source_owner": "SYNTHETIC-OWNER",
            "permission_status": "AUTHORIZED_FOR_REVIEW",
            "analysis_cutoff": "2026-04-12T09:10:00Z",
            "timestamp_policy": "ORIGINAL_TIMEZONE_AWARE",
            "redaction": {
                "personal_identifiers_removed": True,
                "sensitive_ids_pseudonymized": True,
                "time_shifted": False,
                "redacted_fields": [],
            },
            "available_files": [*FILENAMES, "expert_target.json"],
            "outcome_status": "UNKNOWN",
        }
        values = {}
        for name in FILENAMES:
            data = ("SYNTHETIC FILE: " + name).encode("ascii")
            (self.root / name).write_bytes(data)
            values[name] = hashlib.sha256(data).hexdigest()
        self.manifest["input_file_sha256"] = values

    def audit(self, **kw):
        return assess_local_input_sha256(self.manifest, self.root, **kw)

    def test_synthetic_bytes_match_but_not_approved(self):
        report = self.audit()
        self.assertTrue(report["input_file_sha256_matched"])
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertEqual(report["checked_input_count"], 4)
        for key in (
            "source_artifact_hashes_verified", "upstream_run_authenticated",
            "source_rights_verified", "expert_target_opened",
            "independent_expert_review_verified", "training_eligible",
            "gold_eligible", "split_assignment_allowed",
        ):
            self.assertFalse(report[key])

    def test_no_expert_target_is_ever_needed_or_opened(self):
        # The manifest declares a private target but there is no such file.
        self.assertTrue(self.audit()["input_file_sha256_matched"])

    def test_tampered_source_bytes_fail(self):
        (self.root / "diagnosis_result.json").write_bytes(b"SYNTHETIC-TAMPERED")
        report = self.audit()
        self.assertIn("INPUT_SHA256_MISMATCH", report["blocker_codes"])
        self.assertFalse(report["input_file_sha256_matched"])

    def test_missing_source_file_fails_without_path_disclosure(self):
        (self.root / "diagnosis_result.json").unlink()
        report = self.audit()
        self.assertIn("INPUT_FILE_UNAVAILABLE", report["blocker_codes"])
        text = json.dumps(report)
        self.assertNotIn(str(self.root), text)
        self.assertNotIn("SYNTHETIC-TEST-01", text)

    def test_omitted_digest_is_not_interpreted_as_verified(self):
        del self.manifest["input_file_sha256"]["diagnostic_logs.jsonl"]
        report = self.audit()
        self.assertIn("INPUT_SHA256_DECLARATIONS_INCOMPLETE", report["blocker_codes"])
        self.assertFalse(report["input_file_sha256_matched"])

    def test_no_digest_mapping_blocks(self):
        del self.manifest["input_file_sha256"]
        self.assertIn("INPUT_SHA256_DECLARATIONS_MISSING", self.audit()["blocker_codes"])

    def test_hash_for_undeclared_input_blocks(self):
        self.manifest["available_files"].remove("diagnostic_logs.jsonl")
        self.assertIn("INPUT_SHA256_UNDECLARED_FILE", self.audit()["blocker_codes"])

    def test_forbidden_expert_target_hash_is_schema_error(self):
        self.manifest["input_file_sha256"]["expert_target.json"] = "0" * 64
        with self.assertRaises(RealCaseHandoffError):
            self.audit()

    def test_traversal_filename_is_schema_error_before_io(self):
        self.manifest["input_file_sha256"]["../expert_target.json"] = "0" * 64
        with self.assertRaises(RealCaseHandoffError):
            self.audit()

    def test_non_hex_digest_is_schema_error(self):
        self.manifest["input_file_sha256"]["diagnosis_result.json"] = "x" * 64
        with self.assertRaises(RealCaseHandoffError):
            self.audit()

    def test_size_limit_blocks_streamed_read(self):
        report = self.audit(max_file_bytes=2)
        self.assertIn("INPUT_FILE_SIZE_LIMIT", report["blocker_codes"])
        self.assertFalse(report["input_file_sha256_matched"])

    def test_invalid_size_limit_fails_closed(self):
        with self.assertRaisesRegex(RealCaseHandoffError, "^INVALID_LOCAL_HASH_SIZE_LIMIT$"):
            self.audit(max_file_bytes=0)

    def test_missing_directory_fails(self):
        report = assess_local_input_sha256(self.manifest, self.root / "absent")
        self.assertIn("INPUT_DIRECTORY_UNAVAILABLE", report["blocker_codes"])

    def test_real_claim_with_matching_test_bytes_is_not_authenticity_proof(self):
        self.manifest["source_class"] = "ENGINEERING_TEST"
        report = self.audit()
        self.assertEqual(report["decision"], "LOCAL_INPUT_BYTES_MATCH_DECLARATIONS")
        self.assertFalse(report["source_rights_verified"])
        self.assertFalse(report["gold_eligible"])

    def test_symlinked_source_is_rejected_when_supported(self):
        target = self.root / "test-target.bin"
        target.write_bytes(b"SYNTHETIC LINK TARGET")
        path = self.root / "diagnosis_result.json"
        path.unlink()
        try:
            path.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not available on this runner")
        report = self.audit()
        self.assertIn("INPUT_FILE_LINK_OR_ESCAPE", report["blocker_codes"])
        self.assertFalse(report["input_file_sha256_matched"])

    def test_symlinked_directory_is_rejected_when_supported(self):
        alias = self.root / "input-alias"
        try:
            alias.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation not available on this runner")
        report = assess_local_input_sha256(self.manifest, alias)
        self.assertIn("INPUT_DIRECTORY_UNAVAILABLE", report["blocker_codes"])


if __name__ == "__main__":
    unittest.main()
