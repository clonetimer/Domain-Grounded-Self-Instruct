# P5-C2 offline source-rights intake audit (2026-11-18)

The coordinator's complete kit contains `C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json`: seven distinct public source publications for the current 15 synthetic L1 tasks, with no inferred reuse permission. The same publication can support multiple fact cards and tasks.

## Review-only procedure

1. Retain the original blank JSON unchanged as the trusted reference, associated with its coordinator kit SHA-256 and collection projection hash.
2. Make a copy in a controlled workspace. For each source document, optionally set `rights_review_status` to `EVIDENCE_SUBMITTED_FOR_RIGHTS_REVIEW`, `UNRESOLVED`, or `REUSE_DENIED`.
3. For evidence submitted, set `license_or_permission_evidence_ref` to `sha256:<64 lowercase hex>` of an independently retained rights document. The evidence itself must remain in the controlled workspace. It is NOT uploaded to this public repository.
4. Only `REUSE_DENIED` can set `rights_decision=DENIED`; all other rights decisions remain null pending authenticated independent legal/rights review. Always retain `permitted_reuse_scope=null` and `rights_cleared=false`.
5. Run the audit using two local files:
   `python scripts/audit_l1_c2_source_rights_intake.py --blank <trusted-blank.json> --submission <edited-private.json>`.

The auditor checks exact cohort/source/document/episode/L0 bindings and rejects stale manifests, missing or duplicate publications, unsupported permissions, and direct training approval. Output is only aggregate status counts. It never returns a private rights reference or individual reviewer details.

## Boundaries

**Evidence submitted is not permission granted.** An offline hash reference does not authenticate the document, signer, legal authority, scope, or copyright. Legal rights review, L0 source fidelity, two-person scientific scoring, five REAL cases and full SFT release gates remain separate. There is no automated permission approval, Gold promotion, official split assignment, paid API call or model training. All tests use `SYNTHETIC_TEST_ONLY` data.
