# P5-C: SFT-first data production plan

Status: execution plan only. It does not admit data, assign official splits, authorize export, or start model training.

## 1. Product objective and progress measure

DGSI's product is a trustworthy, traceable, task-balanced spacecraft fault-diagnosis SFT corpus for the LLM's second-stage engineering diagnosis. The LLM consumes upstream ML findings, diagnostic logs, spacecraft/mission context and permitted historical experience. Raw telemetry remains upstream input by default.

Progress is measured by usable, independently reviewed examples and event-family coverage—not PR count, schema count, test count, synthetic row count, or generated text volume.

Every delivery report must distinguish candidate packets, source-reviewed packets, independently expert-reviewed packets, externally admitted SFT-eligible packets, actually serialized SFT examples, and examples authorized and actually used in training. Never collapse these statuses into one "dataset size".

## 2. Frozen data policy

Maintain the user-approved PARALLEL data tracks.

### Track A — REAL_CASE_CANDIDATE

Actual or de-identified engineering cases. A case remains a candidate until source provenance/rights, de-identification, upstream ML result, diagnostic logs, spacecraft/mission context and independent expert adjudication are complete.

Required model-visible input:
- upstream ML diagnosis and its model/run/score semantics;
- diagnostic logs and their source/time references;
- spacecraft configuration, mission phase and operating mode;
- qualified historical Context and transfer limitations.

A real source report alone is not a complete diagnosis example. Do not fabricate absent ML outputs, logs, spacecraft state or mission operations to make the packet look complete.

### Track B — LITERATURE_DERIVED_SYNTHETIC

Synthetic scenarios derived from independently reviewed public L0 event facts. Keep field-level provenance, generation recipe/version, explicit assumptions and not-simulated items. Synthetic ML outputs, run IDs, logs, timestamps, configuration and mission context must remain explicitly synthetic.

Synthetic data can expand rare-task and adversarial coverage. It is never relabeled as an actual flight/test record or REAL_GOLD.

### Historical experience — CONTEXT

Historical cases remain a separate, qualified context input. They can inform comparison and transfer limitations but cannot become direct evidence for the current event or vote on its root cause. Incompatible, rejected, unresolved, future and same-event-family history must be blocked or explicitly treated as adversarial rejection cases.

## 3. Current baseline and actual bottleneck

The L1 literature pilot contains 15 synthetic packets across 9 source event families and all six task types. Twelve referenced L0 event cards remain AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION. The packets are REVIEW_REQUIRED, have no official split, and are not training-authorized. No REAL_GOLD case has been admitted and no fine-tuning run has started.

Therefore the first production bottleneck is source and target admission, not scenario generation throughput.

Do not expand the 15-packet pilot by paraphrasing the same event and counting variants as independent cases. Preserve event-family grouping for review, coverage and split isolation.

## 4. Execution stages and exit criteria

### P5-C0 — Freeze the dataset contract and scoreboard

Deliver:
- immutable inventory separating track, event family, packet, source-card and review status;
- task-type coverage and event-family coverage reports;
- one source-to-target lineage view per candidate;
- a blocked/admitted/serialized/trained status vocabulary;
- frozen target rubric and controlled-effectiveness metrics.

Exit only when counts can be reproduced from manifests and never mix synthetic packets, real candidates, Gold, validator fixtures or knowledge-only sources.

### P5-C1 — L0 source admission and real-case intake

For the 12 referenced L0 cards:
1. retrieve and inspect the exact cited public source passage;
2. confirm source statement, certainty, event class, episode grouping, recorded disposal and migration limitations;
3. obtain independent domain-expert review under the existing review rubric;
4. record disagreements for secure adjudication;
5. fingerprint the reviewed source-card version and invalidate dependent L1 review receipts if the card changes.

In parallel, prepare a private REAL_CASE_CANDIDATE intake queue. Request only the evidence needed to build a complete case: authorized source, upstream ML output and score semantics, diagnostic log, spacecraft/mission context, time basis, and source/evidence locators. Missing evidence remains missing; do not fill it with synthetic values in the real track.

Exit: each source is explicitly accepted for its permitted use, revised, rejected, or remains pending. No source status is inferred from a passing validator.

### P5-C2 — L1 task and target adjudication

Review each task for:
- task instruction matching one of the six frozen task types;
- source fidelity and synthetic/real track correctness;
- phenomenon versus cause distinction;
- fault-source localization versus affected-component identification;
- ML score semantics and upstream model/run traceability;
- evidence relevance, completeness and contradiction handling;
- uncertainty and abstention appropriateness;
- recorded disposal versus planned/recommended action;
- historical Context transfer limits;
- formal assistant target containing conclusions, not curator prompts or hidden reasoning checklists.

Use two independent reviewers. Resolve disagreements through the existing secure adjudication route. A bound receipt is not itself reviewer authentication or expert approval.

Exit: only externally admitted tasks may proceed to a controlled experiment. L1 approval, Gold admission, split assignment and training permission remain separate decisions.

### P5-C3 — Balanced corpus construction and split freeze

Build coverage across:
- six task types;
- fault source and affected-component distinctions;
- confirmed, candidate, competing and unresolved causes;
- measurement-chain confounders and common-cause cross-subsystem effects;
- conflicting current evidence;
- insufficient-evidence and correct-abstention cases;
- historical no-hit, qualified transfer, rejected precedent, hardware mismatch, future history and same-event-family rejection.

Split by source event_family_id and incident/run lineage, not by packet or paraphrase. Keep every task variant from one event family in a single split. Holdout source reports and event families must not be used for generation, prompt construction or retrieval corpus construction.

Do not force a nominal percentage split while the independent event-family inventory is too small. Report actual counts and mark unsupported evaluation strata NOT_RUN.

### P5-C4 — SFT serialization and release gate

Reuse the existing L1-to-SFT release preflight and standalone target contract. The serializer must:
- consume only admitted L1 packets;
- produce the existing three-message system/user/assistant structure;
- keep model-visible context separate from curator-only fields;
- serialize a structured diagnostic report target;
- preserve case/source/run/evidence references and artifact hashes;
- reject synthetic/real track confusion, invalid provenance and cross-split leakage.

The release preflight currently emits zero SFT records and remains blocked pending external admission. Do not weaken this boundary to make the first dataset appear trainable.

Exit: authorized SFT serialization count equals the count of externally admitted examples; all rejected/pending packets remain excluded and auditable.

### P5-C5 — Controlled training and effectiveness evaluation

Follow the existing pre-registration draft. Compare Base, matched Generic Self-Instruct, DGSI synthetic, DGSI real Gold when available, and the same DGSI model with historical Context enabled. Keep source strata separate and match data/optimization budgets where feasible.

Primary metrics:
1. fault-source localization;
2. affected-component identification;
3. evidence consistency and attribution;
4. uncertainty calibration and abstention;
5. disposal/action fidelity;
6. historical Context transfer/non-transfer fidelity.

Secondary metrics include report completeness/readability, actionability, latency and token cost. Use blinded expert evaluation and adjudication. If no authorized real holdout exists, mark the real-holdout result NOT_RUN; do not substitute synthetic data.

KG/path-augmented representation remains an optional parallel experimental arm. First establish the non-KG baseline corpus and evaluation protocol, then run the paired A–E representation ablation on identical admitted cases. Do not make KG JSON a mandatory input or claim it improves SFT before results support that claim.

## 5. Data-quality scoreboard

Publish a reproducible snapshot with the following counts, separated by REAL_CASE_CANDIDATE and LITERATURE_DERIVED_SYNTHETIC:

| Measure | Required interpretation |
|---|---|
| Source cards reviewed / accepted / rejected / pending | Source admission, not packet approval |
| Candidate packets / reviewed / admitted | Task curation status |
| Distinct event families | Independent source coverage, not row count |
| Six task-type counts | Task competence coverage |
| Evidence-complete targets | Every material claim traceable to permitted evidence |
| Reviewer agreement / adjudication pending | Review quality and unresolved disagreement |
| REAL_GOLD count | Only externally admitted real cases |
| SFT serialized count | Only outputs of authorized release gate |
| Official split counts | Event-family-disjoint immutable manifests |
| Training runs / holdout results | Actual experiments, not plans or dry runs |

Hard stops:
- no current-event direct support from historical Context;
- no synthetic field represented as real observation;
- no unresolved/rejected source or target silently promoted;
- no duplicated event family across splits;
- no target claim without permitted evidence;
- no training/export without external authorization.

## 6. Engineering work prioritization

Continue building tools only when they unblock a named data-quality or production bottleneck. Each engineering PR must state which data-production step it enables, which dataset-quality failure it prevents, how the improvement is measured on representative cases, and what it does not prove.

B4.4 artifact invalidation is valuable because it protects review freshness. B4.5 expert annotation benchmark is valuable only when it measures expert-adjudicated diagram labels/ports/links on real or authorized source figures. It must not become an isolated computer-vision benchmark detached from the SFT target.

Do not prioritize further generic CLI polish or schema expansion when no corresponding data-production blocker exists.

## 7. Immediate next actions

1. Finish B4.4 exact-head CI and close only after PR + Push, Ubuntu + Windows, full toolkit ZIP/detached tests pass.
2. Produce the P5-C0 machine-readable baseline inventory from existing L1 manifests; no new synthetic rows.
3. Prepare a review queue for the 12 L0 event cards, retaining exact source passages and review state.
4. Prepare the REAL_CASE_CANDIDATE evidence intake checklist for actual upstream ML outputs, diagnostic logs and spacecraft/mission context.
5. Run the existing L1 coverage and release preflight to record the actual blocked counts.
6. Only after source admission, revise/extend tasks to fill demonstrated coverage gaps and proceed to C2/C3.

## 8. Current claims boundary

This plan is an execution guide, not a claim that the current pilot is approved, complete, or trainable. Current baseline remains 15 literature-derived synthetic packets, 9 source event families, 12 referenced L0 cards pending domain-expert confirmation, zero admitted REAL_GOLD, zero official splits, zero authorized SFT exports and zero fine-tuning runs.
