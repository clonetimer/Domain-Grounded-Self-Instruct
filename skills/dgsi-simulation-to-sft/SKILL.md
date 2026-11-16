---
name: dgsi-simulation-to-sft
description: Use when converting spacecraft simulation-platform design documents, subsystem/model specifications, test reports, fault-injection records, simulation run logs, and upstream ML diagnosis outputs into evidence-grounded spacecraft fault-diagnosis instruction-tuning candidates.
---

# DGSI Simulation-to-SFT Production Skill

**Status: DRAFT / candidate-generation only.** This Skill is a portable, provider-neutral production contract. It does not authorize Gold promotion, formal dataset splits, SFT export, or model training.

## Mission

Convert authorized spacecraft engineering materials into traceable diagnostic training candidates for a second-stage LLM. The LLM interprets:
- upstream ML/statistical diagnosis results;
- timestamped alarms, events, operator and engineering logs;
- spacecraft/subsystem/component configuration;
- mission phase, operating mode and recent operations;
- time-safe historical cases and source-bounded engineering knowledge.

Raw telemetry remains with upstream ML. Do not make the LLM a raw time-series detector in this workflow.

## Mandatory operating rules

1. **Evidence before generation.** Inventory and fingerprint sources before drafting any case. Never invent a missing ML result, log, configuration, test, threshold, timestamp, component, mechanism or outcome.
2. **Separate four information classes.** (a) source-observed facts, (b) simulator/model design declarations, (c) scenario or test assumptions, and (d) hidden simulator truth / post-run adjudication. Keep these classes distinct in every artifact.
3. **Hide truth from the model.** Fault injection labels, injected component/mode/time, simulator truth channels, QA-only truth, expected labels, split assignments and post-event teardown/repair outcomes must never enter the model-facing prompt unless they were legitimately available by the declared analysis cutoff and are not labels.
4. **Do not equate injection with physical validity.** An injection record proves what the simulator was configured to inject. It does not alone prove that the model represented the physical failure correctly or that the expected observable effect occurred.
5. **Distinguish symptom, fault source and affected components.** A system-level symptom or affected component is not automatically the root-cause component.
6. **Preserve uncertainty.** Keep observed, confirmed, most-likely, candidate, suspected, unresolved and not-recorded statuses distinct. Never upgrade an ML ranking score to a probability without calibration evidence.
7. **No fabricated real records.** If an AI creates illustrative logs, timestamps, ML scores or spacecraft configuration absent from source material, label each as a synthetic assumption and classify the case as literature-/design-derived synthetic, never real.
8. **No false disposal claims.** Distinguish executed action, planned action, recommended next step, conditional procedure and not recorded.
9. **History is Context, not a vote.** Include prior cases only with provenance, outcome status, as-of time and hardware applicability limitations. Similar symptoms do not prove a shared mechanism.
10. **Fail closed.** Missing critical evidence produces an incomplete candidate, an explicit abstention, or rejection—not a guessed value.
11. **Human review is mandatory.** Automated schema/CI checks are structural checks, not scientific approval.
12. **Respect rights and privacy.** Use only materials the user is authorized to share with the selected AI provider. De-identify spacecraft IDs, serials, people, credentials and restricted mission details.

## Workflow

### Stage 0 — Confirm task boundary and permissions
- Confirm that the materials may be processed by the selected AI service.
- Record source owner, permission basis, confidentiality class and redaction status.
- Confirm whether the target is ADCS, EPS, COMM, thermal or integrated spacecraft diagnosis.
- Do not upload bulk raw telemetry or the full R21 archive by default.

### Stage 1 — INGEST: build an evidence inventory
Read the supplied documents and identify:
- platform architecture and object hierarchy (spacecraft → subsystem → unit/component);
- physical/model relationships, assumptions, limits and unmodelled effects;
- test setup, baseline, test conditions, measured results and acceptance criteria;
- fault-injection configuration and simulator/run identifiers;
- execution logs, alarms, events, mode changes and timestamps;
- upstream ML result bundles and score semantics;
- spacecraft configuration and operational context;
- historical cases and source references;
- post-run QA truth and expert adjudication, stored separately.

For each extracted claim, record source file ID, SHA-256 (when available), page/section or log line/time range, exact excerpt or concise faithful paraphrase, claim type, certainty, and limitations. Do not cite a whole document when a precise page, section, table, figure or log range is available.

### Stage 2 — Classify evidence and source track
Use one of these explicit classes:
- `REAL_CASE_CANDIDATE`: an actual, authorized engineering/test episode with authentic upstream records. It is not Gold.
- `SIMULATION_CASE_CANDIDATE`: an actual run from the user's simulator, with immutable run artifacts and separate QA truth. It is simulated, not a real flight record.
- `LITERATURE_DERIVED_SYNTHETIC`: an illustrative scenario constrained by a public source.
- `DESIGN_DERIVED_HYPOTHETICAL`: a hypothetical case inferred from design/model relationships; not an observed failure.
- `SYNTHETIC_TEST_ONLY`: validator or adversarial fixture; never count as training data.
- `KNOWLEDGE_SOURCE_NOT_EVENT`: design/manual/ontology material that informs reasoning but does not describe an actual event.

Do not silently map simulation candidates to real flight cases. Use the repository's current L1 track contract where applicable; if the current schema does not yet support a class, preserve it in the intake sidecar and do not coerce it into another class.

### Stage 3 — Build L0 source/fact cards
Create one source/fact card per source event or bounded design claim group. Capture:
- exact source locator and fingerprint;
- event family and episode IDs (one report may contain multiple episodes);
- phenomenon and observed evidence;
- source-attributed cause statement and certainty;
- fault-source component;
- affected components and system effects;
- physical mechanism and assumptions;
- executed/planned/recommended/not-recorded disposal;
- missing evidence and migration constraints;
- review questions.

A design document may define a component relationship but cannot, by itself, prove that a particular flight failure occurred.

### Stage 4 — Build L1 diagnostic cases
For each candidate episode, build a truth-free model-facing input:
- upstream ML diagnosis (method/version/run ID/status/findings/score semantics/evidence IDs/limitations);
- diagnostic logs in temporal order;
- spacecraft configuration and subsystem/component context;
- mission phase, operating mode, environment and recent operations;
- historical Context only when available by analysis cutoff;
- source-bounded knowledge passages.

Keep `analysis_cutoff` explicit. Anything learned after this time belongs in the hidden target / QA sidecar, not the user prompt.

Generate task variants only when they test a genuinely different capability:
- `diagnostic_synthesis`
- `historical_case_reuse`
- `conflict_reconciliation`
- `evidence_sufficiency`
- `next_step_recommendation`
- `handover_summary`

Do not create superficial paraphrases to inflate sample counts.

### Stage 5 — Create a hidden truth / adjudication sidecar
For simulation candidates, preserve separately:
- simulator build/version and run ID;
- immutable run manifest and artifact hashes;
- injected fault ID/component/mode/time/duration/parameters;
- simulator QA truth streams and post-run physical-effect checks;
- expected observable effects and whether they actually occurred;
- independent test assertions and discrepancies;
- reviewer decision and evidence.

This sidecar is for validators and human reviewers only. It must not be copied into the model-facing input or assistant answer as an observed fact unless the task is explicitly an authorized simulation-truth reasoning task.

### Stage 6 — Generate assistant target
Produce a concise structured engineering report that:
- summarizes the observed phenomenon;
- interprets upstream ML findings without overstating them;
- separates fault source from affected components;
- links each material claim to supplied evidence IDs;
- compares plausible mechanisms and contradictory evidence;
- uses qualified certainty;
- identifies missing evidence and abstains where necessary;
- recommends diagnostic follow-up, not unrecorded completed repairs.

Do not include curator prompts, hidden labels, reviewer questions or chain-of-thought. Output conclusions and concise evidence-based rationale only.

### Stage 7 — AUDIT
Run the quality gates in `references/QUALITY_AUDIT.md`. Validate JSON against the exact repository schemas and run the repository validator. Check temporal leakage, truth leakage, source references, event-family lineage, target/input identity and split isolation. Every candidate remains `REVIEW_REQUIRED` until independently reviewed.

### Stage 8 — Package handoff
Return:
1. source inventory and evidence ledger;
2. L0 cards;
3. L1 candidate packets;
4. hidden truth/QA sidecars in a separate restricted directory;
5. validation report and blocker list;
6. human review sheets;
7. SHA-256 manifest;
8. a clear count by source class, event family, task type and review status.

Never call a candidate dataset Gold or training-ready merely because it passes schema validation.

## Required references

Read these files before production:
- `references/WORKFLOW.md`
- `references/SOURCE_INGESTION.md`
- `references/SIMULATION_TRUTH_SEPARATION.md`
- `references/GENERATION_TASKS.md`
- `references/QUALITY_AUDIT.md`
- `references/AI_HANDOFF_PROMPTS.md`
- `templates/EPISODE_INTAKE_TEMPLATE.md`

Use the repository contracts:
- `resources/source_fact_card.schema.json`
- `resources/diagnostic_case.schema.json`
- `resources/l1_task_packet.schema.json`
- `resources/diagnostic_sft.schema.json`

The L1 packet schema currently supports the existing real-candidate and literature-derived-synthetic tracks. Design-derived hypothetical candidates use the separate `schemas/design_derived_batch.schema.json` contract. Simulation-run candidates still require a separately reviewed run-receipt schema extension; preserve them in intake format and do not mislabel them.

## Final output vocabulary

Allowed status labels: `DRAFT`, `REVIEW_REQUIRED`, `INCOMPLETE_EVIDENCE`, `REJECTED`, `HUMAN_REVIEWED_CANDIDATE`.

Only the authorized DGSI release process may later admit a record for training. This Skill cannot authorize training.
