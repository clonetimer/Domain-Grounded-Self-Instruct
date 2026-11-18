"""Join the current-scientific and source-rights *structural* review gates.

This is NOT an admission, legal-rights decision, reviewer authentication,
Gold promotion, SFT serializer, split assignment, or training authorization.
The input receipts remain private; the returned report is aggregate only.
"""
from __future__ import annotations

from typing import Any

from .l1_blind_review_manifest import L1BlindReviewManifestError
from .l1_c2_current_scored_review_preflight import (
    audit_c2_scored_review_against_current_sources,
)
from .l1_c2_current_rights_preflight import (
    audit_c2_rights_intake_against_current_sources,
)
from .l1_c2_rights_intake_audit import C2SourceRightsIntakeError


class C2JointReviewError(ValueError):
    """Fixed, content-free rejection code; no source or reviewer material."""


def audit_c2_joint_review_against_current_sources(
    rights_blank: dict[str, Any],
    rights_submission: dict[str, Any],
    scored_manifest: dict[str, Any],
    scored_submissions: list[dict[str, Any]],
    current_l1_collection: dict[str, Any],
    current_l0_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Check *both* private review tracks against one independently loaded cohort.

    The current L0/L1 artifacts must be read from an authorized repository
    checkout, not extracted from the submitted worksheets. A passing report
    means both forms are structurally bound to a matching source snapshot,
    not that any scientific, identity, or intellectual-property review passed.
    """
    if (
        not isinstance(rights_blank, dict)
        or not isinstance(scored_manifest, dict)
        or not isinstance(rights_submission, dict)
        or not isinstance(scored_submissions, list)
        or not isinstance(current_l1_collection, dict)
        or not isinstance(current_l0_fact_cards, list)
    ):
        raise C2JointReviewError("C2_JOINT_INPUT_SHAPE_INVALID")

    try:
        rights = audit_c2_rights_intake_against_current_sources(
            rights_blank, rights_submission,
            current_l1_collection, current_l0_fact_cards,
        )
    except C2SourceRightsIntakeError as exc:
        raise C2JointReviewError("C2_JOINT_RIGHTS_PREFLIGHT_REJECTED") from exc

    try:
        scientific = audit_c2_scored_review_against_current_sources(
            scored_manifest, scored_submissions,
            current_l1_collection, current_l0_fact_cards,
        )
    except L1BlindReviewManifestError as exc:
        raise C2JointReviewError("C2_JOINT_SCIENCE_PREFLIGHT_REJECTED") from exc

    # Defense in depth: the two separately generated coordinator manifests
    # must identify exactly the same immutable collection projection.
    digest_a = rights_blank.get("collection_projection_sha256")
    digest_b = scored_manifest.get("collection_projection_sha256")
    if not isinstance(digest_a, str) or digest_a != digest_b:
        raise C2JointReviewError("C2_JOINT_COHORT_FINGERPRINT_MISMATCH")

    # Never turn structural validation of independently supplied *claims*
    # into a credential, scientific verdict, source-rights clearance, or SFT.
    if (
        rights.get("current_public_source_snapshot_matched") is not True
        or scientific.get("current_public_source_snapshot_matched") is not True
        or rights.get("source_rights_verified") is not False
        or scientific.get("expert_review_complete") is not False
        or rights.get("training_authorized") is not False
        or scientific.get("training_authorized") is not False
    ):
        raise C2JointReviewError("C2_JOINT_UNAUTHORIZED_ADMISSION_STATE")

    return {
        "schema_version": "dgsi-c2-joint-review-preflight.v1",
        "decision": "BOTH_RECEIPT_STRUCTURES_VALID_EXTERNAL_ADMISSION_PENDING",
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "science_packet_count": scientific["packet_count"],
        "science_rubric_validated_count":
            scientific["ten_dimension_rubric_validated_count"],
        "source_document_count": rights["distinct_source_document_count"],
        "science_adjudication_status_counts":
            scientific["adjudication_status_counts"],
        "rights_evidence_referenced_document_count":
            rights["referenced_evidence_document_count"],
        "current_public_source_snapshot_matched": True,
        "scientific_expert_identity_authenticated": False,
        "scientific_expert_review_complete": False,
        "source_rights_verified": False,
        "real_gold_count": 0,
        "official_splits_assigned": False,
        "not_for_sft": True,
        "sft_records_emitted": 0,
        "gold_eligible": False,
        "training_authorized": False,
    }
