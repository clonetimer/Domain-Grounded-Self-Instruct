# DGSI P5-C2 package delivery contract — 2026-11-18

## Two deliverables

This milestone produces two separately versioned outputs:

1. **Portable DGSI Skill/toolkit** — reusable production instructions, schemas, validators, preview CLI, blind-review manifest CLI, complete two-reviewer kit generator, current-source-bound expert/rights intake, references and regression tests. Built as `dgsi-simulation-to-sft-toolkit-0.2.0-rc.3.zip`.
2. **L1 synthetic dataset review kit** — a controlled, review-only package for the frozen 15-task / 9-event-family candidate. It contains two independently distributable reviewer archives, the coordinator manifest, a blank source-rights queue and SHA-256 checksums. It is not an SFT dataset release.

## Build the Skill package

From a clean repository checkout:

```bash
python -m pip install -r requirements-validation.txt
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit-0.2.0-rc.3.zip
python -m unittest discover -s tests -p "test_portable_toolkit_package_build.py" -v
```

The package manifest records per-file byte counts and SHA-256 digests. The regression extracts the actual ZIP into a clean directory without repository `PYTHONPATH`, runs the preview, blind-review and complete review-kit CLIs against external L0/L1 fixtures, verifies the generated reviewer ZIPs, and checks that no training authorization is present.

RC3 additionally receives the actual generated A/B blank forms through the extracted expert-intake CLI. The round-trip must report 15 pending tasks, 30 incomplete scorecards and zero paired reviews. RC2 remains an immutable earlier toolkit; its already delivered review forms remain compatible because the candidate and handoff schema are unchanged.

GitHub Actions workflow `.github/workflows/package-p5c2.yml` publishes only this reusable Skill ZIP as an Actions artifact. The candidate data/reviewer package is deliberately not uploaded to a public artifact because source-use rights are still pending.

## Build the L1 synthetic dataset review kit

From the same trusted checkout, after reviewing the source-use and privacy boundary:

```bash
python scripts/create_l1_c2_complete_review_kit.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json \
  --output-file local_C2_15_tasks_unreviewed.zip
```

The destination parent directory must already exist and the output path must be new. The generator creates:

- `reviewer_A.zip` and `reviewer_B.zip`, each containing a blank Word/JSON scorecard and the same source-bound scientific dossier;
- a coordinator manifest binding the collection fingerprint and both reviewer archive hashes;
- a blank source-rights clearance queue grouped by unique publication, not by task count;
- SHA-256 checksums and explicit REVIEW_ONLY notices.

Send reviewer A and reviewer B their respective inner ZIPs separately through an authorized channel. Keep the outer package and coordinator manifest in the controlled workspace. Never put completed expert forms, reviewer identities or restricted source materials into the public repository.

## Receive independent expert forms

Only `tasks[].scorecard` is editable in returned JSON copies. Provide independently loaded current L0/L1 files; all other form metadata must remain unchanged. A blank or partial form produces a pending-completion report, not an invented completed review.

```bash
python scripts/audit_l1_c2_current_expert_intake.py \
  --reviewer-a /authorized/review/reviewer-A-return.json \
  --reviewer-b /authorized/review/reviewer-B-return.json \
  --current-collection /authorized/input/l1-candidate-collection.json \
  --current-l0-facts /authorized/input/l0-source-facts.json \
  --output-file /authorized/review/current-expert-intake.json
```

Stdout contains aggregate counts; the new private file contains the task queue without reviewer tokens or scores. Complete pairs use the existing ten-dimension rubric and remain pending identity verification or secure adjudication. The separate rights process remains necessary. See [current expert intake](P5C2_CURRENT_EXPERT_INTAKE_20261118.md).

## Receive a rights worksheet

Retain the original blank queue from the coordinator ZIP. Audit each separately edited submission against independently loaded current L0/L1 inputs:

```bash
python scripts/audit_l1_c2_current_rights_intake.py \
  --blank /authorized/review/C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json \
  --submission /authorized/review/rights-submission.json \
  --current-collection /authorized/input/l1-candidate-collection.json \
  --current-l0-facts /authorized/input/l0-source-facts.json
```

The four-file command regenerates the complete queue before checking the submission. A source-document, event-family, episode, fact or task change requires a new blank and review round. A `STRUCTURALLY_BOUND_RIGHTS_REVIEW_ONLY_NOT_CLEARANCE` result reports structural agreement only, with zero rights clearance and zero training authorization. Evidence references identify separately retained documents; they do not authenticate the documents or grant reuse permission.

## Current dataset state

| Measure | State |
|---|---:|
| L1 synthetic candidate packets | 15 |
| Source event families | 9 |
| L0 fact cards bound to this cohort | 12 |
| Unique source publications in rights queue | 7 |
| Independent expert adjudications | 0 |
| Rights-cleared publications | 0 |
| Official train/validation/test splits | 0 |
| SFT rows emitted | 0 |
| Training authorized | No |

The L0 repository contains an additional unbound ISEE expert-system card; it is not counted in this cohort's 12 bound cards or seven-publication rights queue.

## Release interpretation

A successful package build establishes structural integrity. RC3 retains RC2's byte-for-byte reproducibility under different clocks within the same Python/compression implementation. It does not establish scientific correctness, reviewer identity, source rights, REAL Gold, SFT authorization or training readiness.

The Skill package may be distributed as a candidate-generation tool. The dataset package must remain a controlled review candidate until independent science review and source-use rights are completed. The two outputs must retain separate manifests and SHA-256 hashes.
