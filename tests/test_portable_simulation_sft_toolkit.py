from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
TOOLKIT = ROOT / "skills" / "dgsi-simulation-to-sft"


class PortableSimulationSftToolkitTests(unittest.TestCase):
    def test_required_portable_files_exist(self):
        required = [
            "SKILL.md",
            "README.md",
            "VERSION",
            "TOOLKIT_MANIFEST.json",
            "references/WORKFLOW.md",
            "references/SOURCE_INGESTION.md",
            "references/DOCUMENT_INGESTION_ADAPTERS.md",
            "schemas/document_ingestion.schema.json",
            "references/SIMULATION_TRUTH_SEPARATION.md",
            "references/GENERATION_TASKS.md",
            "references/QUALITY_AUDIT.md",
            "references/AI_HANDOFF_PROMPTS.md",
            "references/CROSS_AI_EVALUATION.md",
            "references/SIMULATION_RUN_RECEIPT.md",
            "schemas/design_derived_batch.schema.json",
            "schemas/simulation_run_receipt.schema.json",
            "schemas/cross_ai_evaluation.schema.json",
            "templates/CROSS_AI_EVALUATION_TEMPLATE.json",
            "templates/EPISODE_INTAKE_TEMPLATE.md",
            "templates/BATCH_MANIFEST_TEMPLATE.json",
            "templates/HUMAN_REVIEW_QUEUE.csv",
        ]
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((TOOLKIT / relative).is_file())

    def test_manifest_fails_closed(self):
        manifest = json.loads((TOOLKIT / "TOOLKIT_MANIFEST.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["status"], "DRAFT_CANDIDATE_GENERATION_ONLY")
        self.assertFalse(manifest["training_authorized"])
        self.assertFalse(manifest["gold_authorized"])
        self.assertFalse(manifest["sft_export_authorized"])
        self.assertIn("SIMULATION_CASE_CANDIDATE", manifest["candidate_tracks"])

    def test_cross_ai_evaluation_schema_and_template_are_valid(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((TOOLKIT / "schemas" / "cross_ai_evaluation.schema.json").read_text(encoding="utf-8"))
        template = json.loads((TOOLKIT / "templates" / "CROSS_AI_EVALUATION_TEMPLATE.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        errors = list(Draft202012Validator(schema).iter_errors(template))
        self.assertEqual([], [error.message for error in errors])
        self.assertFalse(template["training_authorized"])

    def test_cross_ai_evaluation_status_gates_are_progressive(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((TOOLKIT / "schemas" / "cross_ai_evaluation.schema.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        template = json.loads((TOOLKIT / "templates" / "CROSS_AI_EVALUATION_TEMPLATE.json").read_text(encoding="utf-8"))
        self.assertEqual([], list(validator.iter_errors(template)))  # protocol can be prepared before runs

        invalid_runs = copy.deepcopy(template)
        invalid_runs["status"] = "RUNS_RECORDED"
        self.assertTrue(list(validator.iter_errors(invalid_runs)))  # run stage requires >=2 runs

        run_base = {
            "provider": "provider-placeholder", "model_id": "model-placeholder",
            "model_version": None, "run_at": "2026-11-16T00:00:00Z",
            "settings_fingerprint": "1" * 64, "raw_output_sha256": "2" * 64,
            "candidate_count": 6, "status": "COMPLETE",
        }
        valid_runs = copy.deepcopy(template)
        valid_runs["runs"] = [
            dict(run_base, blind_alias="AI-A01"),
            dict(run_base, blind_alias="AI-B02", raw_output_sha256="3" * 64),
        ]
        valid_runs["status"] = "RUNS_RECORDED"
        self.assertEqual([], list(validator.iter_errors(valid_runs)))

        pending = copy.deepcopy(valid_runs)
        pending["status"] = "ADJUDICATION_PENDING"
        self.assertTrue(list(validator.iter_errors(pending)))  # no adjudication scores yet

        pending["adjudication"]["dimensions"] = [
            {"blind_alias": "AI-A01", "dimension": "fact_fidelity", "score": 2, "evidence_note": "Source locator verified."}
        ]
        self.assertEqual([], list(validator.iter_errors(pending)))

        adjudicated = copy.deepcopy(pending)
        adjudicated["status"] = "ADJUDICATED"
        adjudicated["adjudication"]["reference_basis"] = "SOURCE_GROUNDED_HUMAN_ADJUDICATION"
        self.assertEqual([], list(validator.iter_errors(adjudicated)))

        invalid_adjudicated = copy.deepcopy(adjudicated)
        invalid_adjudicated["adjudication"]["reference_basis"] = "NOT_ADJUDICATED"
        self.assertTrue(list(validator.iter_errors(invalid_adjudicated)))

    def test_batch_template_is_valid_json_and_excludes_truth_from_generator(self):
        template = json.loads(
            (TOOLKIT / "templates" / "BATCH_MANIFEST_TEMPLATE.json").read_text(encoding="utf-8")
        )
        self.assertFalse(template["provider_processing_authorized"])
        self.assertFalse(template["truth_separation"]["included_in_generator_upload"])
        self.assertFalse(template["output_policy"]["training_authorized"])

    def test_skill_contains_core_truth_and_evidence_boundaries(self):
        skill = (TOOLKIT / "SKILL.md").read_text(encoding="utf-8")
        for required in (
            "INGEST",
            "AUDIT",
            "Fault injection",
            "analysis_cutoff",
            "fault-source component",
            "Raw telemetry remains with upstream ML",
            "Human review is mandatory",
        ):
            with self.subTest(required=required):
                self.assertIn(required, skill)

    def test_full_toolkit_zip_contains_run_receipt_module_and_is_not_user_data(self):
        script = ROOT / "scripts" / "package_dgsi_simulation_to_sft.py"
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "full-toolkit.zip"
            result = subprocess.run(
                [sys.executable, str(script), "--output", str(output)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with zipfile.ZipFile(output) as archive:
                names = set(archive.namelist())
                required = {
                    "skills/dgsi-simulation-to-sft/SKILL.md",
                    "skills/dgsi-simulation-to-sft/schemas/simulation_run_receipt.schema.json",
                    "skills/dgsi-simulation-to-sft/references/SIMULATION_RUN_RECEIPT.md",
                    "scripts/audit_simulation_run_receipt.py",
                    "scripts/create_simulation_receipt_fixture.py",
                    "scripts/package_simulation_receipt_module.py",
                    "tests/test_simulation_run_receipt.py",
                    "scripts/audit_cross_ai_evaluation.py",
                    "tests/test_cross_ai_evaluation.py",
                    "src/dgsi/cross_ai_evaluation.py",
                    "scripts/ingest_dgsi_document.py",
                    "tests/test_document_ingestion.py",
                    "src/dgsi/document_ingestion.py",
                }
                self.assertTrue(required.issubset(names), required - names)
                self.assertFalse(any("design_report_0918_pilot" in name for name in names))
                self.assertFalse(any("target_private" in name or "hidden_truth" in name for name in names))
                manifest = json.loads(archive.read("PACKAGE_SHA256_MANIFEST.json"))
                self.assertFalse(manifest["training_authorized"])
                self.assertFalse(manifest["gold_authorized"])
                self.assertFalse(manifest["sft_export_authorized"])
                for item in manifest["files"]:
                    self.assertEqual(
                        hashlib.sha256(archive.read(item["path"])).hexdigest(),
                        item["sha256"],
                    )
        packager = (ROOT / "scripts" / "package_dgsi_simulation_to_sft.py").read_text(encoding="utf-8")
        self.assertIn("scripts/package_simulation_receipt_module.py", packager)
        self.assertIn("tests/test_simulation_run_receipt.py", packager)


if __name__ == "__main__":
    unittest.main()
