# P3: historical memory is not current-event truth; verify as-of availability

## Audited upstream interface

In clonetimer/AstroGraph-LLM, src/astrograph/integrations/material_case_memory.py provides a confirmed-memory retrieval method (retrieve_confirmed). Its hit fields include case_id, verified_fault_id, proposed_fault_id, reviewer, truth_source_ref, equipment_scope, snapshot, source_group_id, relation_status, status=CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH, diagnostic_vote_allowed=false. It explicitly excludes the current source-group and enforces equipment scope.

However, the confirmed-memory storage contains available_at and verified_at timestamps while the retrieval hit currently **does not return them**. Retrieval bounds availability against current wall-clock time, not a DGSI SFT case's historical analysis_cutoff. Consequently a historical memory confirmed later could be supplied as if it was known at the earlier diagnostic decision time: **future-information leakage**.

## Implemented DGSI fail-closed guard

The new function in src/dgsi/history_temporal_gate.py accepts an external hit and an explicit analysis_cutoff, current incident family, and equipment scope. It rejects:

- missing, naive or post-cutoff available_at and verified_at;
- availability earlier than expert verification;
- reuse of a case from the *same incident family*;
- cross-equipment history transfer;
- any historical record claiming a current diagnostic vote or lacking the exact historical-not-current-truth status;
- inconsistent prior ML misclassification flags, missing independent truth-source reference, or invalid memory snapshot metadata.

Only a verified pre-cutoff history hit can return PASS_TEMPORAL_METADATA_ONLY, which still **does not** authenticate any source document or establish permission, expert independence, Gold review or training eligibility. The function never returns case IDs, memory bodies or truth-source text.

**Upstream compatibility finding:** unmodified AstroGraph retrieval hits omit both timestamps and therefore correctly remain BLOCKED. No DGSI code forges a date or assumes that a present-day approved memory was available at the historical cutoff. To enable a real-case workflow, an authorized AstroGraph source custodian must provide the timestamp fields from verified memory decision records or extend the upstream retrieval contract with them; this change must be reviewed separately.

## SFT boundaries

Historical confirmed fault IDs establish **prior-case outcomes**, not confirmation of the current fault source; a prior upstream misclassification must remain visible. Where a historical case is unconfirmed, it remains UNRESOLVED or UNKNOWN. No raw telemetry, synthetic Gold or restricted record may enter public fixtures. The 16 new tests are SYNTHETIC-only and demonstrate temporal leak rejection, cross-scope/family rejection and the metadata-only acceptance limit.

CI: both mandatory Ubuntu and Windows validation jobs must pass. This change is a small Draft PR stacked on the source-admission gate; main remains unchanged.
