# Source ingestion: design reports, test reports and run logs

## 1. Source inventory

For each file record:
- stable pseudonymous `source_id`;
- filename and media type;
- source class: `DESIGN_DOCUMENT`, `MODEL_SPECIFICATION`, `TEST_REPORT`, `SIMULATION_RUN_LOG`, `FAULT_INJECTION_RECORD`, `UPSTREAM_ML_RESULT`, `ENGINEERING_REVIEW`, `HISTORICAL_CASE`, `OTHER`;
- owner/permission basis and confidentiality level;
- version/date and applicable software/simulator build;
- SHA-256 and file size;
- pages/sections/tables/figures or log time ranges;
- whether the source is contemporaneous, retrospective or generated;
- known omissions and redactions.

## 2. Design documents

Extract declarations, not assumed observations:
- system and object hierarchy;
- component identity and parent/child relationships;
- signal and energy flow;
- physical state variables, equations and constitutive relationships;
- assumptions, simplifications and valid operating ranges;
- interface contracts, units, coordinate frames and sign conventions;
- nominal parameters, tolerances and parameter provenance;
- fault modes explicitly modeled and fault modes not modeled;
- redundancy, protection, control and fallback logic.

Tag each extracted statement:
- `DESIGN_DECLARATION`
- `MODEL_ASSUMPTION`
- `MODEL_LIMITATION`
- `PHYSICAL_RELATIONSHIP`
- `CONFIGURATION_FACT`

A design declaration does not establish that the corresponding failure occurred in a run or in flight.

## 3. Test reports

Extract:
- test objective and acceptance criteria;
- DUT configuration and hardware/software/simulator versions;
- test conditions, initial conditions, environment and operating mode;
- instrumentation and measurement uncertainty;
- baseline and comparison method;
- procedure and event chronology;
- measured outcomes, anomalies and deviations;
- pass/fail decision and its scope;
- unresolved observations, exclusions and follow-up work.

Keep measured results distinct from test-author interpretation. A test pass validates only the stated test scope and conditions.

## 4. Simulation run logs

Preserve:
- immutable run ID and simulator build;
- scenario ID, random seed and configuration hash;
- timestamp origin, units, time zone and sampling cadence;
- event, alarm, mode transition, command and engineering log records;
- run start/end, termination status and restart/replay lineage;
- artifact references and hashes;
- errors, dropped samples, missing channels and data-quality flags.

Do not copy high-rate telemetry arrays into the LLM prompt. Link the upstream ML result bundle and evidence artifact IDs instead.

## 5. Upstream ML result bundle

Preserve without reinterpretation:
- algorithm/method, implementation version and model ID;
- training/model version where applicable;
- input dataset/run reference and analysis window;
- analysis scope and selected channels/features;
- status: normal, anomaly, fault candidate, multiple candidates, insufficient data or data-quality error;
- ranked candidates and component localization;
- numeric score and exact score semantics (distance, ranking score, likelihood, calibrated probability, etc.);
- calibration evidence, if any;
- supporting evidence IDs and known limitations.

A ranking score is not a probability by default. Do not replace upstream uncertainty with a definitive LLM diagnosis.

## 6. Log normalization

Normalize only representation, never meaning:
- retain original timestamp and timezone; if shifted for privacy, apply one consistent documented offset;
- preserve event ordering and inter-event intervals;
- retain source type: alarm, event, operator note, engineering analysis, maintenance, telecommand, review or other;
- preserve units and original values;
- mark missing timestamps as missing rather than inventing them;
- keep original text or a traceable redacted excerpt and record redaction.

## 7. Evidence ledger

Each atomic claim should resolve to:
`source_id + source_hash + locator + claim_type + certainty + claim_boundary`.

Recommended claim types:
- observation;
- configuration;
- design declaration;
- physical mechanism;
- causal inference;
- test result;
- simulator setup;
- ML finding;
- operator/engineering interpretation;
- disposal/action;
- limitation.

If no exact locator is available, mark the claim `UNLOCATED` and block causal use until reviewed.
