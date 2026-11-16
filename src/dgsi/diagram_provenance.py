"""Fail-closed provenance gate joining document manifests, extracted assets and OCR records."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
DOCUMENT_SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/document_ingestion.schema.json"
OCR_SCHEMA = ROOT / "skills/dgsi-simulation-to-sft/schemas/ocr_candidates.schema.json"


class DiagramProvenanceError(ValueError):
    """Stable, payload-free provenance validation error."""


def _schema_validate(record: dict[str, Any], schema_path: Path, code: str) -> None:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(record))
    except (OSError, json.JSONDecodeError, TypeError):
        raise DiagramProvenanceError(code) from None
    if errors:
        raise DiagramProvenanceError(code)


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), size


def validate_diagram_asset_provenance(
    document_manifest: dict[str, Any],
    ocr_record: dict[str, Any],
    asset_path: str | Path,
) -> dict[str, Any]:
    """Verify exact document/asset/OCR identity and pixel-box bounds.

    The asset path is explicit; this function never resolves paths from an
    untrusted manifest. It emits aggregate metadata only and never returns OCR
    text, document text, local paths, or source payloads.
    """
    _schema_validate(document_manifest, DOCUMENT_SCHEMA, "DIAGRAM_DOCUMENT_MANIFEST_INVALID")
    _schema_validate(ocr_record, OCR_SCHEMA, "DIAGRAM_OCR_RECORD_INVALID")

    path = Path(asset_path)
    if path.is_symlink() or not path.is_file():
        raise DiagramProvenanceError("DIAGRAM_ASSET_UNAVAILABLE")
    try:
        actual_hash, actual_size = _sha256_file(path)
    except OSError:
        raise DiagramProvenanceError("DIAGRAM_ASSET_UNAVAILABLE") from None

    assets = document_manifest["assets"]
    matches = [item for item in assets if item.get("asset_id") == ocr_record["asset_id"]]
    if len(matches) != 1:
        raise DiagramProvenanceError("DIAGRAM_ASSET_ID_NOT_UNIQUE_IN_SOURCE")
    asset = matches[0]

    if asset.get("extraction_status") != "EXTRACTED":
        raise DiagramProvenanceError("DIAGRAM_ASSET_BYTES_NOT_EXTRACTED")
    if asset.get("sha256") != actual_hash or ocr_record["asset_sha256"] != actual_hash:
        raise DiagramProvenanceError("DIAGRAM_ASSET_HASH_MISMATCH")
    if asset.get("size_bytes") != actual_size:
        raise DiagramProvenanceError("DIAGRAM_ASSET_SIZE_MISMATCH")

    width = ocr_record["image_width"]
    height = ocr_record["image_height"]
    line_ids: set[str] = set()
    word_count = 0
    for line in ocr_record["lines"]:
        line_id = line["line_id"]
        if line_id in line_ids:
            raise DiagramProvenanceError("DIAGRAM_OCR_LINE_ID_DUPLICATE")
        line_ids.add(line_id)
        for box in [line["bbox_px"], *(word["bbox_px"] for word in line["words"])]:
            left, top = box["left"], box["top"]
            box_width, box_height = box["width"], box["height"]
            if box_width <= 0 or box_height <= 0:
                raise DiagramProvenanceError("DIAGRAM_OCR_BOX_EMPTY")
            if left + box_width > width or top + box_height > height:
                raise DiagramProvenanceError("DIAGRAM_OCR_BOX_OUT_OF_BOUNDS")
        word_count += len(line["words"])

    return {
        "decision": "PROVENANCE_CONSISTENT_REVIEW_REQUIRED",
        "source_id": document_manifest["source_id"],
        "source_sha256": document_manifest["sha256"],
        "asset_id": asset["asset_id"],
        "asset_sha256": actual_hash,
        "asset_size_bytes": actual_size,
        "ocr_line_count": len(line_ids),
        "ocr_word_count": word_count,
        "review_status": "REVIEW_REQUIRED",
        "training_authorized": False,
        "gold_authorized": False,
    }
