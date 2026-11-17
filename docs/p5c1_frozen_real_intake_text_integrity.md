# P5-C1 frozen REAL intake free-text integrity

Date: 2026-11-17  
Scope: the existing **public, metadata-only** five-candidate intake snapshot; no raw cases or private logs.

## Issue

The initial P5-C1 validator enforces missing ML/log fields, zero Gold and strict keys, but still accepted arbitrary free-text changes in `cases[].notes`, `source_document.review_scope`, `source_document.content_reviewed_artifact`, and `required_next_evidence`. Such edits could silently add unreviewed excerpts to a checked-in public fixture without triggering its preflight.

## Contract

After all field-specific fail-closed checks, canonical JSON (`sort_keys=True`, UTF-8, no insignificant whitespace, no NaN) must match the SHA-256 fingerprint of the original checked-in sanitized metadata. This is a **snapshot integrity check**, not an authentication signature, source-rights assessment, expert approval, or claim that cryptographic hashes establish event independence. It also does not protect against deliberate code-and-fixture co-editing without code review.

Unreviewed edits are blocked with the fixed, payload-free code `REAL_INTAKE_SNAPSHOT_TEXT_DRIFT`. The CLI continues to emit only aggregate counts and no case notes or source content. The original fixture remains unchanged.

Updates to legitimately corrected source summaries require a **new versioned intake snapshot and review**; do not rebaseline the fingerprint in place or treat this register as a REAL evidence-submission pipeline. Use separate permissioned evidence receipts to handle source permission, de-identification, actual upstream ML runs, diagnostic logs, chronology, mission context, independent expert reviews and Gold authorization.

## Regression

Five `SYNTHETIC_TEST_ONLY` tests cover note injection, source review-scope injection, reviewed-artifact substitution, arbitrary evidence-request text, and JSON object-key reordering. Full Ubuntu and Windows PR CI remains required at the same latest head. No train/validation/test split or fine-tuning is authorized.
