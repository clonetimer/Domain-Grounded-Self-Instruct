# DGSI C2 Current Expert Intake Implementation Plan

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans as appropriate. Track completion in the sibling progress.md.

**Goal:** Close the A/B form return path and reconcile the complete verified toolkit into main without losing existing material.

**Architecture:** A small adapter regenerates current handoffs, checks immutable envelopes and partial input domains, and delegates complete pairs to the single existing rubric. A CLI separates aggregate stdout from optional private queue output. Source integration preserves both remote histories.

**Tech Stack:** Existing Python 3.11+ stdlib, existing jsonschema runtime, unittest, GitHub CI.

**Spec:** ../specs/2026-11-18-current-expert-intake-design.md

## Global Constraints

- Never fabricate expert reviews, identities, rights clearance, official splits or SFT authorization.
- Only scorecard fields in the existing A/B handoff may change.
- Current L0/L1 inputs are independently supplied; don't trust a submitted manifest as current.
- Reuse the existing complete-pair ten-dimension rubric; partial input is not rubric validated.
- CLI errors and stdout must not expose reviewer payload, scores, task IDs or filesystem paths.
- No new dependency. Preserve old RC2 and reviewer artifacts. No remote force pushes.

## Review Focus

- Old forms internally agree after cohort/L0 mutation: reject against regenerated current inputs.
- Malformed or partially filled single scorecard: reject invalid shapes/types; otherwise report missing completion without fabricated scores.
- Global A/B token swapping, duplicate task rows or bool-as-int values: reject rather than counting apparent independence or coverage.
- Private scores/tokens hidden in errors or invalid JSON: fixed output codes and no partial output file.
- Existing output, symlink or racing writer: fail atomically without truncating another file.

## Task 1: Current-bound expert intake adapter and CLI

Files: create src/dgsi/l1_c2_expert_intake.py, scripts/audit_l1_c2_current_expert_intake.py, tests/test_l1_c2_expert_intake.py, tests/test_l1_c2_expert_intake_cli.py.

Interface: audit_c2_expert_intake_against_current_sources(reviewer_a, reviewer_b, current_l1_collection, current_l0_fact_cards) -> dict containing aggregate fields plus task_queue. Fixed-code C2ExpertIntakeError. CLI --reviewer-a, --reviewer-b, --current-collection, --current-l0-facts, optional --output-file.

- [ ] Write and run failing tests for blank, partial, complete, revise/reject, disagreements, stale sources/cohort, metadata mutation, missing/duplicate/unknown task, reordered rows, invalid scores/tokens and no leaked private payload.
- [ ] Implement the adapter and CLI without changing the rubric; verify focused tests and neighboring review suites.
- [ ] Test actual subprocess input/errors/no-clobber and duplicate JSON keys, not source-text matching.
- [ ] Produce a bounded patch and concise evidence for independent review.

## Task 2: Main reconciliation, operator workflow and portable artifact

Files: README.md; retained docs/P5C2_SPECIALIZED_TASK_REVIEW_2026-11-17.md; docs/P5C2_CURRENT_EXPERT_INTAKE_20261118.md; docs/P5C2_MAIN_RECONCILIATION_20261118.md; docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md; scripts/package_dgsi_simulation_to_sft.py; .github/workflows/package-p5c2.yml; skills/dgsi-simulation-to-sft/{VERSION,TOOLKIT_MANIFEST.json,references/OPERATOR_QUICKSTART.md}; tests/test_portable_toolkit_package_build.py.

Consumes Task 1 interface and paths. Produces RC3 portable package, source reconciliation and operator instructions.

- [ ] Preserve main-only historical document, annotate superseded paths, update current README entrypoint and command examples.
- [ ] Add failing extracted-toolkit smoke assertion for the new CLI with actual external blank forms; add CLI/tests/docs allowlist and RC3 metadata.
- [ ] Run relevant tests and full source test suite once complete; independent reviewer reads actual diff and tests.
- [ ] Create remote feature commit with both pinned parents; verify resulting tree against all unchanged baseline blobs and intended changed/new files.
- [ ] Open main-targeted PR; wait for current head Ubuntu/Windows/package CI; merge with expected head if green and live base unchanged.

## Task 3: Actual handoff status and recorded experience

- [ ] Run extracted RC3 intake on the delivered A/B blank forms and current authorized L0/L1 inputs; expected 15 pending tasks, 30 incomplete scorecards, 0 validated pairs.
- [ ] Record experience 107 onward based on findings, preserved merge evidence and tested behavior.
- [ ] Verify final archive manifests/hashes and save toolkit, actual pending status and delivery receipt; do not republish fictional test assessments.
- [ ] Report main integration state, actual operator next steps, fresh verification and explicit limits.
