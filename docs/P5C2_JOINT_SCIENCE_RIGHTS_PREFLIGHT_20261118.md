# P5-C2 cross-track current-source review integrity (2026-11-18)

## Why this gate exists

The C2 scientific ten-dimension scorecard and seven-document source-rights
worksheet are separately audited against current L0/L1 files. Distributing
and collecting them as independent packets can obscure which dataset snapshot
was actually reviewed by both groups. A rights form cannot substitute for a
scientific scorecard; two structurally valid forms do not authenticate humans
or legal grants. This step provides one **read-only, same-source-snapshot
structural check** and a privacy-safe aggregate status.

## Local use (private review workspace only)

```bash
python scripts/audit_l1_c2_joint_review.py \
  --rights-blank /secure/unmodified-rights-queue.json \
  --rights-submission /secure/edited-rights-queue.json \
  --science-manifest /secure/unmodified-science-manifest.json \
  --science-submissions /secure/private-scored-submissions.json \
  --current-collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --current-l0-facts examples/l0_public_literature_fact_cards_2026-11-15.json
```

The current L0/L1 inputs must be separately loaded from an authorized,
version-controlled checkout. Do **not** derive them from either editable
review form. Each review preflight reconstructs its own current manifest.
The two source-projection fingerprints must be equal. Any stale source or
cohort, forged clearance, incomplete review coverage, or false review
approval fails closed.

The CLI returns only counts, fixed rejection codes, and permanent blocked
authorization flags. Reviewer tokens, scores, scientific comments, license
evidence refs, prompt text, and diagnostic targets are not returned.
Never commit completed worksheets, identifiable reviewers or private rights
evidence to this public repository.

## Acceptance boundary and development lesson

Structural review status is **not** expert sign-off or legal clearance. Even
if every synthetic test scorecard says `ACCEPT_L1` and every rights document
contains an evidence reference, neither proves source license, independent
reviewer authentication, ten-dimension science correctness, Gold status,
official split eligibility or permission to train. The current pilot remains
15 LITERATURE_DERIVED_SYNTHETIC tasks, nine event families, with 13 L0 cards
pending external domain review and zero real Gold.

Regression: `PYTHONPATH=src python -m unittest discover -s tests -p
'test_l1_c2_joint_review_preflight.py' -v`. Before calling this phase
complete, validate the exact latest head using both mandatory Ubuntu and
Windows CI jobs. A test success alone must not be described as scientific
admission.

Development lesson: bind **both** human-review workflows to a single
independently retrieved source snapshot and report only an aggregate
non-release status. Avoid writing another review rubric or treating a
metadata fingerprint as a scientific/legal approval.
