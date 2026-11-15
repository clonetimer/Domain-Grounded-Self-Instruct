# P4: global L1 lineage and cross-collection holdout preflight

**Scope: read-only, metadata-only, SYNTHETIC_TEST_ONLY adversarial fixtures.**
This is not a source review, expert adjudication, Gold declaration, data split
approval, nor authorization to train a model.

## Defect class

Prior L1 checks are collection-scoped. Separate exports can reuse an identical
task ID, carry divergent versions of an L0 fact card, allocate the same event
family to different splits, or retrieve a target from another collection as
historical Context. The previous within-collection holdout gate cannot detect
all cross-collection repetitions.

## Implemented API

`dgsi.l1_global_lineage.audit_l1_cross_collection_lineage(batches, hypothetical_splits=None, reviewed_aliases=None)`

Every batch is `{"collection": <L1 collection>, "source_fact_cards": [<L0 facts>]}`.
The function invokes existing L1 collection validation on *every batch first*;
it never trusts standalone lineage labels as adequate evidence. It then rejects:

- Duplicate collection/task IDs across batches.
- A source card ID reused with different immutable JSON content (SHA-256).
- Reused event-family targets assigned to different splits in separate batches.
- Historical Context exposing another split's target in a different collection.
- A claimed event-family alias without L0 citations covering **both** families,
  an undecided review flag, contradictory mappings, or chained/cyclic aliases.
- A historical case that resolves to the current event through an explicitly
  declared identity alias, even if source-group strings are different.

A hypothetical split mapping is accepted **only as an offline test plan** and
does not alter collections or bypass their independent-review admission gates.
Current pilot packets remain unassigned. Official assignments still require
the original L1 validator to accept expert-reviewed inputs.

## Boundaries

The source-card consistency digest deliberately covers the *complete* card.
A later authorized review update must be versioned consistently across
snapshots rather than silently mixed into old exports.

The module does not infer aliases from matching spacecraft names, matching
failure vocabulary, similar reports or textual embeddings. Alias declarations
must name two actually present L0 event families and cite L0 cards for both,
but `DOMAIN_EXPERT_CONFIRMED` is **an asserted metadata field, not authenticated
reviewer identity**. Source permission, evidence truth, signed review receipts,
and trusted global alias adjudication remain separate prerequisites. Cross-
collection checks cannot discover an unknown or deliberately concealed
duplicate event family without independent source adjudication.

No raw telemetry is an LLM input. Synthetic ML scores and logs are not real
spaceflight records. The return value always sets `training_authorized=false`,
`gold_eligible_count=0`; `STRUCTURAL_PREFLIGHT_ONLY` must not be interpreted
as a validated experimental split.

## Replay

```bash
python -m unittest tests.test_l1_global_lineage -v
python -m unittest discover -s tests -v
```

Mandatory Ubuntu and Windows validation must both succeed on the same latest
PR head before this code stage is accepted. No mainline merge or model fine-
tuning is requested here.

## Next source-review action

Review actual alias/episode identity and case-source versions offline, then
bind any accepted identity decisions to verifiable expert receipts. Do not put
private case files, reviewer identities, R21 telemetry, operations logs or
credentials in the public DGSI repository.
