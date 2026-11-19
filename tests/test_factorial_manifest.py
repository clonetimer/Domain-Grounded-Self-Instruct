import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "evaluation" / "refinement_20261120" / "validate_factorial_manifest.py"
SPEC = importlib.util.spec_from_file_location("dgsi_factorial_manifest", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixture():
    cases = [
        {"case_id": "opaque-01", "source_cluster_id": "cluster-new-A",
         "input_sha256": "a" * 64, "target_schema_sha256": "b" * 64},
        {"case_id": "opaque-02", "source_cluster_id": "cluster-new-B",
         "input_sha256": "c" * 64, "target_schema_sha256": "b" * 64},
    ]
    source_evidence_records = [
        {
            "source_cluster_id": cluster_id,
            "primary_source_url": f"https://example.invalid/{cluster_id}",
            "source_document_id": f"TEST-{cluster_id}",
            "source_document_sha256": "e" * 64,
            "source_locators": ["test fixture locator: page 1"],
            "rights_basis": "test-only fixture assertion; not a real rights determination",
            "rights_scope": "test-only derivative use scope",
            "rights_review_ref": "test-fixture-rights-review",
            "exposure_audit_scope": [
                "repository_and_pr_history",
                "prior_development_bundles",
                "connected_retrieval_and_prior_conversations",
            ],
            "exposure_audit_ref": "test-fixture-exposure-audit",
            "independence_rationale": "Synthetic unit-test fixture only; no real source independence is asserted.",
            "review_status": "PASS",
            "reviewer_token": "test-curator-token",
            "reviewed_at": "2026-11-20",
        }
        for cluster_id in ("cluster-new-A", "cluster-new-B")
    ]
    policy = "d" * 64
    arms = []
    for arm_id, evolution, selection in [
        ("A", False, False), ("B", False, True),
        ("C", True, False), ("D", True, True),
    ]:
        arms.append({
            "arm_id": arm_id, "evolution_enabled": evolution,
            "selection_enabled": selection, "candidate_count": 3 if selection else 1,
            "policy_sha256": policy,
            "cases": [{"case_id": row["case_id"],
                       "input_sha256": row["input_sha256"],
                       "target_schema_sha256": row["target_schema_sha256"]} for row in cases],
        })
    return {
        "schema_version": "dgsi-2x2-run-manifest.v1",
        "status": "PRE_GENERATION_VALIDATION_ONLY",
        "model_calls_authorized": False, "training_authorized": False,
        "retry_budget": 0, "regeneration_budget": 0,
        "policy_sha256": policy,
        "excluded_source_cluster_ids": ["prior-dev-cluster", "DOC-CLUSTER-03", "DOC-CLUSTER-06"],
        "holdout_gate": {
            "rights_verified": True, "development_exposure_excluded": True,
            "source_cluster_independence_verified": True,
            "reference_answers_escrowed": True, "case_manifest_frozen": True,
        },
        "cases": cases, "arms": arms,
        "source_evidence_records": source_evidence_records,
    }


class FactorialManifestTests(unittest.TestCase):
    def test_valid_manifest_is_comparable_but_not_executable(self):
        report = MODULE.validate_manifest(fixture())
        self.assertTrue(report["valid"])
        self.assertEqual(report["arm_count"], 4)
        self.assertEqual(report["case_count"], 2)
        self.assertFalse(report["model_calls_authorized"])
        self.assertFalse(report["training_authorized"])

    def test_source_evidence_records_are_required_and_cluster_bound(self):
        data = fixture()
        data.pop("source_evidence_records")
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_EVIDENCE_RECORDS_MISSING"):
            MODULE.validate_manifest(data)
        data = fixture()
        data["source_evidence_records"][1]["source_cluster_id"] = "unbound-cluster"
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_EVIDENCE_CLUSTER_SET_MISMATCH"):
            MODULE.validate_manifest(data)

    def test_source_evidence_requires_rights_and_full_exposure_scope(self):
        data = fixture()
        data["source_evidence_records"][0]["rights_review_ref"] = ""
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_REVIEW_EVIDENCE_INCOMPLETE"):
            MODULE.validate_manifest(data)
        data = fixture()
        data["source_evidence_records"][1]["exposure_audit_scope"].remove("connected_retrieval_and_prior_conversations")
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_EXPOSURE_AUDIT_SCOPE_INCOMPLETE"):
            MODULE.validate_manifest(data)

    def test_source_evidence_rejects_invalid_url_hash_or_review_status(self):
        data = fixture()
        data["source_evidence_records"][0]["primary_source_url"] = "http://example.invalid/source"
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_PRIMARY_URL_INVALID"):
            MODULE.validate_manifest(data)
        data = fixture()
        data["source_evidence_records"][0]["source_document_sha256"] = "bad"
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_DOCUMENT_HASH_INVALID"):
            MODULE.validate_manifest(data)
        data = fixture()
        data["source_evidence_records"][0]["review_status"] = "PENDING"
        with self.assertRaisesRegex(MODULE.ManifestError, "SOURCE_REVIEW_NOT_PASSED"):
            MODULE.validate_manifest(data)

    def test_arm_case_mismatch_is_blocked(self):
        data = fixture()
        data["arms"][3]["cases"][0]["input_sha256"] = "e" * 64
        with self.assertRaisesRegex(MODULE.ManifestError, "ARM_INPUT_OR_SCHEMA_MISMATCH"):
            MODULE.validate_manifest(data)

    def test_arm_missing_case_is_blocked(self):
        data = fixture()
        data["arms"][1]["cases"].pop()
        with self.assertRaisesRegex(MODULE.ManifestError, "ARM_HOLDOUT_CASE_SET_MISMATCH"):
            MODULE.validate_manifest(data)

    def test_factorial_factor_or_candidate_count_drift_is_blocked(self):
        data = fixture()
        data["arms"][2]["selection_enabled"] = True
        with self.assertRaisesRegex(MODULE.ManifestError, "FACTORIAL_ARM_FACTOR_MISMATCH"):
            MODULE.validate_manifest(data)
        data = fixture()
        data["arms"][1]["candidate_count"] = 1
        with self.assertRaisesRegex(MODULE.ManifestError, "CANDIDATE_COUNT_MISMATCH"):
            MODULE.validate_manifest(data)

    def test_incomplete_rights_or_exposure_gate_is_blocked(self):
        for key in ("rights_verified", "development_exposure_excluded",
                    "source_cluster_independence_verified", "reference_answers_escrowed",
                    "case_manifest_frozen"):
            data = fixture()
            data["holdout_gate"][key] = False
            with self.subTest(gate=key), self.assertRaisesRegex(MODULE.ManifestError, "HOLDOUT_GATE_NOT_PASSED"):
                MODULE.validate_manifest(data)

    def test_reference_or_score_side_channel_is_blocked(self):
        data = fixture()
        data["arms"][0]["cases"][0]["reference_answer"] = "hidden"
        with self.assertRaisesRegex(MODULE.ManifestError, "REFERENCE_OR_SCORE_LEAKAGE"):
            MODULE.validate_manifest(data)

    def test_previous_development_source_cluster_cannot_be_smuggled_in(self):
        data = fixture()
        data["cases"][0]["source_cluster_id"] = "DOC-CLUSTER-03"
        with self.assertRaisesRegex(MODULE.ManifestError, "PREVIOUSLY_EXPOSED_SOURCE_CLUSTER"):
            MODULE.validate_manifest(data)

    def test_single_source_cluster_is_not_enough(self):
        data = fixture()
        data["cases"][1]["source_cluster_id"] = data["cases"][0]["source_cluster_id"]
        for arm in data["arms"]:
            arm["cases"][1]["case_id"] = data["cases"][1]["case_id"]
        with self.assertRaisesRegex(MODULE.ManifestError, "INSUFFICIENT_INDEPENDENT_SOURCE_CLUSTERS"):
            MODULE.validate_manifest(data)


if __name__ == "__main__":
    unittest.main()
