# P4: historical Context must not expose another split's diagnostic target

Scope: **SYNTHETIC-only structural regression and offline collection audit**. No Gold admission or training permission.

## Defect

Existing L1 collection validation isolated the *current* target by its source event family. A packet could nevertheless refer to another packet's current target incident as a retrieved historical case, even when those packets were allocated to different train/validation/test splits. The historical retrieval cutoff and source-card matching gates do not replace holdout isolation.

Example: the FUSE scenario cites a public Cassini history card. If FUSE is assigned to validation and the Cassini incident is itself a current target in train, the validation prompt receives the conclusion associated with a training target family. The inverse split assignment has the same flaw. This is a **cross-split exposure risk**, not evidence that either historical observation is false.

## Implemented gate

When (and only when) a collection supplies a complete split assignment:

1. Preserve the existing task ID, complete assignment and current-event family isolation checks.
2. Derive each target's event family from **validated L0 source cards**, never from user-written free-text context.
3. For every history_context item, compare its event_family_id against event families used as current diagnostic targets elsewhere in the collection.
4. If that prior family is itself a target of a *different* split, block with the stable payload-free code `L1_HISTORY_CONTEXT_REFERENCES_OTHER_SPLIT_TARGET`.
5. Keep the independent-expert-review prerequisite: even when the cross-split audit passes, the unreviewed 15-packet pilot cannot obtain official assignments. Do not weaken `L1_SPLIT_BEFORE_INDEPENDENT_REVIEW`.

Adversarial tests use the public literature-derived FUSE/Cassini fixtures plus invented SYNTHETIC histories. They cover both directions of contamination, unrelated families, complete/incomplete split assignments, same-family separation and the no-split pilot.

## Boundaries

The audit checks event-family **identity** within this one collection, not semantic aliases across datasets or previously exported training snapshots; these require a separate global lineage registry. A shared historical source that is not a target of the present collection is not rejected by this cross-split test, but remains subject to as-of, review status, equipment applicability, provenance and evidence-use gates. It does not guarantee publication rights, independent reviewer status or true historical correctness.

No private R21 telemetry, operational logs, restricted records, expert identities or paid models are used. Pilot remains REVIEW_REQUIRED, Gold=0, training_authorized=false, with no approved train/validation/test assignments.

## Verification

Run `python -m unittest tests.test_l1_history_cross_split_target_gate -v` or the existing full repository test suite. Ubuntu and Windows CI must pass for this PR's **exact latest head** before declaring acceptance.
