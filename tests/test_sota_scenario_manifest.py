"""Synthetic-only checks of offline SOTA canonical-input digest attestation."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dgsi.sota_construction_scorecard import ARMS, ScorecardError
from dgsi.sota_scenario_manifest import (
    MANIFEST_SCHEMA, audit_local_sota_scenarios, canonical_scenario_sha256,
)


def scenario(group="G1"):
    return {
        "comparison_unit_id": f"SLOT-{group}",
        "source_group": group,
        "event_family": group,
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "requested_task_type": "diagnostic_synthesis",
        "shared_input": {
            "upstream_ml_result": {"finding": "SYNTHETIC_TEST_ONLY"},
            "diagnostic_logs": [],
            "spacecraft_mission_context": {"configuration": "SYNTHETIC_TEST_ONLY"},
            "analysis_cutoff": "2026-11-18T00:00:00Z",
            "historical_context": [],
            "provenance": {"synthetic": True, "source_refs": ["SYNTHETIC_TEST_ONLY"]},
        },
    }


def trial(arm, entry):
    return {
        "trial_id": arm + "-" + entry["comparison_unit_id"],
        "source_group": entry["source_group"],
        "event_family": entry["event_family"],
        "comparison_unit_id": entry["comparison_unit_id"],
        "requested_task_type": entry["requested_task_type"],
        "canonical_scenario_sha256": canonical_scenario_sha256(entry),
        "arm": arm, "track": entry["track"],
        "attempts": 1, "accepted_candidates": 0,
        "generation_tokens": 0, "token_budget": 1000,
        "critical_failures": [], "review_status": "PENDING",
        "reviewer_tokens": [], "scores": {},
    }


def documents(entry=None):
    entry = entry if entry is not None else scenario()
    return (
        {"schema_version": "dgsi-sota-construction-scorecard.v1",
         "purpose": "CONSTRUCTION_ONLY", "trials": [trial(a, entry) for a in ARMS]},
        {"schema_version": MANIFEST_SCHEMA, "scenarios": [entry]},
    )


class ScenarioManifestTests(unittest.TestCase):
    def reject(self, code, trials, manifest):
        with self.assertRaisesRegex(ScorecardError, "^" + code + "$"):
            audit_local_sota_scenarios(trials, manifest)

    def test_matched_manifest_verifies_all_five_arms_without_admission(self):
        trials, manifest = documents()
        result = audit_local_sota_scenarios(trials, manifest)
        self.assertTrue(result["manifest_digests_match_local_inputs"])
        self.assertEqual(result["comparison_status"], "MATCHED_UNREVIEWED")
        self.assertEqual(result["trials_checked"], 5)
        self.assertFalse(result["source_rights_verified"])
        self.assertFalse(result["historical_as_of_verified"])
        self.assertFalse(result["training_authorized"])

    def test_changed_ml_result_cannot_reuse_old_fingerprint(self):
        trials, manifest = documents()
        manifest["scenarios"][0]["shared_input"]["upstream_ml_result"]["finding"] = "CHANGED_SYNTHETIC_INPUT"
        self.reject("SOTA_MANIFEST_DIGEST_MISMATCH", trials, manifest)

    def test_changed_history_or_cutoff_cannot_reuse_old_fingerprint(self):
        for field, value in (
            ("historical_context", [{"summary": "CHANGED_SYNTHETIC_HISTORY"}]),
            ("analysis_cutoff", "2026-11-19T00:00:00Z"),
        ):
            trials, manifest = documents()
            manifest["scenarios"][0]["shared_input"][field] = value
            self.reject("SOTA_MANIFEST_DIGEST_MISMATCH", trials, manifest)

    def test_meta_drift_cannot_reuse_unit(self):
        trials, manifest = documents()
        manifest["scenarios"][0]["requested_task_type"] = "evidence_sufficiency"
        self.reject("SOTA_MANIFEST_METADATA_MISMATCH", trials, manifest)

    def test_manifest_missing_or_duplicate_units_are_blocked(self):
        trials, manifest = documents()
        manifest["scenarios"] = []
        self.reject("SOTA_MANIFEST_UNIT_NOT_FOUND", trials, manifest)
        trials, manifest = documents()
        manifest["scenarios"].append(scenario())
        self.reject("SOTA_MANIFEST_DUPLICATE_UNIT", trials, manifest)

    def test_unrequested_manifest_unit_is_not_silently_accepted(self):
        trials, manifest = documents()
        manifest["scenarios"].append(scenario("EXTRA"))
        self.reject("SOTA_MANIFEST_UNUSED_UNIT", trials, manifest)

    def test_missing_as_of_or_raw_telemetry_is_blocked(self):
        entry = scenario()
        del entry["shared_input"]["analysis_cutoff"]
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_INPUT_FIELDS$"):
            canonical_scenario_sha256(entry)
        entry = scenario()
        entry["shared_input"]["analysis_cutoff"] = "2026-11-18T00:00:00"
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_CUTOFF_INVALID$"):
            canonical_scenario_sha256(entry)
        entry = scenario()
        entry["shared_input"]["raw_telemetry"] = [1, 2, 3]
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_FORBIDDEN_INPUT$"):
            canonical_scenario_sha256(entry)

    def test_fabricated_real_or_unbound_synthetic_provenance_is_rejected(self):
        entry = scenario()
        entry["shared_input"]["provenance"] = {"synthetic": False}
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_SYNTHETIC_PROVENANCE$"):
            canonical_scenario_sha256(entry)
        entry = scenario()
        entry["shared_input"]["provenance"]["source_refs"] = []
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_SYNTHETIC_PROVENANCE$"):
            canonical_scenario_sha256(entry)

    def test_noncanonical_float_nan_is_blocked(self):
        entry = scenario()
        entry["shared_input"]["upstream_ml_result"]["numeric"] = float("nan")
        with self.assertRaisesRegex(ScorecardError, "^SOTA_MANIFEST_JSON_INVALID$"):
            canonical_scenario_sha256(entry)

    def test_no_scenario_content_hash_or_ids_disclosed(self):
        trials, manifest = documents()
        result = audit_local_sota_scenarios(trials, manifest)
        text = json.dumps(result)
        self.assertNotIn("SYNTHETIC_TEST_ONLY", text)
        self.assertNotIn("SLOT-G1", text)
        self.assertNotIn(trials["trials"][0]["canonical_scenario_sha256"], text)


if __name__ == "__main__":
    unittest.main()
