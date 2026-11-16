# DGSI Simulation-to-SFT Toolkit

Portable production Skill for converting authorized spacecraft simulation and engineering materials into evidence-grounded fault-diagnosis instruction-tuning candidates.

## Contents

- `SKILL.md`: primary portable Skill entry point.
- `references/`: ingestion, truth separation, task design, audit and provider-neutral delegation procedures.
- `templates/`: episode intake, batch manifest and human review queue.

## Required repository contracts

Use these existing contracts from the DGSI repository at the same revision:
- `resources/source_fact_card.schema.json`
- `resources/diagnostic_case.schema.json`
- `resources/l1_task_packet.schema.json`
- `resources/diagnostic_sft.schema.json`

The current L1 schema supports `REAL_CASE_CANDIDATE` and `LITERATURE_DERIVED_SYNTHETIC`. `DESIGN_DERIVED_HYPOTHETICAL` candidates use the separate `schemas/design_derived_batch.schema.json` contract. `SIMULATION_CASE_CANDIDATE` still needs a separately reviewed run-receipt schema extension; do not misclassify it.

## Quick start with another AI

1. Give the AI this entire folder, not only the main Skill file.
2. Provide authorized and de-identified design/test reports and selected run logs.
3. Do **not** provide the hidden truth/QA folder to the generation AI.
4. Start with `INGEST` using Prompt A in `references/AI_HANDOFF_PROMPTS.md`.
5. Review the source inventory and L0 facts before allowing `GENERATE`.
6. Run an independent `AUDIT` using Prompt C.
7. Return only review-queue-ready candidates for human adjudication.

## Current capability boundary

This toolkit defines a portable workflow and output contract. It is not yet a fully automated universal document parser, simulator adapter, authenticated review system or SFT exporter. The existing Basilisk R84-R3A receipt adapter is specific to its pinned artifact contract and does not automatically validate arbitrary simulation packages.

Candidate generation does not mean Gold approval or training authorization. No sample is training-ready until source rights/privacy, scientific validity, independent domain review, lineage and official split admission are complete.
