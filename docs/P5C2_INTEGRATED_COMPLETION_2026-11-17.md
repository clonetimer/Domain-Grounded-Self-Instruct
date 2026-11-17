# P5-C2 Integrated Completion — C2-B through C2-E

Status: formally started. This is one integrated milestone with four coordinated workstreams and one shared release gate. It does not claim expert approval or authorize training.

## Product objective

Produce a stable, versioned, scientifically reviewed L1 candidate collection and a deterministic, fail-closed model-facing projection. The deliverable is the complete candidate corpus, review dispositions, coverage report, projection manifest and round-trip verification—not a succession of isolated tools.

The existing 15-packet v0.1 collection and 9 source event families are the frozen audit baseline. The v0.2 specialized-task correction remains a separate review candidate and must be assessed before promotion. Neither collection is automatically approved.

## Workstream B — scientific content review

Review every existing packet against its exact L0 source card and source passage:
- event and episode identity; distinguish separate incidents and test/flight events;
- observed phenomenon versus hypothesized cause;
- fault-source component versus affected components;
- physical mechanism and measurement-chain semantics;
- causal/temporal relationships supported by source facts;
- source certainty and alternative explanations;
- recorded disposal versus recommended/conditional/executed action;
- source-use rights and derivative/training restrictions.

Every packet receives a review disposition: RETAIN_CANDIDATE, REVISE_CANDIDATE, QUARANTINE_SOURCE_RIGHTS, REJECT_CANDIDATE or PENDING_EXPERT. A curator review is not independent expert approval. Where the source does not support a claim, preserve the uncertainty or remove the claim; do not repair it using unsupported general knowledge.

## Workstream C — formal target review

Review each Assistant Target as a diagnostic product:
- phenomenon and machine-result interpretation;
- fault-source localization and affected-object identification;
- direct current-scenario evidence support;
- uncertainty, competing hypotheses and abstention;
- historical Context transfer and rejection;
- disposal semantics and actionability;
- structured target versus report_text consistency.

Keep the historical L0 source in its bounded source/context field. It may constrain the historical mechanism and source certainty, but it is not direct evidence of the current synthetic scenario. Synthetic ML findings and logs are evidence only within the explicitly synthetic scenario, not physical verification.

Each retained target must be one canonical `formal_target`; `case.expected_output` must remain semantically identical. Curator prompts, reviewer notes and adjudication fields are never part of the model-facing user message or assistant target.

## Workstream D — model projection and serialization

Implement one deterministic allowlisted projection from the full L1 packet:
- select only the approved model-visible input fields;
- omit the entire `internal_review`, review receipts, reviewer identities, curator prompts and adjudication subtree;
- preserve synthetic track and source/evidence provenance;
- preserve the distinction between current scenario evidence and historical Context;
- serialize the existing three-message system/user/assistant structure;
- round-trip parse and validate every serialized row against the canonical target;
- bind the complete collection, source facts, task IDs, event-family IDs, user projections and target digests in one order-independent manifest.

For this milestone, execute projection and round-trip checks in a **blocked metadata-only preflight**. Emit zero SFT rows. No source card with unresolved expert status or training-use rights can pass the external admission gate. This gives us a reproducible serialization-ready candidate without pretending it is authorized training data.

## Workstream E — coverage gap analysis and bounded supplement

Calculate coverage at both packet and independent event-family levels:
- six task types;
- flight versus ground-test events;
- fault domains and component levels;
- measurement-chain confounders;
- cross-subsystem/common-cause effects;
- conflicting evidence and competing causes;
- insufficient-evidence and correct-abstention cases;
- historical compatible transfer, no-hit, mismatch, rejected precedent and same-family exclusion;
- disposal recommendation, execution and effect verification.

First classify each gap as covered, weakly covered, missing, or not assessable. Add a synthetic task only when it addresses a demonstrated gap and is supported by an independently reviewed source event/family. Keep all variants of one source event family together. Do not create paraphrases to inflate independent sample count. If source rights or event diversity block a gap, report the gap rather than fabricate a substitute.

## Shared execution and integration order

These are workstreams, not separate release milestones:
1. Freeze baseline and review contract.
2. Run C2-B and C2-C reviews across all 15 packets in parallel; produce per-packet dispositions and a consolidated defect register.
3. Apply bounded corrections in a new immutable collection version; keep v0.1 and v0.2 snapshots unchanged.
4. Complete C2-D allowlisted projection and three-message round-trip on the corrected candidate collection.
5. Complete C2-E coverage gap analysis; add only source-justified candidates, then rerun B/C/D over the full collection.
6. Produce one integrated report and one release candidate manifest with exact file hashes and counts.

## Acceptance criteria

- Every original packet has an explicit C2-B and C2-C disposition.
- Every correction is tied to a source fact, evidence reference or explicit schema/target rule.
- No unresolved source-rights item is silently admitted.
- No context-only L0 reference is presented as current-scenario direct support.
- No curator/internal review content reaches model projection or target.
- One canonical target source; duplicated target representations are equal or release is blocked.
- All projected messages pass round-trip validation and source/event-family lineage checks.
- Coverage reports packet counts and independent event-family counts separately.
- Any added task is traceable to a reviewed source family and a demonstrated gap.
- All remaining limitations and expert decisions are explicit.
- CI passes on Ubuntu and Windows, including targeted tests and full regression.

## Release-state vocabulary

- `ENGINEERING_REVIEWED_CANDIDATE`: curator review and structural/semantic checks complete.
- `EXPERT_ADJUDICATED`: independent expert review and disagreements resolved.
- `RIGHTS_CLEARED`: source-use authorization confirmed for the intended use.
- `SFT_AUTHORIZED`: all applicable external admission and release gates passed.
- `TRAINED`: an actual authorized training run exists.

These states are not interchangeable. P5-C2 can deliver an engineering-reviewed, serialization-ready candidate with a blocked preflight. It cannot manufacture expert adjudication, source rights, REAL_GOLD, or training permission.

## Current baseline and non-claims

- 15 literature-derived synthetic packets.
- 9 source event families.
- All 15 REVIEW_REQUIRED at the frozen v0.1 baseline.
- Zero REAL_GOLD, zero official splits, zero authorized SFT records, zero fine-tuning runs.
- No claim of model effectiveness or real-world generalization.
- No real-case evidence is synthesized into this literature track.

Machine-readable contract: `examples/p5c2_integrated_review_contract_2026-11-17.json`.
