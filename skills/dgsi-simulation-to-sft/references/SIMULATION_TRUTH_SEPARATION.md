# Simulation truth separation and Basilisk intake

## Three planes

### A. Model-visible diagnostic input
May contain only information available to the diagnostic LLM at the declared `analysis_cutoff`:
- upstream ML outputs and evidence references;
- diagnostic logs available by cutoff;
- spacecraft configuration and operational context;
- prior cases available by cutoff;
- source-bounded design/test knowledge intended for the operator/diagnostician.

### B. Hidden simulator truth / QA plane
Restricted to validation and human review:
- injected fault ID, component, mode, parameters, start/end time;
- internal simulator state not observable to the diagnostic chain;
- truth labels, expected targets, fault windows and split assignments;
- QA-only channels and post-run physical-effect checks;
- teardown, repair, adjudication or retrospective findings unavailable at cutoff.

### C. Public source / design knowledge plane
Contains design declarations, test procedures, model assumptions and public literature facts. It can constrain plausible interpretations but does not automatically prove a specific run event.

Never merge these planes into one prompt.

## Basilisk-specific checks

When Basilisk is the simulator:
- record Basilisk version, native module/process configuration, spacecraft model and build/source revision;
- record simulation seed, run manifest, task/specification ID and parameter/configuration hashes;
- distinguish truth state, ideal observation, sensor measurement, estimator output, FSW command and applied actuator response;
- preserve native module outputs and their semantics; do not replace them with Python-only synthetic signals while claiming Basilisk-native provenance;
- verify units, coordinate frames, sampling, time alignment and channel mapping;
- identify whether a sensor channel is ideal state feedback, noisy measurement, estimator output or hardware-equivalent observation;
- record model simplifications and missing physical effects;
- independently verify that injected faults create the claimed physical/observable effect;
- prevent simulator QA truth, injected fault labels and hidden target IDs from entering the LLM input.

A Basilisk run receipt that passes structural validation is only an evidence-intake candidate. It is not proof of physical fidelity, expert approval or training eligibility.

## Fault injection versus observed effect

Use separate fields for:
- `injection_configured`: what the simulator was instructed to inject;
- `injection_executed`: whether the run confirms the injector executed;
- `physical_effect_observed`: whether independent state/physics checks confirm the intended effect;
- `diagnostic_effect_observed`: whether model-visible channels/logs show the expected diagnostic signature;
- `upstream_ml_detected`: whether upstream ML detected/localized it;
- `qa_adjudication`: reviewer conclusion and supporting evidence.

These are not interchangeable. A case may be:
- injected but no physical effect;
- physical effect exists but is not observable in available channels;
- observable effect exists but ML misses it;
- ML flags an anomaly but localization is wrong;
- ML correctly localizes a fault candidate but root cause remains ambiguous.

Preserve these as valuable distinct tasks, not as one generic PASS/FAIL label.

## Split and replay

- Group all variants, seeds, replays and paraphrases from one scenario/event family into the same split group.
- Do not place one replay in train and its source run in test.
- Do not expose a test split's injection manifest to generation models.
- Freeze simulator build, model configuration, seed policy and source artifact hashes before generating a batch.
- If any upstream artifact changes, invalidate downstream review receipts and regenerate the affected candidate fingerprint.
