# P4 L1 task-coverage matrix and independent blind-review rubric (v0.1)

**Scope:** Metadata-only L1 quality planning. This document and the implementation do **not** authorize SFT training, assign a dataset split, certify real Gold, authenticate reviewers, or make model diagnostic claims.

## 1. Frozen task definitions

Task families are defined by the **formal assistant behavior**, not a case's satellite name or failure mode.

| Task type | Required competence | Adversarial focus |
| --- | --- | --- |
| `diagnostic_synthesis` | Explain upstream ML findings against logs and operating context | Ranking scores are not calibrated probabilities; source versus affected subsystem |
| `historical_case_reuse` | Explain when a reviewed, as-of-available historical case is transferable | Incompatible configuration; same-incident reuse; misleading similarity |
| `conflict_reconciliation` | Reconcile competing ML/log/reference/history evidence | Rejected hypotheses are not positive precedents |
| `evidence_sufficiency` | State whether evidence supports a cause or requires abstention | Missing run version, absent evidence ID, unsupported certainty |
| `next_step_recommendation` | Recommend next diagnostic checks, not fabricated historic disposal | Follow-up actions separate from recorded disposal |
| `handover_summary` | Communicate cause candidates, affected units, uncertainty and disposition | No curator questions in formal assistant target |

Every packet must retain one L0 event family, explicit source fact references, a dedicated `internal_review.not_for_sft=true`, a conclusion-only `formal_target`, and a declared `track`.

## 2. Baseline pilot: independently observed coverage

The first three L1 packets contain **3 literature-derived SYNTHETIC tasks from 3 source event families**. Two are `diagnostic_synthesis` with `NO_HIT`; one is `conflict_reconciliation` with a historical `REJECTED` hypothesis. The other four task families have **zero** pilot packets. All three require expert review. No real Gold packet or formal split exists.

History Context needs controlled, *separately labeled* variants: no hit; confirmed and appropriately scoped; rejected; unresolved; conflicting confirmed/rejected; incompatible hardware; available after cutoff; and same event family. The last three should be **blocked/rejected adversarial tests**, not admitted as valid historical context. Keep hardware and time-incompatible candidates out of model-visible context unless the specific educational objective is to reject an explicitly marked untrusted candidate.

Do not create 20 variants of one incident to claim 20 independent cases. For an approximately 20-packet pilot, report both packet count and **source event-family count**. All variations from one family remain in one split, and no split is assigned to the current unreviewed collection.

## 3. Two-reviewer blinded scorecard

For each L1 packet, two independent domain experts see the same **authorized model-visible context and formal report**, without internal curator prompts, proposed alternative target, reviewer names, experiment arm, or Gold/synthetic marketing labels that would reveal an experimental arm. The reviewers must still be told when upstream diagnostic inputs are SYNTHETIC; blinding never removes provenance safety labeling.

Store expert identities, source permissions, and rich narrative notes in the **authorized review workspace**, not the public DGSI repository. Public code accepts only pseudonymous reviewer tokens, fixed finding codes and seven integer scores (1–5). It cannot verify independence or identity.

| Dimension | 1: unacceptable | 3: partially supported | 5: strong |
| --- | --- | --- | --- |
| `fault_source` | Incorrect or fabricated origin | Candidate plausible but poorly bounded | Source distinct from affected units, conclusion faithful |
| `affected_components` | Confuses affected units with source | Some affected units omitted | Scope consistent with upstream evidence |
| `evidence_fidelity` | Unsupported/misattributed references | Minor gaps | Traceable, correctly scoped and contradictory evidence addressed |
| `uncertainty` | Treats ranking score as probability or falsely confirms | Over/under-calibrated wording | Explicit unknowns, abstention and proper score semantics |
| `disposal_fidelity` | Invents performed actions | Partly supported disposition | Executed/planned/suggested/NOT_RECORDED faithfully separated |
| `historical_context_transfer` | Uses future/rejected/incompatible history to prove cause | Transfer limits incomplete | Time-safe, status-preserving, mechanism/configuration qualified |
| `engineering_actionability` | Unsupported unsafe instructions | Some checks useful | Source-aligned, bounded and feasible follow-up |

Each scorecard uses `dgsi-l1-blind-review.v1`: `blinded_packet_ref`, exactly two `assessments`, each having `reviewer_token`, all seven `scores`, `finding_codes`, and `decision` in `ACCEPT_L1 | REVISE | REJECT`. The validator accepts only fixed codes, no source text or private payload. Reviewers independently submit **before seeing each other's scores**.

Any 2-point-or-greater disagreement on any dimension, any differing overall decision, or a `REVISE` / `REJECT` verdict routes to secure adjudication; no automated approval. Even two matching `ACCEPT_L1` decisions are **only awaiting independent reviewer authentication**. L1 approval, release permission, SFT admission, data split, real Gold and training remain separate controlled decisions.

## 4. Coverage and admission gate

`audit_l1_coverage(collections, source_fact_cards=...)` invokes the underlying L1 collection validator, enforces distinct task IDs across supplied collections, rejects formal split assignments while packets have not passed L1 review, and returns only:

- packet and event-family counts per **separate** real-candidate versus literature-derived synthetic track;
- task-type coverage including missing task families;
- history Context coverage and unreviewed/split assignment counts;
- `real_gold_count=0`, `training_authorized=false`.

This is intentionally *not* a real Gold inventory or data leakage certification. Event-family aliases, real run identities, reviewer identities and source rights require independent authorized evidence. A collection status string alone cannot prove two independent reviews.

## 5. Experiment checklist

Before any model training (requires explicit authorization): freeze holdout incident families and source reports; freeze generation recipes; review upstream score semantics, model/run version, evidence IDs, mission cutoff, history `available_at`/`verified_at`; pre-register arms A (Base), B (Generic Self-Instruct), C (DGSI literature synthetic), D (DGSI real Gold, if admitted), E (same model + historical Context). Match independent holdouts, report synthetic versus real strata separately, include abstention and false-disposal rates. Record `NOT_RUN` for any unavailable real holdout or training arm.

**Current checkpoint:** 3 synthetic L1 tasks, 3 event families, 0 verified real Gold, 0 approved splits, 0 fine-tuning runs, and no effectiveness claim.
