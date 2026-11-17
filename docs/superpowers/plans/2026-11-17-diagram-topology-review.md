# B4.3c port and connection evidence review implementation plan

> **For agentic workers:** use superpowers:executing-plans; execute in this session.

**Goal:** Validate and import manually supplied port/connection proposals against an exact node-only graph, without converting local review metadata into engineering truth.

**Architecture:** Reuse `validate_diagram_annotation` and the existing graph v1. A separate topology receipt binds the canonical graph digest, source/asset identity, declared image geometry, and per-field evidence. Audit returns aggregate counts; explicit import emits a fresh proposed graph. No KG/SFT schema change.

**Tech Stack:** Python standard library + existing jsonschema dependency.

**Spec:** B4.3c continuation of the approved manual-first diagram evidence pipeline; this document records implementation choices.

## Global constraints
- Preserve PARALLEL tracks, history as CONTEXT, no raw telemetry or private source assets.
- Keep new objects AI_PROPOSED or UNRESOLVED; never HUMAN_CONFIRMED, Gold or training-authorized.
- Parent node graph must be unchanged and node-only; no silent merge or overwrite.
- Independently bind connector existence, direction, relation, port label, medium and unit evidence.
- Receipt metadata is not authenticated inspection; declared dimensions are not verified image pixels.

## Approaches
Automatic arrow recognition is deferred because source accuracy is unmeasured. Extending the generic graph schema would affect existing consumers. Use a separate versioned receipt plus the unchanged graph validator.

## Review focus
Cross-object evidence reuse; UNKNOWN direction misread as flow; hidden timestamp validator dependencies; malformed/duplicate JSON and source-text leakage; unintended overwrite/partial output.

## Tasks
- [x] Pin inherited validator/schema bytes by Git blob SHA. The new tests execute the inherited graph validator; full inherited test discovery requires remote CI because this runtime cannot clone the repo.
- [x] Write topology tests first; observe missing-feature failure. Implement strict schema, identity/evidence checks, explicit-offset time validation, deterministic import.
- [x] Write CLI subprocess tests first; implement bounded strict JSON input, aggregate-only stdout and exclusive output creation.
- [x] Integrate portable package and docs; 43 feature/CLI tests and compile check pass. The same 43 tests pass from a detached minimal source bundle. The full-toolkit integration test is added for remote execution, not claimed locally.
- [ ] Commit one coherent feature delta on the pinned remote base, create Draft PR, verify exact-head remote CI and new test signatures. Do not merge main.

## Execution ledger
Base: fc0f8152057c1ded256084d216d66b041de7b70f (PR #107). Remote push workflow 44011424508 SUCCESS on both platforms. PR #108 is an independent P4 track; do not overwrite or claim it integrated.
Local clone blocked by container DNS. Use an isolated source subset with hash-verified inherited files; report local subset counts separately from full remote CI.

Self-review: no independent reviewer tool is available in this session. Checked schema/runtime fields, canonical hashes, evidence scope, unknown-direction handling, CLI writes and package contents. No full-repository local claim.
