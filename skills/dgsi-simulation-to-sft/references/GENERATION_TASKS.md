# Diagnostic task design for simulation-derived and document-derived cases

## Six task types

### 1. diagnostic_synthesis
Input: ML findings, logs, configuration, operations and relevant evidence.
Target: concise diagnosis synthesis with phenomenon, candidate fault source, affected components, evidence, certainty and limitations.

### 2. historical_case_reuse
Input: current diagnostic evidence plus time-safe historical Context.
Target: explain what transfers, what does not, hardware compatibility, contradictions and missing evidence. Historical cases are context, not votes.

### 3. conflict_reconciliation
Input: conflicting ML findings, logs, tests or subsystem reports.
Target: separate supported facts, conflicting claims, alternative explanations and discriminating tests. Do not force a single root cause if evidence does not support it.

### 4. evidence_sufficiency
Input: partial diagnosis packet with known missing evidence.
Target: decide whether evidence supports anomaly detection, component localization or root-cause localization; state what cannot be concluded and what evidence is needed.

### 5. next_step_recommendation
Input: candidate diagnosis and available test/inspection options.
Target: prioritize safe, discriminating follow-up checks with rationale. Do not state that a proposed action has already been executed.

### 6. handover_summary
Input: reviewed case state, current uncertainty, completed checks and open actions.
Target: concise operational handover with confirmed facts, candidates, unresolved issues, evidence references and next owner/action role (not personal identity).

## Simulation-specific scenario matrix

Where supported by real runs, cover:
- normal run / no fault;
- injection configured but not executed;
- injection executed without validated physical effect;
- physical effect but no model-visible signature;
- observable anomaly but upstream ML misses it;
- ML detects anomaly but mislocalizes component;
- correct component localization but ambiguous root cause;
- multiple simultaneous faults with separate causal chains;
- sensor fault versus real plant/actuator fault;
- command issued versus actuator response not achieved;
- mode transition or protection response mistaken for primary fault;
- insufficient evidence / corrupted or misaligned logs;
- history hit with incompatible hardware;
- contradictory historical cases;
- post-cutoff evidence that must not leak into the prompt.

Do not fabricate a scenario matrix row as an actual run. If the corresponding run does not exist, mark it as a proposed future experiment.

## Avoid low-value variants

Do not generate:
- paraphrases with the same input and target;
- multiple tasks whose only difference is wording;
- duplicate samples from one run presented as independent events;
- a diagnosis prompt that includes the injected fault label;
- a target that repeats the hidden label without evidence;
- generic advice detached from the specific evidence packet.

A useful task variant must test a different diagnostic decision or failure mode.
