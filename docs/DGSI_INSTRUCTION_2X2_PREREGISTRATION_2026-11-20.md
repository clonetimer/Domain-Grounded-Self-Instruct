# DGSI 2x2 component experiment preregistration

**Status:** PREREGISTERED_DESIGN_ONLY / NOT_RUN  
**Classification:** coordinator-only; `not_for_sft=true`  
**Depends on:** PR #187 attribution audit and PR #186 bounded refinement implementation.

## Question

Under one fixed DGSI evidence/scope policy, what are the separate and combined effects of (a) instruction evolution and (b) three-candidate instruction selection?

This design does not claim that the current four-case comparison answers that question. In the current run M4 uses the original policy while M5/M6/M7 use strengthened scope/evidence policy; M5/M6/M7 therefore are practical ablations, not a clean factorial.

## Frozen 2x2 arms

| Arm | Evolution | Three-choice selection | Role |
|---|---:|---:|---|
| A | off | off | same-policy DGSI control |
| B | off | on | selection-only ablation |
| C | on | off | evolution-only ablation |
| D | on | on | combined optional strategy |

The two ablations are B and C. D is the combined strategy. Existing CLI recipes remain optional; `baseline` remains the default.

## Holdout and leakage rule

All four arms must use exactly the same case IDs, source-document-cluster membership, visible input bytes, target schema and case order. The case manifest and byte hashes are frozen before generation.

Use new, untouched source-document clusters for this preregistered run. The four cases from the 2026-11-19 comparison and their connected source documents are development-only and are ineligible for this confirmatory run. They may be replayed descriptively, but must not be relabelled as fresh holdout.

No case may be added, removed, replaced, reweighted or reclassified after any generation or review begins. If sufficient independent clusters cannot be sourced, status remains NOT_RUN; do not substitute familiar cases to fill the quota.

## Controls held constant

- Same strengthened DGSI evidence/scope policy in all four arms.
- Same model family/configuration and fixed generation budget per case, as far as the host environment allows; record actual token/compute telemetry when available. If unavailable, state NOT_MEASURED rather than claiming equal compute.
- Same source facts, ML-result fields, logs, mission context, history context, target schema and prompt-visible evidence.
- Evolution may change only the task instruction; it may not add or mutate facts, ML scores, timestamps, logs, equipment configuration, historical records or task type.
- Selection generates exactly three instruction candidates. Candidate ranking is instruction-only and cannot inspect reference answers, other arms, evaluator outputs or hidden evidence.
- The no-selection arms generate one instruction. All arms produce exactly one formal target per case.
- Two independent, method-blind reviewers use the existing frozen rubric. Keep reviewer disagreement; no majority override or score repair.
- No retries, regeneration, post-hoc editing, candidate dropping, threshold changes or evaluator prompt changes.

## Analysis plan

Report per arm and per case:
- raw rubric dimensions and total;
- paired reviewer decisions and disagreements;
- critical failure count and type;
- invalid/rejected candidate counts;
- instruction candidate count and selected candidate ID;
- token/compute telemetry, or NOT_MEASURED;
- source-document-cluster weighted mean as well as case-weighted mean.

Report the evolution main effect, selection main effect and interaction contrast descriptively:
- evolution effect = mean(C,D) - mean(A,B)
- selection effect = mean(B,D) - mean(A,C)
- interaction = (D-C) - (B-A)

Do not infer statistical significance unless the prespecified sample size and analysis support it. Do not select a winner by mean score alone if a critical failure occurs. Publish all four arms, all cases, all disagreements and all failures, including zero/negative gains.

## Stop rule

Run one preregistered round and stop regardless of ranking. Do not tune prompts or thresholds on these results. Any later iteration requires a new preregistration and new untouched source-document clusters.

## Current evidence boundary

The existing four-case results remain unchanged: M4 19.750/20 (3/4 paired accepts), M5 19.875 (3/4), M6 20.000 (4/4), M7 19.625 (2/4). All M6/M7 selections chose I1, so selector-specific benefit was not demonstrated. These results are descriptive GPT advisory scores on visible synthetic development material, not human expert clearance, statistical superiority, real-flight transfer or downstream SFT gain.

**No new generation, model calls, evaluation changes, training splits, Gold promotion or fine-tuning are authorized by this preregistration.**


## Pre-generation manifest gate

Before any authorized run, prepare a manifest conforming to `dgsi-2x2-run-manifest.v1` and validate it offline:

```bash
python evaluation/refinement_20261120/validate_factorial_manifest.py path/to/run-manifest.json
```

The validator requires the four exact arms, identical opaque case IDs and input/schema hashes in every arm, one shared policy hash, three candidates only in selection-enabled arms, at least two independent source-document clusters, and explicit rights/exposure/escrow/freeze gates. It rejects answer/reference/score fields and previously exposed source clusters. A successful validation means comparability metadata passed only; it does not launch generation or authorize model calls.
