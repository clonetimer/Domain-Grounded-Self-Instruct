import json
import tempfile
import unittest
from pathlib import Path

from scripts.inventory_diagnostic_case_assets import build_inventory


class DiagnosticAssetInventoryTests(unittest.TestCase):
    def write_case(self, root: Path, *, synthetic=False, truth=False, csv_log=False, approved=False):
        case = root / "case-001"
        case.mkdir(parents=True)
        diagnosis = {
            "case_id": "SYNTH-001" if synthetic else "CASE-001",
            "candidate_fault_id": "ADCS_RW_FRICTION_INCREASE",
            "diagnostic_summary": "redacted fixture summary",
            "review_status": "UNVERIFIED",
        }
        if truth:
            diagnosis["truth_used"] = True
        (case / "diagnosis_result.json").write_text(json.dumps(diagnosis), encoding="utf-8")
        if csv_log:
            (case / "operations.csv").write_text(
                "timestamp,signal,value,unit\n2026-01-01T00:00:00Z,battery_voltage,25.0,V\n",
                encoding="utf-8",
            )
        else:
            (case / "operations.log").write_text(
                "2026-01-01T00:00:00Z WARN ADCS review requested\n",
                encoding="utf-8",
            )
        (case / "reference.md").write_text("# redacted reference", encoding="utf-8")
        (case / "spacecraft_context.json").write_text(
            json.dumps({"spacecraft_id": "redacted", "configuration": {}}),
            encoding="utf-8",
        )
        if approved:
            (case / "expert_review.json").write_text(
                json.dumps({"status": "APPROVED", "reviewer_id": "reviewer-01", "reviewed_at": "2026-01-02T00:00:00Z"}),
                encoding="utf-8",
            )
        return case

    def test_inventory_is_redacted_and_does_not_export_gold(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_case(root, synthetic=True)
            report = build_inventory(root)
            self.assertEqual(report["case_count"], 1)
            self.assertFalse(report["payload_exported"])
            self.assertFalse(report["gold_approval_granted"])
            self.assertEqual(report["cases"][0]["decision"], "SYNTHETIC_FIXTURE_ONLY")
            self.assertNotIn("diagnostic_summary", json.dumps(report))

    def test_hidden_truth_blocks_case(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_case(root, truth=True)
            report = build_inventory(root)
            self.assertEqual(report["cases"][0]["decision"], "BLOCKED_HIDDEN_TRUTH_OR_LABELS")

    def test_csv_with_signal_value_is_flagged_for_telemetry_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_case(root, csv_log=True)
            report = build_inventory(root)
            self.assertTrue(report["cases"][0]["potential_raw_telemetry_csv"])

    def test_complete_approved_packet_only_reaches_manual_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_case(root, approved=True)
            report = build_inventory(root)
            self.assertEqual(report["cases"][0]["decision"], "READY_FOR_MANUAL_CONTENT_REVIEW")
            self.assertFalse(report["cases"][0]["gold_eligible"])


if __name__ == "__main__":
    unittest.main()
