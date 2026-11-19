# P5-C17 — Six-cluster feasibility and first-pass scientific review queue

Date: 2026-11-19. **DEV_ONLY / coordinator-side / not_for_sft=true**. This is an analysis and an external-expert work queue, **not** an accepted dataset, score, new model evaluator, actual holdout assignment or release authorization.

## Pinned source

- REV1 L1 collection (21 SYNTHETIC tasks, 9 event families), Git blob `f141694748d5425b63b469b5b0b25064e1b402c8`, at `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json`.
- L0 source fact cards, Git blob `73f8f00dd6ecaf60cb75b0e1d566537c4e27579f`, at `examples/l0_public_literature_fact_cards_2026-11-15.json`.
- Computed cohort: `examples/p5c17_six_cluster_review_and_eval_feasibility_DEV_ONLY_20261119.json`.
- These inventories are **not** a real Gold cohort. Neither their row count nor an automatic source fingerprint constitutes domain-scientific approval or document reuse permission.

## Actual experimental denominator

Primary source provenance gives seven publications. When history and knowledge **visible to the model** are also accounted for, #182/P5-C16 connects Cassini and FUSE into a single strict unseen-source group: **six publication-exposure clusters**, not seven independent holdouts or 21 independent scientific events.

| Cluster | Model-visible publication IDs | REV1 task IDs (suffix) | Rows |
| --- | --- | --- | ---: |
| C01 | FUSE-SPIE-2002-RWA + NASA-LLIS-1416 | 008, 012, 014, 020, 021 | 5 |
| C02 | JOURNAL-2026-TWTA-SBAND-POWER-DROP | 011, 015, 019 | 3 |
| C03 | MITLL-TROPICS-LESSONS-2025 | 003, 004, 005, 006, 013, 017 | 6 |
| C04 | NASA-CR-66461 | 002, 007, 016, 018 | 4 |
| C05 | NASA-NTRS-20040171604 | 001 | 1 |
| C06 | NASA-TM-100232 | 009, 010 | 2 |

Task-type distribution: diagnostic_synthesis **11**, conflict_reconciliation **2**, evidence_sufficiency **5**, historical_case_reuse **1**, next_step_recommendation **1**, handover_summary **1**.

**New feasibility finding.** A leave-one-cluster-out development diagnostic would leave zero examples of `historical_case_reuse` and `next_step_recommendation` in the *remaining* cohort when C01 is held out, and zero `handover_summary` when C02 is held out. This means the existing REV1 cannot establish training-driven generalization for all six task types under strict source isolation. Even though six cluster-level folds can be enumerated mathematically, significance estimates from six nonrandom groups are not defensible as robust proof of DGSI gains. These source documents may also have appeared during foundation-model pretraining.

Do **not** label a fold as `train`, `validation` or `test` in the dataset. This matrix is an **analytical exposure grouping only** and does not create official splits.

## Actionable first-pass expert review: 10 of 21 candidates

The following initial calibration batch covers **all six source clusters and all six task types** while including the four currently flagged science questions, SCI-002/009/016/017:

| Task suffix | Cluster | Task role | Focus of independent review |
| --- | --- | --- | --- |
| 001 | C05 | diagnostic_synthesis | Baseline event interpretation and source boundary |
| 002 | C04 | diagnostic_synthesis | SCI-002: power-monitor versus RF causal/evidence roles |
| 003 | C03 | diagnostic_synthesis | Upstream ML candidate versus cross-interface confirmation; synthetic log provenance |
| 009 | C06 | diagnostic_synthesis | SCI-009: injector symptom/causal and disposal chronology |
| 012 | C01 | historical_case_reuse | Cassini PARTIALLY_CONFIRMED, hardware UNKNOWN, missing verified_at, no causal vote |
| 014 | C01 | next_step_recommendation | Proposed checks versus recorded interventions |
| 015 | C02 | handover_summary | Evidence-preserving handover, no mechanism invention |
| 016 | C04 | conflict_reconciliation | SCI-016: competing Lunar Orbiter mechanisms remain competing |
| 017 | C03 | conflict_reconciliation | SCI-017: ground/flight episode and conflicting qualification evidence |
| 020 | C01 | evidence_sufficiency | FUSE unresolved cause and abstention despite synthetic candidate |

These are **ten review assignments, not ten admitted L1 packets**. The remaining eleven packets still require complete two-person review. The selection prioritizes reviewer calibration and coverage, *not* statistical representativeness; C01 is intentionally overrepresented for its singleton task types. For every assignment, the coordinator must bind the exact task_id, packet hash, full permitted source locator, input hash, independent reviewer token, scored rubric and adjudication decision. Reviewers must receive isolated forms; curator-side hypotheses, answer sidecars and paired-arm deltas must not enter model input or the reviewer’s blinded materials. No private reviewer identity or restricted opinion is published.

## What may be evaluated, and what must not be claimed

1. **Before source admission:** use the matrix only to inspect task coverage and request source-specific decisions. Do not fine-tune or export SFT. All 21 remain REVIEW_REQUIRED and 0 expert-admitted.
2. **Development-only skill diagnostic (after suitable approvals):** source-cluster leave-one-group-out may test procedural failure modes, report outcomes for each cluster and task type, and keep exact same inputs and budgets across Base / Generic Self-Instruct / DGSI synthetic methods. It is **not** an untouched final blind benchmark, because the REV1 cases and their science have been used for method development.
3. **Definitive controlled comparison:** acquire and freeze **new independent source-publication groups**, with an external adjudicated, source-disjoint holdout never exposed to dataset constructors or retrieval during generation. Include additional independent cases for the three singleton types. Register sample sizes and scoring rules before observing model output. Keep REAL and SYNTHETIC arms separately sampled and reported.
4. **History Context causal contrast:** current DEV A/B pilot consists of three task pairs but only two independent current diagnostic cores. The historical hits lack independently trustworthy `verified_at` and are not confirmed compatible positive examples. It may be used only to explore rejection of incorrect historical transfer, not to claim a positive retrieval benefit. Do not score against withheld full-L0 answers.
5. **Scoring:** pair the same holdout examples across arms, evaluate fault source separately from affected components, evidence IDs and support, uncalibrated-score interpretation, uncertainty/abstention, disposal fidelity, and history transfer/rejection. Report raw judgments and per-cluster uncertainty; do not replace expert assessments with text similarity or claim statistical superiority using task paraphrases as independent samples.

## Specific blockers and intended external handoff

- **Scientific review:** two independent experts must decide SCI-002/009/016/017 and the first-pass ten tasks, followed by the other eleven; six P5-C14 input-bounded candidate labels remain editorial drafts. Keep independent receipts private, hash-bound and unresolved disagreements blocked.
- **Source rights:** seven underlying publications need rights/reuse-scope documentation. Mere public availability is not authorization for redistribution or training.
- **Real data:** five user REAL L0 candidates still lack complete authorized upstream ML result, logs, configuration/mission context and review evidence; Gold=0.
- **History as-of:** historical `verified_at` evidence remains missing; never invent it or turn a rejected/partially confirmed prior into current root-cause proof.
- **Training and comparisons:** official split=0; serialized admissible SFT=0; model comparison NOT_RUN; training_authorized=false.

**Development lesson:** a six-task-type coverage table can conceal an **evaluation support failure**: three task types appear in only one primary publication exposure cluster each. Prioritizing actual expert decisions and new independent source families is now more valuable than adding another generic validator. Maintain strict denominators (tasks / event families / publications / model-visible clusters / real Gold / reviewed and admitted targets) as distinct quantities.

Related: #180 (input-visible target candidates), #181 (primary-publication holdout), #182 (model-visible-publication holdout), D0 #8 and P3 #4. No original REV1 or source document is modified by this note.
