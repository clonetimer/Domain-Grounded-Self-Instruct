# P5-C2 — immutable REV1 21-task independent expert handoff

## Scientific purpose

The original 21-task C2 review candidate contained an over-specific task 015 structured fault-mode label. PR #155 preserves the earlier cohort and adds a **new, immutable REV1** correction: the task 015 synthetic ML result supports *LNA gain degradation as a candidate*, not an observed hydrogen-poisoning root cause. The earlier single-AI/two-lens advisory **is not two human expert reviews**.

This stacked PR (base: PR #155) adds a REV1-specific, source-snapshot-bound, checkout-only generator. The original PR #154 generator binds the **prior** 21-task cohort. Both pre-REV1 15-task and 21-task review forms are **obsolete for REV1**, and their responses must not be transferred to REV1 as official reviewer receipts.

## Reproducible, no-admission local handoff

Run in a checkout that includes PR #155 and this PR, with a pre-existing, authorized **outside-repository** destination directory:

```bash
python scripts/create_l1_c2_rev1_review_kit.py --output-file /secure/outside/repo/DGSI_C2_REV1_21_REVIEW_ONLY.zip
PYTHONPATH=src python -m unittest discover -s tests -p test_l1_c2_rev1_review_kit.py -v
```

The generated outer ZIP contains separate reviewer A/B ZIP packages with blank ten-dimension Word/JSON forms and full *SYNTHETIC* scientific dossiers, plus the coordinator manifest, a separate blank seven-publication rights queue and SHA-256 sums. Publish the reviewers' packages separately; expert identities, filled forms, rights evidence and restricted source material must remain off this public repository.

The wrapper validates:
- REV1 L1 Git blob `f141694748d5425b63b469b5b0b25064e1b402c8` and unchanged L0 blob `33b831408068e00e366eb6c6c3a0a1751195c685`; CRLF checkout differences alone are normalized.
- Collection ID `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`, fixed projection digest `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`, 21 packets, nine event families, seven distinct source documents and 12 bound L0 cards.
- L0 source review remains pending; L1 tasks remain `REVIEW_REQUIRED`; independent expert review, rights clearance, formal splits and training authorization remain **false**.
- Atomic no-overwrite publication; no output paths inside the repository, including resolved symlinks.
- Task 015 structured target stays `linearizer_LNA_gain_degradation_candidate` (not hydrogen poisoning); prior cohort is rejected.

This script is **not** part of the frozen RC4 allowlist and must not modify any issued portable archive. The tool provides review handoff only; it does not validate source permission, authenticate reviewers, complete expert approval, emit SFT rows, create Gold cases or authorize model fine-tuning.

## Development experience

The earlier 21-task review wrapper correctly pinned its cohort. The actual failure mode arises when an advisory-driven scientific field correction creates REV1 but the review distribution entrypoint still produces the older package. Safe recovery is a new immutable cohort-specific wrapper, independent forms and a test that rejects the old collection ID, rather than mutating old data or reusing old receipts.

Acceptance requires the **same newest PR head** to pass full Ubuntu and Windows CI. Parent PR #155 must remain open/unmerged until explicitly authorized. Independent source-rights and domain-expert judgments remain missing.
