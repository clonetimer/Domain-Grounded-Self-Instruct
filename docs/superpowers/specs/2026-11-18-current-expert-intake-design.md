# DGSI C2 current expert intake and main reconciliation

## Intent

Continue the already authorized integrated DGSI work: make the previously delivered independent A/B reviewer forms usable on return, preserve the complete source history when reconciling main, record new development lessons, and issue a matching portable toolkit. This continues the existing Python/stdlib architecture and current ten-dimension rubric.

## Decisions

The intake is a new adapter over the existing handoff builder and scored-review validator. Rewriting the rubric would create a competing admission rule; accepting a caller-supplied manifest alone would leave stale-cohort risk. Regenerating both blank forms from independent current L0/L1 inputs closes that boundary. This design was chosen by the implementer under the user's instruction to continue, using the existing project's constraints.

Accept the original handoff schema unchanged. Only each task's scorecard is editable. Preserve all header and task metadata, including the original blank-template status strings; the new report describes completion. Task order may vary but task membership must match exactly. Reject extra, unknown, missing or duplicate tasks and altered immutable metadata. Use type-sensitive canonical JSON comparison, not Python equality that conflates false and zero.

Blank and partially completed scorecards are useful inputs: validate exact field/key shape and present values, report PENDING_REVIEW_COMPLETION, and do not claim rubric validation. Completed pairs must call the existing validate_blind_l1_review and audit_c2_scored_review. No fabricated counterpart or default score is allowed. Normalize reviewer tokens with strip for identity comparisons only; all present tokens within one form must identify the same declared reviewer, and A and B must differ. This does not authenticate human identity or independence.

The private report contains task IDs, source/cohort/packet fingerprints, fixed pending states, counts and fixed next-action/reason codes. Never return reviewer tokens, scores, finding-code payloads, free text or copied input. CLI stdout contains aggregate counts and fixed error codes only. An optional --output-file writes the task queue atomically without overwriting an existing file or symlink. Invalid input produces no output file. Empty/partial reviews may succeed as intake with zero completed pairs. All output states keep identity, science/rights adjudication, Gold, split and training authorization false/zero.

Keep reviewer kits already issued for this unchanged candidate valid; do not regenerate or score them. Run the new intake on the actual previously delivered blank JSONs and produce an honestly pending status artifact. Fictional complete reviews exist only in SYNTHETIC_TEST_ONLY tests and are never delivered as expert evidence.

## Integration

Pinned baseline: integration b20b498b6aba84e25845505c201ef9305175eb16 (354 files); main 0e064ae5289a4cacc4b28dcb038c3843267bab2d (4 files). Preserve the main-only specialized-task review document, adding a dated historical note pointing to the current 15-task candidate. Preserve the integrated preview script. No deletions. Use both real remote parents in the reconciliation commit and a feature PR to main, with fresh Ubuntu/Windows and package CI before merging. Recheck live refs before any update. Do not modify branch protection or force-update a moved ref.

## Delivery

Toolkit version 0.2.0-rc.3 preserves RC2 bytes. Include the new module, CLI, tests and operator instructions in the package. Verify extracted CLI behavior using external inputs without repository PYTHONPATH. Record lessons starting at 107 and final commit/tree/CI/artifact hashes in the delivery receipt. The 15 candidates, 9 event families, 12 referenced L0 cards and 7 source documents remain review-only with no actual expert returns.
