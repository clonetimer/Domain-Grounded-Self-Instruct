# P4 — Reused diagnosis-run references bind mission/configuration context

## Failure mode

The global L1 audit already treats a reused `diagnosis_run_ref` as one ML result and
one diagnostic log snapshot. Two *different Case IDs* in the same L0 event
family could nevertheless reuse that run identifier with different spacecraft
configuration or mission operating context. This would reattribute the same
upstream result to an incompatible scenario without changing its provenance ID.

## Fail-closed rule

For each run reference, fingerprint the canonical JSON containing only
`case.input.spacecraft_context` and `case.input.operational_context`.
If the same run reference has a different fingerprint anywhere in a
multi-collection preflight, raise the stable, payload-free code
`GLOBAL_DIAGNOSIS_RUN_CONTEXT_SNAPSHOT_CONFLICT`.

This check is independent of Case ID, collection, split and batch ordering.
It does not include current task's formal target, internal curator review or
retrieved historical Context. Case-level analysis cutoff remains covered by
the pre-existing Case-ID evidence snapshot gate; it is *not* frozen at run
scope so independently justified as-of task horizons are not accidentally
conflated with ML run identity.

If an upstream run is genuinely recomputed for a different mission context,
it needs a separate, traceable run reference (or an explicitly versioned
upstream protocol). This is a local consistency test, **not proof** that a
claimed ML run occurred.

## Replay

```bash
PYTHONPATH=src python -m unittest tests.test_l1_global_run_context_snapshot -v
PYTHONPATH=src python -m unittest discover -s tests -v
```

Five adversarial tests use only `SYNTHETIC_TEST_ONLY` cases: positive
same-run consistency, altered hardware configuration, altered operating
history, reverse order, and a separate-run control. There are no real run
identifiers, operational logs or expert approvals in these fixtures.

## Admission boundary

This gate does not inspect raw telemetry or infer calibrated probabilities.
The existing 15 literature-derived L1 pilot tasks remain
`REVIEW_REQUIRED`, with zero real Gold, no approved official split, and
`training_authorized=false`. The SFT-release guard stays fail-closed
pending independent expert review, trusted source/IP/privacy admission and
explicit release authorization.
