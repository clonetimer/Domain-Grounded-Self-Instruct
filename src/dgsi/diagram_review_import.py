"""Convert bound local text review receipts into proposed, never confirmed graph labels."""
from __future__ import annotations

from typing import Any

from dgsi.diagram_annotation import DiagramAnnotationError, validate_diagram_annotation
from dgsi.diagram_text_review import (
    DiagramTextReviewError,
    validate_diagram_text_review,
)


class DiagramReviewImportError(ValueError):
    """Stable, payload-free graph import error."""


def import_reviewed_text_as_proposed_graph(
    candidate_record: dict[str, Any],
    review_receipt: dict[str, Any],
) -> dict[str, Any]:
    """Create AI_PROPOSED label nodes only; never confirm graph semantics.

    A local receipt is not an authenticated expert approval. ACCEPT_AS_LABEL
    therefore becomes an AI_PROPOSED node with the selected object type as a
    proposal. No ports or edges are created from OCR text or spatial grouping.
    """
    try:
        receipt_summary = validate_diagram_text_review(candidate_record, review_receipt)
    except DiagramTextReviewError as error:
        raise DiagramReviewImportError(str(error)) from None

    candidates = {item["candidate_id"]: item for item in candidate_record["candidates"]}
    nodes = []
    claims = []
    accepted = []
    for decision in review_receipt["decisions"]:
        if decision["decision"] != "ACCEPT_AS_LABEL":
            continue
        candidate = candidates[decision["candidate_id"]]
        node_id = "NODE-" + candidate["candidate_id"]
        object_type = decision["object_type"]
        nodes.append({
            "node_id": node_id,
            "label": candidate["label_text"],
            "object_type": object_type,
            "hierarchy_path": [],
            "evidence_locator": decision["evidence_locator"],
            "review_status": "AI_PROPOSED",
        })
        claims.append({
            "claim": f"Text region proposed as a {object_type} label; semantic identity remains unverified.",
            "source_type": "VISIBLE_LABEL",
            "evidence_locator": decision["evidence_locator"],
            "certainty": "PROPOSED_INTERPRETATION",
        })
        accepted.append(candidate["candidate_id"])

    graph = {
        "schema_version": "dgsi.diagram-annotation.v1",
        "source_id": candidate_record["source_id"],
        "source_sha256": candidate_record["source_sha256"],
        "asset_id": candidate_record["asset_id"],
        "asset_sha256": candidate_record["asset_sha256"],
        "locator": f"asset:{candidate_record['asset_id']}@sha256:{candidate_record['asset_sha256']}",
        "diagram_type": "UNKNOWN",
        "nodes": nodes,
        "ports": [],
        "edges": [],
        "claims": claims,
        "review_status": "REVIEW_REQUIRED",
        "training_authorized": False,
    }
    try:
        graph_summary = validate_diagram_annotation(graph)
    except DiagramAnnotationError as error:
        raise DiagramReviewImportError(str(error)) from None

    return {
        "schema_version": "dgsi.diagram-review-import.v1",
        "diagram_annotation": graph,
        "conversion_receipt": {
            "review_id": review_receipt["review_id"],
            "candidate_record_sha256": review_receipt["candidate_record_sha256"],
            "source_sha256": candidate_record["source_sha256"],
            "asset_sha256": candidate_record["asset_sha256"],
            "accepted_candidate_ids": accepted,
            "review_receipt_decision": receipt_summary["decision"],
            "reviewer_authentication": "NOT_AUTHENTICATED_BY_LOCAL_TOOL",
            "graph_validation": graph_summary,
            "node_status": "AI_PROPOSED",
            "ports_created": 0,
            "edges_created": 0,
            "training_authorized": False,
            "gold_authorized": False,
        },
    }
