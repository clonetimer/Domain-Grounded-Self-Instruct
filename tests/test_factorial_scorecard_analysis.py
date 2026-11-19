import importlib.util
import unittest
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "evaluation" / "refinement_20261120" / "analyze_factorial_scorecard.py"
SPEC = importlib.util.spec_from_file_location("dgsi_factorial_analysis", PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

DIMS = MODULE.DIMENSIONS
ARMS = MODULE.ARMS


def manifest_fixture():
    return [
        {"case_id": "case-01", "source_cluster_id": "cluster-a",
         "input_sha256": "a" * 64, "target_schema_sha256": "b" * 64},
        {"case_id": "case-02", "source_cluster_id": "cluster-b",
         "input_sha256": "a" * 64, "target_schema_sha256": "b" * 64},
    ]


def binding_kwargs():
    manifest_bytes = json.dumps({"cases": manifest_fixture()}, sort_keys=True).encode("utf-8")
    rubric_bytes = b"frozen-rubric-v1"
    return {
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "rubric_sha256": hashlib.sha256(rubric_bytes).hexdigest(),
        "manifest_cases": manifest_fixture(),
    }


def fixture():
    cases = []
    reviewer_tokens = ["reviewer-token-a", "reviewer-token-b"]
    factors = [("case-01", "cluster-a"), ("case-02", "cluster-b")]
    for case_id, cluster in factors:
        reviews = []
        for arm_id, (evolution, selection) in ARMS.items():
            base = {"A": 10, "B": 12, "C": 11, "D": 13}[arm_id]
            for reviewer_index, token in enumerate(reviewer_tokens):
                score = base + reviewer_index
                dimensions = {dim: 1 for dim in DIMS}
                for i, dim in enumerate(DIMS):
                    dimensions[dim] = 2 if i < score - 10 else 1
                reviews.append({
                    "arm_id": arm_id, "reviewer_token": token,
                    "output_valid": True, "dimension_scores": dimensions,
                    "accepted": score >= 11, "critical_failure_codes": [],
                })
        cases.append({
            "case_id": case_id, "source_cluster_id": cluster,
            "input_sha256": "a" * 64, "target_schema_sha256": "b" * 64,
            "reviews": reviews,
        })
    return {
        "schema_version": "dgsi-factorial-review-scorecard.v1",
        "classification": "BLINDED_REVIEW_SCORECARD_NOT_FOR_SFT",
        "manifest_sha256": binding_kwargs()["manifest_sha256"],
        "rubric_sha256": binding_kwargs()["rubric_sha256"],
        "cases": cases,
    }


class FactorialScorecardAnalysisTests(unittest.TestCase):
    def test_paired_factorial_effects_are_calculated_descriptively(self):
        report = MODULE.analyze_scorecard(fixture(), **binding_kwargs())
        self.assertEqual(report["status"], "ANALYZED")
        self.assertEqual(report["complete_four_arm_paired_case_count"], 2)
        self.assertEqual(report["source_cluster_count"], 2)
        self.assertIsNotNone(report["factorial_contrasts_on_complete_paired_cases_only"]["evolution_main_effect"])
        self.assertIsNotNone(report["factorial_contrasts_equal_weight_per_source_cluster"]["evolution_main_effect"])
        self.assertEqual(
            set(report["factorial_contrasts_equal_weight_per_source_cluster"]),
            {"evolution_main_effect", "selection_main_effect", "interaction"},
        )
        self.assertFalse(report["training_authorized"])
        self.assertEqual(set(report["per_dimension_factorial_analysis"]), set(DIMS))
        self.assertIn("evolution_main_effect", report["per_dimension_factorial_analysis"]["source_fidelity"])
        self.assertIn("reviewer_dimension_disagreement_count", report)
        self.assertIn("reviewer_acceptance_disagreement_count", report)

    def test_invalid_outputs_are_counted_not_imputed(self):
        data = fixture()
        review = data["cases"][0]["reviews"][0]
        review["output_valid"] = False
        review["dimension_scores"] = None
        review["accepted"] = False
        review["critical_failure_codes"] = ["INVALID_FORMAT"]
        report = MODULE.analyze_scorecard(data, **binding_kwargs())
        self.assertEqual(report["arm_summary"]["A"]["invalid_output_count_of_reviews"], 1)
        self.assertEqual(report["complete_four_arm_paired_case_count"], 1)
        self.assertEqual(report["case_details"]["case-01"]["A"]["case_mean_score"], None)
        self.assertEqual(report["arm_summary"]["A"]["critical_failure_code_count"], 1)
        self.assertEqual(report["per_dimension_factorial_analysis"]["source_fidelity"]["complete_four_arm_paired_case_count"], 1)

    def test_invalid_output_cannot_be_marked_accepted(self):
        data = fixture()
        review = data["cases"][0]["reviews"][0]
        review["output_valid"] = False
        review["dimension_scores"] = None
        review["accepted"] = True
        with self.assertRaisesRegex(MODULE.ScorecardError, "INVALID_OUTPUT_CANNOT_BE_ACCEPTED"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_no_complete_paired_cases_produces_not_estimable(self):
        data = fixture()
        for case in data["cases"]:
            for review in case["reviews"]:
                review["output_valid"] = False
                review["dimension_scores"] = None
                review["accepted"] = False
        report = MODULE.analyze_scorecard(data, **binding_kwargs())
        self.assertEqual(report["status"], "NOT_ESTIMABLE_NO_COMPLETE_PAIRED_CASES")
        self.assertIsNone(report["factorial_contrasts_on_complete_paired_cases_only"]["interaction"])
        self.assertIsNone(report["factorial_contrasts_equal_weight_per_source_cluster"]["interaction"])

    def test_requires_exactly_two_stable_blinded_reviewer_tokens(self):
        data = fixture()
        data["cases"][0]["reviews"][0]["reviewer_token"] = "reviewer-token-c"
        with self.assertRaisesRegex(MODULE.ScorecardError, "REVIEWER_PANEL_MUST_BE_TWO_BLINDED_TOKENS"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_scorecard_must_bind_to_frozen_manifest_and_rubric(self):
        data = fixture()
        data["manifest_sha256"] = "not-a-hash"
        with self.assertRaisesRegex(MODULE.ScorecardError, "SCORECARD_BINDING_HASH_INVALID"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_scorecard_case_ids_and_hashes_must_match_frozen_manifest(self):
        data = fixture()
        data["cases"][0]["input_sha256"] = "e" * 64
        with self.assertRaisesRegex(MODULE.ScorecardError, "SCORECARD_CASE_BINDING_MISMATCH"):
            MODULE.analyze_scorecard(data, **binding_kwargs())
        data = fixture()
        data["cases"].pop()
        with self.assertRaisesRegex(MODULE.ScorecardError, "SCORECARD_CASE_SET_MISMATCH"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_malformed_manifest_case_rows_fail_closed(self):
        kwargs = binding_kwargs()
        kwargs["manifest_cases"] = [{"missing_case_id": "case-01"}]
        with self.assertRaisesRegex(MODULE.ScorecardError, "MANIFEST_CASE_ROW_INVALID"):
            MODULE.analyze_scorecard(fixture(), **kwargs)

    def test_duplicate_manifest_case_ids_fail_closed(self):
        kwargs = binding_kwargs()
        kwargs["manifest_cases"] = manifest_fixture() + [manifest_fixture()[0]]
        with self.assertRaisesRegex(MODULE.ScorecardError, "MANIFEST_CASE_DUPLICATE"):
            MODULE.analyze_scorecard(fixture(), **kwargs)

    def test_missing_binding_files_fail_closed(self):
        with self.assertRaisesRegex(MODULE.ScorecardError, "SCORECARD_BINDING_FILES_REQUIRED"):
            MODULE.analyze_scorecard(fixture())

    def test_reviewer_panel_must_remain_exactly_two_stable_tokens(self):
        data = fixture()
        data["cases"][0]["reviews"][0]["reviewer_token"] = "reviewer-token-c"
        with self.assertRaisesRegex(MODULE.ScorecardError, "REVIEWER_PANEL_MUST_BE_TWO_BLINDED_TOKENS"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_rejects_missing_or_extra_review_rows(self):
        data = fixture()
        data["cases"][0]["reviews"].pop()
        with self.assertRaisesRegex(MODULE.ScorecardError, "TWO_REVIEWERS_PER_ARM_REQUIRED"):
            MODULE.analyze_scorecard(data, **binding_kwargs())

    def test_rejects_score_range_drift(self):
        data = fixture()
        data["cases"][0]["reviews"][0]["dimension_scores"][DIMS[0]] = 3
        with self.assertRaisesRegex(MODULE.ScorecardError, "DIMENSION_SCORE_INVALID"):
            MODULE.analyze_scorecard(data, **binding_kwargs())


if __name__ == "__main__":
    unittest.main()
