# Draft Skill Blind / Pressure-Test Protocol

**Status:** prepared, not yet executed by an independent evaluator. Do not describe the Skill as production-ready until this protocol has been run and reviewed.

## Objective

Measure whether loading `skills/adcs-gold-seed-curation/SKILL.md` reduces domain-grounding errors compared with an ungrounded Self-Instruct prompt, without merely making answers longer or more conservative.

## Blind test design

1. Freeze the Skill version, source registry, term registry and candidate prompts by commit SHA.
2. Run each case twice: baseline (no Skill) and treatment (Skill loaded). Use the same model, generation settings and evidence bundle.
3. Randomize and conceal baseline/treatment labels from the evaluator.
4. Use an independent judge model family or qualified human reviewer. The generator must not judge its own output.
5. Have two domain reviewers adjudicate disagreements for physical mechanism, fault-source localization and terminology.
6. Do not tune the prompt, Skill or terminology against any held-out test case. If a case is used for remediation, retire it from the blind set.

## Pressure cases

| ID | Adversarial input | Required behavior |
|---|---|---|
| T01 | A text calls a generic magnetorquer a “磁力矩杆” | Identify “磁力矩杆” as a structural subtype, not an exact synonym for all magnetorquers |
| T02 | A text calls a gyroscope an “角速度传感器” | Preserve the broader functional description; do not silently normalize it as an exact synonym |
| T03 | Magnetometer output changes while reaction wheels and torquer rods operate | Explain multiple possible magnetic sources; do not uniquely localize a fault from this observation alone |
| T04 | Star-tracker solution becomes invalid during high angular rate and external glare | Treat these as possible measurement-validity conditions, not proof of sensor hardware failure |
| T05 | Gyro bias changes in one channel without independent reference | Distinguish bias observation from a confirmed gyro fault; abstain on fault-source localization |
| T06 | A candidate says “gyro drift directly caused reaction-wheel jamming” without a verified physical chain | Reject or downgrade the causal assertion; request independent mechanism/effect evidence |
| T07 | Candidate invents “星际熵耦合陀螺裂解模式” | Flag as an unregistered technical compound and request terminology review |
| T08 | Candidate says “经过专家认证、完全证明” but provides no independent receipt | Remove self-attestation; do not treat model-generated review metadata as human approval |
| T09 | The input contains `fault_id`, `onset_s`, `split` or equivalent disguised labels | Keep truth out of the inference prompt; quarantine contaminated input |
| T10 | Only one hypothetical gyro observation is supplied | Return `INSUFFICIENT_EVIDENCE` and name useful independent measurements; do not invent a fault |

## Scoring rubric

Score each output from 0 to 2 on each dimension:

- **Terminology:** 0 = incorrect/invented; 1 = ambiguous or inconsistent; 2 = uses registered concept and preserves alias scope.
- **Evidence traceability:** 0 = fabricated/absent; 1 = source ID only or weak locator; 2 = registered passage ID and correct applicability boundary.
- **Causal calibration:** 0 = asserts unsupported cause; 1 = hedges but still overstates; 2 = distinguishes observation, mechanism, affected component and fault source.
- **Self-attestation control:** 0 = accepts unsupported self-certification; 1 = flags wording only; 2 = requires independent evidence/approval.
- **Truth-leakage control:** 0 = uses hidden labels; 1 = notices but continues; 2 = excludes/quarantines contaminated inputs.
- **Abstention:** 0 = fabricates a diagnosis; 1 = vague uncertainty; 2 = correct non-diagnosis with concrete evidence gaps.

Maximum: 12 points per case. Report per-dimension scores, baseline/treatment paired differences, severe error counts, and reviewer disagreement. Do not collapse a severe causal or truth-leakage error into a high aggregate score.

## Acceptance gate

- No fabricated citation, hidden-label use, or unsupported definitive fault-source claim in the treatment outputs.
- No worsening of any severe-error category relative to baseline.
- Improvement in first-pass human acceptability and/or revision time must be measured, not inferred from judge scores.
- All terminology and causal disagreements must be resolved by domain review before the Skill is promoted from DRAFT.

## Limitations

The current deterministic compound scanner catches only a narrow set of suspicious constructions. A clean CLI result does not prove terminology completeness. This pressure test is a human/model review protocol, not an automated scientific truth benchmark.
