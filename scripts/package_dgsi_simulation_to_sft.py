#!/usr/bin/env python3
"""Build a portable DGSI Simulation-to-SFT toolkit ZIP.

Run from the repository root:
    python scripts/package_dgsi_simulation_to_sft.py
    python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft.zip

Only explicitly allowlisted public Skill, schema, validator and documentation
files are included. Private run artifacts, telemetry, credentials, local
review packets and generated candidate data are never collected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = Path("skills/dgsi-simulation-to-sft")
SCHEMAS = (
    "resources/source_fact_card.schema.json",
    "resources/diagnostic_case.schema.json",
    "resources/l1_task_packet.schema.json",
    "resources/l1_task_packet_collection.schema.json",
    "resources/diagnostic_sft.schema.json",
)
DOCS = (
    "docs/L1_DUAL_TRACK_AND_HISTORY_CONTEXT.md",
    "docs/L1_SFT_RELEASE_PREFLIGHT.md",
    "docs/P2_BASILISK_RECEIPT_INTAKE.md",
    "docs/REAL_DIAGNOSTIC_MATERIAL_REVIEW_HANDOFF.md",
    "docs/DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md",
    "docs/P5B4_DIAGRAM_CANDIDATE_EXTRACTION_CONTRACT.md",
    "docs/P5B4_HUMAN_LABEL_REVIEW_RECEIPTS.md",
    "docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md",
    "docs/P5C2_BLANK_EXPERT_REVIEW_HANDOFF_2026-11-18.md",
    "docs/P5C2_COHORT_BOUND_TEN_DIMENSION_REVIEW_2026-11-18.md",
    "docs/P5C2_COMPLETE_TWO_REVIEWER_KIT_2026-11-18.md",
    "docs/P5C2_PREVIEW_NO_CLOBBER_2026-11-18.md",
    "docs/P5C2_SCIENTIFIC_REVIEW_DOSSIER_2026-11-18.md",
    "docs/P5C2_SOURCE_FACT_REVIEW_STATE_VISIBILITY_2026-11-18.md",
    "docs/P5C2_SOURCE_RIGHTS_DEDUPLICATED_QUEUE_2026-11-18.md",
    "docs/P5C2_PACKAGE_DELIVERY_2026-11-18.md",
    "docs/P5C2_CURRENT_SOURCE_RIGHTS_PREFLIGHT_20261118.md",
    "docs/P5C2_OFFLINE_SOURCE_RIGHTS_INTAKE_20261118.md",
    "docs/P5C2_SOURCE_DOCUMENT_IDENTITY_GUARD_20261118.md",
    "docs/P5C2_CURRENT_EXPERT_INTAKE_20261118.md",
    "docs/P5C2_CONTENT_CORRECTION_2026-11-18.md",
)
VALIDATOR_FILES = (
    "requirements-validation.txt",
    "src/dgsi",
    "tests/test_l1_model_projection_preview.py",
    "scripts/create_l1_blind_review_manifest.py",
    "scripts/create_l1_c2_complete_review_kit.py",
    "scripts/create_l1_c2_expert_review_handoff.py",
    "scripts/create_l1_c2_scientific_dossier.py",
    "scripts/audit_l1_c2_current_rights_intake.py",
    "scripts/audit_l1_c2_current_expert_intake.py",
    "scripts/audit_l1_c2_source_rights_intake.py",
    "tests/test_l1_blind_review_manifest.py",
    "tests/test_l1_blind_review_manifest_cli.py",
    "tests/test_l1_c2_complete_review_kit.py",
    "tests/test_l1_c2_expert_handoff.py",
    "tests/test_l1_c2_scientific_dossier.py",
    "tests/test_l1_c2_scored_review.py",
    "tests/test_l1_c2_source_rights_queue.py",
    "tests/test_l1_c2_current_rights_preflight.py",
    "tests/test_l1_c2_expert_intake.py",
    "tests/test_l1_c2_expert_intake_cli.py",
    "tests/test_l1_c2_rights_intake_audit.py",
    "tests/test_l1_model_preview_cli_no_clobber.py",
    "scripts/audit_diagnostic_sft_lineage.py",
    "scripts/create_l1_model_preview.py",
    "scripts/audit_l1_global_lineage.py",
    "scripts/audit_simulation_run_receipt.py",
    "scripts/create_simulation_receipt_fixture.py",
    "scripts/audit_cross_ai_evaluation.py",
    "scripts/ingest_dgsi_document.py",
    "scripts/ocr_dgsi_image.py",
    "scripts/audit_diagram_asset_provenance.py",
    "scripts/propose_diagram_text_regions.py",
    "scripts/audit_diagram_text_review.py",
    "scripts/import_diagram_text_review.py",
    "scripts/audit_diagram_topology_review.py",
    "tests/test_diagram_topology_review.py",
    "tests/test_diagram_provenance.py",
    "src/dgsi/diagram_text_review.py",
    "src/dgsi/diagram_review_import.py",
    "tests/test_diagram_text_regions.py",
    "tests/test_diagram_text_regions_cli.py",
    "tests/test_diagram_text_review.py",
    "tests/test_diagram_review_import.py",
    "tests/test_diagram_review_import_cli.py",
    "tests/test_ocr_candidates.py",
    "tests/test_cross_ai_evaluation.py",
    "tests/test_document_ingestion.py",
    "tests/test_diagram_annotation.py",
    "scripts/package_simulation_receipt_module.py",
    "tests/test_simulation_run_receipt.py",
)


def files_under(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*") if p.is_file())
    raise FileNotFoundError(path)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="dist/dgsi-simulation-to-sft-toolkit.zip",
        help="Output ZIP path relative to repository root unless absolute.",
    )
    args = parser.parse_args()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output

    include_roots = [SKILL_ROOT, *map(Path, SCHEMAS), *map(Path, DOCS), *map(Path, VALIDATOR_FILES)]
    selected: dict[str, bytes] = {}
    for root in include_roots:
        for file_path in files_under(ROOT / root):
            relative = file_path.relative_to(ROOT).as_posix()
            # Explicitly reject sensitive or generated material even if later
            # directory contents change.
            lowered = relative.lower()
            if any(token in lowered for token in (
                "telemetry", "private", "secret", "credential", "reviewer_identity",
                "target_private", "hidden_truth", "run_bundle", "r21",
            )):
                raise RuntimeError(f"Refusing to package sensitive-looking path: {relative}")
            if file_path.suffix in {".pyc", ".pyo"} or "__pycache__" in file_path.parts:
                continue
            selected[relative] = file_path.read_bytes()

    manifest = {
        "toolkit": "dgsi-simulation-to-sft",
        "version": (ROOT / SKILL_ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "status": "DRAFT_CANDIDATE_GENERATION_ONLY",
        "files": [
            {"path": name, "size_bytes": len(data), "sha256": sha256(data)}
            for name, data in sorted(selected.items())
        ],
        "training_authorized": False,
        "gold_authorized": False,
        "sft_export_authorized": False,
    }
    selected["PACKAGE_SHA256_MANIFEST.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(selected.items()):
            # Fixed metadata makes repeated builds identical in the same runtime.
            info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    print(f"PACKAGE_CREATED={output}")
    print(f"FILES={len(selected)}")
    print(f"SHA256={sha256(output.read_bytes())}")
    print("TRAINING_AUTHORIZED=false")
    print("GOLD_AUTHORIZED=false")
    print("SFT_EXPORT_AUTHORIZED=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
