# Formal diagnostic conclusions vs. curator review metadata

## Purpose

DGSI SFT must teach the model to produce a concise, evidence-bounded engineering diagnosis report. It must not teach the model to repeat the curator's prompts, alternative hypotheses checklist, counterexamples or reviewer questions.

The distinction is a data contract, not a writing-style preference.

## Model-facing assistant target

The formal report contract is `diagnostic_case.schema.json#/properties/expected_output` and is reused for standalone SFT assistant targets.

| Field | Meaning | Target rule |
|---|---|---|
| `phenomenon_analysis` | Analysis of supplied symptoms, alarms, machine findings and their documented relationships | Describe observed/recorded facts; do not invent missing telemetry or log entries |
| `machine_result_interpretation` | Interpretation of upstream ML outputs | Preserve method/status/score semantics and limitations; do not re-run raw telemetry diagnosis |
| `cause_localization` | Fault source, candidate mode, affected components and mechanism conclusion | Preserve CONFIRMED / MOST_LIKELY / CANDIDATE / UNRESOLVED level; source and affected components are separate |
| `evidence_assessment` | Supporting refs, contradicting refs and missing information | Every cited reference must exist in the supplied case packet |
| `historical_experience_relevance` | Relevance and transfer limitations of historical cases | An unresolved/rejected case cannot become confirmed precedent |
| `uncertainty` | Uncertainty level and case-specific reasons | State uncertainty as a conclusion, not an internal thought trace |
| `disposal_status` | Whether the source actually records a disposal action | RECORDED / NOT_RECORDED / RECOMMENDED_ONLY / NOT_APPLICABLE |
| `disposal_measures` | Actions documented as executed/planned or explicitly recommended in the source | EXECUTED actions require supplied source references; NOT_RECORDED requires an empty list |
| `follow_up_actions` | Additional checks or actions recommended by the current report | Must not be represented as historical actions already executed |
| `report_text` | Concise engineering report assembled from the structured conclusions | No curator instructions, reviewer questions or ungrounded facts |

## Internal-only curator review metadata

A Case may carry a root-level `internal_review` object with `not_for_sft=true`. It is not part of the LLM input and not part of the assistant target.

Allowed content:
- `curator_prompts`: quality-control prompts for the dataset builder;
- `alternative_hypotheses_to_check`: review checklist, not a model answer;
- `counterexamples`: possible confounders to check during curation;
- `reviewer_questions`: questions for the domain expert;
- `quality_flags`: source/curation warnings;
- `status`: OPEN / REVIEWED / RESOLVED.

Examples of internal-only text:
- “Do not infer a TWTA internal gun fault merely from the equipment name.”
- “Check whether the power indication may be affected by the measurement chain.”
- “Compare a common-cause explanation against independent failures.”

These are instructions to the curator or reviewer. They must not appear in the assistant's formal diagnosis report. If the evidence supports a conclusion such as “the available records do not localize the fault to the TWTA itself,” that conclusion may be expressed in the report with its evidence references; the original instruction-style prompt remains internal-only.

## Disposal vs. recommended follow-up

These fields must not be conflated:

- **Disposal measure**: what the source says was actually done, planned, or explicitly prescribed in the original procedure.
- **Follow-up action**: what the current LLM report recommends next based on the evidence gap.

For example, if a source case only records “output power dropped 5–7.3 dB” and “cause was cable/isolator contact failure,” but gives no restoration action, use:
- `disposal_status = NOT_RECORDED`
- `disposal_measures = []`
- any newly proposed check belongs in `follow_up_actions`, not `disposal_measures`.

An action may be marked EXECUTED only when a supplied log, maintenance record or adjudicated source supports it. The validator rejects an EXECUTED measure without evidence references and rejects citations that do not resolve to supplied evidence.

## SFT serialization

The SFT user prompt contains only:
- case ID;
- task type;
- registered generic instruction;
- the validated `input` object (upstream ML result, logs, spacecraft/mission context, history and knowledge references).

The SFT assistant message contains only the formal `expected_output` report object. It excludes:
- root-level `internal_review`;
- source `review` metadata;
- private expert adjudication fields;
- hidden simulator truth or post-cutoff outcomes.

The Case→SFT binding gate verifies that the prompt input and assistant report exactly match the source Case. This prevents the report from being silently strengthened or the curator checklist from leaking into the model conversation.

## Quality tests

The contract tests cover:
1. internal review fields are required and explicitly marked `not_for_sft`;
2. curator prompts and reviewer questions do not appear in the user prompt or assistant target;
3. the assistant target has phenomenon analysis, cause localization and disposal status/measures as distinct fields;
4. NOT_RECORDED disposal cannot contain invented actions;
5. EXECUTED disposal requires a supplied evidence reference;
6. recommended follow-up remains distinct from historical disposal;
7. all target citations resolve to the supplied diagnosis/log/history/knowledge evidence.

Schema validity and reference integrity do not establish factual correctness or Gold approval. Independent domain review remains mandatory.


## L0 source fact cards are a separate staging layer

Public literature and user-supplied case summaries may not contain an upstream ML result, diagnostic logs or mission context. Do not fabricate those missing fields just to satisfy the full Case schema.

Use `resources/source_fact_card.schema.json` and `validate_source_fact_card()` for source-grounded L0 records:
- preserve the source's phenomenon statement, cause statement and disposal wording;
- record the certainty exactly as stated by the source, or NOT_STATED;
- record which upstream ML/log/context/history/expert-target materials are actually available;
- keep curator questions in root-level internal_review with not_for_sft=true;
- enforce that L0 cards always have sft_eligible=false.

An L0 card is not a complete diagnostic-context Case and is not an SFT example. It may be promoted to a full Case only after the required ML diagnosis result and context are available or a separately approved literature-derived SYNTHETIC task is intentionally created and labelled as such. The validator reports missing material; it never generates it.
