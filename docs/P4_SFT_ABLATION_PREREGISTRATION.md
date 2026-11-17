# P4 SFT controlled ablation pre-registration (design-only v1)

**Status: NOT_RUN / NOT_ADMITTED.** This is an offline experiment-plan integrity check. It does not execute model inference, create training data, approve source rights, allocate train/validation/test, authenticate reviewers, authorize fine-tuning or measure effectiveness. The example contains no model run, real ML evidence, expert conclusion, training family or holdout family.

## Pre-registered comparison

| Arm | Training treatment | Retrieved historical Context | Primary contrast |
| --- | --- | --- | --- |
| BASE_MODEL | None | No | Base model |
| GENERIC_SELF_INSTRUCT | Generic Self-Instruct | No | Generic instruction tuning |
| DGSI_LITERATURE_DERIVED_SYNTHETIC | DGSI literature-derived synthetic only | No | DGSI grounding |
| DGSI_REAL_GOLD | Authenticated real Gold when approved externally | No | Real-case supervision; NOT_RUN while Gold=0 |
| DGSI_WITH_RETRIEVED_HISTORY | Same DGSI literature-derived treatment as preceding arm | Yes, as-of-valid user Context | Inference-time history contribution |

Arms C and E must eventually use the **exact same trained checkpoint**, with the only planned difference being historical Context (and its disclosed context-budget implications). This module validates treatment categories but cannot prove checkpoint identity. A later independent execution receipt must bind model/checkpoint/tokenizer, evaluation inputs, actual retrieval output, inference settings and evaluator identities.

**Independent test discipline:** freeze source event families before training/recipe selection. Every episode, variant and packet of one underlying event remains in the same partition. Use identical independently approved holdout cases across arms and report real-source versus literature-derived synthetic strata separately. The present 15 unreviewed synthetic task packets from 9 source event families are **not** formally assigned to any split. A provisional candidate list in this schema is not a formal split or certified independence. Case/family aliasing and same fact-card hash across training/holdout candidate pools are rejected. Family references must use ASCII identifiers (`[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}`) and are compared case-insensitively, including across tracks and candidate pools; Unicode lookalikes, invisible controls and free-text aliases fail closed. Different canonical IDs and hashes still do **not** establish independent incidents; expert source-lineage adjudication remains mandatory.

## Seven mandatory metrics

- Fault-source localization (separate originating component from affected components).
- Affected-component accuracy and coverage.
- Evidence consistency and correct candidate-versus-confirmed attribution.
- Uncertainty and appropriate abstention.
- Disposal fidelity: separate recorded executed/planned/original suggestions from model-proposed follow-up actions.
- Historical transfer validity, including rejected/unresolved/conflicting cases, mismatched hardware, same-event reuse and history available only after analysis cutoff.
- Confidence calibration **only when eligible**. Uncalibrated upstream ML ranking scores are not probabilities; they must not be treated as calibration targets. Record NOT_APPLICABLE with reason when reliable probability/outcome ground truth is unavailable.

Add independent review of critical hallucination, future-history leakage, unsupported disposal and false certainty; aggregate metrics are not a substitute. Report event-family denominators, missing strata, adjudicated outcomes and uncertainty intervals; text similarity and synthetic sample volume alone do not establish diagnostic benefit.

## Contract and invocation

- Runtime: src/dgsi/sft_ablation_design.py
- Example: examples/sft_ablation_design_not_run_v0.1.json
- Tests: tests/test_sft_ablation_design.py (SYNTHETIC_TEST_ONLY)

Run locally without network, authentication or payment:

    PYTHONPATH=src python -m unittest tests.test_sft_ablation_design -v
    PYTHONPATH=src python -c "import json; from dgsi.sft_ablation_design import audit_sft_ablation_design as f; print(f(json.load(open('examples/sft_ablation_design_not_run_v0.1.json', encoding='utf-8'))))"

The validator requires all five specified arms, exact treatment/context assignment, NOT_RUN execution states, seven scoring dimensions, identical provisional holdout policy across arms, time/status/hardware-safe historical Context policy, and absence of candidate family/fact-card digest overlap. It rejects extra case text, declared Gold/training authorization, claimed executed evaluations, formally assigned splits and unverified run results. Outputs are aggregate-only, fixed code, always DESIGN_ONLY_EXTERNAL_REVIEW_AND_AUTHORIZATION_REQUIRED. These are design checks, not real-world verification.

## External gates that must precede any experiments

1. Independently verify source authenticity, use/IP rights, de-identification, actual upstream ML result/run/log/configuration and time-limited evidence.
2. Bind exact L0/L1 source/packet fingerprints; complete dual expert review, independent reviewer authentication and discrepancy adjudication in a secure workspace.
3. Obtain explicit approval for formal event-family splits, holdout freeze, data release and fine-tuning. No self-reported approval in a JSON manifest is trusted.
4. Freeze the base model, checkpoints, seeds, evaluation cases, generation recipes, label rubric and score semantics. Independently verify C/E checkpoint equality, and prohibit the independent holdout from any tuning loop.
5. Execute only after explicit authorization; score the same holdout under blinded review and publish per-track denominators and all non-applicable metric reasons.

**Checkpoint 2026-11-17:** 0 verified real Gold, 0 official splits, 0 trained model runs and 0 effectiveness claims. The design-only sample contains no evidence beyond metadata.
