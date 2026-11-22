# P4 — nonconfirmed historical review chronology guard (2026-11-18)

## Why this gate exists

For an unresolved, rejected, partially confirmed, or unknown historical case,
an L1 task previously accepted optional `hit_metadata.verified_at` whenever
it was no later than `analysis_cutoff`. That did **not** compare verification
time with the claimed `available_at` snapshot. A historical status could
therefore be attached retrospectively to an earlier-available document,
making it appear available in a time-safe context before the review occurred.

## Change

When nonconfirmed `verified_at` is supplied, it must be a valid timezone-aware
datetime no later than `analysis_cutoff` **and** no later than `available_at`.
A later review is rejected with a payload-free
`HISTORY_AVAILABLE_BEFORE_VERIFICATION`. The existing confirmed-history
temporal gate already applies an analogous ordering rule.

Absence of `verified_at` for nonconfirmed hits retains the existing
contract; this patch does not claim source authentication. A future revision
can separately decide whether a stricter provenance policy should require it
for every nonconfirmed hit. This is not a substitute for authenticated
historical decision records, permissions, expert review, or source identity
checks.

## Reproducible checks

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_nonconfirmed_history_verification_order.py' -v
PYTHONPATH=src python -m unittest discover -s tests -v
```

Synthetic-only adversaries cover verified-after-availability, identical
timestamps, earlier verification, non-UTC offsets, future verification,
and no-verification legacy records. They load the current 21-task candidate
and unchanged L0 cards; no data are mutated.

## Limits and scientific admission

- An L1 validation result is not Gold, a real flight record, or an approved
  historical conclusion.
- **No** training split assignment, model execution, dataset export, or Gold
  promotion takes place.
- `internal_review` remains separate from model inputs and targets.
- Domain reviewers still need to verify L0 facts, history applicability and
  7 distinct source-publication rights; the 5 REAL case candidates still
  need upstream ML runs/logs/context and independent admission.
- This fix should be judged on the same exact commit by Ubuntu and Windows
  before any integration proposal. Do **not** merge without authorization.

## Development lesson

A single `timestamp <= cutoff` comparison is insufficient when a historical
status is linked to a separately versioned availability snapshot. Compare
the order **review -> availability -> analysis cutoff**, using timezone-aware
datetimes and source-bound status; never infer a missing timestamp from
the wall clock or a document's publication date.
