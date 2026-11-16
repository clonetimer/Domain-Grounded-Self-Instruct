# DGSI Simulation-to-SFT Toolkit

Portable production Skill for converting authorized spacecraft simulation and engineering materials into evidence-grounded fault-diagnosis instruction-tuning candidates.

## Contents

- `SKILL.md`: primary portable Skill entry point.
- `references/`: ingestion, truth separation, task design, audit and provider-neutral delegation procedures.
- `references/DOCUMENT_INGESTION_ADAPTERS.md`: local DOCX/PDF extraction and explicit OCR/table/equation/diagram limits.
- `schemas/document_ingestion.schema.json`: source-hashed document extraction manifest.
- `schemas/diagram_annotation.schema.json`: evidence-linked diagram graph annotation contract.
- `schemas/ocr_candidates.schema.json`: review-required local OCR text and pixel boxes.
- `../../docs/P5B4_DIAGRAM_CANDIDATE_EXTRACTION_CONTRACT.md`: conservative P5-B4 plan for provenance-bound OCR/diagram candidates and acceptance gates.
- `../../docs/DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md`: reusable cross-platform Python/optional-dependency and CI lessons.
- `templates/`: episode intake, batch manifest and human review queue.
- `schemas/simulation_run_receipt.schema.json`: separate local simulation evidence intake, not an L1 task or SFT record.

## Required repository contracts

Use these existing contracts from the DGSI repository at the same revision:
- `resources/source_fact_card.schema.json`
- `resources/diagnostic_case.schema.json`
- `resources/l1_task_packet.schema.json`
- `resources/diagnostic_sft.schema.json`

The current L1 schema supports `REAL_CASE_CANDIDATE` and `LITERATURE_DERIVED_SYNTHETIC`. `DESIGN_DERIVED_HYPOTHETICAL` candidates use the separate `schemas/design_derived_batch.schema.json` contract. Simulation evidence can now use the separate run-receipt intake described below, but formal L1 simulation task representation and SFT release remain unimplemented. Do not misclassify simulation data as real flight or literature records.

## Simulation run receipt intake

Read `references/SIMULATION_RUN_RECEIPT.md` before using run materials. It supplements the main Skill's intake guidance; it does not remove its source review, truth separation or release requirements. The main Skill distinguishes the local simulation evidence receipt from formal L1 task admission: the receipt verifies declared metadata and local bytes but does not create an L1 simulation task, certify engine-native provenance or authorize SFT.

```text
python scripts/create_simulation_receipt_fixture.py --output local_fixture --case unknown-physics
python scripts/audit_simulation_run_receipt.py --receipt local_fixture/receipt.json --artifact-root local_fixture
```

The example is explicitly SYNTHETIC_TEST_ONLY; no simulator/ML execution is claimed. The CLI requires a private local artifact root and prints aggregate-only results. Python API metadata-only mode never claims files were verified. Six evidence stages retain independent YES/NO/UNKNOWN states. Hash checks do not establish physical validity, source authenticity or independent human approval.

A standalone engineering subset can be built with `python scripts/package_simulation_receipt_module.py`; it is not the complete DGSI toolkit. Its Chinese guide, fixtures and tests can run without a repository checkout after installing the declared JSON Schema dependency.

## Quick start with another AI

1. Give the AI this entire folder, not only the main Skill file.
2. Provide authorized and de-identified design/test reports and selected run logs.
3. Do **not** provide the hidden truth/QA folder to the generation AI.
4. Start with `INGEST` using Prompt A in `references/AI_HANDOFF_PROMPTS.md`.
5. Review the source inventory and L0 facts before allowing `GENERATE`.
6. Run an independent `AUDIT` using Prompt C.
7. Return only review-queue-ready candidates for human adjudication.

## Current capability boundary

This toolkit is not yet a fully automated universal document parser, simulator adapter, authenticated review system or SFT exporter. The existing Basilisk R84-R3A receipt adapter is specific to its pinned artifact contract and does not automatically validate arbitrary simulation packages. The new generic receipt utility checks declarations and local bytes; it does not certify native simulator provenance or arbitrary log semantics.

Candidate generation does not mean Gold approval or training authorization. No sample is training-ready until source rights/privacy, scientific validity, independent domain review, lineage and official split admission are complete.

See `references/DIAGRAM_ANNOTATION.md` for the manual-first node/port/edge workflow. Image extraction and graph interpretation are separate; no AI-proposed edge is considered physically verified.

Optional local OCR command: `python scripts/ocr_dgsi_image.py --image <image> --asset-id <id> --output <record.json>`. It requires separately installed Tesseract, Pillow and pytesseract. OCR output remains review-required and does not infer diagram topology.
