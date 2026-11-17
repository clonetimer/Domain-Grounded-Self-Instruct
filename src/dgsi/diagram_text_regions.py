"""Conservative OCR label-region proposals, never engineering graph nodes or SFT.

Every label is copied verbatim from one provenance-checked OCR line.
Cross-line clustering, connectivity, hierarchy, units, and fault semantics
are deliberately not inferred.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from dgsi.diagram_provenance import (
    DiagramProvenanceError,
    validate_diagram_asset_provenance,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/diagram_text_regions.schema.json"
TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
RECIPE = "isolated-ocr-line-v1"


class DiagramTextRegionError(ValueError):
    """Stable error code only. Never disclose source text or local paths."""


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def propose_diagram_text_regions(
    document_manifest: dict[str, Any],
    ocr_record: dict[str, Any],
    asset_path: str | Path,
) -> dict[str, Any]:
    """Return deterministic, unreviewed text-region candidates for local annotation.

    The caller may save the returned OCR text only in an explicitly authorized
    local workspace. Nothing here is eligible for training or a Gold case.
    """
    try:
        receipt = validate_diagram_asset_provenance(
            document_manifest, ocr_record, asset_path
        )
    except DiagramProvenanceError as error:
        raise DiagramTextRegionError(str(error)) from None

    asset_id = receipt["asset_id"]
    if not TOKEN.fullmatch(asset_id):
        raise DiagramTextRegionError("DIAGRAM_ASSET_ID_UNSAFE_FOR_LOCATOR")

    candidates = []
    for line in ocr_record["lines"]:
        line_id = line["line_id"]
        if not TOKEN.fullmatch(line_id):
            raise DiagramTextRegionError("DIAGRAM_OCR_LINE_ID_UNSAFE_FOR_LOCATOR")
        if not line["text"].strip():
            raise DiagramTextRegionError("DIAGRAM_OCR_LINE_TEXT_EMPTY")
        bbox = line["bbox_px"]
        bounds = ",".join(str(bbox[field]) for field in ("left", "top", "width", "height"))
        locator = (
            f"asset:{asset_id}@sha256:{receipt['asset_sha256']}"
            f"#ocr-line:{line_id}#bbox-px:{bounds}"
        )
        identity = {
            "source_sha256": receipt["source_sha256"],
            "asset_sha256": receipt["asset_sha256"],
            "line_id": line_id,
            "label_text": line["text"],
            "bbox_px": bbox,
            "recipe": RECIPE,
        }
        candidate_id = "OCR-" + hashlib.sha256(_canonical_bytes(identity)).hexdigest()[:20]
        candidates.append({
            "candidate_id": candidate_id,
            "label_text": line["text"],
            "ocr_line_ids": [line_id],
            "bbox_px": dict(bbox),
            "evidence_locators": [locator],
            "object_type": "UNKNOWN",
            "interpretation": "UNRESOLVED_OCR_TEXT",
            "review_status": "MANUAL_REVIEW_REQUIRED",
        })

    candidates.sort(key=lambda c: (
        c["bbox_px"]["top"], c["bbox_px"]["left"],
        c["ocr_line_ids"][0], c["candidate_id"],
    ))
    record = {
        "schema_version": "dgsi.diagram-text-regions.v1",
        "source_id": receipt["source_id"],
        "source_sha256": receipt["source_sha256"],
        "asset_id": asset_id,
        "asset_sha256": receipt["asset_sha256"],
        "ocr_record_sha256": hashlib.sha256(_canonical_bytes(ocr_record)).hexdigest(),
        "generation_recipe": RECIPE,
        "candidates": candidates,
        "review_status": "REVIEW_REQUIRED",
        "not_for_sft": True,
        "training_authorized": False,
        "gold_authorized": False,
    }
    try:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        invalid = next(Draft202012Validator(schema).iter_errors(record), None)
    except (OSError, ValueError, TypeError):
        raise DiagramTextRegionError("DIAGRAM_TEXT_REGIONS_SCHEMA_UNAVAILABLE") from None
    if invalid is not None:
        raise DiagramTextRegionError("DIAGRAM_TEXT_REGIONS_SCHEMA_INVALID")
    return record
