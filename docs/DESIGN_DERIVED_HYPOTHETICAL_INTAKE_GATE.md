# Design-derived hypothetical intake: fail-closed boundary (P4)

This is a **non-SFT intake** contract for design-document facts and imagined diagnostic questions. It is not the `LITERATURE_DERIVED_SYNTHETIC` L1 track or the `REAL_GOLD_TRACK`.

## Validating locally

```bash
python -m pytest -q tests/test_design_report_0918_pilot.py tests/test_design_derived_intake_gate.py tests/test_portable_toolkit_package_build.py
```

`validate_design_derived_batch(batch, expected_source_sha256=...)` checks the dedicated Draft 2020-12 schema, candidate/fact IDs, declared counts, source-fact binding, and the optional **independently computed** source SHA-256. A claimed hash by itself does not establish permission, originality, identity of the real-world event, or measured validity.

Every `model_visible_input` now carries `evidence_status=HYPOTHETICAL_NOT_OBSERVED` and admits only design platform context, a task request, and cited design-fact IDs. Hidden truth, curator internal review, real run references and ML scores are not accepted as input keys. All six examples retain `INCOMPLETE_EVIDENCE`, a null fault source, and no inferred completed disposal.

The validator returns fixed-code failures and a **metadata-only**, `NON_SFT_INTAKE_ONLY` report. It never renders a prompt/target pair, emits SFT records, converts design declarations to observed events, upgrades a candidate to Gold, assigns official train/validation/test splits, or authorizes training.

## Scope and unresolved gates

The design-source fingerprint is checked against the authorized original bytes *outside* the public repository. The original file and any private review findings are not packaged or committed. The portable ZIP builder only includes allowlisted source/docs/schemas; an executable smoke test verifies the ZIP manifest and every entry digest.

The current 0918 pilot has 20 design declarations, six hypothetical candidates, no observed fault episodes, no verified fault-injection executions, no simulator run logs, and no upstream ML result bundles. It cannot be used as evidence of diagnostic effectiveness. Actual simulation-case admission requires a separately reviewed run-receipt contract and upstream-diagnosis alignment; eventual SFT release requires independent source/IP/privacy and human review authorization.
