# DGSI episode intake template

Copy one per event/episode. Do not guess missing fields.

## Identity and rights
- Pseudonymous episode ID:
- Source track: REAL_CASE_CANDIDATE / SIMULATION_CASE_CANDIDATE / LITERATURE_DERIVED_SYNTHETIC / DESIGN_DERIVED_HYPOTHETICAL / SYNTHETIC_TEST_ONLY / KNOWLEDGE_SOURCE_NOT_EVENT
- Source owner:
- Permission basis for selected AI provider:
- Confidentiality class:
- De-identification performed:
- Source files and SHA-256:
- Simulator / platform / model version:

## System context
- Spacecraft/platform:
- Subsystem:
- Unit/component:
- Configuration/version:
- Mission phase:
- Operating mode:
- Environment:
- Analysis cutoff (timezone-aware):

## Upstream diagnosis (do not invent)
- Method/model/version:
- Run ID:
- Analysis window:
- Status:
- Findings/candidates:
- Score and score semantics:
- Supporting evidence IDs:
- Known limitations:
- If unavailable, write NOT_PROVIDED.

## Logs and tests
- Alarm/event/operator/engineering/maintenance/telecommand logs:
- Timestamp/timezone source:
- Test conditions and baseline:
- Test result:
- Data-quality limitations:
- Evidence artifact references:

## Model-visible evidence boundary
- What was available by analysis cutoff:
- What was not available:
- Historical Context actually supplied:
- Post-cutoff evidence excluded:
- Hidden truth excluded:

## Candidate diagnosis target (review-required)
- Observed phenomenon:
- ML result interpretation:
- Fault-source candidate:
- Affected components:
- Mechanism and evidence:
- Contradictory evidence:
- Certainty:
- Missing evidence:
- Recommended next checks:
- Disposal/action status:

## Hidden QA / adjudication sidecar (never attach to generator)
- Injection configured:
- Injection executed:
- Physical effect independently observed:
- Diagnostic effect observed:
- Upstream ML detected:
- Correctly localized:
- Post-run adjudication:
- Supporting QA references:
- Reviewer decision:

## Review status
- Automatic validation:
- Independent source audit:
- Domain reviewer:
- Decision: REJECTED / INCOMPLETE_EVIDENCE / REVIEW_REQUIRED / HUMAN_REVIEWED_CANDIDATE
- Corrections and reviewer notes:
