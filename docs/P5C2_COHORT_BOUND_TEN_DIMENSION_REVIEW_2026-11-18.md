# P5-C2 — one ten-dimension rubric, cohort-bound scored-review preflight

Status: **development-only**. Applies to the frozen 15 literature-derived SYNTHETIC L1 review candidates, sourced from nine independent event families. All remain REVIEW_REQUIRED, rights unresolved, with zero Gold, zero formal splits and zero training authorization.

## Gap resolved

Earlier P4 code has the selected `validate_blind_l1_review` ten-dimension/two-assessor scientific rubric, while the later C2 fingerprint manifest `check_blind_review_pair` verifies only two short recommendations. Two bare `ACCEPT` strings are **not** a substitute for ten scientific scores, finding codes or secure adjudication. The two paths must not become competing admission gates.

`src/dgsi/l1_c2_scored_review.py` bridges them instead of creating a new rubric. It checks the **current whole-collection SHA-256, full packet SHA-256 and referenced public L0 source SHA-256**, then calls the **existing** ten-dimension validator. `blinded_packet_ref` must equal `sha256:<packet_sha256>`; only fixed-value error codes and aggregate metadata leave the preflight. A stale cohort invalidates even an unchanged task. Any score gap, duplicate reviewer token, material finding, 2-point dimension disagreement or inconsistent pending state is rejected or routed to secure adjudication according to the existing rubric.

The simple `check_blind_review_pair` function is retained as a *compatibility structure check*, **not** a scientific signoff. For a C2 quality review, the scored bridge is the only relevant rubric path.

## Envelope (authorized workspace, not a public reviewer artifact)

`dgsi-c2-scored-blind-review-submission.v1` requires exactly:
- `schema_version`, `task_id`, `collection_projection_sha256`, `packet_sha256`, `source_public_sha256`;
- `blind_review` with existing `dgsi-l1-blind-review.v1` fields: `blinded_packet_ref`, two independent `assessments`, ten integer scores 1–5, fixed `finding_codes`, and `decision` values `ACCEPT_L1|REVISE|REJECT`;
- `adjudication_status` = `PENDING_SECURE_ADJUDICATION` or `PENDING_REVIEWER_AUTHENTICATION` as required by the rubric.

The batch interface accepts one `{task_id, submission}` record per task in the current manifest. Missing/duplicate tasks and altered cohort binding fail closed. Reviewer identities, free-form private notes, real source restrictions or private logs must be stored only in an authorized expert-review workspace, not in the repository, issue comments, CI artifacts or public test fixtures. Reviewer tokens in tests are explicitly `SYNTHETIC_TEST_ONLY`.

## External scientific and release gates

Successful validation is **structural only**. An independent authority must still:
1. Confirm that each reviewer is a distinct human expert and blinding was preserved; resolve disagreements securely, without promoting rejected/partial historical cases.
2. Verify the L0 literature passage and certainty, event/episode separation, intended training/derivative-use rights and synthetic-field assumptions.
3. Verify the L1 ML finding/log semantics, direct-versus-historical evidence roles, cause versus affected component, uncertainty and no fabricated disposition.
4. Bind the authoritative disposition to the same cohort/packet/source digests; any mutation triggers re-review.
5. Only then consider a separate *explicitly authorized* release and holdout protocol. REAL Gold remains a separate track.

Engineering tests are run with `python -m unittest tests.test_l1_c2_scored_review` (with `PYTHONPATH=src`). Ubuntu and Windows required workflows remain mandatory on the exact latest PR head.

**Non-claims:** review test scores are fictional fixtures; no expert approval, source rights, held-out model comparison, actual SFT row or fine-tuning result is represented here.
