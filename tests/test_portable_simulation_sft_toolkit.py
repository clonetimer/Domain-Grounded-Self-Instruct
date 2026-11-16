from __future__ import annotations

import json
from pathlib import Path
import unittest


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
            "references/SIMULATION_TRUTH_SEPARATION.md",
            "references/GENERATION_TASKS.md",
            "references/QUALITY_AUDIT.md",
            "references/AI_HANDOFF_PROMPTS.md",
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

    def test_packaging_script_is_present(self):
        self.assertTrue((ROOT / "scripts" / "package_dgsi_simulation_to_sft.py").is_file())


if __name__ == "__main__":
    unittest.main()
