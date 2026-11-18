# Exploratory ADCS + EPS Model-Internal A/B Pretest

**Status: EXPLORATORY ONLY — NOT A FORMAL INDEPENDENT BLIND EVALUATION**

Date: 2026-11-14  
Model: GPT-6 in the current ChatGPT session  
Cases: 7 public-literature stress cases (3 ADCS, 4 EPS)  
Live Responses API calls: 0  
Independent judge model family: not used

## 1. What was tested

For each case, two concise candidate answer summaries were drafted under:
- **Baseline:** task and public source facts, without the domain Skill.
- **Treatment:** same task and source facts, with the relevant ADCS or EPS Skill constraints.

Candidate summaries were assigned anonymous A/B labels using the same deterministic case-order seed as the runner. The evaluator scored the anonymous text against the six-dimension rubric before mapping scores back to the hidden conditions.

This was a same-model, in-context exploratory exercise. The generator and evaluator were both GPT-6 in one conversation. It is therefore **not** independent-model blind testing, not a live API run, and not evidence of a population-level quality improvement. The baseline/treatment outputs were concise prose summaries rather than complete JSON seed records.

## 2. Cases and observed failure patterns

| Case | Domain | Baseline failure pattern observed in the paired summary | Skill-treatment behavior |
|---|---|---|---|
| A01 NEOSSat magnetometer | ADCS | Conflated residual magnetic dipole disturbance with the cause of magnetometer failure | Separated sensor failure, disturbance source and momentum-accumulation effect |
| A03 NEOSSat X-wheel | ADCS | Upgraded a suspected electrical cause to a confirmed fault and treated co-powered rate-sensor loss as sensor failure | Preserved suspected status and represented rate-sensor loss as operational coupling |
| A04 gyro-bias FDD model | ADCS | Converted an additive measurement-fault model into a claim of actual gyro hardware failure | Kept model formulation, bias estimation and hardware diagnosis distinct |
| E01 IMAGE SSPC instant trip | EPS | Upgraded the FRB's likely SEU explanation to a definitive cause | Preserved likely status and explained physical switch/status-bit mismatch |
| E03 NOAA-13 solar-array bus | EPS | Converted a surmised bolt/insulation mechanism into a confirmed physical cause | Separated observed no-charge telemetry from the review's inferred mechanism |
| E06 WMAP battery collapse | EPS | Promoted electrolyte bridging consensus theory to confirmed root cause | Preserved unresolved root cause and the theory's status |
| E07 IMAGE counterfactuals | EPS | Turned alternative battery/array failure analyses into candidate actual IMAGE faults | Kept the battery/array cases as counterfactuals unsupported by the observed telemetry |

## 3. Rubric scores

Each dimension is scored 0–2: terminology, evidence traceability, causal calibration, self-attestation control, truth/counterfactual control, and abstention/uncertainty.

| Case | Baseline | Skill treatment | Main score difference |
|---|---:|---:|---|
| A01 | 7/12 | 11/12 | Unsupported cross-link between disturbance source and sensor failure removed |
| A03 | 7/12 | 11/12 | Suspected cause and coupled sensor behavior correctly qualified |
| A04 | 6/12 | 11/12 | Model assumption no longer presented as observed hardware fault |
| E01 | 7/12 | 11/12 | Likely SEU explanation no longer presented as conclusive |
| E03 | 7/12 | 11/12 | Surmised mechanical/electrical path no longer presented as confirmed |
| E06 | 7/12 | 11/12 | Consensus theory no longer presented as definitive root cause |
| E07 | 7/12 | 11/12 | Counterfactual failure analyses no longer treated as observed faults |
| **Total** | **48/84** | **77/84** | **+29 rubric points in this exploratory set** |

The compact candidate summaries did not include explicit registered passage IDs in their visible prose, so evidence-traceability received only 1/2 in both conditions. This was a useful procedural finding: source-passage traceability must be enforced in the generated structured record, not merely assumed from the prompt context.

## 4. Engineering action taken from this pretest

The blind runner's candidate JSON Schema now requires at least one registered source_passage_id for every generated claim. The offline seed validator also rejects a claim that references neither evidence_ids nor source_passage_ids. Regression tests cover both requirements.

## 5. What this result does and does not mean

It indicates that the Skills encode useful guardrails for the specific public-literature failure patterns tested here. It does **not** establish:
- that an independent model family would produce the same ranking;
- that the live Responses API runner has been executed;
- that the Skill improves first-pass human acceptance on naturally generated data;
- that 91.7% is a real accuracy or acceptance rate;
- that the source interpretations have been approved by a qualified ADCS/EPS expert.

## 6. Formal next gate

Run the 13-case suite with the live Responses API runner using the same generator model for baseline and treatment, a separately declared judge model family, randomized A/B order and local-only output. Then have qualified ADCS/EPS reviewers adjudicate all critical causal, component-localization and source-interpretation findings. Keep both Skills DRAFT until that work is complete.
