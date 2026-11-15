# AstroGraph diagnosis-result mapping and intake review

## Intended data flow

`raw telemetry -> upstream ML diagnosis -> AstroGraph result bundle -> DGSI context packet -> LLM synthesis -> expert-reviewed report`

DGSI does not re-run the upstream detector. It consumes the structured diagnosis result and links it to logs, mission context, historical cases and reviewed knowledge.

## Supported source contracts inspected

### 1. AstroGraph unified diagnosis result

Source contract: `protocols/diagnosis/unified_diagnosis_result.schema.json`.

Relevant fields:
- `case_id`, `input_mode`, `backend`, `status`, `resolution_basis`;
- `primary_effect_id`, `primary_subsystem`, `primary_component`;
- `diagnostic_evidence[]` with evidence ID, field, statistic, values/delta/threshold and interpretation;
- `engine_runs[]` with engine identity, eligibility, execution status, status, reason codes and detected effect IDs;
- `candidates[]` with effect ID, supporting/contradicting engines, screening score and evidence summary;
- `data_quality[]`, `labels_used`, `truth_used`, `deterministic` and `claim_boundary`.

Mapping:
- Unified status is mapped to a DGSI upstream status, not to a confirmed fault label.
- Candidate effect IDs become `FAULT_CLASS` findings with their screening scores.
- Screening scores are explicitly marked as deterministic evidence-coverage scores, not calibrated probabilities.
- Diagnostic evidence IDs are retained; numeric telemetry arrays are not imported.
- `labels_used=true` or `truth_used=true` causes rejection from LLM-facing context.
- Backend is retained as producer method when no more specific method identifier is supplied; missing version is recorded as `NOT_RECORDED`, never guessed.

### 2. Legacy external diagnosis result

Observed in `examples/platform_acceptance_cases_v1/TC01...` and `examples/result_log_review/`:
- `case_id`, `subsystem` / `equipment_scope`;
- `candidate_fault_id` or `candidate_faults[]`;
- `diagnostic_summary`;
- `review_status`, commonly `UNVERIFIED`.

Mapping:
- A single candidate becomes a candidate finding, not a diagnosis confirmation.
- Multiple candidates remain separate.
- A `NORMAL` result with no candidate remains normal.
- No score, model version or evidence IDs are fabricated when the legacy result omits them; the adapter records these limitations.
- A log keyword cannot create a new ML candidate when the upstream result has none.

Implementation: `src/dgsi/astrograph_adapter.py`.

## Diagnostic logs: acceptance gate

Before a real source packet can enter expert Gold review, check:

1. **Source integrity:** original report/log references, immutable source hashes, source owner and permitted use.
2. **Case identity:** stable incident/episode ID; all logs, summaries and report revisions linked to one episode group.
3. **Temporal coherence:** every packet has an explicit timezone-aware analysis_cutoff; timestamps and time zones normalized; event order consistent; logs after the decision cutoff are rejected; no post-outcome information leaks into the as-of diagnosis context.
4. **Algorithm provenance:** upstream method/model/version, analysis scope, run ID, status, candidate list, score semantics/calibration and known limitations.
5. **Log authenticity:** distinguish onboard alarm, operator note, engineering interpretation, maintenance action and later retrospective conclusion. Preserve author role and timestamp where available.
6. **Context sufficiency:** spacecraft/configuration, subsystem/component mapping, mission phase, operating mode, recent operations and relevant constraints.
7. **Historical experience:** prior case outcome must be CONFIRMED, PARTIALLY_CONFIRMED, REJECTED, UNRESOLVED or UNKNOWN; transfer limitations must be explicit.
8. **Evidence boundaries:** support, contradiction and missing evidence are separate. A reference passage can support general mechanism knowledge but cannot confirm a specific incident by itself.
9. **Truth and label separation:** no injection truth, hidden evaluation labels, test answers or post-hoc adjudication in the LLM user input.
10. **Deduplication and split:** incident/episode family, spacecraft/configuration, source document and report revision grouped before split. No row-level split or paraphrase leakage.
11. **Expert target quality:** target report independently reviewed; reviewer identity and timestamp captured; unresolved conclusions remain unresolved.
12. **Privacy/IP:** redact spacecraft identifiers, operational details and restricted content before any public export. Public DGSI stores schemas, synthetic fixtures and aggregate inventories only.

## Readiness gate

`validate_diagnostic_case()` checks packet structure and semantic boundaries.

`evaluate_case_readiness()` checks whether a packet can proceed to expert Gold review:
- upstream diagnosis run reference and source hashes;\n- diagnostic logs have timestamps and do not exceed the analysis cutoff;\n- no hidden injection truth, labels or expected answers are present in the LLM input;
- recorded algorithm/method version;
- diagnostic logs;
- spacecraft configuration and mission context;
- reviewer identity and timestamp if already marked APPROVED.

It returns `READY_FOR_EXPERT_GOLD_REVIEW` or `BLOCKED`, and always `gold_eligible=false`. Only the authorized expert workflow may grant Gold approval.

## Current repository-visible source verdict

The AstroGraph TC01–TC09 acceptance cases are explicitly synthetic. They are suitable for testing normalization, conflict handling, abstention and safe report behavior. They are not actual historical spacecraft cases and their `expected_output.json` files are workflow assertions, not expert-authored SFT targets.

The D3 reaction-wheel dataset manifest describes 90 completed engineering simulation runs under E0 assumptions. It may support upstream ML development and synthetic diagnosis-result generation, but it is not real flight history or independently confirmed operational experience.

No repository-visible real spacecraft diagnosis/log/context packet with verifiable expert disposition was established in the inspected sources. Actual restricted/local case stores require authorized local aggregate inventory before selecting real SFT material.

## Acceptance for first real pilot

- First select 5–10 complete real or properly de-identified incident packets.
- Reject packets with missing provenance, missing diagnosis outputs, incoherent logs, insufficient context or unverified target conclusions.
- Have a qualified reviewer adjudicate the final LLM report target.
- Only then assemble 20 schema-valid, human-approved examples for a controlled pilot.
- Synthetic fixtures remain a separate test suite and never inflate real-case counts.

## Formal output vs. curator-only reasoning

The assistant target is not a reasoning checklist. The formal diagnostic report must separate:
- `phenomenon_analysis`: recorded symptoms and their established relationships;
- `cause_localization`: fault source, affected components, mechanism and certainty status;
- `disposal_status` / `disposal_measures`: actions actually documented in the source case. If absent, set NOT_RECORDED and keep the list empty;
- concise evidence and uncertainty qualification.

Curator-only review prompts, alternative hypotheses to check, common misdiagnosis warnings and questions for the user belong in the root-level `internal_review` field. They must not enter the model-visible input or assistant target. A conclusion such as “the current evidence does not localize the fault to the TWTA itself” may appear in the target only when it is supported by the case evidence and expressed as a conclusion, not as an imperative thought prompt.

Do not relabel a proposed troubleshooting action as a historical disposal measure. Keep actual recorded recovery actions separate from any optional, clearly labelled follow-up recommendation.
