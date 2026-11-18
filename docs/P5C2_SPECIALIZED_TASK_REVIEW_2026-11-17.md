# P5-C2 specialized L1 task review and bounded correction

> Historical curator-review record from source snapshot `10ad4aba6d50ba4635db969725ed6d100ba29584`. The v0.2 candidate and test paths named below describe that earlier work and are not present in the current integrated tree. The current candidate is [the C2 15-packet collection](../examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json), with [per-packet dispositions](../examples/p5c2_packet_review_dispositions_2026-11-17.json) and [the integrated curator review](P5C2_INTEGRATED_CURATOR_REVIEW_2026-11-17.md). The evidence-role correction now covers all 15 packets. This record does not establish independent expert approval, source-use clearance or training authorization.

Status: review candidate only. Source snapshot: `10ad4aba6d50ba4635db969725ed6d100ba29584`. The original v0.1 collection remains unchanged. The v0.2 review candidate is not expert-approved, split-assigned, Gold or training-authorized.

## 1. Scope

Reviewed the five specialized tasks:
- `L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003` — conflict_reconciliation
- `L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012` — historical_case_reuse
- `L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013` — evidence_sufficiency
- `L1-CASSINI-RWA-NEXT-STEP-SYNTH-014` — next_step_recommendation
- `L1-SPACEBORNE-TWTA-LNA-HANDOVER-SYNTH-015` — handover_summary

This is a source/logic review by the curator, not independent expert adjudication.

## 2. Findings

### F01 — Context-only L0 source refs were listed as current supporting evidence

In all five specialized tasks, the L0 knowledge-evidence ID (for example `L0-E-003`, `L0-E-008` or `L0-E-011`) appeared in `cause_localization.candidates[].supporting_refs` and `evidence_assessment.supporting_refs`. Yet each L0 item explicitly states that it is a historical source fact and does not verify the current synthetic scenario.

Why this matters:
- The source can constrain historical mechanism, source certainty and task construction.
- The synthetic ML finding and synthetic logs are the current scenario inputs.
- Putting the L0 source ID in the current supporting-evidence list blurs contextual source grounding with evidence observed in the current scenario.

Correction in v0.2 candidate:
- Remove the L0 knowledge-evidence IDs from current-cause supporting refs and current evidence supporting refs.
- Keep the L0 material in `case.input.knowledge_evidence` with its explicit claim boundary.
- Keep synthetic ML/log references as current-scenario inputs, with limitations that they are synthetic and not physical verification.

This does not claim that synthetic ML/logs are real-world evidence; they are scenario evidence for the synthetic task only.

### F02 — Rejected SEL history was marked hardware COMPATIBLE despite explicit hardware difference

The two TROPICS Pathfinder tasks used `SYNTHETIC-HISTORY-SEL-REJECTED-001`. The item had `hardware_compatibility=COMPATIBLE` while its applicability limitation explicitly said the historical hardware configuration differs from the current scenario.

Correction in v0.2 candidate: set the compatibility assessment to `UNKNOWN`. Preserve the rejected outcome and all transfer limitations. A broad shared interface is a similarity basis, not proof of hardware compatibility.

### F03 — Specialized-task coverage is still only one packet per task type

Each of the five specialized task types has one example. The tasks demonstrate a template, not robust capability. Do not inflate the count by paraphrasing; create additional cases only when an independently sourced event family and a distinct diagnostic challenge are available.

### F04 — FUSE history-reuse task preserves important mechanism distinctions

The FUSE target separates:
- 2000-08-04 pitch-wheel Kapton-liner bubble / rotor contact hypothesis;
- 2001-02-16 yaw-wheel similar but separate episode;
- 2001-11/12 later complete failures attributed by the vendor to thermal housing distortion;
- Cassini low-speed lubrication redistribution as a different mechanism with hardware compatibility UNKNOWN.

No mechanism collapse was found in the reviewed target. Retain all source uncertainty and avoid transferring Cassini operating advice.

### F05 — TWTA handover task correctly preserves ground-test and LNA localization

The handover target keeps the case as a ground transponder performance test and localizes the historical source cause to LNA chips in linearizer modules, not the TWTA electron gun/helix/EPC. The current synthetic candidate remains unconfirmed and the source's executed module replacement is not presented as an action executed in the current synthetic scenario.

### F06 — Pathfinder conflict/evidence-sufficiency targets retain uncertainty

The two Pathfinder targets keep cross-interface short as a candidate/likely historical explanation, preserve rejected SEL as negative context and request direct electrical/topology evidence. The correction is limited to evidence-role classification and hardware compatibility.

## 3. Bounded review-candidate change

New immutable candidate collection:
`examples/l1_literature_synthetic_task_packets_v0.2_review_candidate.json`

Changes only five specialized packets:
- remove context-only L0 knowledge-evidence IDs from current supporting refs;
- set Pathfinder rejected-history hardware compatibility to UNKNOWN;
- rebind `case.expected_output` to the corrected `formal_target`.

No source fact, synthetic ML value, log, timestamp, diagnosis, certainty, disposal action, event-family ID or task count was changed. The original v0.1 snapshot is untouched.

## 4. Targeted tests

`tests/test_p5c2_specialized_task_review_candidate.py` checks:
- v0.2 collection passes the existing L1 collection validator;
- all five specialized tasks keep contextual L0 evidence out of current supporting refs;
- source facts remain available in the contextual knowledge-evidence field;
- rejected SEL hardware compatibility is UNKNOWN;
- formal_target and case.expected_output remain equal;
- all packets remain REVIEW_REQUIRED, Gold-disabled and training-disabled.

A passing test establishes structural contracts only, not expert correctness.

## 5. Admission state

- 15 synthetic packets / 9 source event families.
- All 15 REVIEW_REQUIRED.
- Zero expert-adjudicated L1 targets.
- Zero official splits.
- Zero authorized SFT records.
- Zero REAL_GOLD.
- Zero training runs.

The v0.2 file is a review candidate. It must not replace v0.1 as a production baseline until the source/logic review and independent domain review are completed.
