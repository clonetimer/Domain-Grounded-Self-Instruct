# DGSI vs. SOTA instruction-data construction methods — comparison protocol

**Status:** experiment design for product closeout. Execution is pending a frozen, permitted evaluation corpus and explicit model/API/compute approval.

## 1. Research question

Under the same source material, generator model, token budget, output schema and evaluation rubric, does DGSI produce better spacecraft fault-diagnosis supervision than established general-purpose synthetic instruction-data methods?

Measure:
- source/evidence fidelity and claim-level support;
- separation of upstream ML findings, observed logs, hypotheses and confirmed conclusions;
- fault-source versus affected-component localization;
- uncertainty, conflict handling and justified abstention;
- historical-context applicability and temporal safety;
- executed/planned/recommended/not-recorded action fidelity;
- traceability, duplication, accepted yield, curator effort and cost.

A separate downstream question asks whether SFT on approved DGSI data improves second-stage diagnosis on unseen event families. This is conditional and must not be conflated with construction-quality evaluation.

## 2. Methods

| Arm | Construction method | Implementation boundary |
|---|---|---|
| M0 | Self-Instruct | Same seed-task pool; generate instruction, input and output; apply invalidity and similarity filtering. No DGSI-specific evidence validators. |
| M1 | Evol-Instruct / WizardLM-style | Same seed tasks; depth evolution (constraints, depth, specificity, reasoning steps) and breadth mutation; eliminate failed or non-informative evolutions. |
| M2 | Magpie-style | Use a documented aligned-model pre-query template to elicit user queries and responses, constrained to the same spacecraft-diagnosis source scope. Call this a Magpie-style adaptation, not the official method, unless its original template and procedure are reproduced. |
| M4 | DGSI | L0 source facts, field-level provenance, ML result + logs + mission context + time-safe history, task taxonomy, evidence/target separation, source-closure checks, uncertainty and abstention. |
| M5 (ablation) | DGSI without retrieved history | Same DGSI process with historical Context removed. This isolates Context contribution; it is not a separate SOTA baseline. |

**Primary references**
- Self-Instruct, ACL 2023: https://aclanthology.org/2023.acl-long.754/
- WizardLM / Evol-Instruct, ICLR 2024: https://proceedings.iclr.cc/paper_files/paper/2024/hash/82eec786fdfbbfa53450c5feb7d1ac92-Abstract-Conference.html
- Magpie, ICLR 2025: https://proceedings.iclr.cc/paper_files/paper/2025/hash/be06e3802e9411381feece79b4d960c1-Abstract-Conference.html
- Official Magpie implementation: https://github.com/magpie-align/magpie

UltraFeedback is primarily a preference-feedback resource, not a directly equivalent instruction-construction baseline. Keep it for a separate preference-optimization study if needed.

## 3. Fair-comparison controls

1. Same frozen and permitted source pool, source excerpts and model-visible evidence for every arm. Exclude a source from all arms if its use is not permitted.
2. Same generator model/version, decoding settings, maximum output budget, per-source attempts and total token/call budget. Record deviations.
3. Same task scope and target schema. Baselines do not receive DGSI-only labels or validator feedback unless explicitly tested as an ablation.
4. Keep hidden source truth, post-event investigation facts reserved for targets, curator notes and injection labels out of every model prompt.
5. Compare equal accepted-candidate counts and report yield per 100 attempts; report both example-count and token-count matching.
6. Apply the same normalization and near-duplicate filtering after generation.
7. Blind and randomize method labels before independent scoring.
8. Freeze hashes for sources, prompts, model, generation settings, validators, rubric, holdout and outputs.
9. Development cases cannot also be final blind holdout. Any case used to tune prompts, Skill rules or scoring is retired from holdout.
10. Retain prompts, rejected candidates and reason codes, cost, time and content hashes in controlled experiment artifacts.

## 4. Evaluation

### A. Candidate-construction quality (can run before SFT)

Primary metrics:
- claim-level evidence support precision;
- evidence attribution and locator accuracy;
- unsupported-specificity / over-localization rate;
- epistemic calibration (confirmed, likely, candidate, unresolved);
- conflict reconciliation accuracy;
- action-state fidelity;
- justified abstention and discriminating next-step quality;
- historical-context transfer, rejection and temporal safety;
- hidden-truth, source-only and curator-note leakage;
- schema and serialization validity.

Secondary metrics:
- task/event-family coverage, semantic diversity, near-duplicate rate;
- accepted-candidate yield per 100 attempts;
- first-pass acceptability and human correction time;
- tokens, API cost and wall-clock time per accepted candidate.

Report critical failures separately. Critical failures include fabricated sources/ML/logs/actions, hidden-label leakage, unsupported definitive root-cause claims, historical evidence presented as current direct evidence, and false claims of expert approval or source permission. A high average score cannot cancel a critical failure.

### B. Downstream SFT comparison (conditional)

Only run when there is a separate training cohort with independent review and source-use permission, plus an untouched event-family holdout.

Compare:
- Base model (no SFT);
- Self-Instruct SFT;
- Evol-Instruct SFT;
- Magpie-style SFT;
- DGSI SFT;
- DGSI SFT + time-safe Context, paired against the same DGSI checkpoint without retrieved history.

Hold constant the base checkpoint, tokenizer, optimizer, schedule, sequence length, training tokens/steps, batch size, LoRA/full-finetune choice, seed policy and inference settings. Match both example count and token count. If a baseline cannot produce valid data under the shared evidence constraints, report its failure/yield; do not hand-repair only that arm.

Split by incident/episode, event family, source document and spacecraft/configuration. No paraphrase, variant or history-linked task may cross splits. Keep the final test set untouched until methods, prompts and rubric are frozen.

Primary downstream metrics: diagnosis correctness, evidence support, fault-source localization, affected-component identification, uncertainty calibration, conflict handling, abstention, historical transfer and action-state fidelity. Report each task family and source track separately.

## 5. Current-data boundary

The current 21 literature-derived tasks are an Evaluation Suite / review candidate, not an approved training corpus. They can test generation, validation, conflict, uncertainty, history and action-state behavior. They cannot simultaneously be the method-development seed, training set and final blind test.

The five user-provided cases are L0 source facts, not complete ML/log/context packets. AAS RUN-03F is SYNTHETIC_TEST_ONLY, not REAL or Gold. Current AI advisory scores are not independent human labels.

If no separate approved training cohort exists, the downstream SFT comparison is NOT RUN. Do not fill the gap with the 21 evaluation tasks or the AAS test fixture. Candidate-construction quality comparison may proceed only on sources permitted for that evaluation, with claims limited to that scope.

## 6. Execution sequence and stopping rule

1. Freeze this protocol and identify a permitted source pool.
2. Freeze a representative development set and separate unseen evaluation set.
3. Implement only the minimum adapters needed to reproduce M0–M4; reuse existing DGSI schemas, validators and evaluation runner.
4. Generate equal-budget candidate pools and retain rejected outputs/reason codes.
5. Blind-score construction quality and report paired per-case deltas and critical failures.
6. Run downstream SFT only if approved training data and an untouched holdout exist.
7. Publish the comparison and stop. Do not build a generic benchmarking platform for this one experiment.

This protocol does not authorize paid model calls, training jobs or source redistribution. Obtain explicit operator approval for provider, model, budget and compute before those runs.

## 7. Decision rule

DGSI is supported as a better construction method only if it improves pre-registered primary metrics over the strongest feasible baseline without increasing critical failures, with transparent cost/yield reporting. A downstream performance claim requires the separate SFT experiment and independent holdout. If gains appear only on synthetic evaluation cases, state that limitation; do not claim real-flight operational improvement.
