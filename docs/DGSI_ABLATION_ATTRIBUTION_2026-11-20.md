# DGSI ablation attribution audit — 2026-11-20

**Classification:** coordinator analysis only; `not_for_sft=true`.  
**Source snapshot:** `fed424e76e25df77e553c3be683f1ca3546090e2` (PR #186).  
**Frozen visible-input manifest:** `d36cacfb898ca249cd199abd634fb23acad961d3ced946c8360abf6aaad10368`.

## Purpose

This audit does not rerun generation, alter any evaluation case, change rubric weights, or reinterpret the existing GPT reviews. It makes the component contrasts and their limits explicit before any later experiment is designed.

## Existing comparison (unchanged)

| Arm | Configuration | Mean / 20 | Paired accepts | Critical-failure candidates |
|---|---|---:|---:|---:|
| M4 | Original DGSI | 19.750 | 3/4 | 0 |
| M5 | DGSI + evolution only | 19.875 | 3/4 | 0 |
| M6 | DGSI + three-candidate selection only | 20.000 | 4/4 | 0 |
| M7 | DGSI + evolution + selection | 19.625 | 2/4 | 0 |

The same four frozen cases were used for every arm. They cover three task types and four event families, but only **two connected source-document clusters** (three TROPICS cases and one NASA case).

## Ablation deltas — descriptive, not causal

| Contrast | Mean-score delta | Paired-accept delta | Honest reading |
|---|---:|---:|---|
| M5 − M4 | +0.125 | 0 | Tiny score increase; no acceptance gain |
| M6 − M4 | +0.250 | +1 | Best observed arm, but baseline policy differs |
| M7 − M4 | −0.125 | −1 | Combined arm underperformed original DGSI |
| M7 − M5 | −0.250 | −1 | Adding selection to evolve-only was worse in this run |
| M7 − M6 | −0.375 | −2 | Adding evolution to select-only was worse in this run |
| M6 − M5 | +0.125 | +1 | Select-only ranked higher descriptively; not a clean isolated effect |

All arms had zero detected critical-failure candidates. Fourteen of 24 candidates met paired development acceptance; five reviewer disagreements remain recorded.

### Important confounding

M5/M6/M7 share a strengthened evidence-role and scope policy. M4 is the original DGSI policy. Therefore M5/M6/M7 versus M4 mixes recipe changes with policy refinement.

M5, M6 and M7 are practical ablation arms, but this is **not a fully identified 2×2 factorial** because the same-policy no-evolution/no-selection control is missing. Candidate counts and prompt structures also differ; exact token/compute matching was not available.

### Selector-specific result

All four M6 cases and all four M7 cases selected candidate `I1` under the deterministic tie rule. Candidate scores were generator self-reports. Consequently, this run does **not** demonstrate a benefit from choosing a later instruction candidate, nor does it isolate a learned selector effect.

## Recommendation

Keep `select` as an optional development recipe because it was the best observed arm in this bounded run. Keep baseline as the default. Do not make `evolve-select` the default: it scored below M4, M5 and M6 here.

Do not claim statistical superiority, global optimality, real-flight transfer or downstream SFT gain. These are GPT advisory scores on visible synthetic materials, not human expert adjudications.

## Next experiment — only after preregistration

To identify component effects, use a new, untouched set of source-document clusters and a same-policy 2×2 design:

1. Strengthened DGSI policy, no evolution/no selection.
2. Same policy + evolution only.
3. Same policy + three-candidate selection only.
4. Same policy + evolution + selection.

Freeze input bytes, source-cluster membership, prompts, rubric, candidate budget, reviewer instructions and stopping rule before generation. Use independent blinded reviewers; record actual compute/token telemetry if available. Do not tune on this four-case development bundle. Run one preregistered round and report every arm, invalid output, disagreement and zero/negative gain.

## Scope and safety

This is a read-only attribution audit. It does not add or promote SFT examples, assign official splits, claim human review, authorize Gold, call external model APIs, or start fine-tuning. The original PR #186 experiment files remain untouched.
