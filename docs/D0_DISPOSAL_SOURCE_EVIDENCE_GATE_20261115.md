# D0/P3 — Disposal source-record attribution gate (2026-11-15)

## Product boundary

The assistant learns second-stage interpretation of **upstream ML results + diagnosis logs + mission/configuration context + historical experience**. Raw telemetry stays upstream. This stage is a fail-closed *source-reference* gate, not a generator of disposal actions, a proof of physical cause, or a Gold approval.

## Found gap and change

PR #35 isolated formal reports from curator review notes and required an evidence ref for EXECUTED disposal. Two narrower gaps remained:

1. Standalone SFT export validated target JSON structure but did **not** apply the Case's disposal status consistency rules.
2. PLANNED and RECOMMENDED actions could have empty citations, while an EXECUTED action could cite only a machine finding or a literature passage. A model candidate is not a record of an executed procedure.

`diagnostic_context.py` now uses the same disposal status validator for both Case and standalone SFT:

- `NOT_RECORDED` and `NOT_APPLICABLE` require `disposal_measures=[]`.
- `RECORDED` requires at least one `EXECUTED` measure; `RECOMMENDED_ONLY` must not include an `EXECUTED` measure.
- Every measure must cite a source record: an input diagnostic-log ID or a knowledge-evidence ID. Machine findings and retrieved historical case references alone cannot document current-case disposal.
- `EXECUTED` measures additionally require at least one *diagnostic log* citation; a literature passage alone cannot establish execution.
- Model-proposed next checks remain `follow_up_actions`, not `disposal_measures`.

The existing overall evidence-ID uniqueness and resolution checks remain in force. The guard applies to Case and SFT direct validation and is inherited by Case→SFT binding.

## Limitations and adversarial scope

A syntactically valid log citation **does not prove** its text documents the action, who executed it, whether it was authorized, or when it happened. Log type itself is insufficient to decide that question. A reviewer must inspect source passages, time boundaries and action wording in the authorized environment. Structural PASS must never become Gold or be described as an executed flight measure.

The new regression cases are explicitly **SYNTHETIC_TEST_ONLY** and use the already illustrative Case/SFT fixtures. No user-provided five-case documents, restricted R21, flight logs, credentials or private expert targets are copied to this public repository.

## Verification and release boundary

Required PR-head gate: Ubuntu and Windows mandatory jobs both SUCCESS on the exact latest head, with no weakened checks. Keep Draft; do not auto-merge, fine-tune or promote samples. Track D0 #8 and P3 #4.

Next: source-text-level disposal adjudication and user expert review of five local L0 cards plus 11 literature L0 cards, separately from the model-facing formal target.
