---
name: eps-gold-seed-curation
description: Use when drafting or reviewing Self-Instruct seed tasks for spacecraft Electrical Power Subsystem (EPS) fault diagnosis, including solar-array circuits, battery cells and thermal control, power distribution, solid-state power controllers, bus-voltage regulation and radiation-induced effects.
---

# EPS Gold Seed Curation (DRAFT, public-literature pilot)

Generate **candidate** tasks only. Never turn a possible mechanism, counterfactual analysis or telemetry signature into a confirmed flight fault without case-specific evidence and independent human review.

## 1. Define the EPS boundary

Use EPS as **Electrical Power Subsystem / 电源分系统**. This project does not use EPC as its second domain.

For this pilot, distinguish:
- **Power generation:** solar cells, strings, panels/arrays, deployment, array wiring and array-to-bus connections.
- **Energy storage:** battery packs, cell stacks, individual cells, charging and state-of-charge management.
- **Power management and distribution:** bus regulation, power distribution units, solid-state power controllers, load switches, bus-voltage limiters and protection logic.
- **Thermal support:** battery heaters, heater-control electronics, thermistors and thermal-control interfaces.
- **Control and monitoring:** reset circuits, current/voltage/status telemetry, fault-detection and recovery logic.

Do not merge a solar-array fault with a battery fault merely because battery charge decreases. Do not treat a load-side switch trip as a battery failure.

## 2. Use registered public evidence

Inspect `resources/sources.json`, `resources/source_passages.json` and `resources/eps_terms.json`.

Core public sources include:
- NASA IMAGE Failure Review Board: SSPC instant trip, stale status telemetry, and alternative battery/solar-array hypotheses.
- NASA NOAA-13 Lessons Learned: suspected solar-array bus-to-ground short following thermal/mechanical interaction.
- IDEASSat on-orbit analysis: likely EPS reset-circuit cause involving a CMOS Schmitt-trigger inverter; SEL is discussed as a plausible mechanism, not a conclusively observed event.
- NASA TERRA: battery cell voltage anomaly and simultaneous battery-heater control-circuit anomalies.
- NASA TDRS-8: six failed solar-array circuits, BVL parasitic shunting and underperforming battery cells.
- NASA WMAP NESC assessment: repeated NiH2 cell voltage collapses; definitive root cause remained unresolved, with electrolyte bridging as the team's consensus theory.
- NASA SmallSat Power chapter and EPS reliability research: architecture and subsystem-level context, not case-specific fault proof.

Use exact registered `source_passage_ids`; never invent a page number, section, threshold or source statement.

## 3. Preserve the strength of the source conclusion

Every candidate must distinguish:
- **Observed:** telemetry or operational record directly states an event or measurement.
- **Localized:** a report identifies a component or circuit boundary.
- **Likely / suspected:** an investigation favors a cause but retains alternatives.
- **Hypothesis:** a physical mechanism considered plausible but not demonstrated.
- **Counterfactual:** an alternative fault case analyzed to rule it in/out, not an observed flight failure.
- **Design-level failure mode:** a plausible failure path, not evidence it happened on a specific spacecraft.

Examples:
- IMAGE: the FRB considered an SEU-induced SSPC instant trip the *likely* cause of lost transponder power; it also explicitly said battery short/open and solar-array short/open were not indicated by telemetry. Do not label those alternatives as actual IMAGE failures.
- NOAA-13: preserve that the bus-to-ground short and protruding mounting bolts were surmised by the review; do not claim destructive inspection confirmed the exact contact point.
- IDEASSat: preserve “likely cause” for the reset-circuit inverter; SEL is a possible mechanism, not a directly confirmed event unless separately evidenced.
- TERRA: battery cell and heater-control anomalies occurred together; do not invent a causal direction between them.
- TDRS-8: six array circuits were reported failed; BVL modules shunted static current instead of regulating; the source does not specify the failed internal semiconductor.
- WMAP: a 1.4 V cell drop is consistent with complete self-discharge; the NESC team did not determine a definitive root cause. Electrolyte bridging is a consensus theory, not a proven failure mechanism.

## 4. Separate component, signature and propagation

For each seed, explicitly separate:
1. physical fault-source component or circuit;
2. measured symptom (voltage, current, temperature, status bit, SOC);
3. local electrical mechanism;
4. protection/control response;
5. downstream load and mission effect;
6. uncertainty and alternative explanations.

Do not infer root cause from one scalar:
- Low battery voltage can reflect cell degradation, discharge state, thermal condition, charge-control behavior, load changes or upstream generation/regulation faults.
- Low solar-array current depends on illumination, attitude, temperature, array configuration, circuit condition and operating point.
- A bus voltage anomaly can originate from source, storage, regulator, distribution, load or protection logic.
- A stale “closed” status bit does not prove that a solid-state power controller is physically conducting.

## 5. Candidate generation and review

1. Use `dgsi-seed.v1` with `domain=eps`.
2. Use `input.kind=HYPOTHETICAL` for literature-derived synthetic prompts. Use `TRACE` only when a separately verified local run receipt exists.
3. Do not include hidden labels, suspected cause, fault ID, event time or split metadata in model-facing input unless the task explicitly asks for literature reasoning and those facts are part of the public source passage.
4. Atomize claims into observation, mechanism, causal hypothesis and uncertainty. Cite registered passage IDs and keep source conclusion strength intact.
5. If a source reports a likely cause, use a qualified status and list alternatives; do not promote it to confirmed.
6. If a source passage is counterfactual, never generate a positive flight-fault label from it.
7. Run the offline validator. A structural PASS is not a factual correctness certificate.
8. Present source passage, candidate, correction and uncertainty to a human EPS reviewer. Human approval and Gold freeze are separate governed actions.

## Quick checks

| Generated claim | Required correction |
|---|---|
| “Battery voltage dropped, therefore the battery cell shorted” | Keep symptom and mechanism separate; inspect cell-level evidence and alternative EPS causes |
| “Solar array current fell, therefore the solar cells failed” | Check illumination, attitude, temperature, topology, regulation and circuit-level evidence |
| “IMAGE lost communications because its battery shorted” | Reject: IMAGE FRB found healthy battery telemetry and considered this alternative unlikely |
| “IMAGE SSPC instant trip was conclusively caused by SEU” | Preserve FRB's “likely cause” wording and alternatives |
| “NOAA-13 bolts were proven to penetrate insulation” | Preserve the source's surmised mechanism and review-board conclusion |
| “IDEASSat SEL was directly observed” | Source identifies the reset inverter as likely cause and discusses SEL as a possible mechanism |
| “TERRA heater failure caused the battery cell failure” | The report records simultaneous anomalies, not a proven causal direction |
| “WMAP voltage collapse proves internal short” | NESC did not determine a definitive root cause; electrolyte bridging was a consensus theory |
| “TDRS-8 BVL anomaly proves a specific transistor failure” | Source reports parasitic shunting, not the failed internal part |

**Status:** DRAFT. This public-literature pilot is not a universal EPS failure taxonomy. Domain-expert review and independent blind evaluation are required before production use.
