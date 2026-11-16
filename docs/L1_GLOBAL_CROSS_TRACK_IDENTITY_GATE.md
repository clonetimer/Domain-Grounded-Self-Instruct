# P4: Global Case / diagnosis run cross-track isolation

## Threat model

A literature-derived synthetic task and a real-case candidate may refer to
the same source event family, but must never silently share a diagnostic
`case_id` or an upstream `diagnosis_run_ref`. Reusing either identity
would permit synthetic ML evidence or diagnostic logs to be misrepresented as
a real upstream execution. Event-family equality is not evidence of track
equivalence.

## Contract

The read-only cross-collection preflight now binds Case IDs and diagnosis-run
references to the L1 packet's `track`. Cross-track reuse fails with a
payload-free error code:

- `GLOBAL_CASE_ID_CROSSES_TRACKS`
- `GLOBAL_DIAGNOSIS_RUN_CROSSES_TRACKS`

Different IDs in the two tracks remain permitted for tasks based on the
same event family; the event family still controls any hypothetical split
leakage checks. These checks apply before formal splits and are independent
of the case's target or historical Context. This is *identity consistency*,
not proof of source authenticity, license, reviewer identity, actual ML run,
or authorization to train.

## Reproduction

```bash
PYTHONPATH=src python -m unittest tests.test_l1_global_track_identity -v
PYTHONPATH=src python -m unittest discover -s tests -v
```

Five `SYNTHETIC_TEST_ONLY` fixtures exercise independent dual-track
identifiers, reuse of Case IDs, reuse of run refs, and reversed batch order.
No private data or genuine expert reviews are present.

## Release boundary

This branch adds no training serializer and does not alter the existing
fail-closed `require_l1_sft_release()` policy. The literature-derived L1
pilot stays `REVIEW_REQUIRED`, with no real Gold, no official split,
and `training_authorized=false`.
