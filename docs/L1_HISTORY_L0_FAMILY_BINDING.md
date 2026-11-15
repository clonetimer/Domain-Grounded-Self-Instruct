# P4 historical hit → L0 event-family consistency gate

**Scope:** SYNTHETIC-only regression and metadata-level L1 validation; neither real-case verification nor Gold/training authorization.

## Defect addressed

The pre-existing gate required every retrieved historical hit to cite an explicit source reference. A malformed packet could still cite a *real, valid, unrelated* public literature L0 card while declaring a different historical event family. Self-consistent `hit_metadata.source_group_id` did not independently validate the true cited source event family. Separately, a current L0 event could be recycled as a prior if the L1 Case source group carried the `LITERATURE-DERIVED:` prefix but the history entry used the unprefixed family ID.

## Structural contract

In `validate_l1_task_packet`, after resolving the supplied L0 cards:

1. For every history hit, fail if `history_context.items[].event_family_id` equals the event family of any current `source_fact_refs` L0 card. A prefix on `case.provenance.source_group` is not a basis for claiming an independent prior.
2. For **each** public L0 card referenced by **each** history hit, require `source_card.event_family_id == history_hit.event_family_id`. Do not accept another valid public card as evidence of this specific prior.
3. Preserve explicit `SYNTHETIC-...` prior references as invented fixtures; their event identity cannot be independently verified through a public L0 fact card. Existing time, review-state, equipment and no-diagnostic-vote gates remain in force.
4. Return fixed error codes without exposing source content or case identifiers: `CURRENT_L0_EVENT_FAMILY_CANNOT_BE_HISTORY`, `HISTORY_HIT_L0_SOURCE_FAMILY_MISMATCH`.

Seven `SYNTHETIC_TEST_ONLY` tests exercise legitimate FUSE/Cassini context, a wrong TROPICS source cited as Cassini, extra unrelated public refs, a current event repackaged as history, fabricated internally consistent history metadata and synthetic rejected priors. The 15-packet pilot regression is included.

## Remaining limits

Matching two declared event-family strings is **not** proof of provenance, chronology, reviewer independence, publication rights, correct translation across spacecraft hardware, or applicability to the current ML result. Alias/deduplication reconciliation still requires independent source verification. The public repository must not receive private telemetry, operational logs, case identities, restricted expert notes or authentication data.

This gate does not change packet admission flags, source fact status, split assignment, gold eligibility or training authorization.
