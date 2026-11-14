---
name: epc-gold-seed-curation
description: Use when drafting or reviewing Self-Instruct seed tasks about satellite SSPA/TWTA Electronic/Electrical Power Conditioners (EPC), especially high-voltage outputs, microdischarge, SSPA current anomalies, and confusion between EPC, TWT, TWTA, SSPA and spacecraft EPS.
---

# EPC Gold Seed Curation (DRAFT, public-literature pilot)

Generate **candidate** tasks only. Do not infer an EPC root cause from an amplifier-level symptom, and do not promote any candidate to Gold without independent human review.

## 1. Resolve the EPC architecture before drafting

EPC is context-sensitive in the public literature:

- In TWTA literature and ECSS-E-HB-20-05A, EPC means **Electronic Power Conditioner**. A TWTA comprises a TWT and its EPC. The EPC supplies stable high-voltage outputs and supporting control, telemetry and protection.
- In the Inmarsat SSPA paper by Lohmeyer & Cahoy, EPC is written as **Electrical Power Conditioner** and is described as part of an SSPA with FET amplifier devices.
- **EPS** is the spacecraft Electrical Power Subsystem. It is not a synonym for EPC.
- **TWT** is the vacuum electron device; **TWTA** is the amplifier assembly; **EPC** is the power-conditioning unit. Do not merge these entities.

Select the correct term ID from `resources/epc_terms.json` and retain the SSPA/TWTA context in the seed.

## 2. Ground claims in the correct source passage

Inspect `resources/sources.json` and `resources/source_passages.json`. Use registered passage IDs:

- ECSS §4.4.2.1–4.4.2.2: TWTA/EPC architecture, output rails, control and protection.
- ECSS §§4.3.3–4.3.4: partial discharge versus Paschen/full breakdown.
- ECSS §8.1.1: high-voltage converter problem classes.
- TWTA microdischarge paper: transient high-voltage removal/restart and the anode-voltage recovery signature.
- Inmarsat SSPA radiation paper: hard/soft SSPA anomaly categories, current thresholding and the explicit lack of confirmed causes for the 26 reported anomalies.
- JWST lessons learned: a TWTA-1 power-off was attributed by the manufacturer to an EPC parts failure, but the specific part/mechanism is not stated.
- TWTA reliability paper: insufficient cathode emission and vacuum degradation are TWT failure mechanisms; helix current/anode voltage are TWTA performance indicators, not EPC-unique signatures.

A registered source passage supports only its stated claim boundary. A design handbook is not an in-orbit failure report.

## 3. Mandatory component and mechanism separation

For each candidate, separate:

1. spacecraft EPS/main-bus input;
2. EPC input filter and preregulator;
3. EPC power-conversion/high-voltage generation and output regulators;
4. TWT cathode, helix, collector and filament interfaces;
5. RF amplifier/system-level output;
6. protection state, restart and telemetry reporting.

Use this separation when writing claims. A low SSPA current or loss of RF output does not, by itself, identify the EPC as the failed component. A cathode-emission or vacuum problem belongs to the TWT unless the evidence localizes it to the EPC. An EPC high-voltage trip/restart may be a designed protection response to a microdischarge, not a permanent hardware failure.

## 4. Preserve the high-voltage vocabulary

- **Microdischarge**: event-specific term used in TWTA operational literature; it can trigger momentary HV removal and restart.
- **Partial discharge**: localized discharge that does not immediately cause full breakdown; ECSS notes its potential to accelerate insulation ageing.
- **Paschen breakdown**: full gaseous-insulation breakdown under pressure/gap/voltage conditions; not synonymous with partial discharge.
- **Hard/soft failure**: the cited Inmarsat paper's operator classification of SSPA anomalies. Do not generalize it as a universal EPC failure taxonomy.
- **Anode voltage / helix current**: performance/telemetry variables; their variation is not a unique root-cause label.

Never invent universal voltage/current thresholds. The SSPA paper explicitly notes that current thresholds are hardware/fleet specific.

## 5. Candidate generation and review

1. Create a `dgsi-seed.v1` candidate with a truth-free input. Use `HYPOTHETICAL` unless a separately verified local trace receipt exists.
2. Atomize the answer into claims: observed signature, component, mechanism hypothesis, protection behavior, consequence and uncertainty.
3. Cite registered `source_passage_ids` for mechanism claims. Keep SSPA observations separate from TWTA EPC architecture.
4. If the source identifies only an EPC assembly but not the failed internal part, state the assembly-level localization and preserve the missing subcomponent as unknown.
5. If a paper reports a suspected environmental influence but no confirmed cause, do not upgrade association to causality.
6. Run the offline validator. Treat suspicious terms and scope mismatches as review items; do not rewrite a false claim merely to evade a detector.
7. Present the source passage, original candidate, correction and uncertainty to a human domain reviewer. Human approval and Gold freeze are separate governed actions.

## Quick checks

| Generated claim | Required correction |
|---|---|
| “EPC is the spacecraft EPS” | Separate amplifier EPC from spacecraft EPS |
| “TWTA and EPC are the same component” | Model TWTA = TWT + EPC |
| “Low SSPA current proves EPC failure” | Keep the symptom at SSPA level until component isolation evidence exists |
| “26 Inmarsat anomalies were caused by radiation” | The cited paper does not confirm individual causes or a general causal relationship |
| “Anode voltage dip means permanent EPC breakdown” | Check microdischarge, protection and restart behavior |
| “TWT cathode emission degradation is an EPC fault” | Attribute the mechanism to the TWT unless evidence localizes it to the EPC |
| “Partial discharge is Paschen breakdown” | Distinguish local partial discharge from full gaseous breakdown |
| “The JWST case proves a failed EPC preregulator” | The source only says an EPC parts failure; the failed part is not identified |

**Status:** DRAFT. The public-literature test suite is not a flight-hardware fault taxonomy. Independent evaluator and domain-expert review are required before production use.
