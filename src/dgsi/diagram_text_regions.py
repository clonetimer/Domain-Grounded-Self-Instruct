"""Conservative OCR label-region proposals, never engineering graph nodes or SFT.

Every label is copied verbatim from one provenance-checked OCR line.
Only bounded two-line alignment hypotheses are proposed; larger clusters,
connectivity, hierarchy, units, and fault semantics are deliberately not inferred.
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
RECIPE = "isolated-lines-plus-pair-hypotheses-v2"
PAIR_RULE = "horizontal-overlap-ge-0.5-and-vertical-gap-le-2x-height-v1"


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

    lines = ocr_record["lines"]
    for line in lines:
        if not TOKEN.fullmatch(line["line_id"]):
            raise DiagramTextRegionError("DIAGRAM_OCR_LINE_ID_UNSAFE_FOR_LOCATOR")
        if not line["text"].strip():
            raise DiagramTextRegionError("DIAGRAM_OCR_LINE_TEXT_EMPTY")

    def make_candidate(group: list[dict[str, Any]], candidate_type: str) -> dict[str, Any]:
        ordered = sorted(group, key=lambda line: (
            line["bbox_px"]["top"], line["bbox_px"]["left"], line["line_id"]
        ))
        line_ids = [line["line_id"] for line in ordered]
        left = min(line["bbox_px"]["left"] for line in ordered)
        top = min(line["bbox_px"]["top"] for line in ordered)
        right = max(line["bbox_px"]["left"] + line["bbox_px"]["width"] for line in ordered)
        bottom = max(line["bbox_px"]["top"] + line["bbox_px"]["height"] for line in ordered)
        bbox = {"left": left, "top": top, "width": right-left, "height": bottom-top}
        bounds = ",".join(str(bbox[field]) for field in ("left", "top", "width", "height"))
        locator_kind = "ocr-line" if len(ordered) == 1 else "ocr-lines"
        locator_ids = line_ids[0] if len(ordered) == 1 else ",".join(line_ids)
        locator = (
            f"asset:{asset_id}@sha256:{receipt['asset_sha256']}"
            f"#{locator_kind}:{locator_ids}#bbox-px:{bounds}"
        )
        label_text = ordered[0]["text"] if len(ordered) == 1 else "\\n".join(
            line["text"] for line in ordered
        )
        identity = {
            "source_sha256": receipt["source_sha256"],
            "asset_sha256": receipt["asset_sha256"],
            "line_ids": line_ids,
            "label_texts": [line["text"] for line in ordered],
            "bbox_px": bbox,
            "candidate_type": candidate_type,
            "grouping_rule": PAIR_RULE if len(ordered) > 1 else None,
            "recipe": RECIPE,
        }
        candidate_id = "OCR-" + hashlib.sha256(_canonical_bytes(identity)).hexdigest()[:20]
        result = {
            "candidate_id": candidate_id,
            "candidate_type": candidate_type,
            "label_text": label_text,
            "ocr_line_ids": line_ids,
            "bbox_px": bbox,
            "evidence_locators": [locator],
            "object_type": "UNKNOWN",
            "interpretation": "UNRESOLVED_OCR_TEXT",
            "review_status": "MANUAL_REVIEW_REQUIRED",
        }
        if len(ordered) > 1:
            result["grouping_rule"] = PAIR_RULE
        return result

    candidates = [make_candidate([line], "SINGLE_LINE") for line in lines]

    # Pair hypotheses only: two adjacent lines with substantial horizontal
    # overlap and a bounded vertical gap. Keep the original singleton records.
    ordered_lines = sorted(lines, key=lambda line: (
        line["bbox_px"]["top"], line["bbox_px"]["left"], line["line_id"]
    ))
    for index, first in enumerate(ordered_lines):
        a = first["bbox_px"]
        for second in ordered_lines[index + 1:]:
            b = second["bbox_px"]
            gap = b["top"] - (a["top"] + a["height"])
            if gap < 0:
                continue
            overlap = max(0, min(a["left"] + a["width"], b["left"] + b["width"]) - max(a["left"], b["left"]))
            min_width = min(a["width"], b["width"])
            if min_width <= 0 or overlap / min_width < 0.5:
                continue
            if gap > 2 * max(a["height"], b["height"]):
                # Later lines are further down, so subsequent pairs cannot fit.
                break
            candidates.append(make_candidate([first, second], "MULTI_LINE_HYPOTHESIS"))

    candidates.sort(key=lambda c: (
        c["bbox_px"]["top"], c["bbox_px"]["left"],
        len(c["ocr_line_ids"]), tuple(c["ocr_line_ids"]), c["candidate_id"],
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
