# DGSI Skill effectiveness report — evidence-based closeout snapshot

**Report date:** 2026-11-18  
**Product version inspected:** 0.2.0-rc.4  
**Scope:** existing repository evidence and the AAS RUN-03F integration demonstration. This report distinguishes actual test evidence from unrun experiments.

## Executive finding

DGSI has demonstrated a functioning source-grounded candidate-production workflow, review handoff, structural validation, and one end-to-end ingestion example from an actual AAS software test run. It has **not yet demonstrated, through an independent live blind evaluation, that DGSI outperforms SOTA instruction-data construction methods or improves downstream SFT diagnosis**.

The current case collections are Evaluation Suite fixtures, not a formal training dataset. No SFT training or model-effectiveness claim is made.

## 1. Product and evaluation assets

| Asset | Current evidence | Correct interpretation |
|---|---|---|
| Portable DGSI Skill | VERSION 0.2.0-rc.4; previous clean-room package builds and hash checks recorded in project history | Candidate-generation/data-curation product; closeout package still requires final release verification |
| L1 REV1 suite | 21 literature-derived synthetic tasks, 9 event families, 7 primary source groups | Evaluation/review candidate, not 21 independent incidents or training rows |
| ADCS/EPS pressure suite | 13 cases: 6 ADCS + 7 EPS | Tests adjacent domain curation Skills; not a direct DGSI SFT benchmark |
| ADCS/EPS process holdout | 8 cases: 4 ADCS + 4 EPS | Small process holdout; not guaranteed unseen to foundation-model pretraining |
| User-supplied cases | 5 L0 source-fact records | Useful source-faithfulness fixtures; incomplete L1 input and not Gold |
| AAS RUN-03F | One executed score-only integration example; 24 synthetic inputs, 24 anomaly predictions, no ground truth and empty metrics | Demonstrates upstream ML result ingestion and conservative second-stage interpretation; SYNTHETIC_TEST_ONLY |

## 2. Observed effectiveness evidence

### 2.1 DGSI-specific integration demonstration

The AAS RUN-03F fixture demonstrates:
- exact linkage to the source AAS test archive and score-only task;
- preservation of the model ID, algorithm, feature name/unit, prediction labels, threshold metadata, scaling metadata and source hashes;
- explicit preservation of `ground_truth_available=false` and `metrics={}`;
- no physical root-cause localization and no match to any of the five REAL L0 cases;
- a diagnostic draft that requests unit, scaling, threshold semantics and independent-channel checks.

Important correction to the first draft: the values around 49.56–50.55 are **per-sample scores**, not a threshold array. The actual decision threshold is 2.5 (also represented as 24 per-sample decision thresholds of 2.5). The earlier integration note that called the score vector a threshold array is superseded. The source chart trace distinguishes `scores`, `decision_threshold` and `decision_thresholds`.

This is a useful integration/abstention example, not a model-accuracy result. The field mapping correction is recorded in [AAS_RUN03F_INTEGRATION_FIELD_MAPPING_CORRECTION_2026-11-18.md](AAS_RUN03F_INTEGRATION_FIELD_MAPPING_CORRECTION_2026-11-18.md); use the corrected local demonstration package, not the superseded original.

### 2.2 Existing exploratory A/B evidence (adjacent ADCS/EPS curation Skills)

The repository records a same-model, same-session exploratory comparison on 7 public-literature cases:
- baseline: 48/84 rubric points;
- Skill treatment: 77/84 rubric points;
- paired difference: +29 rubric points.

This result is explicitly exploratory. Generator and evaluator were the same GPT-6 session; zero live API calls; no independent judge family; outputs were compact summaries rather than complete structured seed records. It concerns ADCS/EPS curation Skills, not a direct DGSI-vs-Self-Instruct construction benchmark. It must not be reported as independent proof of DGSI effectiveness or generalization.

### 2.3 Automated engineering checks

Repository CI and package tests validate schema, provenance, source-bound evidence, serialization, packaging and adversarial rejection behavior. These are implementation-quality checks. Test pass counts are not diagnostic accuracy, expert acceptance or data-construction superiority metrics.

## 3. Metrics: observed vs. not measured

| Metric | Current evidence | Status |
|---|---|---|
| Suite task coverage | 21 L1 candidate tasks across 6 task types; 13 pressure cases; 8 process holdouts | Measured inventory |
| AAS result-ingestion fidelity | 24/24 predictions preserved; ground truth unavailable; no root-cause localization | Demonstrated for one synthetic fixture |
| Schema/serialization | Existing automated tests and clean-room package tests | Engineering validation only |
| Claim-level evidence precision | No blinded human-scored DGSI comparison | NOT MEASURED |
| Fault-source localization accuracy | No independent adjudicated evaluation | NOT MEASURED |
| Causal over-localization rate | Exploratory examples only; no formal DGSI-wide scoring | NOT MEASURED |
| Uncertainty/abstention accuracy | One AAS example and synthetic challenge cases; no independent aggregate | NOT MEASURED |
| Conflict reconciliation accuracy | Test cases exist; no independent scored evaluation | NOT MEASURED |
| Historical Context transfer | Coverage and chronology checks exist; no blind human outcome evaluation | NOT MEASURED |
| Action-state fidelity | Candidate examples and schema checks exist; no independent aggregate | NOT MEASURED |
| First-pass human acceptability / correction time | No completed paired human study | NOT MEASURED |
| Generation yield / cost per accepted candidate | No matched-budget generation run | NOT MEASURED |
| DGSI vs SOTA construction quality | Protocol drafted; no matched generation arms executed | NOT RUN |
| Downstream SFT benefit | No approved training corpus and no training run | NOT RUN |



## 4.1 Method-level comparison from published papers (not a DGSI experiment result)

| Method | Published construction mechanism | What it contributes to the comparison | Domain-grounding distinction to test |
|---|---|---|---|
| Self-Instruct (ACL 2023) | Bootstrap instructions, inputs and outputs from a language model; filter invalid or similar samples | Basic seed-driven self-generation baseline | Does source closure and explicit evidence/target separation reduce unsupported claims? |
| Evol-Instruct / WizardLM (ICLR 2024) | Iteratively rewrite seed instructions into more complex instructions and mix evolved samples | Complexity/depth and breadth evolution baseline | Does complexity evolution improve diagnostic coverage without increasing false causal specificity? |
| Auto-Instruct (Findings EMNLP 2023) | Generate diverse candidate instructions and rank them with an instruction-quality scorer trained over existing tasks | Generation-plus-ranking baseline | Does generic instruction ranking select technically plausible but weakly grounded spacecraft cases? |
| Magpie (ICLR 2025) | Prompt aligned models with pre-query conversation templates to elicit user queries and responses | Aligned-model self-synthesis baseline | Does open-ended query synthesis preserve required ML/log/context evidence and operational constraints? |
| DGSI | Source-bound L0/L1 facts, field provenance, model-visible ML/log/context packet, history cutoff, evidence validation and explicit uncertainty | Proposed domain-grounded construction method | Tests whether domain grounding improves evidence support, action fidelity and abstention under matched budgets |

The published papers study broad instruction/alignment data and report results on their own models, data and benchmarks. Their headline scores are **not directly comparable** to DGSI and are not copied into this project's result table. The empirical comparison remains NOT RUN until matched arms are generated and blind-scored.

## 4. SOTA comparison status

The preregistered comparison includes Self-Instruct, Evol-Instruct/WizardLM, Auto-Instruct, Magpie-style adaptation and DGSI. The first executable study should compare candidate-construction quality under a shared, permitted source pool and matched generator/model/token budget.

No live generation calls have been made for this comparison. No result should be fabricated from existing candidate counts or from the adjacent ADCS/EPS exploratory pretest.

Downstream SFT comparison remains NOT RUN because there is no separately approved training cohort and untouched event-family holdout. The 21 evaluation tasks and AAS fixture must not be used to fill that gap.

## 5. Limitations and closeout decision

**What is demonstrated**
- reusable DGSI candidate-production and review workflow exists;
- evidence/target separation and conservative status handling are represented in schemas and examples;
- AAS score-only execution evidence can be projected into a DGSI-style second-stage input without claiming a physical fault;
- evaluation fixtures cover synthesis, conflict, insufficiency, history, handover and upstream-result ingestion.

**What is not demonstrated**
- independent domain-expert acceptance of the 21-task cohort;
- rights-cleared SFT corpus;
- DGSI superiority over SOTA construction methods;
- downstream fine-tuning gains on unseen event families;
- operational improvement on real flight diagnosis.

**Closeout decision:** the Skill can be packaged and handed off as a candidate-generation/evaluation product, subject to final clean-environment release verification. The formal SFT dataset and SOTA/downstream model-effectiveness claims remain separate future results, not implied by this product release.
