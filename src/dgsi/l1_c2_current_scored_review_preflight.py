"""Review-only scored-receipt intake against independent current L0/L1 data.

A scored receipt may be internally consistent with an OLD coordinator manifest.
Regenerate that manifest from the current version-controlled source snapshot,
rather than treating an untrusted/old manifest as the authority.

This checks metadata structure only. It never authenticates human reviewers,
scientific truth, rights, adjudication, or a training release.
"""
from __future__ import annotations

from typing import Any

from .l1_blind_review_manifest import (
    L1BlindReviewManifestError,
    build_l1_blind_review_manifest,
)
from .l1_c2_scored_review import audit_c2_scored_review_batch


def audit_c2_scored_review_against_current_sources(
    supplied_manifest: dict[str, Any],
    submissions: list[dict[str, Any]],
    current_l1_collection: dict[str, Any],
    current_l0_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Fail closed if scored submissions are bound only to an obsolete manifest.

    The collection/cards MUST be loaded independently from authorized,
    version-controlled current artifacts; never reconstruct from the editable
    scorecards or the supplied manifest. The batch must cover the entire cohort.
    """
    try:
        if not isinstance(current_l1_collection, dict):
            raise TypeError("collection shape")
        if not isinstance(current_l0_fact_cards, list):
            raise TypeError("L0 cards shape")
        current_manifest = build_l1_blind_review_manifest(
            current_l1_collection, source_fact_cards=current_l0_fact_cards
        )
    except (KeyError, TypeError, ValueError, AttributeError, IndexError) as exc:
        raise L1BlindReviewManifestError(
            "C2_SCORED_CURRENT_SOURCE_SNAPSHOT_INVALID"
        ) from exc

    # Match the entire metadata object: a matching cohort hash alone is not
    # sufficient if a source fact identity, task list or binding is changed.
    if not isinstance(supplied_manifest, dict) or supplied_manifest != current_manifest:
        raise L1BlindReviewManifestError(
            "C2_SCORED_STALE_OR_TAMPERED_COORDINATOR_MANIFEST"
        )

    report = audit_c2_scored_review_batch(current_manifest, submissions)
    # No reviewed scorecard or reviewer token is returned. A matching source
    # snapshot is never an expert signature or source-rights clearance.
    return {
        **report,
        "current_public_source_snapshot_matched": True,
        "identity_authenticated": False,
        "source_rights_verified": False,
        "expert_review_complete": False,
        "not_for_sft": True,
        "official_splits_assigned": False,
        "training_authorized": False,
        "gold_eligible": False,
        "sft_records_emitted": 0,
    }
