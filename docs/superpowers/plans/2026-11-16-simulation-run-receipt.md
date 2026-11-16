# Simulation Run Receipt Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: use superpowers:executing-plans; implement task-by-task.

**Goal:** Deliver a local-only receipt validation tool, tests and portable engineering module.
**Architecture:** Separate receipt schema, independently testable validator, small CLI and synthetic fixture builder. Full existing L1 behavior remains unchanged.
**Tech Stack:** Python 3.11+; jsonschema >=4.22,<5; unittest.
**Spec:** docs/superpowers/specs/2026-11-16-simulation-run-receipt-design.md

## Global Constraints
No source/QA payload printed, no real-log fabrication, no auto SFT release. Work on new branch based on PR #75. Original document and extracted user content not included in new commits or portable package.

## Review Focus
Windows-style unsafe paths; UNKNOWN versus NO; late evidence; QA-to-visible aliasing; detached ZIP execution.

### Task 1 — Contract and validation
- [x] Add failing tests for six stages, references, timestamps, replay and authorization.
- [x] Implement schema and `validate_simulation_run_receipt(receipt, artifact_root=None)`.
- [x] Verify metadata-only mode explicitly reports that bytes were not checked.

### Task 2 — Files and CLI
- [x] Add failing tests for file hashes, bounded JSON reading, duplicate keys, symlinks, hidden labels and CLI payload-free errors.
- [x] Implement root-scoped local reads, byte verification and CLI.
- [x] Test negative/unknown outcomes and actual-run versus fixture boundary.

### Task 3 — Portable handoff
- [x] Add a synthetic fixture builder and standalone ZIP builder, then test detached extraction and command execution.
- [x] Update full-toolkit allowlist for new CLI/fixture builder; document scientific limits in a Chinese guide.
- [x] Run focused local suite (36 tests).
- [ ] Inspect exact-head remote CI before claiming full inherited regression.

## Review record
No independent model reviewer was available in this execution. Manual code review and failing-before-fix regressions found and repaired error-code masking for a symlink root and a missing package initializer in the detached ZIP. Cross-provider behavioral evaluation remains NOT_RUN.
