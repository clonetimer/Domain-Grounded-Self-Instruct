# R4 — ADCS diagnostic evidence pilot gate

## Decision

R84-R3A is accepted as a **native telemetry provenance and observability pilot**. It is not a diagnostic training dataset and must not be used to claim diagnostic generalization or model improvement.

R84-R3B is accepted as a **measurement-layer sensitivity replay** only. Its numerical wheel-speed measurement assumptions are not calibrated to the simulated wheel hardware and must not be presented as measured flight telemetry.

The next scientific data campaign is R4: a multi-wheel, multi-state, multi-effect native ADCS closed-loop campaign with hidden fault truth and independent run-level splits.

## What R84-R3A actually establishes

The merged SatAgentSimulation PR #107 and Actions artifact #13507208414 establish:

- 12 unique Basilisk-native arms plus one exact seeded replay;
- one target wheel (RW0), one initial state, two guidance references (0° and 0.9°), three actuator torque-capacity levels and two IMU gyro-noise levels;
- official Basilisk IMU output, native RW state-feedback speed, native FSW command torque and FSW tracking-error estimate;
- 12/12 physical baseline comparisons with maximum physics delta 0.0;
- six IMU noise-isolation pairs where all non-IMU telemetry deltas are 0.0;
- exact replay and source/native payload provenance.

This proves the selected channels can be recorded and their provenance checked in this bounded setup. It does **not** demonstrate general fault separability: the design has one wheel, one initial condition and one actuator-capacity degradation family.

The model-facing wheel-speed channel is ideal native state feedback, not a measured encoder. FSW command torque is not delivered torque. Actual applied torque, C++ actuator capacity and hub truth remain QA-only. Motor current is not measured.

## What R84-R3B adds — and does not add

SatAgentSimulation PR #108 / Actions run 42353192085 adds a deterministic observation-layer replay with explicit sampling, quantization, noise, bias, dropout, latency and timestamp jitter.

The replay audit reports:
- 403 identity-control rows;
- 208 sensitivity rows;
- 611 changed wheel-speed values;
- 13 explicit missing wheel-speed values;
- non-wheel channels unchanged;
- truth excluded and replay deterministic.

All nonzero measurement parameters are explicitly uncalibrated sensitivity assumptions. R3B is useful for testing missing-data and timing robustness in downstream algorithms, but it does not turn the R3A ideal state-feedback channel into a hardware-calibrated sensor. Keep R3A ideal feedback as an upper-bound control and R3B as a separately labelled sensitivity condition.

## Native ADCS capability boundary

The current `subsystem.adcs_unified_native.v1` capability is an engineering-preview mixed-native runtime: official Basilisk modules plus project SysModels and runtime event injection in one Basilisk Process/Task. Its v32 effect evidence records the following effects as `VERIFIED_NATIVE_EFFECT` for the registered engineering runtime, not as hardware or flight validation:

- `adcs_rw_jamming`: zeroes normal wheel torque authority; the capability describes scheduled braking/locking in the command path, not bearing structural dynamics.
- `adcs_rw_motor_failure`: applies the requested torque scale.
- `rw_friction_degradation`: changes effective drag; the model represents viscous drag, not Coulomb/static friction.
- `gyro_bias_step` and `gyro_noise_increase`: alter project-native IMU sensor behavior.
- `adcs_reaction_wheel_speed_limit`: applies an operational speed constraint, not a component-health fault.

The capability explicitly states that sensor fusion is deterministic and not flight-correlated. Any derived current `I = tau/Kt` remains a model-derived estimate, not a measured current channel.

## R4 campaign design requirements

R4 must expand the evidence in dimensions that R3A did not cover. Freeze the exact design and seed list before native execution.

### Coverage

1. **Wheel identity:** exercise RW0, RW1 and RW2; do not infer other wheel behavior from RW0 alone.
2. **Initial state:** use multiple registered initial attitude/rate states, including a nominal control and nonzero states.
3. **Effect families:** healthy controls plus torque-authority loss / motor failure, jamming, viscous-friction increase, gyro-bias step and gyro-noise increase. Keep constraints such as speed limiting separately labelled from faults.
4. **Severity:** cover more than one preregistered severity per degradable effect, using only supported parameter ranges and recording the effective value actually read back by the runtime.
5. **Excitation:** retain matched control/reference profiles across healthy and faulted pairs. Include more than one attitude-command profile so a fault is not only observable under one excitation.
6. **Repeatability:** use independent deterministic seeds for each unique run and at least one exact replay per frozen control family.
7. **Duration and sampling:** include sufficient pre-event and post-event windows at a sample interval that resolves the event response. Do not inherit R3A's 6 s / 31-point pilot window as the R4 diagnostic dataset window.

### Model-facing input and hidden truth

- Model-facing telemetry contains observations and operational estimates only.
- Fault IDs, injected severity, injection timestamps, event receipts, effective actuator truth, hub truth and simulator QA remain in a separate truth/QA sidecar.
- Keep sensor measurement, state feedback, command telemetry, operational estimates and applied physical effects as distinct channel classes.
- Do not leak `label.*`, `event.active_effects`, injection configuration or QA-only fields through aliases or derived features.
- Affected-component localization must not be treated as fault-source localization without separate evidence.

### Run-level split and leakage control

- Split by independent run/scenario group before feature extraction, seed generation or model training.
- Keep all time windows, derived features, augmented views, replays and paraphrased instructions from one physical run in the same split.
- Keep source document, simulator scenario, seed family and near-duplicate instruction lineage in provenance.
- No random row-level split.
- Hold out at least one complete combination of wheel identity, initial state or excitation profile for transfer testing; pre-register which dimension is held out.
- Do not use public-literature holdout cases to tune R4 labels or Skills. Retire any holdout used for remediation.

## R4 exit gates

R4 may produce candidate diagnostic seeds only after all gates pass:

1. Native execution provenance and simulator build are pinned.
2. Each effect has direct runtime assertions and a corresponding physical/telemetry response.
3. Healthy matched controls establish false-alarm behavior.
4. Pre-event behavior matches its paired healthy reference within the preregistered tolerance.
5. Event time, channel units, sampling grid and message provenance are verified.
6. Fault truth is physically separated from model-facing input.
7. Run/scenario/source split audit passes with no group leakage.
8. Qualified ADCS review approves effect semantics, causal boundaries and labels.
9. Ambiguous and insufficient-evidence cases are intentionally represented; the generator is allowed to abstain.

## First diagnostic seed pilot after R4

Only after R4 admission, generate 30–50 candidate ADCS tasks. Balance healthy, faulted, ambiguous and insufficient-evidence cases. Every atomic claim must bind to a telemetry evidence locator, a registered domain passage where applicable, and explicit applicability assumptions.

Compare ordinary Self-Instruct against the domain-grounded treatment on the same evidence bundle. Measure first-pass expert approval, correction time, final accepted yield, unsupported causal claims and component-localization errors. Fine-tuning is a later experiment, not an automatic consequence of seed generation.

## Non-claims

Neither R3A nor R3B establishes diagnostic accuracy, flight realism, hardware calibration, model improvement, training eligibility or Gold Seed status. R4 is a research evidence campaign; it does not qualify an on-orbit fault-management system.
