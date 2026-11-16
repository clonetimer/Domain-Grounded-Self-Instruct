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

The expanded pilot contains **15 literature-derived SYNTHETIC tasks from 9 source event families**. Ten are `diagnostic_synthesis`; one each are `conflict_reconciliation`, `historical_case_reuse`, `evidence_sufficiency`, `next_step_recommendation` and `handover_summary`. Twelve use `NO_HIT`; two include a historical `REJECTED` hypothesis; one includes a `PARTIALLY_CONFIRMED` Cassini history item with `UNKNOWN` hardware compatibility. Flight and ground-test sources are represented separately. Related episodes from TROPICS flight CRC, Lunar Orbiter III TWTA and NASA 22 N hydrazine testing remain grouped by event family. All 15 require independent expert review. No real Gold packet or formal split exists.

History Context needs controlled, *separately labeled* variants: no hit; confirmed and appropriately scoped; rejected; unresolved; conflicting confirmed/rejected; incompatible hardware; available after cutoff; and same event family. The last three should be **blocked/rejected adversarial tests**, not admitted as valid historical context. Keep hardware and time-incompatible candidates out of model-visible context unless the specific educational objective is to reject an explicitly marked untrusted candidate.

Do not create 20 variants of one incident to claim 20 independent cases. For an approximately 20-packet pilot, report both packet count and **source event-family count**. All variations from one family remain in one split, and no split is assigned to the current unreviewed collection.

## 3. Two-reviewer blinded scorecard

For each L1 packet, two independent domain experts see the same **authorized model-visible context and formal report**, without internal curator prompts, proposed alternative target, reviewer names, experiment arm, or Gold/synthetic marketing labels that would reveal an experimental arm. The reviewers must still be told when upstream diagnostic inputs are SYNTHETIC; blinding never removes provenance safety labeling.

Store expert identities, source permissions, and rich narrative notes in the **authorized review workspace**, not the public DGSI repository. Public code accepts only pseudonymous reviewer tokens, fixed finding codes and ten integer scores (1–5). It cannot verify independence or identity.

| Dimension | 1: unacceptable | 3: partially supported | 5: strong |
| --- | --- | --- | --- |
| `source_fidelity` | Represents synthetic data as real or strengthens source certainty | Minor source-boundary omissions | Historical source certainty and synthetic provenance preserved |
| `phenomenon_analysis` | Adds unsupported observations or confuses symptom and cause | Timeline/symptom summary incomplete | Only supplied observations, correct sequence and clear symptom/cause boundary |
| `ml_interpretation` | Promotes candidate to confirmation or score to probability | Candidate/status semantics partly preserved | Algorithm result, score semantics and limitations faithfully explained |
| `fault_source` | Incorrect or fabricated origin | Candidate plausible but poorly bounded | Source distinct from affected units, conclusion faithful |
| `affected_components` | Confuses affected units with source | Some affected units omitted | Scope consistent with upstream evidence |
| `evidence_fidelity` | Unsupported/misattributed references | Minor gaps | Traceable, correctly scoped and contradictory evidence addressed |
| `uncertainty` | False certainty or unjustified confidence | Over/under-calibrated wording | Explicit unknowns, abstention and appropriate certainty |
| `disposal_fidelity` | Invents performed actions | Partly supported disposition | Executed/planned/suggested/NOT_RECORDED faithfully separated |
| `historical_context_transfer` | Uses future/rejected/incompatible history to prove cause | Transfer limits incomplete | Time-safe, status-preserving, hardware/mechanism qualified |
| `engineering_actionability` | Unsupported unsafe instructions | Some checks useful | Source-aligned, bounded and feasible follow-up |

Each scorecard uses `dgsi-l1-blind-review.v1`: `blinded_packet_ref`, exactly two `assessments`, each having `reviewer_token`, all ten `scores`, `finding_codes`, and `decision` in `ACCEPT_L1 | REVISE | REJECT`. The validator accepts only fixed codes, no source text or private payload. Reviewers independently submit **before seeing each other's scores**.

Any 2-point-or-greater disagreement on any dimension, any differing overall decision, any substantive finding code, or a `REVISE` / `REJECT` verdict routes to secure adjudication; no automated approval. Even two matching `ACCEPT_L1` decisions are **only awaiting independent reviewer authentication**. L1 approval, release permission, SFT admission, data split, real Gold and training remain separate controlled decisions.

## 4. Coverage and admission gate

`audit_l1_coverage(collections, source_fact_cards=...)` invokes the underlying L1 collection validator, enforces distinct task IDs across supplied collections, rejects formal split assignments while packets have not passed L1 review, and returns only:

- packet and event-family counts per **separate** real-candidate versus literature-derived synthetic track;
- task-type coverage including missing task families;
- history Context coverage and unreviewed/split assignment counts;
- `real_gold_count=0`, `training_authorized=false`.

This is intentionally *not* a real Gold inventory or data leakage certification. Event-family aliases, real run identities, reviewer identities and source rights require independent authorized evidence. A collection status string alone cannot prove two independent reviews.

## 5. Experiment checklist

Before any model training (requires explicit authorization): freeze holdout incident families and source reports; freeze generation recipes; review upstream score semantics, model/run version, evidence IDs, mission cutoff, history `available_at`/`verified_at`; pre-register arms A (Base), B (Generic Self-Instruct), C (DGSI literature synthetic), D (DGSI real Gold, if admitted), E (same model + historical Context). Match independent holdouts, report synthetic versus real strata separately, include abstention and false-disposal rates. Record `NOT_RUN` for any unavailable real holdout or training arm.

**Current checkpoint:** 15 literature-derived synthetic L1 tasks, 9 source event families, 0 verified real Gold, 0 approved splits, 0 fine-tuning runs, and no effectiveness claim.


The FUSE history-reuse task uses the Cassini RWA case only as qualified Context. The Cassini case is PARTIALLY_CONFIRMED, its actual equipment scope differs from the current FUSE wheel, and hardware compatibility is UNKNOWN. The formal target must retain this limitation and must not cite the Cassini case as support for the FUSE cause. Its synthetic `available_at` is conservatively normalized to end-of-day on the 2004-05-10 NASA LLIS lesson date.


The pilot covers all six declared Case task types. The evidence-sufficiency variant shares the TROPICS Pathfinder event family with the diagnostic-synthesis task; the next-step variant shares the Cassini RWA event family; the handover variant shares the S-band TWTA ground-test family. These are task-type variants, not additional independent fault episodes, and must stay in their source-family split.


## 6. Immutable scorecard-to-source binding

The existing ten-dimension scorecard remains the sole selected review rubric. The separate integrity sidecar introduced by PR #43 fingerprints the exact model-visible L1 task and the referenced L0 cards, then validates the scorecard against those digests and the pending secure-adjudication state. See [L1 blind-review receipt binding](L1_BLIND_REVIEW_RECEIPT_BINDING.md). This does not provide reviewer authentication, source-licensing proof, Gold approval or training authorization.


## 7. L0 source review status

The L0 collection referenced by the current pilot has `review_status=AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`. This is an AI-assisted curation state, not independent domain-expert confirmation. The L1 task packets bind exact L0 fact-card bytes, but a digest proves only which version was reviewed; it does not prove that the source passage was interpreted correctly.

Before an L1 packet can be considered for an effectiveness experiment, the reviewers must inspect the cited public source itself and verify:
- the exact event or test type (flight, ground test, or knowledge-only);
- the source's original certainty and distinction between observation, cause statement and hypothesis;
- event-family and episode separation;
- source-recorded disposal versus proposed/conditional actions;
- whether the L1 scenario has introduced assumptions not present in the source.

The current 15 packets remain synthetic task-coverage fixtures. Neither the L0 source-card review nor the L1 task review is complete. No SFT export, split assignment, Gold admission or fine-tuning is authorized.
