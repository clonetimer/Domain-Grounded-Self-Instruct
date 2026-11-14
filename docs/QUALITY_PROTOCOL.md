# P1 Quality and Governance Protocol

## What passes and what does not

The offline preflight supports two separate domains: ADCS and EPS. Each has its own term catalog and source-bounded Skill. The preflight checks registry IDs, registered source-passage references, alias classes, selected suspicious technical compounds, self-certifying language, selected causal wording, evidence references, direct input label leakage, physical-claim scope, causal review metadata, admissible simulation runs, and human approval metadata.

Mechanism/causal claims must cite registered source_passage_ids whose allowed_claim_types includes the claim type; a free-text locator cannot substitute. These checks do not establish that a prose statement is true. The compound-term scanner is intentionally narrow and cannot guarantee discovery of all unregistered technical expressions.

A result with decision=REVIEW_REQUIRED must be manually examined for suspicious compounds. A result with decision=CANDIDATE_CHECKS_PASSED is still an AI/synthetic candidate; scanner silence is not proof that every term is registered. HUMAN_REVIEWED may produce GOLD_METADATA_ELIGIBLE_MANUAL_AUTHENTICATION_REQUIRED, but the validator never authenticates reviewer identity and never moves a record into a Gold dataset.

## Evidence tiers

1. **Reference indexed:** NASA, ESA, CNSA, Basilisk, papers or project code is in the source index; the exact passage and conditions still require review.
2. **Catalog/declaration:** channel names, model capabilities, fault-effect identifiers, engineering mappings. These cannot establish observed symptoms or case-level causality.
3. **Observed trace candidate:** local/raw telemetry with source identity, time grid, unit schema and effect receipt. Not admissible until independent verification.
4. **Admitted trace:** trace hash verified, injection/event window human-reviewed, physical effect observed, split authorized, truth kept out of inference input.
5. **Gold seed:** independently domain-reviewed output with provenance; review audit and freeze are separate from machine checks.

No run is admitted in v0.1. The public registry intentionally has runs: []. AAS and AstroGraph source schemas are references, not public copies of R21 data.

## Domain-specific evidence boundaries

### ADCS
- A measured channel anomaly is not automatically a component fault.
- Affected component and fault-source component are distinct.
- A sensor validity failure is not automatically hardware failure.
- Correlation between gyro, wheel, magnetometer and controller telemetry is not automatically a causal chain.
- Preserve source uncertainty in flight cases such as NEOSSat's suspected X-wheel electrical cause.

### EPS
- A battery voltage drop does not by itself prove an internal short.
- Solar-array current reduction does not by itself prove a cell failure; check illumination, temperature, array topology, bus state and regulation.
- A distribution switch/SSPC state bit may differ from its physical conduction state.
- Distinguish an observed event, a likely cause, a hypothesis and a counterfactual failure analysis.
- Preserve WMAP's unresolved root cause, TERRA's simultaneous battery/heater anomalies, NOAA-13's surmised ground short, and IMAGE's counterfactual battery/array hypotheses.

## Mandatory review workflow

1. Register the domain source and exact source_passage_id (section/page locator, allowed claim types, claim boundary), terminology IDs and provenance before generation.
2. Generate a small candidate with truth-free input and explicit observed vs. hypothetical evidence.
3. Atomize output into typed claims. Identify entity, component, channel, operating mode, units and certainty.
4. Run the offline validator. For every flagged term, citation or logical leap: correct, downgrade to uncertainty, or reject the sample. DOCUMENT_EXCERPT evidence must match a registered passage ID and source ID. Never rewrite a wrong physical claim merely to satisfy a detector.
5. A second reviewer verifies complex causal edges and any claimed fault-source localization with independent evidence.
6. Confirm artifact IDs, source passages, fault-window receipt and data split. Record a human decision; freeze Gold in a separate controlled process.
7. Keep Gold Seed / Synthetic Train / Validation / Test / Rejected nonoverlapping by provenance group (run, scenario, source, model and near-duplicate instructions). Never tune prompts against a test holdout.

## Pilot measurement contract

For the ADCS/EPS pilot, report results separately by domain. Record first-pass human approval rate, rejected rate, corrected-to-approved delivery yield, human revision time, terminology violations, unsupported factual statements, unsupported causal relations, counterfactual-to-observed label errors and holdout contamination. Compare baseline and Skill-assisted generation with the same evidence bundle and blind review rubric. Do not use the same generator/judge as sole truth authority.
