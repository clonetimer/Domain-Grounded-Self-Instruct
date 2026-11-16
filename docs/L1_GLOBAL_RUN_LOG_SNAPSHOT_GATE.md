# P4: reused upstream diagnosis-run log snapshot binding

## Problem

The global L1 lineage audit already prevents an upstream `diagnosis_run_ref`
from being bound to different ML results, even across different Case IDs.
But a second Case within the same event family could reuse that run ID while
silently replacing diagnostic log content. Because diagnosis logs are a primary
part of the upstream material supplied to the LLM for secondary diagnosis,
this weakens run-level provenance.

## Additional fail-closed rule

For every run reference appearing in a cohort, compute a canonical JSON
SHA-256 fingerprint of `case.input.diagnostic_logs`. Reject inconsistent
fingerprints with the payload-free code
`GLOBAL_DIAGNOSIS_RUN_LOG_SNAPSHOT_CONFLICT`.

The check is independent of any official or hypothetical dataset split,
independent of Case ID, and symmetric under batch ordering. List order is
significant for diagnostic log sequences; JSON object key order is not.

A different upstream run reference may carry a different log snapshot.
Different prompts, targets, history Context or `internal_review` do not
change the fingerprint. This code does not inspect raw telemetry and does
not infer whether an ML score is calibrated.

## Test and admission boundary

`PYTHONPATH=src python -m unittest tests.test_l1_global_run_log_snapshot -v`

The test fixtures are all `SYNTHETIC_TEST_ONLY`. They do not represent
flight logs or actual ML runs. The existing 15-packet literature-derived
pilot remains `REVIEW_REQUIRED`. This structural gate cannot authenticate
expert review, source rights, de-identification, train/validation/test
assignments or release authorization. The L1-to-SFT guard remains
fail-closed, producing zero SFT records.

## Caveat

This contract deliberately treats a `diagnosis_run_ref` as identifying a
single documented diagnostic log snapshot. A future upstream adapter that
supports separately identifiable log revisions must assign explicit
versioned run/log references rather than silently replacing content while
reusing an existing identifier.
