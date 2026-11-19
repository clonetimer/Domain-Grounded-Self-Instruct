"""Synthetic-only regression tests; no unpublished review payloads or model input."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from dgsi import history_pair_science_audit as audit


class HistoryPairScienceAuditTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.archive = Path(work.name) / "dev.zip"
        self.task = "SYNTHETIC-EXAMPLE-001"
        self.prior = {
            "case_ref": "PRIOR-001", "source_case_refs": ["OPEN-PUBLIC-001"],
            "available_at": "2024-01-01T00:00:00Z", "outcome_status": "REJECTED",
            "hardware_compatibility": "UNKNOWN", "event_family_id": "PRIOR-FAMILY",
            "applicability_limitations": ["different equipment"],
        }
        inp = {
            "analysis_cutoff": "2025-01-01T00:00:00Z",
            "raw_telemetry_included": False, "machine_diagnosis": {"status": "FAULT_CANDIDATE"},
            "diagnostic_logs": [], "spacecraft_context": {}, "operational_context": {},
            "knowledge_evidence": [{"evidence_id": "CURRENT-001"}], "historical_cases": [],
        }
        base = {
            "analysis_cutoff": inp["analysis_cutoff"], "case_id": "CASE-DEV-001",
            "data_classification": "LITERATURE_DERIVED_SYNTHETIC_NOT_REAL_RECORD",
            "input": inp, "instruction": "Interpret an explicitly synthetic candidate",
            "task_type": "diagnostic_synthesis",
        }
        yes = copy.deepcopy(base)
        yes["input"]["historical_cases"] = [self.prior]
        self.members = {
            f"model_visible_inputs/{self.task}/arm_A.json": yes,
            f"model_visible_inputs/{self.task}/arm_B.json": copy.deepcopy(base),
        }
        self.entry = {
            "task_id": self.task, "case_id": base["case_id"],
            "task_type": base["task_type"], "event_family": "CURRENT-FAMILY",
            "analysis_cutoff": inp["analysis_cutoff"],
            "arm_A": "HISTORY", "arm_B": "NO_HIT",
            "history_refs": ["PRIOR-001"], "history_outcome_statuses": ["REJECTED"],
            "history_hardware_compatibilities": ["UNKNOWN"],
            "history_available_at": [self.prior["available_at"]],
            "history_only_knowledge_evidence_removed_from_both_arms": [],
        }
        self.manifest = {
            "purpose": "DEV_ONLY_HISTORY_SOURCE_ISOLATED_NEGATIVE_TRANSFER_PAIRS_NOT_TRAINING",
            "training_authorized": False, "gold_eligible": False,
            "official_split_assigned": False, "source_rights_verified": False,
            "expert_review_complete": False, "positive_history_evaluation": "NOT_EVALUABLE",
            "experiment_execution": "NOT_RUN", "pairs": [self.entry],
        }
        self.write()

    def write(self):
        yes, no = list(self.members.values())
        self.entry["core_input_sha256"] = audit._digest({
            k: v for k, v in yes["input"].items() if k != "historical_cases"
        })
        self.entry["with_history_input_sha256"] = audit._digest(yes)
        self.entry["without_history_input_sha256"] = audit._digest(no)
        with ZipFile(self.archive, "w") as z:
            z.writestr("coordinator_ONLY_pairing_manifest.json", json.dumps(self.manifest))
            for name, obj in self.members.items():
                z.writestr(name, json.dumps(obj))

    def reject(self, code):
        with self.assertRaises(audit.HistoryPairAuditError) as cm:
            audit.audit_pair_zip(self.archive)
        self.assertEqual(str(cm.exception), code)

    def test_metadata_only_success(self):
        result = audit.audit_pair_zip(self.archive)
        self.assertEqual(result["pair_count"], 1)
        self.assertEqual(result["hits_without_verified_at"], 1)
        self.assertEqual(result["positive_history_transfer"], "NOT_EVALUABLE")
        self.assertFalse(result["training_authorized"])

    def test_shared_prior_evidence_leak_even_when_hashes_match(self):
        for obj in self.members.values():
            obj["input"]["knowledge_evidence"].append({"evidence_id": "HIST-LEAK"})
        self.write()
        self.reject("PAIR_HISTORY_SOURCE_LEAK")

    def test_uncontrolled_current_ml_change(self):
        list(self.members.values())[1]["input"]["machine_diagnosis"]["status"] = "CONFIRMED"
        self.write()
        self.reject("PAIR_UNCONTROLLED_CORE_CHANGE")

    def test_future_history_blocked(self):
        self.prior["available_at"] = "2025-02-01T00:00:00Z"
        self.entry["history_available_at"] = [self.prior["available_at"]]
        self.write()
        self.reject("PAIR_FUTURE_HISTORY_LEAK")

    def test_false_time_ledger_blocked(self):
        self.entry["history_available_at"] = ["2020-01-01T00:00:00Z"]
        self.write()
        self.reject("PAIR_HISTORY_TIME_LEDGER_MISMATCH")

    def test_future_verification_blocked(self):
        self.prior["verified_at"] = "2025-02-01T00:00:00Z"
        self.write()
        self.reject("PAIR_FUTURE_HISTORY_LEAK")

    def test_curator_content_blocked(self):
        list(self.members.values())[0]["input"]["internal_review"] = {"hidden": "answer"}
        self.write()
        self.reject("PAIR_REVIEW_OR_TARGET_LEAK")

    def test_training_authorization_cannot_be_set(self):
        self.manifest["training_authorized"] = True
        self.write()
        self.reject("PAIR_RELEASE_GUARD_INVALID")

    def test_metadata_status_falsification(self):
        self.entry["history_outcome_statuses"] = ["CONFIRMED"]
        self.write()
        self.reject("PAIR_HISTORY_METADATA_MISMATCH")

    def test_same_event_family_cannot_be_history(self):
        self.prior["event_family_id"] = "CURRENT-FAMILY"
        self.write()
        self.reject("PAIR_HISTORY_PROVENANCE_INVALID")

    def test_confirmed_compatible_prior_not_negative_cohort(self):
        self.prior["outcome_status"] = "CONFIRMED"
        self.prior["hardware_compatibility"] = "COMPATIBLE"
        self.entry["history_outcome_statuses"] = ["CONFIRMED"]
        self.entry["history_hardware_compatibilities"] = ["COMPATIBLE"]
        self.write()
        self.reject("PAIR_POSITIVE_TRANSFER_NOT_IN_NEGATIVE_COHORT")

    def test_manifest_digest_tampering(self):
        self.entry["core_input_sha256"] = "0" * 64
        with ZipFile(self.archive, "w") as z:
            z.writestr("coordinator_ONLY_pairing_manifest.json", json.dumps(self.manifest))
            for name, obj in self.members.items():
                z.writestr(name, json.dumps(obj))
        self.reject("PAIR_UNCONTROLLED_CORE_CHANGE")


if __name__ == "__main__":
    unittest.main()
