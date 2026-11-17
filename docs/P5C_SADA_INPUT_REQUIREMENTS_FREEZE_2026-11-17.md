# P5-C1 SADA candidate intake: freeze required evidence fields (2026-11-17)

## Failure mode

The first-case SADA metadata preflight previously validated only that each `required_dgsi_inputs.*.required` value was a nonempty list of distinct strings. A candidate could replace the required algorithm/model version, score semantics, evidence references, diagnostic time basis, or as-flown configuration with arbitrary placeholders and still obtain the normal `BLOCKED_PENDING_REAL_EVIDENCE` audit result. That output would be misleading as a source-contract consistency check, even though it did not authorize Gold or training.

## Correction

- Freeze the three required field arrays to the exact currently declared, ordered versioned schema. Do not accept arbitrary additions, deletion, substitution or reordering without an explicit version update and review.
- Preserve `history_context` as CONTEXT-only; it is not present-case evidence.
- Reject non-string required field types with `SADA_MAP_INPUTS_INVALID`; reject altered, well-formed field lists with `SADA_MAP_INPUT_REQUIREMENTS_DRIFT`.
- Add four `SYNTHETIC_TEST_ONLY` adversarial tests for deletion, substitution, reordering, and wrong type. They do not contain real telemetry or private evidence.

This guard only validates a candidate's *requested evidence checklist*, not whether the evidence was submitted, authentic, timely, permitted, or independently reviewed. SADA remains REAL_CASE_CANDIDATE. Source rights, real ML/log receipts, two expert reviews, Gold admission, official split and training remain unavailable/unauthorized.

**Branch dependency:** this change builds on Draft PR #119 and is itself Draft; never merge automatically. CI must be checked on the exact latest head for Ubuntu and Windows before claiming code validation.
