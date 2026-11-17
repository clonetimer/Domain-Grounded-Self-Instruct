# P5-C2 structural audit of the 15-packet L1 literature pilot

Snapshot: `10ad4aba6d50ba4635db969725ed6d100ba29584`  
Status: structural/lineage audit only. No packet is expert-approved or training-authorized.

## Results

- 15 literature-derived synthetic task packets.
- 9 distinct source event families.
- All 6 task types are represented, but distribution is 10 diagnostic_synthesis and one each of conflict_reconciliation, historical_case_reuse, evidence_sufficiency, next_step_recommendation and handover_summary.
- All 15 are `REVIEW_REQUIRED`.
- All 15 have synthetic provenance declarations for ML findings, diagnostic logs, spacecraft context and operational context.
- All source fact references resolve to the L0 collection.
- All formal-target evidence references resolve to declared input evidence IDs in this structural pass.
- All 15 contain an `internal_review` subtree marked `not_for_sft=true`.
- `formal_target` equals `case.expected_output` in all 15 packets.
- Zero official split assignments, zero authorized SFT records, zero REAL_GOLD, zero training runs.

Machine-readable details: `examples/p5c2_l1_pilot_structural_audit_2026-11-17.json`.

## Data-product findings

### 1. Coverage is not balance

The pilot demonstrates that six task types exist, not that all six capabilities are robust. Ten of fifteen packets are diagnostic synthesis. Each specialized task type has only one example. Do not expand by blind duplication; first review the specialized examples, then identify whether genuine source-family diversity supports additional cases.

### 2. Curator material requires a strict model-facing projection

Every packet contains internal review material. The `not_for_sft` flag is necessary but not sufficient. Any future serializer must build an explicit allowlisted model-facing projection and structurally omit the entire `internal_review` subtree, review notes, reviewer fields, curator questions and adjudication-only content. Add negative tests that inject these fields at root and nested locations.

### 3. Event families are the independence unit

Fifteen packets represent nine source event families. Related variants must remain together in future splits. Packet count is not incident count, and a paraphrase/task variant is not an independent event.

### 4. Synthetic provenance is explicit but not scientific validation

All core input classes are marked synthetic and the reference graph is structurally closed. This does not prove that generated event sequences, values, component relationships, ML score semantics or causal interpretations are physically plausible. Those require source-grounded expert review.

### 5. One canonical target source is required

Each packet duplicates the target in `case.expected_output` and `formal_target`. They are equal in the current snapshot. The serializer must choose one canonical target source and reject any drift between the two representations; do not manually maintain two divergent answers.

### 6. Source rights and source approval block admission

All 15 remain REVIEW_REQUIRED. Public availability does not establish third-party training rights. The L0 source approval and rights status must flow into the dependent L1 packet and release preflight. A green validator cannot override a source-use restriction.

## Review order

1. Specialized task variants (conflict reconciliation, historical reuse, evidence sufficiency, next-step recommendation, handover) because each currently has only one example.
2. Measurement-chain confounder (Lunar Orbiter III power monitor).
3. Multi-module localization (spaceborne S-band TWTA LNA).
4. Cross-subsystem/common-cause Pathfinder event.
5. Distinct episode and mitigation-transfer cases (TROPICS A/B, hydrazine injector/catalyst, FUSE/Cassini RWA).

For each packet, review source facts and certainty, synthetic input plausibility, evidence-reference correctness, target fidelity, uncertainty and disposal semantics. Review the L0 source and rights before considering any L1 admission.

## Explicit non-claims

This audit does not validate domain correctness, independent expert agreement, source licensing, real-case generalization, SFT export or model performance. No new synthetic packets were generated. No formal split was assigned. All fixtures and task packets remain non-Gold and training-disabled.
