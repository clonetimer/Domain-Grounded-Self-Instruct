# DGSI product closeout plan

**Decision:** close out the current Skill as a reusable, tested candidate-generation and data-curation product. Treat development case collections as an Evaluation Suite, not a formal SFT dataset or a product-release blocker.

## Product boundary

- **Product:** DGSI Skill/toolkit — instructions, schemas, L0/L1 workflows, evidence and context handling, validation, review handoff and export guidance.
- **Evaluation Suite:** the 21 literature-derived tasks, five user-provided L0 case facts, AAS RUN-03F and other fixtures. Their purpose is to test Skill behavior, coverage and failure modes. They are not automatically Gold or training data.
- **Formal SFT dataset:** a separate future application outcome. It requires its own source permission, human adjudication, split and release decisions; its absence does not block Skill closeout.

## Five closeout deliverables

1. **Portable Skill package** — install/use instructions, version, dependency boundary, reproducible archive and SHA-256 manifest.
2. **Evaluation Suite** — frozen, versioned test cases with source/track labels, expected behaviors, known limitations and explicit separation of test-only fixtures from trainable data.
3. **Skill effectiveness report** — measured task coverage, evidence fidelity, causal calibration, uncertainty/abstention, action-state fidelity, history safety, schema validity, critical failures, cost and yield. Separate automated checks, AI advisory and human review.
4. **User/developer handoff** — operator guide, known limitations, development lessons and exact clean-environment commands.
5. **SOTA data-construction comparison** — compare DGSI against Self-Instruct, Evol-Instruct/WizardLM and a clearly labelled Magpie-style adaptation under matched source/model/token budgets. First compare candidate-data quality; run downstream SFT only if a separate authorized training cohort and untouched event-family holdout exist. Follow docs/DGSI_SOTA_DATA_CONSTRUCTION_COMPARISON.md.

## Closeout acceptance

- All five deliverables have concrete files and reproducible evidence.
- Skill package installs and runs independently from a clean environment.
- Evaluation cases are correctly labelled; no test fixture is promoted to formal training data.
- Effectiveness report distinguishes observed results from planned or unavailable evaluations.
- Comparison protocol and results are reported honestly; an unrun downstream SFT arm is explicitly NOT RUN, not simulated.
- No further tooling expansion unless an actual closeout blocker is demonstrated.

## Explicit non-blockers

The following do not block shipping the Skill product: completion of the 21-task human expert review; rights clearance for every evaluation-only source beyond the permission required to distribute the Skill itself; completion of the five REAL L1 cases; creation of a Gold SFT dataset; or a downstream fine-tuning run. They remain separate evaluation or future dataset work. Any redistributed source content still requires appropriate rights; keep restricted source text out of the public package.

## Current evidence snapshot

At plan creation, main contains a portable toolkit line (0.2.0-rc.4), a 21-task literature-derived synthetic review cohort, five user-provided L0 case facts and an AAS RUN-03F SYNTHETIC_TEST_ONLY integration demonstration. These demonstrate implementation and evaluation fixtures, not a completed SOTA comparison or approved SFT corpus. Recheck main and release artifacts before declaring final product release.
