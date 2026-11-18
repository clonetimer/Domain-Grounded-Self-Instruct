# P4 — Reused L1 Case IDs bind source artifact receipts

## Failure mode

A same-event-family Case ID could be reused with an unchanged current ML result,
diagnostic log, configuration and analysis cutoff, while the
`provenance.source_artifact_hashes` list was silently replaced. The prior
global current-event fingerprint covered `diagnosis_run_refs` but not the
SHA-256 source receipts. This could conceal a changed source artifact behind
a familiar Case ID even when the visible input remained identical.

## Rule

The read-only cross-collection preflight now includes the sorted
`source_artifact_hashes` in the immutable Case evidence fingerprint.
A mismatch raises `GLOBAL_CASE_ID_EVIDENCE_SNAPSHOT_CONFLICT`.
The existing L1 local schema still validates SHA-256 syntax. The global
comparison does not verify artifact bytes, authorization, IP rights, domain
review or training readiness. Historical Context retrieval references and
task-specific formal targets remain outside the current-event fingerprint,
because controlled Context ablations may legitimately vary.

The audit returns metadata only and preserves
`gold_eligible_count=0` and `training_authorized=false`.
It does not write training splits, export SFT, auto-promote Gold or
introduce simulated run/log material into a real-data track.

## Reproducible synthetic regressions

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_global_case_run_family.py' -v
```

Tests include a **SYNTHETIC_TEST_ONLY** source-digest swap and a
same-Case reuse with identical fixture receipts. Fixture hashes do not
represent real engineering artifacts or authentic ML run records.

## Remaining boundary

The global preflight is not yet mandatory at a production L1→SFT
serialization path. Full export admission must also require independent
expert-reviewed source permissions, review receipts bound to immutable
task/source hashes, verified as-of historical Context, track-aware split
isolation and explicit training authorization. This PR does not create an
exporter or bypass those conditions.
