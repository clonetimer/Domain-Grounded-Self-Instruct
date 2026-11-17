# P5-C1 evidence request matrix for the five real-case candidates

Status: evidence-request preparation only. This document is derived from the user's five-case source fact cards. It does not assert that any requested artifact exists or has been retrieved.

## Why a case-specific matrix is necessary

A generic request for “ML results and logs” is insufficient. Each case has different discriminating evidence. The objective is to obtain the smallest authorized evidence set that can validate the source diagnosis, chronology, fault-source localization and disposal semantics without fabricating missing inputs.

## Common evidence required for a complete DGSI second-stage diagnosis input

| ID | Evidence | Minimum content |
|---|---|---|
| E01 | Source authorization | Provenance, de-identification and permission for intended processing/training |
| E02 | Upstream ML result | Actual model/algorithm version, run ID, score meaning, candidate ranking and evidence references |
| E03 | Diagnostic logs | Original timestamps/time basis, event IDs, source locators and integrity hashes |
| E04 | Spacecraft configuration | Relevant as-flown/as-tested component and subsystem configuration |
| E05 | Mission context | Mission phase, operating mode, command/telemetry mode and constraints |
| E06 | Measurement dictionary | Physical measurement points, units, sensor identity, calibration/validity and time alignment |
| E07 | Disposal evidence | Separate source recommendation, actual execution record and post-action verification |
| E08 | Independent review | Two independent expert assessments and adjudication of material disagreements |

A case may not possess every artifact. If unavailable, mark it NOT_AVAILABLE and record why. Do not replace missing evidence with a plausible synthetic value in the REAL track.

## Case-specific evidence

### USER-ADCS-SADA-001 — SADA disc-ring / brush contact

1. Original time series and event timestamps for the three total-current and main-error-voltage drops.
2. Sensor definitions and physical locations for the reported 181°C shaft and 150°C housing temperatures.
3. Solar-array angle command, drive state and stall chronology during south-array adjustment.
4. Inspection, test, maintenance or failure-analysis evidence supporting debris-induced arc in the disc-ring/brush power path.
5. Whether south-array shutdown was commanded and executed, when it occurred, and subsequent status.

Do not assume the three drops, temperature peaks and stall are simultaneous without source chronology. Do not represent shutdown as verified execution based only on the source disposal field.

### USER-COMM-TWTA-002 — High-power cable / isolator contact

1. Time-aligned helix current, RF output power, TWTA A/EPC A/isolator A temperatures, microwave temperature and triplexer temperature.
2. Connector inspection, contact resistance, interface condition and high-power reflection evidence at the cable-to-isolator input.
3. Source record clarifying “可自行恢复”: did the phenomenon clear without ground action, and what evidence establishes that?
4. Post-recovery power/current/temperature trend and duration of stable operation.

Do not invent a recovery command. “Can recover by itself” is not equivalent to a verified successful recovery or an identified operational action.

### USER-COMM-KU-TWTA-003 — EPDF over-power dissipation

1. EPDF state/telemetry, protection status and diagnostic evidence supporting the stated cause.
2. Timestamped helix-current rise, protection trigger (if any), automatic shutdown and restart.
3. Original logic/state table mapping the three conditional disposal branches to actual protection and shutdown states.
4. Backup switch, restart and ten-cycle preheat records if those actions were performed.
5. Post-restart continuous operation and verification.

The three branches are conditional procedures. Do not encode any branch as an executed disposal action without the corresponding command/state records.

### USER-PROP-THRUSTER-004 — 2# thruster temperature / thrust anomaly

1. Sensor identity, physical location, unit and validity for the reported -33°C reading.
2. Previous-day high-temperature event, propulsion firing and attitude maneuver completion chronology.
3. Thrust-reduction basis: direct measurement, estimate or inferred telemetry, including calibration and uncertainty.
4. Time-aligned wheel 1/2 speeds, roll/pitch errors and the later 0.6-degree attitude-error alarm.
5. Evidence for incomplete-combustion product accumulation, abnormal combustion and the stated structural damage.
6. Exact control-strategy changes, command/procedure, execution time and measured effect.

Do not treat wheel-speed increase as proof of the thruster root cause. Preserve it as an observed cross-subsystem effect until temporal and causal evidence supports a stronger relation. Do not promote “structural damage” beyond its source evidence.

### USER-ADCS-RW-BEARING-005 — Reaction-wheel bearing lubrication

1. Timestamped 27°C, 50.27°C and 74.2°C readings, sensor location and operating state.
2. Inspection, disassembly, maintenance or test evidence for feedline blockage and bearing oil starvation.
3. Current, torque, speed, vibration or other evidence supporting increased bearing friction.
4. Actual configuration-switch command/state transition and timestamp.
5. Whether the 2000 rpm limit was a recommendation, approved operating constraint or executed command; include telemetry showing actual speed limitation if available.

Do not convert a conditional recommendation into an executed control action.

## Evidence receipt and storage

For each supplied artifact, record metadata only in the public repository:
- case ID and evidence item ID;
- artifact type and source system;
- source owner/authorization status;
- acquisition time and original time basis;
- original filename or secure storage locator (opaque reference only);
- SHA-256 of the exact received bytes;
- de-identification status and reviewer;
- claim(s) the artifact is intended to support;
- whether it is direct observation, upstream model output, derived analysis or historical Context.

Raw logs, telemetry, command histories, private reports and identifying material remain in the user's authorized private storage. Do not commit them to a public or broadly shared repository. Hashes prove byte identity only, not source authenticity or engineering truth.

## Completion rule

A case becomes an evidence-complete DGSI input candidate only when required upstream ML output, diagnostic logs, spacecraft/mission context and the case-specific discriminating evidence are either supplied and traceable or explicitly justified as not applicable under an expert-approved task scope.

Evidence completeness does not itself grant REAL_GOLD status. Source rights, two independent reviews, adjudication, event-family split isolation and the existing release authorization remain separate gates.

Current snapshot: five REAL_CASE_CANDIDATE; zero evidence-complete cases; zero independent reviews complete; zero REAL_GOLD; zero official splits; zero authorized SFT records; training disabled.
