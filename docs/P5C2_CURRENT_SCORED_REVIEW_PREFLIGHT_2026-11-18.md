# P5-C2 current-source scored review preflight (2026-11-18)

## Fixed scientific review integrity gap

The existing 10-dimension, two-expert validator correctly binds each submitted scorecard to the **supplied** coordinator manifest. That manifest can, however, be self-consistent and obsolete following an L0 fact correction or a changed L1 task. An old scorecard must not silently carry forward to the current science-review cohort.

The new preflight independently builds the current fingerprint manifest from checked-out, version-controlled L0 and L1 artifacts, **compares its entire metadata structure** to the supplied coordinator manifest, and only then calls the existing whole-cohort scored-review validator. It rejects old L0 source facts, L1 modifications, falsified task bindings, modified admission flags and incomplete task review sets.

## Local procedure (private reviewer materials only)

```bash
python scripts/audit_l1_c2_current_scored_review.py \
  --manifest /secure/original-coordinator-manifest.json \
  --submissions /secure/private-scored-submissions.json \
  --current-collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --current-l0-facts examples/l0_public_literature_fact_cards_2026-11-15.json
```

The submissions JSON is an **array** of `{"task_id": "...", "submission": {...}}` records for every member of the current cohort, using the existing scored-review protocol. Example scores and token values in unit tests are `SYNTHETIC_TEST_ONLY`; they are not real expert signatures or reviews. Never check private submissions into GitHub.

This command is **review-only** and returns metadata counts plus fixed rejection codes. A matching snapshot is not proof of review independence, reviewer identity, scientific correctness, source rights or permission to use data. All 15 existing SYNTHETIC task packets remain pending; Gold, official split assignment, SFT export and training remain blocked. Updating a current source invalidates the old manifest and requires re-review rather than rewriting source material or upgrading an old receipt.

## Regression evidence and development lesson

Run `python -m unittest discover -s tests -p 'test_l1_c2_current_scored_review_preflight.py' -v` in an environment with the repository `src` on `PYTHONPATH`. Mandatory CI is **same latest PR head** on Ubuntu and Windows; a unit pass alone does not satisfy scientific admission. Revalidate source currentness **before** ingesting scored receipts, the same way the rights-intake preflight checks the independently loaded current source snapshot.
