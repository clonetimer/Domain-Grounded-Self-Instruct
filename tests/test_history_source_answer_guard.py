"""Synthetic-only regression for the current-event source-answer history side-channel."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from zipfile import ZipFile

from dgsi.history_source_answer_guard import (
    audit_history_source_boundary, HistorySourceBoundaryError,
)


class HistorySourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "synthetic.zip"
        self.task = "SYNTHETIC-TASK-001"
        self.old = "Current-case source hypothesis states material X as a cause"
        self.new = "Different hardware, do not transfer physical explanation"
        self.entry = {
            "task_id": self.task,
            "arm_A": "NO_HIT", "arm_B": "HISTORY",
        }
        self.manifest = {
            "training_authorized": False,
            "expert_review_complete": False,
            "source_rights_verified": False,
            "pairs": [self.entry],
        }
        self.redaction = {
            "task_id": self.task,
            "history_case_ref": "PRIOR-SYNTH-01",
            "field_path": "input.historical_cases[*].applicability_limitations",
            "source_field_utf8": self.old,
            "source_field_sha256": sha256(self.old.encode()).hexdigest(),
            "replacement_field_utf8": self.new,
            "forbidden_current_source_substrings": ["material X as a cause"],
        }
        self.ledger = {
            "coordinator_only": True,
            "not_for_sft": True,
            "review_state": "PENDING_INDEPENDENT_REVIEW",
            "redactions": [self.redaction],
        }
        self.record = {
            "input": {
                "historical_cases": [{
                    "case_ref": "PRIOR-SYNTH-01",
                    "applicability_limitations": [self.new],
                    "outcome_status": "REJECTED",
                }],
            },
        }
        self.write()

    def write(self):
        with ZipFile(self.path, "w") as z:
            z.writestr("coordinator_ONLY_pairing_manifest.json",
                       json.dumps(self.manifest))
            z.writestr("coordinator_ONLY_current_source_sanitization.json",
                       json.dumps(self.ledger))
            z.writestr(f"model_visible_inputs/{self.task}/arm_B.json",
                       json.dumps(self.record))

    def reject(self, code):
        with self.assertRaises(HistorySourceBoundaryError) as cm:
            audit_history_source_boundary(self.path)
        self.assertEqual(str(cm.exception), code)

    def test_valid_sanitization_remains_review_required(self):
        result = audit_history_source_boundary(self.path)
        self.assertEqual(result["audited_redactions"], 1)
        self.assertEqual(result["model_scoring"], "NOT_RUN")
        self.assertFalse(result["training_authorized"])

    def test_source_hypothesis_reintroduced_in_other_limitation(self):
        self.record["input"]["historical_cases"][0][
            "applicability_limitations"].append(self.old)
        self.write()
        self.reject("SOURCE_BOUNDARY_RESIDUAL_HINT")

    def test_replacement_does_not_match_current_history(self):
        self.record["input"]["historical_cases"][0][
            "applicability_limitations"] = ["unrelated"]
        self.write()
        self.reject("SOURCE_BOUNDARY_REPLACEMENT_MISMATCH")

    def test_wrong_history_case_ref(self):
        self.record["input"]["historical_cases"][0][
            "case_ref"] = "OTHER-PRIOR"
        self.write()
        self.reject("SOURCE_BOUNDARY_PRIOR_BINDING_INVALID")

    def test_manipulated_original_digest(self):
        self.redaction["source_field_sha256"] = "0" * 64
        self.write()
        self.reject("SOURCE_BOUNDARY_LEDGER_INVALID")

    def test_missing_review_restriction(self):
        self.ledger["not_for_sft"] = False
        self.write()
        self.reject("SOURCE_BOUNDARY_RELEASE_OR_REVIEW_GUARD")

    def test_cannot_assert_training_authorized(self):
        self.manifest["training_authorized"] = True
        self.write()
        self.reject("SOURCE_BOUNDARY_RELEASE_OR_REVIEW_GUARD")

    def test_redaction_must_remove_actual_marker(self):
        self.redaction["forbidden_current_source_substrings"] = [
            "never was here",
        ]
        self.write()
        self.reject("SOURCE_BOUNDARY_NOT_AN_ACTUAL_REDACTION")

    def test_history_arm_swap_detected(self):
        self.entry["arm_A"] = "HISTORY"
        self.entry["arm_B"] = "NO_HIT"
        self.write()
        self.reject("SOURCE_BOUNDARY_INVALID_MEMBER")


if __name__ == "__main__":
    unittest.main()
