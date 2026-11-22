# P5-C2 REV1 — deliver the actual 21-task blank expert-review ZIP

## Product goal and version
The usable deliverable is the **21-task immutable REV1** expert-review handoff, not merely a generator or a passing test. This is the literature-derived **SYNTHETIC** track; it does not create real Gold, an approved dataset, or permission to fine-tune.

Frozen input binding:
- Collection ID: `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`
- L1 Git blob: `f141694748d5425b63b469b5b0b25064e1b402c8`
- L0 Git blob: `33b831408068e00e366eb6c6c3a0a1751195c685`
- Projection SHA-256: `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`
- 21 candidate tasks, 9 event families, 7 distinct source documents, 12 bound L0 cards.

## Download and distribute
The dedicated GitHub Actions workflow [DGSI P5-C2 REV1 independent expert review-only artifact](../.github/workflows/p5c2-rev1-review-artifact.yml) builds a downloadable, three-day-lived artifact. It runs for changes to the workflow or its exact cohort dependencies, and can be dispatched manually when this workflow is present on the default branch.

1. Open the successful workflow run and download the `dgsi-c2-rev1-21-review-only-<run_id>` Actions artifact.
2. Verify `SHA256SUMS.txt` against `DGSI_C2_REV1_21_REVIEW_ONLY.zip`, then inspect the coordinator manifest. The inner Word/JSON scorecards must still be **BLANK**.
3. Unpack and distribute `reviewer_A.zip` and `reviewer_B.zip` independently through approved channels. Each contains the complete synthetic scientific dossier in JSON/HTML and a separate blank ten-dimension review form (Word/JSON).
4. Give the coordinator the distinct, **blank** seven-document rights queue. Rights require human source-by-source evidence, not public access, a generic publisher policy, or a checksum.
5. Bind each independent returned review to the exact `task_id`, packet hash, source bindings, collection projection and unique reviewer token. Use the existing local preflight and adjudication gates. Never put filled reviews, reviewer identities, private logs, signed rights receipts, or restricted source files in GitHub or a public Actions artifact.

Only *blank forms and synthetic source-derived dossiers already represented in the public repository* are uploaded. This job has `contents: read`, uses no credentials or paid model calls, and sets three-day artifact retention. **A successful artifact job is distribution readiness, not science approval.**

## Acceptance and remaining blockers
The job must verify the full ZIP contents, the fixed REV1 projection, both blank forms, review and source-rights pending status, and `sft_records_emitted=0`. Separately, the PR's **same latest head** must pass the normal Ubuntu and Windows validation. Packaging cannot replace that CI gate.

After handoff, both independent domain expert reviews remain needed for all 21 candidate tasks, together with genuine rights clearance for the seven sources and real upstream result+logs+context evidence for the five REAL candidates. Current training and Gold admission remain false. No official split should be assigned; the shared-publication/history-connected holdout audit must also be respected.

## Development experience
- **Problem:** a verified handoff generator is not the same as delivering a reviewer-ready artifact. Old 15/21 task forms are unsafe after the task-015 material correction.
- **Implementation:** call the frozen REV1-specific generator in an isolated CI job and audit the actual ZIP members, source-rights queue, independent blank scorecards and non-admission flags *before* uploading any artifact. Include the output checksum for a local transfer check.
- **Failure avoided:** do not publish previously completed reviewer replies or sensitive evidence in a public repository; never claim that a hash validates human identity or source license. Keep review-only artifact retention short.
- **Workflow principle:** a single distributable handoff is more useful than another layer of admission plumbing. Do not alter RC4 package contents, original Case data, or test gates.
