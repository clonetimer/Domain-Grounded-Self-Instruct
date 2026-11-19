"""Descriptive, paired analysis for a frozen DGSI 2x2 blinded-review scorecard.

No model calls, tuning, score imputation, retries, or training authorization.
Invalid outputs remain visible and are never assigned fabricated numeric penalties.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from validate_factorial_manifest import validate_manifest

DIMENSIONS = (
    "source_fidelity", "phenomenon_analysis", "ml_interpretation",
    "fault_source", "affected_components", "evidence_fidelity",
    "uncertainty", "disposal_fidelity", "historical_context_transfer",
    "engineering_actionability",
)
ARMS = {
    "A": (False, False),
    "B": (False, True),
    "C": (True, False),
    "D": (True, True),
}


class ScorecardError(ValueError):
    pass


def _mean(values):
    return sum(values) / len(values) if values else None


def analyze_scorecard(data: dict, *, manifest_sha256: str | None = None, rubric_sha256: str | None = None, manifest_cases: list | None = None) -> dict:
    if not isinstance(data, dict) or data.get("schema_version") != "dgsi-factorial-review-scorecard.v1":
        raise ScorecardError("SCORECARD_SCHEMA_INVALID")
    if data.get("classification") != "BLINDED_REVIEW_SCORECARD_NOT_FOR_SFT":
        raise ScorecardError("SCORECARD_CLASSIFICATION_INVALID")
    for hash_field in ("manifest_sha256", "rubric_sha256"):
        value = data.get(hash_field)
        if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
            raise ScorecardError("SCORECARD_BINDING_HASH_INVALID")
    if manifest_sha256 is None or rubric_sha256 is None or manifest_cases is None:
        raise ScorecardError("SCORECARD_BINDING_FILES_REQUIRED")
    if data["manifest_sha256"] != manifest_sha256 or data["rubric_sha256"] != rubric_sha256:
        raise ScorecardError("SCORECARD_BINDING_HASH_MISMATCH")
    cases = data.get("cases")
    expected_by_id = {row["case_id"]: row for row in manifest_cases}
    if len(expected_by_id) != len(manifest_cases):
        raise ScorecardError("MANIFEST_CASE_DUPLICATE")
    scorecard_by_id = {}
    for row in cases if isinstance(cases, list) else []:
        if isinstance(row, dict) and isinstance(row.get("case_id"), str):
            scorecard_by_id[row["case_id"]] = row
    if set(scorecard_by_id) != set(expected_by_id):
        raise ScorecardError("SCORECARD_CASE_SET_MISMATCH")
    for case_id, expected in expected_by_id.items():
        actual = scorecard_by_id[case_id]
        if any(actual.get(key) != expected.get(key) for key in
               ("source_cluster_id", "input_sha256", "target_schema_sha256")):
            raise ScorecardError("SCORECARD_CASE_BINDING_MISMATCH")
    if not isinstance(cases, list) or not cases:
        raise ScorecardError("CASES_MISSING")

    case_ids = set()
    reviewer_tokens = set()
    rows_by_case = {}
    cluster_by_case = {}
    for case in cases:
        if not isinstance(case, dict) or set(case) != {"case_id", "source_cluster_id", "input_sha256", "target_schema_sha256", "reviews"}:
            raise ScorecardError("CASE_ROW_INVALID")
        case_id, cluster = case["case_id"], case["source_cluster_id"]
        for hash_field in ("input_sha256", "target_schema_sha256"):
            value = case[hash_field]
            if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                raise ScorecardError("CASE_BINDING_HASH_INVALID")
        if not isinstance(case_id, str) or not case_id.strip() or not isinstance(cluster, str) or not cluster.strip():
            raise ScorecardError("CASE_ID_OR_CLUSTER_INVALID")
        if case_id in case_ids:
            raise ScorecardError("DUPLICATE_CASE_ID")
        case_ids.add(case_id)
        cluster_by_case[case_id] = cluster
        reviews = case["reviews"]
        if not isinstance(reviews, list) or len(reviews) != 8:
            raise ScorecardError("TWO_REVIEWERS_PER_ARM_REQUIRED")
        by_arm = {arm: [] for arm in ARMS}
        for review in reviews:
            required = {"arm_id", "reviewer_token", "output_valid", "dimension_scores", "accepted", "critical_failure_codes"}
            if not isinstance(review, dict) or set(review) != required:
                raise ScorecardError("REVIEW_ROW_INVALID")
            arm = review["arm_id"]
            token = review["reviewer_token"]
            if arm not in ARMS or not isinstance(token, str) or not token.strip():
                raise ScorecardError("REVIEW_ID_INVALID")
            reviewer_tokens.add(token)
            if type(review["output_valid"]) is not bool or type(review["accepted"]) is not bool:
                raise ScorecardError("REVIEW_BOOLEAN_INVALID")
            if not review["output_valid"] and review["accepted"]:
                raise ScorecardError("INVALID_OUTPUT_CANNOT_BE_ACCEPTED")
            codes = review["critical_failure_codes"]
            if not isinstance(codes, list) or any(not isinstance(code, str) or not code.strip() for code in codes):
                raise ScorecardError("CRITICAL_FAILURE_CODES_INVALID")
            scores = review["dimension_scores"]
            if review["output_valid"]:
                if not isinstance(scores, dict) or set(scores) != set(DIMENSIONS):
                    raise ScorecardError("DIMENSION_SCORE_SET_INVALID")
                if any(type(score) is not int or score not in (0, 1, 2) for score in scores.values()):
                    raise ScorecardError("DIMENSION_SCORE_INVALID")
            elif scores is not None:
                raise ScorecardError("INVALID_OUTPUT_MUST_NOT_HAVE_SCORE")
            by_arm[arm].append(review)
        if any(len(by_arm[arm]) != 2 for arm in ARMS):
            raise ScorecardError("TWO_REVIEWERS_PER_ARM_REQUIRED")
        panel_tokens = {r["reviewer_token"] for r in reviews}
        if len(panel_tokens) != 2:
            raise ScorecardError("REVIEWER_PANEL_MUST_BE_TWO_BLINDED_TOKENS")
        if any({r["reviewer_token"] for r in by_arm[arm]} != panel_tokens for arm in ARMS):
            raise ScorecardError("REVIEWER_PAIR_MISMATCH_ACROSS_ARMS")
        rows_by_case[case_id] = by_arm

    if len(reviewer_tokens) != 2:
        raise ScorecardError("REVIEWER_PANEL_MUST_BE_STABLE_ACROSS_CASES")
    clusters = sorted(set(cluster_by_case.values()))
    per_case = {}
    arm_case_scores = {arm: {} for arm in ARMS}
    arm_acceptance = {arm: [] for arm in ARMS}
    arm_invalid = {arm: 0 for arm in ARMS}
    arm_critical = {arm: 0 for arm in ARMS}
    arm_dimension_case_scores = {arm: {dimension: {} for dimension in DIMENSIONS} for arm in ARMS}
    reviewer_dimension_disagreements = 0
    reviewer_acceptance_disagreements = 0

    for case_id, by_arm in rows_by_case.items():
        per_case[case_id] = {}
        for arm, reviews in by_arm.items():
            valid = [r for r in reviews if r["output_valid"]]
            invalid_count = 2 - len(valid)
            arm_invalid[arm] += invalid_count
            arm_critical[arm] += sum(len(r["critical_failure_codes"]) for r in reviews)
            arm_acceptance[arm].append(sum(1 for r in reviews if r["accepted"]) / 2)
            if len(valid) == 2:
                totals = [sum(r["dimension_scores"].values()) for r in valid]
                arm_case_scores[arm][case_id] = _mean(totals)
            else:
                arm_case_scores[arm][case_id] = None
            if len(valid) == 2:
                dims_a, dims_b = valid[0]["dimension_scores"], valid[1]["dimension_scores"]
                for dimension in DIMENSIONS:
                    if dims_a[dimension] != dims_b[dimension]:
                        reviewer_dimension_disagreements += 1
                    arm_dimension_case_scores[arm][dimension][case_id] = (
                        dims_a[dimension] + dims_b[dimension]
                    ) / 2
            if reviews[0]["accepted"] != reviews[1]["accepted"]:
                reviewer_acceptance_disagreements += 1
            per_case[case_id][arm] = {
                "reviewer_total_scores": [sum(r["dimension_scores"].values()) if r["output_valid"] else None for r in reviews],
                "case_mean_score": arm_case_scores[arm][case_id],
                "both_reviewers_accepted": all(r["accepted"] for r in reviews),
                "invalid_output_count": invalid_count,
                "critical_failure_codes": [code for r in reviews for code in r["critical_failure_codes"]],
            }

    complete_cases = [
        case_id for case_id in case_ids
        if all(arm_case_scores[arm][case_id] is not None for arm in ARMS)
    ]
    means = {}
    cluster_means = {}
    for arm in ARMS:
        scored = [arm_case_scores[arm][case_id] for case_id in case_ids if arm_case_scores[arm][case_id] is not None]
        means[arm] = _mean(scored)
        by_cluster = {}
        for cluster in clusters:
            vals = [arm_case_scores[arm][case_id] for case_id in case_ids
                    if cluster_by_case[case_id] == cluster and arm_case_scores[arm][case_id] is not None]
            if vals:
                by_cluster[cluster] = _mean(vals)
        cluster_means[arm] = _mean(list(by_cluster.values()))

    paired = {arm: {} for arm in ARMS}
    for arm in ARMS:
        paired[arm] = {
            case_id: arm_case_scores[arm][case_id]
            for case_id in complete_cases
        }
    contrasts = {}
    if complete_cases:
        evolution_diffs = [
            ((paired["C"][case_id] + paired["D"][case_id]) / 2)
            - ((paired["A"][case_id] + paired["B"][case_id]) / 2)
            for case_id in complete_cases
        ]
        selection_diffs = [
            ((paired["B"][case_id] + paired["D"][case_id]) / 2)
            - ((paired["A"][case_id] + paired["C"][case_id]) / 2)
            for case_id in complete_cases
        ]
        interaction_diffs = [
            (paired["D"][case_id] - paired["C"][case_id])
            - (paired["B"][case_id] - paired["A"][case_id])
            for case_id in complete_cases
        ]
        contrasts = {
            "evolution_main_effect": _mean(evolution_diffs),
            "selection_main_effect": _mean(selection_diffs),
            "interaction": _mean(interaction_diffs),
        }
    else:
        contrasts = {
            "evolution_main_effect": None,
            "selection_main_effect": None,
            "interaction": None,
        }

    dimension_analysis = {}
    for dimension in DIMENSIONS:
        complete_dimension_cases = [
            case_id for case_id in case_ids
            if all(arm_dimension_case_scores[arm][dimension].get(case_id) is not None for arm in ARMS)
        ]
        if complete_dimension_cases:
            scores = {
                arm: [arm_dimension_case_scores[arm][dimension][case_id] for case_id in complete_dimension_cases]
                for arm in ARMS
            }
            dimension_analysis[dimension] = {
                "complete_four_arm_paired_case_count": len(complete_dimension_cases),
                "arm_means": {arm: _mean(values) for arm, values in scores.items()},
                "evolution_main_effect": _mean([
                    ((arm_dimension_case_scores["C"][dimension][case_id] + arm_dimension_case_scores["D"][dimension][case_id]) / 2)
                    - ((arm_dimension_case_scores["A"][dimension][case_id] + arm_dimension_case_scores["B"][dimension][case_id]) / 2)
                    for case_id in complete_dimension_cases
                ]),
                "selection_main_effect": _mean([
                    ((arm_dimension_case_scores["B"][dimension][case_id] + arm_dimension_case_scores["D"][dimension][case_id]) / 2)
                    - ((arm_dimension_case_scores["A"][dimension][case_id] + arm_dimension_case_scores["C"][dimension][case_id]) / 2)
                    for case_id in complete_dimension_cases
                ]),
                "interaction": _mean([
                    (arm_dimension_case_scores["D"][dimension][case_id] - arm_dimension_case_scores["C"][dimension][case_id])
                    - (arm_dimension_case_scores["B"][dimension][case_id] - arm_dimension_case_scores["A"][dimension][case_id])
                    for case_id in complete_dimension_cases
                ]),
            }
        else:
            dimension_analysis[dimension] = {
                "complete_four_arm_paired_case_count": 0,
                "arm_means": {arm: None for arm in ARMS},
                "evolution_main_effect": None,
                "selection_main_effect": None,
                "interaction": None,
            }

    return {
        "schema_version": "dgsi-factorial-analysis-report.v1",
        "classification": "DESCRIPTIVE_ANALYSIS_NOT_FOR_SFT",
        "status": "ANALYZED" if complete_cases else "NOT_ESTIMABLE_NO_COMPLETE_PAIRED_CASES",
        "case_count": len(case_ids),
        "source_cluster_count": len(clusters),
        "complete_four_arm_paired_case_count": len(complete_cases),
        "complete_four_arm_paired_case_ids": sorted(complete_cases),
        "arm_summary": {
            arm: {
                "case_weighted_mean_score": means[arm],
                "source_cluster_weighted_mean_score": cluster_means[arm],
                "mean_two_reviewer_acceptance_fraction": _mean(arm_acceptance[arm]),
                "invalid_output_count_of_reviews": arm_invalid[arm],
                "critical_failure_code_count": arm_critical[arm],
            } for arm in ARMS
        },
        "factorial_contrasts_on_complete_paired_cases_only": contrasts,
        "per_dimension_factorial_analysis": dimension_analysis,
        "reviewer_dimension_disagreement_count": reviewer_dimension_disagreements,
        "reviewer_acceptance_disagreement_count": reviewer_acceptance_disagreements,
        "case_details": per_case,
        "limitations": [
            "Descriptive paired analysis only; no significance or superiority claim.",
            "No score imputation or numeric penalty is assigned to invalid outputs.",
            "Factorial score contrasts use only cases with valid scored outputs in all four arms; invalid-output rates are reported separately.",
            "Source-cluster-weighted means give each represented source cluster equal weight.",
            "With few source clusters, population-level uncertainty is not estimable from this report.",
            "GPT or other model-based review is not human expert adjudication.",
        ],
        "model_calls_authorized": False,
        "training_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scorecard", type=Path)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--rubric", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        scorecard_bytes = args.scorecard.read_bytes()
        manifest_bytes = args.manifest.read_bytes()
        rubric_bytes = args.rubric.read_bytes()
        data = json.loads(scorecard_bytes.decode("utf-8"))
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        manifest_report = validate_manifest(manifest)
        if not manifest_report.get("valid"):
            raise ScorecardError("RUN_MANIFEST_INVALID")
        report = analyze_scorecard(
            data,
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
            rubric_sha256=hashlib.sha256(rubric_bytes).hexdigest(),
            manifest_cases=manifest["cases"],
        )
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ScorecardError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, "status": report["status"], "output": str(args.output)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
