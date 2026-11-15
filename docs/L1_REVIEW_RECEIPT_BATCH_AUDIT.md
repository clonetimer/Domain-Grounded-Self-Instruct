# DGSI L1 review receipt batch audit

## Purpose

A single L1 packet can be fingerprint-bound to a two-reviewer scorecard, but a collection needs an aggregate completeness check. The batch audit requires exactly one receipt for every task in the frozen L1 collection.

## Contract

`audit_l1_review_receipt_batch(collection, source_fact_cards, receipts)`:

1. Validates the collection and every packet against its current L0 source facts.
2. Requires a one-to-one mapping between packet task IDs and receipt entries.
3. Rejects missing, duplicate and unknown task references.
4. Runs the immutable packet/L0 fingerprint check for each receipt.
5. Counts scorecards awaiting reviewer authentication separately from those requiring secure adjudication.
6. Returns aggregate counts only; it does not expose task IDs, source text, reviewer tokens or digests.

## Security and approval boundaries

- A receipt proves only that the scorecard references the current packet and L0 fact-card bytes.
- It does not authenticate reviewer identity or independence.
- It does not establish source rights, de-identification, technical correctness or semantic Gold approval.
- A substantive finding requires secure adjudication even when both scorecards say ACCEPT_L1.
- The current 15-packet pilot remains REVIEW_REQUIRED. No receipt in the repository is a real expert review.
- The batch audit always returns zero L1 experiment approvals, zero Gold and no training authorization.

## Synthetic regression coverage

`tests/test_l1_review_receipt_batch.py` uses only synthetic reviewer tokens and synthetic scorecards to test full 15-packet coverage, missing/duplicate/unknown task references, cross-packet receipt reuse, changed L0 facts and secure-adjudication routing. These fixtures are not expert reviews or training data.
