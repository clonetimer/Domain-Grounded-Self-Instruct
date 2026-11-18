# P5-C3: document-connected holdout independence (2026-11-18)

## Scientific failure mode

An event-family split gate is necessary but insufficient. The current
15-task/9-event-family synthetic pilot contains **three TROPICS event families
from the same source publication**, and the FUSE historical-reuse task cites
a **Cassini source document** that also underpins current-target Cassini tasks.
Permitting different splits for these targets can leak underlying source
assertions or historical answers across the supposedly independent holdout.

## Implemented, review-only

`dgsi.l1_holdout_independence.audit_l1_holdout_independence` validates the
existing L1/L0 candidate and computes connected components over:

1. the current event family (including multi-episode task variants),
2. the unique identity of each bound publication, and
3. literature-bound retrieved history, connecting a consumer to current-target
   tasks that use the prior event family or publication.

The return value contains **only aggregate group sizes and counts**, no case
texts, source IDs, task IDs, review tokens, or proposed train/validation/test
assignments. `check_hypothetical_holdout_partition` is an adversarial helper,
not a splitter; even a structurally valid hypothetical partition remains
unapproved and cannot authorize any training or export.

For the current unchanged review candidate, the expected audit is **15 tasks,
9 event families, 7 distinct bound publications and only 6 document/history-
connected groups**, with task group sizes `[1,2,2,2,3,5]`. These numbers
are NOT additional real cases or scientifically independent expert-verified
samples.

## Reproducible structural test

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_holdout_independence.py' -v
```

The eight `SYNTHETIC_TEST_ONLY` cases challenge TROPICS publication reuse,
FUSE→Cassini historical cross-reference, two Lunar Orbiter episodes, document
identity drift, malformed hypothetical labels and incomplete assignments.

## Limitations and gates

This graph intentionally **over-connects** ambiguous literature references.
It does not discover uncited derivative studies, paraphrase overlap, citation
aliasing under different source IDs, hidden case duplicates or pretraining
exposure of a model. It does not choose a held-out group, assign formal splits,
reveal private reviewer information, verify reuse permissions or certify any
expert verdict.

The repository's existing event-family gate remains in force. **No formal
train/validation/test split is assigned to the unreviewed collection.** Before
a future independent-holdout experiment, connect this conservative graph check
to the approved split-admission workflow and complete scientific/rights
reviews. Separate REAL Gold, synthetic development and held-out literature
strata. Evaluate fault-source localization, evidence fidelity, affected parts,
uncertainty, disposal fidelity and history transfer rather than text similarity
alone.

Development lesson: a common paper and its cited historical source can
cross event-family boundaries; paper-level and history-to-target connectivity
must be evaluated *before* claiming an independent holdout.
