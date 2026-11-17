# P5-B4.3a: local human text-region review receipts

Status: implementation candidate; review-required only.

## Purpose

Record a human review decision against the exact OCR text-region candidate record without treating a local metadata receipt as identity authentication, scientific validation, or SFT approval.

## Input contract

- Candidate record must validate against `dgsi.diagram-text-regions.v1`.
- Review receipt must validate against `dgsi.diagram-text-review.v1`.
- Source SHA-256, asset ID, asset SHA-256 and canonical candidate-record SHA-256 must match exactly.
- Every decision must reference an existing candidate ID exactly once.
- The evidence locator must exactly match one of the candidate's source-bound locators.
- `ACCEPT_AS_LABEL` requires a human-selected object type. `REJECT_LABEL` and `UNRESOLVED` cannot set one.
- Partial review is allowed; unreviewed candidates remain unreviewed.

## Local audit

```bash
python scripts/audit_diagram_text_review.py \
  --candidate-record review/regions.json \
  --review-receipt review/decisions.json
```

The CLI reads only the explicitly selected JSON files, performs no network calls and writes no files. It prints aggregate counts only.

## Trust boundary

The receipt contains a caller-supplied reviewer reference, but the local validator cannot authenticate the person, role, signature, or whether the source image was actually inspected. Its output is therefore `REVIEW_RECEIPT_BOUND_NOT_AUTHENTICATED`, not a verified human approval.

A receipt does not create or update diagram nodes, ports or edges. It does not prove OCR correctness or engineering semantics. Human acceptance here means only that a reviewer chose to accept a text region as a label candidate and selected an object-type proposal. A separate annotation-import and evidence adjudication stage is still required.

All candidate and receipt records remain `REVIEW_REQUIRED`, `not_for_sft=true`, `training_authorized=false`, and `gold_authorized=false`. No formal split, Gold admission, SFT export or training authorization is granted.
