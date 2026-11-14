# Domain-Grounded Self-Instruct — delivery roadmap

## Phase 1 / P1: grounded curation foundation

**Deliver:** source registry, ADCS terminology draft, fault/effect catalog, telemetry dictionary, empty simulation truth admission registry, JSON contract, offline validator, adversarial tests and draft Skill.

**Exit:** tests pass, CLI preflight passes for a clearly hypothetical abstention example, known fabricated terms/causal overreach/self-attestation/truth leakage fail, source provenance remains distinguishable. Alias semantics and 11 public source-passage locators are now registered; all preferred terms remain draft pending domain review. The draft Skill remains unapproved pending independent blind evaluation.

## Phase 2 / P2: verified evidence admission

Build a local-only (or access-controlled) ingestion adapter to pin Basilisk version, run settings, channel/unit mappings, trace hash, injection timestamps, event windows, verified physical response and split policy. Reject `DECLARED_ONLY`, catalog-only and source-free runs. Keep raw R21 and other restricted traces out of the public repository. Explicitly separate gyro/RW runtime fields from older AAS CSV labels and map them only with reviewed aliases.

## Phase 3 / P3: assisted Self-Instruct pilot

Generate **candidate** instruction-answer pairs from selected public source passages, graph relations and admitted telemetry. Sample both normal/ambiguous/insufficient-evidence cases and concrete fault hypotheses. Review 30–50 seed candidates manually; do not assert output-label correctness from generator agreement or synthetic trace alone.

## Phase 4 / P4: correction UI and quality evaluation

Present the original prompt, evidence locators, candidate output, atomized claims, terminology alerts and suggested revisions side-by-side. Expose accept/edit/reject with append-only audit trail. Evaluate hidden test cases and independent expert adjudication. Compute first-pass approval and final delivery yield, plus manual minutes per accepted seed.

## Phase 5 / P5: freeze and fine-tuning export

Freeze only human-approved Gold Seed, and keep training-only synthetic expansion separate. Run leakage/near-duplicate checks across source documents, simulation runs, and train/dev/test boundaries. Export to target fine-tuning schemas, preserving review/provenance sidecars. No release until independent evaluation confirms suitability.

## Known open engineering questions

- Source licensing / private dataset distribution and per-reference version pinning.
- Reviewer authentication and tamper-evident audit receipts (metadata currently insufficient).
- Technical phrase discovery beyond the current narrow suspicious-compound heuristic; a clean scan does not prove vocabulary completeness.
- Real multi-sensor conditional independence and causal evidence, not just declared graph edges.
- Mechanism-to-measurement mapping across Basilisk, SatAgentSimulation and AAS channel schemas.
- Independent judge calibration and evidence-based factual audit on previously unseen reports.
