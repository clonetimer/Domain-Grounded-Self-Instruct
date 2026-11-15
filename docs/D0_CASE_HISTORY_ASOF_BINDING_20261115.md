# D0: bind cited history to an as-of memory snapshot (2026-11-15)

## Scope

DGSI is an SFT **second-stage diagnostic synthesis** dataset built from upstream
ML diagnosis results, diagnostic logs, mission/configuration context and
previously available history. Raw telemetry remains upstream of the LLM.
Historical memory describes a **prior** incident; it never votes to confirm
the current incident's root cause.

## Source inspection

Inspected `clonetimer/AstroGraph-LLM`:
`src/astrograph/integrations/material_case_memory.py`. The confirmed table
holds `available_at`, the confirmation body holds `verified_at`, and
`retrieve_confirmed()` filters against **current wall clock**, while
its returned hit omits both times. This cannot prove that the hit was available
at an earlier DGSI `analysis_cutoff`. Do not infer or synthesize timestamps.

Existing `history_temporal_gate.py` screens individual enriched hits but was
not bound to the historical references actually included in a Case prompt.

## This change

`src/dgsi/case_history_asof.py` combines the real Case's cited
`historical_cases[].case_ref`, current source group, cutoff and configured
component with explicitly supplied history hit metadata:

- A Case-labeled CONFIRMED history must have exactly one matching hit with
  pre-cutoff verification/availability and the correct incident and scope.
- Extra or duplicate history hits, missing hit metadata, a future confirmation,
  same-incident reuse or cross-equipment transfer block the audit.
- UNRESOLVED, REJECTED, UNKNOWN and PARTIALLY_CONFIRMED histories are **not**
  silently promoted by a supplied confirmed-memory hit. Without a hit they
  remain qualified references requiring manual review, not Gold.
- No inferred case identity, diagnosis outcome or current root-cause vote.
- All output is aggregate counts and fixed reason codes with no IDs/paths,
  memory text, source references or target answers.

The read-only local CLI is:

```sh
python scripts/audit_case_history_asof.py \
  --case /authorized/local/case.json \
  --history-hits /authorized/local/enriched_hits.json \
  --equipment-scope reaction_wheel_2
```

The paths are examples only; restricted files must remain local and authorized.
The tool reads JSON but does not modify it or upload anything. Each hit's
`available_at` and `verified_at` must come from authenticated upstream
records; the current raw AstroGraph retrieval output remains BLOCKED.

## Gate semantics

`PASS_ASOF_METADATA_ONLY` verifies internal claim consistency and timestamp
ordering, **not** authenticity of the source, historical reviewer independence,
rights, current root cause, split integrity, Gold approval or training consent.
`MANUAL_HISTORY_REVIEW` is nonzero/hold. `BLOCKED` is nonzero/reject.
`NO_HISTORY_REFERENCES` only means that no historical citation was supplied.
Independent source and expert verification remain mandatory.

Synthetic fixture tests are adversarial boundary tests only. No REAL_FLIGHT
claim, expert Gold, R21 telemetry, restricted case or paid service is introduced.

## Next independent audits

1. Check authorized upstream run receipts and source hashes against the local
   pseudonymized Case; declarations alone do not establish provenance.
2. Perform existing cross-split history exposure and event-family audits.
3. Obtain 5–10 authorized/de-identified real diagnostic packets for independent
   specialist review before selecting 20 controlled SFT samples.
