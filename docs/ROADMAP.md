# Domain-Grounded Self-Instruct — delivery roadmap

## Product objective

Build a high-quality supervised fine-tuning dataset for a spacecraft fault-diagnosis LLM that performs **diagnostic interpretation and experience reuse from upstream ML diagnosis outputs, diagnostic logs and spacecraft/mission context**.

The LLM is not the primary raw-telemetry detector. Upstream ML/statistical methods process telemetry and produce anomaly/fault candidates, localization, residual summaries and evidence references. DGSI teaches the LLM to interpret those outputs with operational context, historical cases and reviewed domain knowledge, resolve evidence conflicts, assess uncertainty and produce engineering diagnosis reports.

## System responsibility boundary

- **ML / signal diagnosis:** raw telemetry, time series, anomaly detection, feature/residual calculation, fault candidate scoring and component localization.
- **LLM / DGSI SFT:** consume structured ML diagnosis results, diagnostic logs, operational history, spacecraft configuration, mission mode, historical cases and knowledge evidence. Produce evidence-bounded synthesis, experience reuse, conflict reconciliation, sufficiency assessment and next-step recommendations.
- **Expert / engineering review:** approve, correct or reject the LLM report and preserve the reviewed decision as an experience record.

Raw telemetry is not the default LLM SFT input. A reference to an upstream analysis artifact may be retained for traceability, but waveform arrays and high-rate telemetry are not embedded in the prompt. ML scores must retain their semantics and calibration status; they are not probabilities by default.

## Phase 0 / D0: inventory real diagnosis assets

**Deliver:** redacted inventory of diagnostic reports, ML result bundles, alarms/events, engineering logs, spacecraft configuration/context, historical case records, reviewed outcomes and source lineage.

Prioritize existing AstroGraph diagnostic outputs and history over new simulation campaigns. Do not presume R21's 56 GB of telemetry is itself an LLM training corpus. Identify which upstream ML diagnosis outputs and linked logs/context are available and reviewable.

**Exit:** an asset matrix with counts, formats, source groups, review state, privacy/IP restrictions, field coverage and missing context. No raw private telemetry or reports are copied into this public repository.

## Phase 1 / P1: grounded curation foundation

**Deliver:** public source registry and passage index, separate ADCS/EPS terminology catalogs, domain curation Skills, fault/effect catalog, telemetry/diagnosis-result terminology, versioned schemas, offline validator, adversarial tests and literature-based evaluation suite.

The existing dgsi-seed.v1 is retained as a legacy candidate/curation contract. The new LLM-facing product contracts are:
- resources/diagnostic_case.schema.json — structured diagnosis + logs + context + historical experience + reviewed target.
- resources/diagnostic_sft.schema.json — chat-style SFT export with source-group provenance and human-review state.

**Exit:** structural and rule-based preflight passes; factual correctness and causal claims require independent domain review. Skills remain DRAFT until independent evaluation and qualified review.

## Phase 2 / P2: upstream diagnosis evidence and provenance

Retain the local-only Basilisk receipt adapter to verify where upstream ML evidence came from, the simulator/run provenance, physical-effect checks and truth separation. P2 is an **upstream evidence lineage gate**, not a requirement to place telemetry in the LLM prompt.

For each ML diagnosis result bundle, preserve method/model/version, input dataset/run references, analysis scope, output candidates, score semantics/calibration, supporting evidence IDs, known limitations and data-quality status. Link it to diagnostic logs and spacecraft context. Never leak simulator injection truth or test labels into the LLM input.

## Phase 3 / P3: context-grounded Self-Instruct pilot

Generate candidate diagnosis-context cases from reviewed historical diagnostic records and existing ML diagnosis outputs. The LLM input comprises the machine diagnosis result, diagnostic logs, spacecraft configuration, mission phase/operating mode, recent operations, maintenance history, relevant prior cases and source-bound knowledge passages. It does not comprise raw telemetry.

Task families:
- diagnostic_synthesis
- historical_case_reuse
- conflict_reconciliation
- evidence_sufficiency
- next_step_recommendation
- handover_summary

Start with 20 manually curated cases to test schema and task coverage. Then target a 300–500 example controlled SFT pilot if sufficient approved source cases exist. Do not force the target count by fabricating cases or copying paraphrases.

## Phase 4 / P4: expert correction and quality evaluation

Present source diagnosis output, logs, context, retrieved history, candidate report, atomic claims and evidence locators side-by-side. Expose accept/edit/reject with append-only audit trail.

Measure interpretation correctness, evidence attribution, fault-source versus affected-component distinction, historical-case applicability, conflict handling, uncertainty calibration, appropriate abstention, next-step actionability, first-pass approval, correction time and final accepted yield.

## Phase 5 / P5: freeze and fine-tuning export

Freeze only human-approved Gold examples. Keep model-generated Silver drafts separate and out of formal SFT. Split by incident/episode, historical case family, spacecraft/configuration and source-document group; all logs, summaries, paraphrases and derived variants from one incident remain in one split. Export chat messages and provenance sidecars. No release until independent evaluation confirms suitability.

## Role of simulation and R4

Basilisk, SatAgentSimulation, R21 and R84/R4 remain important upstream sources:
- validate and produce ML diagnosis results;
- supply controlled physical-effect evidence;
- create additional diagnostic episodes where historical logs are sparse;
- support lineage and audit of the upstream ML output.

They do not change the LLM's task into raw-telemetry diagnosis. R4 multi-wheel experiments may proceed as an upstream ML/evidence campaign, but they must not block the first DGSI pilot if existing reviewed diagnostic result bundles and context are sufficient.

## Model-effectiveness experiment

Compare the same base LLM and identical held-out diagnosis-context packets:
1. base LLM;
2. ordinary Self-Instruct SFT;
3. DGSI context-grounded SFT.

Evaluate report interpretation, evidence correctness, experience transfer, conflict handling, fault-source reasoning, uncertainty/abstention and actionable follow-up. This measures the incremental value of DGSI SFT, not the upstream ML detector's telemetry accuracy.

## Non-goals

- Do not train the LLM to reproduce the upstream ML detector from raw telemetry in this project.
- Do not represent ML screening scores as calibrated probabilities without calibration evidence.
- Do not convert an ML candidate into confirmed root cause without corroborating context/evidence.
- Do not treat a historical unresolved case as a confirmed precedent.
- Do not treat simulation injection truth as an LLM-visible fact.
