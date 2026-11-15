import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RealCaseHandoffContractTests(unittest.TestCase):
    def test_handoff_manifest_schema_is_strict_and_pseudonymous(self):
        schema = json.loads((ROOT / "resources/real_case_handoff.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertFalse(schema["additionalProperties"])
        self.assertIn("case_id", schema["required"])
        self.assertIn("event_family_id", schema["required"])
        self.assertIn("analysis_cutoff", schema["required"])
        self.assertIn("permission_status", schema["required"])
        self.assertIn("redaction", schema["required"])

    def test_review_handoff_keeps_target_separate_from_input(self):
        text = (ROOT / "docs/REAL_DIAGNOSTIC_MATERIAL_REVIEW_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("target_private/", text)
        self.assertIn("analysis_cutoff", text)
        self.assertIn("Raw telemetry arrays", text)
        self.assertIn("AUTHORIZED_FOR_TRAINING", (ROOT / "resources/real_case_handoff.schema.json").read_text(encoding="utf-8"))

    def test_handoff_does_not_auto_grant_gold(self):
        text = (ROOT / "docs/REAL_DIAGNOSTIC_MATERIAL_REVIEW_HANDOFF.md").read_text(encoding="utf-8")
        self.assertIn("None of these statuses automatically means Gold", text)
        self.assertIn("SYNTHETIC_TEST_ONLY", text)


if __name__ == "__main__":
    unittest.main()
