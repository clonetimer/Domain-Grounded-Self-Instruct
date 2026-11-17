"""Blank, fingerprint-bound C2 expert handoff; never an expert verdict.

Public metadata only. Reviewers must inspect the source facts and full L1
candidate through separately authorized channels. No model-facing material,
private reviewer token, scoring opinion or SFT example is exported.
"""
from __future__ import annotations

from typing import Any

from .l1_blind_review_manifest import build_l1_blind_review_manifest
from .l1_coverage_review import REVIEW_DIMENSIONS, FINDING_CODES

_VERSION = "dgsi-c2-blank-expert-handoff.v1"


def build_c2_expert_handoff(
    collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]],
    reviewer_slot: str,
) -> dict[str, Any]:
    """Create ONE independent reviewer's unfilled, source-bound handoff.

    The upstream manifest builder revalidates all 15/N packets, synthetic
    provenance, event families and the collection projection. Each reviewer
    receives their *own* document, never the other reviewer's assessment.
    """
    if reviewer_slot not in ("A", "B"):
        raise ValueError("C2_HANDOFF_REVIEWER_SLOT_INVALID")
    manifest = build_l1_blind_review_manifest(
        collection, source_fact_cards=source_fact_cards
    )
    tasks = []
    for entry in manifest["review_packets"]:
        tasks.append({
            "task_id": entry["task_id"],
            "case_id": entry["case_id"],
            "event_family": entry["event_family"],
            "task_type": entry["task_type"],
            "collection_projection_sha256": entry["collection_projection_sha256"],
            "packet_sha256": entry["packet_sha256"],
            "source_public_sha256": entry["source_public_sha256"],
            "source_fact_bindings": entry["source_fact_bindings"],
            "blinded_packet_ref": "sha256:" + entry["packet_sha256"],
            "reviewer_slot": reviewer_slot,
            "scorecard": {
                "reviewer_token": None,
                "scores": {dimension: None for dimension in REVIEW_DIMENSIONS},
                "finding_codes": [],
                "decision": None,
            },
            "source_rights_status": "PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW",
            "review_status": "NOT_REVIEWED",
        })
    if len(tasks) != manifest["packet_count"]:
        raise ValueError("C2_HANDOFF_PACKET_COUNT_MISMATCH")
    return {
        "schema_version": _VERSION,
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "status": "BLANK_EXTERNAL_EXPERT_REVIEW_REQUIRED",
        "notice": (
            "BLANK FORM ONLY. No expert assessed these candidates. "
            "Scores, tokens and decisions must be completed privately; "
            "independence, source rights and scientific admission require "
            "separate authorization. This is not a training dataset."
        ),
        "collection_id": manifest["collection_id"],
        "collection_projection_sha256": manifest["collection_projection_sha256"],
        "packet_count": manifest["packet_count"],
        "event_family_count": manifest["event_family_count"],
        "reviewer_slot": reviewer_slot,
        "rubric_dimensions": list(REVIEW_DIMENSIONS),
        "allowed_finding_codes": sorted(FINDING_CODES),
        "tasks": tasks,
        "source_rights_verified": False,
        "reviewer_authenticated": False,
        "expert_adjudicated_count": 0,
        "official_splits_assigned": False,
        "sft_records_emitted": 0,
        "gold_eligible": False,
        "training_authorized": False,
    }
