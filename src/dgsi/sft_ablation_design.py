"""Read-only DGSI SFT ablation pre-registration audit (no model execution).

This is a design-consistency validator, not an admission, review, dataset
split, evaluation-result or training-authorization service. Never reads cases.
"""
from __future__ import annotations

import re
from typing import Any


ARMS = (
    "BASE_MODEL",
    "GENERIC_SELF_INSTRUCT",
    "DGSI_LITERATURE_DERIVED_SYNTHETIC",
    "DGSI_REAL_GOLD",
    "DGSI_WITH_RETRIEVED_HISTORY",
)
TRAINING_SOURCES = {
    "BASE_MODEL": "NONE",
    "GENERIC_SELF_INSTRUCT": "GENERIC_SELF_INSTRUCT",
    "DGSI_LITERATURE_DERIVED_SYNTHETIC": "LITERATURE_DERIVED_SYNTHETIC",
    "DGSI_REAL_GOLD": "REAL_GOLD",
    "DGSI_WITH_RETRIEVED_HISTORY": "LITERATURE_DERIVED_SYNTHETIC",
}
METRICS = (
    "fault_source_localization",
    "affected_component_accuracy",
    "evidence_consistency",
    "uncertainty_and_abstention",
    "disposal_fidelity",
    "historical_transfer_validity",
    "confidence_calibration_if_eligible",
)
TRACKS = {"REAL_GOLD", "LITERATURE_DERIVED_SYNTHETIC"}
HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
# Canonical source-family aliases are ASCII identifiers, never display labels.
# Reject compatibility glyphs/invisible characters rather than guessing identity.
FAMILY_REF = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


class SFTAblationDesignError(ValueError):
    """Fixed, content-free error code (never interpolates user data)."""


def _fail(code: str) -> None:
    raise SFTAblationDesignError(code)


def _exact(obj: Any, keys: set[str], code: str) -> None:
    if not isinstance(obj, dict) or set(obj) != keys:
        _fail(code)


def _families(items: Any, code: str) -> tuple[set[str], set[str], dict[str, int]]:
    """Validate provisional family aliases, not official split assignments."""
    if not isinstance(items, list):
        _fail(code)
    found: set[str] = set()
    digests: set[str] = set()
    counts = {track: 0 for track in sorted(TRACKS)}
    for item in items:
        _exact(item, {"family_ref", "track", "fact_card_sha256"}, code)
        ref, track, digest = (item[k] for k in ("family_ref", "track", "fact_card_sha256"))
        if not isinstance(ref, str) or FAMILY_REF.fullmatch(ref) is None:
            _fail(code)
        if not isinstance(track, str) or track not in TRACKS or not isinstance(digest, str) or HEX_SHA256.fullmatch(digest) is None:
            _fail(code)
        canonical_ref = ref.casefold()
        if canonical_ref in found:
            _fail("ABLATION_DUPLICATE_FAMILY")
        if digest in digests:
            _fail("ABLATION_DUPLICATE_SOURCE_FACT_DIGEST")
        found.add(canonical_ref)
        digests.add(digest)
        counts[track] += 1
    return found, digests, counts


def audit_sft_ablation_design(plan: dict[str, Any]) -> dict[str, Any]:
    """Audit pre-registration; return aggregate-only, permanently non-executable.

    Even synthetic test plans with nonempty family lists do not grant approval.
    Real training/evaluation requires independently authorized source, reviewer,
    split and run receipts that this routine neither accepts nor generates.
    """
    _exact(plan, {
        "schema_version", "arm_specs", "evaluation_metrics", "candidate_training_families",
        "candidate_holdout_families", "holdout_policy", "history_policy",
        "gold_eligible", "training_authorized", "evaluation_executed",
    }, "INVALID_ABLATION_ENVELOPE")
    if plan["schema_version"] != "dgsi-sft-ablation-design.v1":
        _fail("INVALID_ABLATION_VERSION")
    if any(plan[k] is not False for k in ("gold_eligible", "training_authorized", "evaluation_executed")):
        _fail("ABLATION_UNAUTHORIZED_PROMOTION")
    _exact(plan["holdout_policy"], {"provisional_only", "unit", "same_across_arms"}, "INVALID_HOLDOUT_POLICY")
    policy = plan["holdout_policy"]
    if policy != {"provisional_only": True, "unit": "EVENT_FAMILY", "same_across_arms": True}:
        _fail("ABLATION_HOLDOUT_POLICY_UNSAFE")
    _exact(plan["history_policy"], {
        "retrieval_mode", "analysis_cutoff_enforced", "timestamp_required",
        "source_status_preserved", "same_family_excluded", "hardware_scope_required",
    }, "INVALID_HISTORY_POLICY")
    hp = plan["history_policy"]
    if hp != {
        "retrieval_mode": "USER_CONTEXT_ONLY",
        "analysis_cutoff_enforced": True,
        "timestamp_required": True,
        "source_status_preserved": True,
        "same_family_excluded": True,
        "hardware_scope_required": True,
    }:
        _fail("ABLATION_HISTORY_POLICY_UNSAFE")
    if not isinstance(plan["evaluation_metrics"], list) or tuple(plan["evaluation_metrics"]) != METRICS:
        _fail("ABLATION_METRIC_SET_INCOMPLETE")
    arms = plan["arm_specs"]
    if not isinstance(arms, list) or len(arms) != len(ARMS):
        _fail("ABLATION_ARMS_INCOMPLETE")
    seen: set[str] = set()
    for arm in arms:
        _exact(arm, {"arm", "training_source", "context_mode", "run_status"}, "INVALID_ABLATION_ARM")
        name = arm["arm"]
        if not isinstance(name, str) or name not in TRAINING_SOURCES or name in seen:
            _fail("ABLATION_ARM_UNKNOWN_OR_DUPLICATE")
        seen.add(name)
        if arm["training_source"] != TRAINING_SOURCES[name]:
            _fail("ABLATION_TRAINING_SOURCE_MISMATCH")
        expected_context = "AS_OF_RETRIEVED" if name == "DGSI_WITH_RETRIEVED_HISTORY" else "NONE"
        if arm["context_mode"] != expected_context:
            _fail("ABLATION_CONTEXT_CONFOUND")
        if arm["run_status"] != "NOT_RUN":
            _fail("ABLATION_UNVERIFIED_RUN_CLAIM")
    if seen != set(ARMS):
        _fail("ABLATION_ARMS_INCOMPLETE")
    training, train_digests, train_counts = _families(
        plan["candidate_training_families"], "INVALID_TRAINING_FAMILY_PROPOSAL")
    holdout, holdout_digests, holdout_counts = _families(
        plan["candidate_holdout_families"], "INVALID_HOLDOUT_FAMILY_PROPOSAL")
    if training & holdout:
        _fail("ABLATION_EVENT_FAMILY_EXPOSURE")
    if train_digests & holdout_digests:
        _fail("ABLATION_SOURCE_FACT_DIGEST_EXPOSURE")
    # Counts only. Never disclose case/family identifiers, source texts or digests.
    return {
        "schema_version": "dgsi-sft-ablation-design-audit.v1",
        "decision": "DESIGN_ONLY_EXTERNAL_REVIEW_AND_AUTHORIZATION_REQUIRED",
        "arm_count": len(seen),
        "candidate_training_family_count": len(training),
        "candidate_holdout_family_count": len(holdout),
        "candidate_training_family_count_by_track": train_counts,
        "candidate_holdout_family_count_by_track": holdout_counts,
        "real_gold_count": 0,
        "formal_split_assigned": False,
        "results_recorded": False,
        "training_authorized": False,
        "note": "Provisional metadata is not an approved independent holdout or run receipt.",
    }
