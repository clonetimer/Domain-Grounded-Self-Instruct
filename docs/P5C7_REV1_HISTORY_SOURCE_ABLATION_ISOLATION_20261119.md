# P5-C7 — REV1 history-only source leakage in the negative-transfer A/B controls (2026-11-19)

**Classification:** AI scientific pre-audit; `not_for_sft=true`. **No expert decision, real Gold, source-rights clearance, training authorization or model execution.** This note documents one defect in the *DEV_ONLY paired-input projection*, not a modification of immutable REV1 L0/L1 facts.

## Reproduced defect (v0.1 input projection)

Task `L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012` has a `NO_HIT` arm with `input.historical_cases=[]`, but its unchanged `input.knowledge_evidence` contained:

- `evidence_id=HIST-L0-E-008`
- `source_id=NASA-LLIS-1416`
- a Cassini reaction-wheel historical explanation and its applicability limitation.

The `HISTORY` arm contained that same excerpt. Thus the so-called `NO_HIT` arm **still received the historical source's substantive contents**, confounding the proposed historical-Context A/B test. Matching `core_input_sha256` and changing only `historical_cases` was insufficient to exclude historical information carried by a different field. This was detected by inspecting the six locally generated inputs from P5-C6 against their coordinator manifest. **Do not score or use the original v0.1 FUSE pair as a clean no-history control.**

## Corrected DEV_ONLY v0.2 projection (local deliverable, not committed source data)

1. On the *fixed, source-kit-hash-bound reviewer snapshot*, classify the known prior-only `HIST-L0-E-008` / `NASA-LLIS-1416` source record as **history-specific**, not current-event `knowledge_evidence`.
2. Remove that record from the **shared** `knowledge_evidence` of *both* FUSE arms, retaining only the current FUSE `L0-E-012` source evidence. This changes the dev projection; it does **not** silently modify the immutable REV1 packet.
3. Put the originally declared historical summary **only** in the `HISTORY` arm's `historical_cases`, preserving its `case_ref`, `source_case_refs`, `event_family_id`, `outcome_status=PARTIALLY_CONFIRMED`, `hardware_compatibility=UNKNOWN`, equipment scope, applicability limitations and declared `available_at`. Do not invent a missing `verified_at`.
4. Keep other current upstream ML findings, synthetic logs, current-event source knowledge, task instruction, configuration and cutoff identical between arms. Retain each `NO_HIT` arm's empty `historical_cases`.
5. Fail closed if the FUSE historical-source classification drifts or new `HIST-` evidence appears without review; pin both the source-review ZIP hash and collection projection SHA-256.

The other two TROPICS pairs did not have this prior-only `knowledge_evidence` leak; their history entries receive the same traceable metadata preservation.

## Reproducible checks completed locally

- Original source review ZIP SHA-256: `07e6ac7ad9c92d89aee6fb8123c61849684ba0ddd6571122de949cc81ed5eda1`.
- Frozen collection projection SHA-256 remains `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`.
- Corrected dev ZIP SHA-256: `89e55e253ad3dfb8b90cc3308a2824280da5360f09e79d18ea337fa1f18eea00`.
- 3 task-level pairs / 6 model-visible inputs; **2 distinct current evidence cores and 2 event families** (TROPICS 003 and 013 are not independent events).
- Each corrected pair differs only under `input.historical_cases`. Neither arm retains the Cassini `HIST-L0-E-008` record in common `knowledge_evidence`.
- ZIP member digests (9), archive CRC, schema status and temporal checks pass. Two independent rebuilds from the *same pinned source* produce bit-identical archives; ZIP timestamps are fixed for reproducibility.
- No model run or blind expert scoring; negative-history-transfer outcome remains `NOT_RUN`, positive confirmed-compatible history benefit remains `NOT_EVALUABLE`.

The corrected ZIP includes the read-only Python 3.11+ reproduction script and its coordinator-only evidence-removal audit manifest. Neither model-visible input nor private reviewer forms are placed in this public repo.

## Scientific limits and next action

These three negative-history samples assess **whether the model resists invalid transfer**, not the value of confirmed compatible prior experience. Status is `REVIEW_REQUIRED`. The accepted sources, historical timing semantics, hardware fit, science labels, rights and independent A/B decisions must still be verified before formal evaluation. Cases SCI-002, SCI-009, SCI-016, SCI-017 remain open.

**Development lesson:** Information-flow separation must be checked by **scientific role**, not just by JSON field name. A valid structure-level one-field ablation can still leak the intervention through a second, ostensibly shared field.
