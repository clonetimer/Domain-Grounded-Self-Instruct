"""SYNTHETIC_TEST_ONLY: contract and byte-verification tests, not flight data."""
from __future__ import annotations
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from jsonschema import FormatChecker

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def fixture(root: Path) -> dict:
    roles = ["CONFIGURATION", "EXECUTION_RECORD", "PHYSICS_QA", "DIAGNOSTIC_LOG", "ML_RESULT", "ML_EVALUATION", "SPACECRAFT_CONTEXT", "OPERATIONAL_CONTEXT"]
    visible_roles = {"DIAGNOSTIC_LOG", "ML_RESULT", "SPACECRAFT_CONTEXT", "OPERATIONAL_CONTEXT"}
    artifacts = []
    for index, role in enumerate(roles):
        data = (json.dumps({"evidence_origin": "SYNTHETIC_TEST_ONLY", "record": f"fixture-{index}"}) + "\n").encode()
        relative = f"artifacts/a{index}.json"
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        artifacts.append({"artifact_id": f"A{index}", "run_id": "SYNTHETIC-RUN-1", "role": role,
                          "visibility": "MODEL_VISIBLE" if role in visible_roles else "QA_ONLY",
                          "path": relative, "format": "json", "size_bytes": len(data),
                          "sha256": hashlib.sha256(data).hexdigest(), "available_at": "2026-01-01T00:00:05Z"})
    stages = ["injection_configured", "injection_executed", "physical_effect_observed", "diagnostic_effect_observed", "upstream_ml_detected", "upstream_ml_localized"]
    return {"schema_version": "dgsi-simulation-run-receipt.v1", "evidence_origin": "SYNTHETIC_TEST_ONLY",
            "candidate_class": "SIMULATION_CASE_CANDIDATE", "run_id": "SYNTHETIC-RUN-1",
            "event_family_id": "SYNTHETIC-FAMILY-1", "scenario_id": "SYNTHETIC-SCENARIO-1", "replay_of": None,
            "simulator": {"engine": "OTHER", "version": "fixture-only", "model_revision": "test-fixture", "configuration_sha256": artifacts[0]["sha256"], "random_seed": 1},
            "started_at": "2026-01-01T00:00:00Z", "ended_at": "2026-01-01T00:00:10Z", "analysis_cutoff": "2026-01-01T00:00:06Z",
            "artifacts": artifacts, "model_visible_artifact_refs": ["A3", "A4", "A6", "A7"],
            "stages": {s: {"status": "YES", "evidence_refs": [f"A{i}"]} for i, s in enumerate(stages)},
            "review_status": "REVIEW_REQUIRED", "training_authorized": False, "gold_authorized": False, "sft_export_authorized": False}


class SimulationRunReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.receipt = fixture(self.root)

    def api(self):
        spec = importlib.util.find_spec("dgsi.simulation_run_receipt")
        self.assertIsNotNone(spec, "simulation run receipt validator is not implemented")
        return importlib.import_module("dgsi.simulation_run_receipt")

    def validate(self, r=None, *, verify=True):
        return self.api().validate_simulation_run_receipt(r or self.receipt, artifact_root=self.root if verify else None)

    def reject(self, code, r=None, *, verify=True):
        api = self.api()
        with self.assertRaisesRegex(api.SimulationReceiptError, "^" + code + "$"):
            self.validate(r, verify=verify)

    def test_self_contained_contract_exists(self):
        self.api()

    def test_fixture_is_not_counted_as_real_run(self):
        out = self.validate()
        self.assertEqual(out["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertEqual(out["artifact_bytes_verified"], 8)
        self.assertEqual(out["actual_simulation_run_count"], 0)
        self.assertFalse(out["training_authorized"])
        self.assertFalse(out["gold_authorized"])
        self.assertEqual(out["sft_records_emitted"], 0)

    def test_metadata_mode_never_claims_bytes_verified(self):
        out = self.validate(verify=False)
        self.assertEqual(out["artifact_bytes_verified"], 0)
        self.assertEqual(out["verification_scope"], "METADATA_ONLY")

    def test_unknown_is_not_no_or_success(self):
        self.receipt["stages"]["physical_effect_observed"] = {"status": "UNKNOWN", "evidence_refs": []}
        self.assertEqual(self.validate()["unknown_stage_count"], 1)

    def test_no_requires_evidence_but_is_valid_outcome(self):
        self.receipt["stages"]["upstream_ml_detected"]["status"] = "NO"
        self.assertEqual(self.validate()["reported_no_stage_count"], 1)
        self.receipt["stages"]["upstream_ml_detected"]["evidence_refs"] = []
        self.reject("SIM_STAGE_EVIDENCE_REQUIRED")

    def test_false_positive_and_missed_detection_are_not_forced_success(self):
        self.receipt["stages"]["physical_effect_observed"]["status"] = "NO"
        self.receipt["stages"]["diagnostic_effect_observed"]["status"] = "NO"
        self.receipt["stages"]["upstream_ml_detected"]["status"] = "YES"
        self.receipt["stages"]["upstream_ml_localized"]["status"] = "NO"
        self.assertEqual(self.validate()["reported_no_stage_count"], 3)

    def test_yes_cannot_use_wrong_role(self):
        self.receipt["stages"]["physical_effect_observed"]["evidence_refs"] = ["A0"]
        self.reject("SIM_STAGE_EVIDENCE_ROLE_MISMATCH")

    def test_dangling_and_duplicate_stage_refs(self):
        for refs, code in [(["NOT-THERE"], "SIM_UNRESOLVED_ARTIFACT_REF"), (["A2", "A2"], "SIM_SCHEMA_INVALID")]:
            with self.subTest(refs=refs):
                r = copy.deepcopy(self.receipt)
                r["stages"]["physical_effect_observed"]["evidence_refs"] = refs
                self.reject(code, r)

    def test_duplicate_artifact_ids_and_cross_run_files(self):
        r = copy.deepcopy(self.receipt)
        r["artifacts"][1]["artifact_id"] = "A0"
        self.reject("SIM_DUPLICATE_ARTIFACT_ID", r)
        self.receipt["artifacts"][0]["run_id"] = "OTHER-RUN"
        self.reject("SIM_CROSS_RUN_ARTIFACT")

    def test_configuration_digest_is_bound_to_configuration_artifact(self):
        self.receipt["simulator"]["configuration_sha256"] = "f" * 64
        self.reject("SIM_CONFIGURATION_FINGERPRINT_MISMATCH")

    def test_paths_are_portable_relative_no_traversal_or_streams(self):
        for bad in ["../escape.json", "/abs.json", "C:/abs.json", "C:relative.json", "..\\secret", "foo//bar", "./foo", "foo/../bar", "foo:stream", "foo/bar.", "foo/CON", "foo/a ", "\\\\server\\share"]:
            with self.subTest(path=bad):
                r = copy.deepcopy(self.receipt)
                r["artifacts"][0]["path"] = bad
                self.reject("SIM_UNSAFE_ARTIFACT_PATH", r, verify=False)

    def test_case_insensitive_path_alias_rejected(self):
        self.receipt["artifacts"][1]["path"] = "ARTIFACTS/A0.JSON"
        self.reject("SIM_ARTIFACT_PATH_ALIAS", verify=False)

    def test_shared_hidden_visible_digest_rejected(self):
        self.receipt["artifacts"][3]["sha256"] = self.receipt["artifacts"][0]["sha256"]
        self.reject("SIM_CROSS_VISIBILITY_DIGEST_ALIAS", verify=False)

    def test_missing_modified_or_size_mismatch_bytes(self):
        p = self.root / self.receipt["artifacts"][0]["path"]
        p.write_bytes(b"wrong")
        self.reject("SIM_ARTIFACT_SIZE_MISMATCH")
        self.receipt["artifacts"][0]["size_bytes"] = 5
        self.reject("SIM_ARTIFACT_HASH_MISMATCH")
        p.unlink()
        self.reject("SIM_ARTIFACT_NOT_READABLE")

    def test_symlink_not_followed(self):
        p = self.root / self.receipt["artifacts"][0]["path"]
        target = self.root / "original.json"
        p.rename(target)
        try:
            p.symlink_to(target)
        except OSError:
            self.skipTest("symlink creation not supported in this environment")
        self.reject("SIM_SYMLINK_FORBIDDEN")

    def test_hidden_roles_cannot_be_model_visible(self):
        self.receipt["artifacts"][0]["visibility"] = "MODEL_VISIBLE"
        self.reject("SIM_HIDDEN_ROLE_EXPOSED", verify=False)

    def test_hidden_reference_cannot_be_selected(self):
        self.receipt["model_visible_artifact_refs"].append("A0")
        self.reject("SIM_HIDDEN_ARTIFACT_SELECTED", verify=False)

    def test_model_visibility_selection_must_be_complete(self):
        self.receipt["model_visible_artifact_refs"].remove("A3")
        self.reject("SIM_VISIBLE_SELECTION_MISMATCH", verify=False)

    def test_future_visible_evidence_blocked_unreferenced_qa_may_be_later(self):
        # Later QA can be archived, but cannot support a claimed as-of stage.
        self.receipt["stages"]["physical_effect_observed"] = {"status": "UNKNOWN", "evidence_refs": []}
        self.receipt["artifacts"][2]["available_at"] = "2026-01-02T00:00:00Z"
        self.validate()
        self.receipt["artifacts"][3]["available_at"] = "2026-01-02T00:00:00Z"
        self.reject("SIM_POST_CUTOFF_VISIBLE_ARTIFACT")

    def test_future_qa_cannot_support_asof_stage_outcome(self):
        # Stage attestations are not exempt merely because their source is QA_ONLY.
        for status in ("YES", "NO", "UNKNOWN"):
            with self.subTest(stage_status=status):
                r = copy.deepcopy(self.receipt)
                r["stages"]["physical_effect_observed"]["status"] = status
                r["artifacts"][2]["available_at"] = "2026-01-01T00:00:06.000001Z"
                self.reject("SIM_POST_CUTOFF_STAGE_EVIDENCE", r, verify=False)

    def test_stage_receipt_cutoff_is_timezone_aware_and_inclusive(self):
        self.receipt["artifacts"][2]["available_at"] = "2026-01-01T09:00:06+09:00"
        self.validate(verify=False)
        self.receipt["artifacts"][2]["available_at"] = "2026-01-01T09:00:07+09:00"
        self.reject("SIM_POST_CUTOFF_STAGE_EVIDENCE", verify=False)

    def test_future_qa_can_remain_when_not_cited_by_any_stage(self):
        self.receipt["stages"]["physical_effect_observed"] = {"status": "UNKNOWN", "evidence_refs": []}
        self.receipt["artifacts"][2]["available_at"] = "2026-01-02T00:00:00Z"
        self.assertEqual(self.validate(verify=False)["unknown_stage_count"], 1)

    def test_timezone_required_and_end_order_checked(self):
        self.receipt["started_at"] = "2026-01-01T00:00:00"
        self.reject("SIM_INVALID_TIMESTAMP")
        self.receipt["started_at"] = "2026-01-01T00:00:11Z"
        self.reject("SIM_INVALID_RUN_CHRONOLOGY")

    def test_timestamp_error_independent_of_optional_format_plugins(self):
        for plugins in (True, False):
            with self.subTest(optional_format_plugins=plugins):
                r = copy.deepcopy(self.receipt)
                r["started_at"] = "2026-01-01T00:00:00"
                if plugins:
                    self.reject("SIM_INVALID_TIMESTAMP", r, verify=False)
                else:
                    with mock.patch.dict(FormatChecker.checkers, {}, clear=True):
                        self.reject("SIM_INVALID_TIMESTAMP", r, verify=False)

    def test_qa_timestamp_is_checked_without_optional_format_plugins(self):
        for bad in ("2026-02-30T00:00:00Z", "2026-01-01T00:00:00", "not-a-date"):
            with self.subTest(timestamp=bad):
                r = copy.deepcopy(self.receipt)
                r["artifacts"][2]["available_at"] = bad
                with mock.patch.dict(FormatChecker.checkers, {}, clear=True):
                    self.reject("SIM_INVALID_TIMESTAMP", r, verify=False)

    def test_timestamp_profile_rejects_ambiguous_or_lossy_inputs(self):
        bad_values = ["20260101T000000Z", "2026-01-01 00:00:00Z", "2026-01-01",
                      "2026-01-01T00:00:00-00:00", "2026-01-01T00:00:00+00:60",
                      "2026-01-01T00:00:60Z", "2026-01-01T00:00:00.0000001Z"]
        for bad in bad_values:
            with self.subTest(timestamp=bad):
                r = copy.deepcopy(self.receipt)
                r["analysis_cutoff"] = bad
                with mock.patch.dict(FormatChecker.checkers, {}, clear=True):
                    self.reject("SIM_INVALID_TIMESTAMP", r, verify=False)

    def test_timezone_offsets_compare_instants_and_accept_lowercase_z(self):
        self.receipt["analysis_cutoff"] = "2026-01-01T09:00:06+09:00"
        self.receipt["artifacts"][3]["available_at"] = "2026-01-01t00:00:06z"
        self.validate()
        self.receipt["artifacts"][3]["available_at"] = "2026-01-01T09:00:07+09:00"
        self.reject("SIM_POST_CUTOFF_VISIBLE_ARTIFACT")

    def test_fractional_future_evidence_is_not_rounded_to_cutoff(self):
        self.receipt["artifacts"][3]["available_at"] = "2026-01-01T00:00:06.000001Z"
        self.reject("SIM_POST_CUTOFF_VISIBLE_ARTIFACT")

    def test_cutoff_before_run_rejected(self):
        self.receipt["analysis_cutoff"] = "2025-12-31T23:00:00Z"
        self.reject("SIM_INVALID_ANALYSIS_CUTOFF")

    def test_replay_does_not_cross_source_family(self):
        self.receipt["replay_of"] = {"run_id": "SYNTHETIC-RUN-0", "event_family_id": "WRONG", "scenario_id": self.receipt["scenario_id"]}
        self.reject("SIM_REPLAY_LINEAGE_MISMATCH")
        self.receipt["replay_of"]["event_family_id"] = self.receipt["event_family_id"]
        self.validate()
        self.receipt["replay_of"]["run_id"] = self.receipt["run_id"]
        self.reject("SIM_REPLAY_SELF_REFERENCE")

    def test_renaming_fixture_to_actual_is_not_admitted(self):
        self.receipt["evidence_origin"] = "ACTUAL_SIMULATION_RUN"
        self.reject("SIM_SYNTHETIC_FIXTURE_MISLABELED")

    def test_no_silent_privilege_upgrade(self):
        for field in ["training_authorized", "gold_authorized", "sft_export_authorized"]:
            with self.subTest(field=field):
                r = copy.deepcopy(self.receipt)
                r[field] = True
                self.reject("SIM_SCHEMA_INVALID", r)
        self.receipt["review_status"] = "APPROVED"
        self.reject("SIM_SCHEMA_INVALID")

    def test_nested_extra_truth_fields_rejected(self):
        self.receipt["simulator"]["fault_id"] = "HIDDEN"
        self.reject("SIM_SCHEMA_INVALID")

    def test_report_does_not_echo_ids_paths_targets_or_payloads(self):
        text = json.dumps(self.validate())
        for private in ["SYNTHETIC-RUN-1", "artifacts/a0.json", "configuration_sha256", "fixture-0"]:
            self.assertNotIn(private, text)

    def test_strict_json_duplicate_keys_and_nonfinite(self):
        api = self.api()
        for text in ['{"a":1,"a":2}', '{"v":NaN}', '{"v":Infinity}', '{"v":1e999}']:
            with self.subTest(text=text):
                with self.assertRaises(api.SimulationReceiptError):
                    api.load_receipt_text(text)

    def test_known_hidden_label_in_visible_payload_is_rejected(self):
        a = self.receipt["artifacts"][3]
        data = b'{"evidence_origin":"SYNTHETIC_TEST_ONLY","nested":{"injection_time":10}}'
        (self.root / a["path"]).write_bytes(data)
        a["size_bytes"] = len(data)
        a["sha256"] = hashlib.sha256(data).hexdigest()
        self.reject("SIM_VISIBLE_TRUTH_KEY")

    def test_valid_jsonl_is_checked_and_empty_jsonl_rejected(self):
        a = self.receipt["artifacts"][3]
        a["format"] = "jsonl"
        data = b'{"record":"one"}\n{"record":"two"}\n'
        (self.root / a["path"]).write_bytes(data)
        a["size_bytes"] = len(data)
        a["sha256"] = hashlib.sha256(data).hexdigest()
        self.validate()
        data = b' \n'
        (self.root / a["path"]).write_bytes(data)
        a["size_bytes"] = len(data)
        a["sha256"] = hashlib.sha256(data).hexdigest()
        self.reject("SIM_INVALID_ARTIFACT_JSON")

    def test_missing_required_visible_categories_reported_not_fabricated(self):
        self.receipt["artifacts"][4]["visibility"] = "QA_ONLY"
        self.receipt["model_visible_artifact_refs"].remove("A4")
        out = self.validate()
        self.assertEqual(out["missing_input_role_count"], 1)
        self.assertFalse(out["diagnostic_input_complete"])

    def test_input_not_mutated(self):
        before = copy.deepcopy(self.receipt)
        self.validate()
        self.assertEqual(self.receipt, before)

    def test_cli_success_and_failure_are_aggregate_only(self):
        p = self.root / "receipt.json"
        p.write_text(json.dumps(self.receipt), encoding="utf-8")
        cmd = [sys.executable, str(ROOT / "scripts/audit_simulation_run_receipt.py"), "--receipt", str(p), "--artifact-root", str(self.root)]
        ok = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["sft_records_emitted"], 0)
        p.write_text('{"secret":"should-not-leak", "secret":1}', encoding="utf-8")
        bad = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(bad.returncode, 2)
        self.assertNotIn("should-not-leak", bad.stdout + bad.stderr)
        self.assertNotIn(str(self.root), bad.stdout + bad.stderr)
        self.assertEqual(json.loads(bad.stdout)["error_code"], "SIM_DUPLICATE_JSON_KEY")

    def test_existing_root_symlink_error_is_not_reclassified(self):
        link = self.root / "root-link"
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except OSError:
            self.skipTest("symlink creation not supported")
        api = self.api()
        with self.assertRaisesRegex(api.SimulationReceiptError, "^SIM_SYMLINK_FORBIDDEN$"):
            api.validate_simulation_run_receipt(self.receipt, artifact_root=link)

    def test_actual_label_cannot_hide_fixture_payload_by_renaming_ids(self):
        self.receipt["evidence_origin"] = "ACTUAL_SIMULATION_RUN"
        self.receipt["run_id"] = "ACTUAL-CLAIM-1"
        self.receipt["event_family_id"] = "FAMILY-CLAIM-1"
        self.receipt["scenario_id"] = "SCENARIO-CLAIM-1"
        for a in self.receipt["artifacts"]:
            a["run_id"] = self.receipt["run_id"]
        self.reject("SIM_SYNTHETIC_FIXTURE_MISLABELED")

    def test_detached_module_zip_runs_without_repository_checkout(self):
        package = ROOT / "scripts/package_simulation_receipt_module.py"
        self.assertTrue(package.is_file(), "standalone receipt module packager is not implemented")
        import zipfile
        archive_path = self.root / "module.zip"
        built = subprocess.run([sys.executable, str(package), "--output", str(archive_path)], capture_output=True, text=True)
        self.assertEqual(built.returncode, 0, built.stderr)
        extracted = self.root / "detached"
        with zipfile.ZipFile(archive_path) as archive:
            for name in archive.namelist():
                self.assertNotIn("design_report_0918", name)
                self.assertFalse(name.endswith(".docx"))
                self.assertFalse(name.endswith(".pyc"))
            self.assertIn("src/dgsi/__init__.py", archive.namelist())
            manifest = json.loads(archive.read("PACKAGE_MANIFEST.json"))
            for entry in manifest["files"]:
                self.assertEqual(hashlib.sha256(archive.read(entry["path"])).hexdigest(), entry["sha256"])
            archive.extractall(extracted)
        generated = self.root / "generated-fixture"
        create = subprocess.run([sys.executable, str(extracted / "scripts/create_simulation_receipt_fixture.py"), "--output", str(generated), "--case", "unknown-physics"], capture_output=True, text=True)
        self.assertEqual(create.returncode, 0, create.stderr)
        audited = subprocess.run([sys.executable, str(extracted / "scripts/audit_simulation_run_receipt.py"), "--receipt", str(generated / "receipt.json"), "--artifact-root", str(generated)], cwd=self.root, capture_output=True, text=True)
        self.assertEqual(audited.returncode, 0, audited.stderr)
        report = json.loads(audited.stdout)
        self.assertEqual(report["unknown_stage_count"], 1)
        self.assertEqual(report["decision"], "SYNTHETIC_TEST_ONLY")
        self.assertEqual(report["artifact_bytes_verified"], 8)
        self.assertEqual(report["sft_records_emitted"], 0)
        again = subprocess.run([sys.executable, str(extracted / "scripts/create_simulation_receipt_fixture.py"), "--output", str(generated)], capture_output=True, text=True)
        self.assertEqual(again.returncode, 2)

    def test_fixture_builder_records_distinct_outcomes(self):
        builder = ROOT / "scripts/create_simulation_receipt_fixture.py"
        self.assertTrue(builder.is_file(), "fixture builder is not implemented")
        for case, yes, no, unknown in [("complete", 6, 0, 0), ("unknown-physics", 5, 0, 1), ("missed-detection", 4, 1, 1), ("no-execution", 1, 3, 2)]:
            with self.subTest(case=case):
                dest = self.root / case
                created = subprocess.run([sys.executable, str(builder), "--output", str(dest), "--case", case], capture_output=True, text=True)
                self.assertEqual(created.returncode, 0, created.stderr)
                r = json.loads((dest / "receipt.json").read_text(encoding="utf-8"))
                out = self.api().validate_simulation_run_receipt(r, artifact_root=dest)
                self.assertEqual((out["reported_yes_stage_count"], out["reported_no_stage_count"], out["unknown_stage_count"]), (yes, no, unknown))


if __name__ == "__main__":
    unittest.main()
