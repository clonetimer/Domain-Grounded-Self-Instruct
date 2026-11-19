# P5-C16 — Unseen-publication holdout must include visible historical evidence

Date: 2026-11-19. Scope: **DEV_ONLY scientific audit**; `not_for_sft=true`. Source: frozen 21-task REV1 and its bound 13-card L0 fact-card set. This is a read-only analysis, not a new training split.

## Previously missed exposure

P5-C15 correctly grouped **21 synthetic task variants -> 9 source event families -> 7 primary cited publications** and prevented primary-source document leakage. However, task **L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012** has primary publication `FUSE-SPIE-2002-RWA` while its **model-visible** historical context references `LIT-CASSINI-RWA-DRAG-007`, and its `knowledge_evidence` includes `source_id=NASA-LLIS-1416`. Cassini tasks 008, 014, 021 use `NASA-LLIS-1416` as the primary publication. Therefore a *strict unseen-literature* experiment that trains on FUSE-012 and tests on Cassini, or vice versa, could inadvertently expose the held-out Cassini source through the FUSE input.

This matters even though the Cassini comparison is explicitly `PARTIALLY_CONFIRMED`, with `hardware_compatibility=UNKNOWN`. Its uncertainty status limits causal transfer; it does **not** make Cassini publication text invisible to the model.

## Actual new audit

`dgsi.l1_model_visible_source_holdout.audit_l1_model_visible_source_holdout` extends P5-C15's primary-document grouping with source exposures in:

1. `case.input.knowledge_evidence[*].source_id`;
2. `history_context.items[*].source_refs` linked to known L0 cards;
3. reused `history_context.items[*].case_ref` and explicitly synthetic source references, without pretending those synthetic identifiers are real publications.

Missing/unresolved public source IDs and discrepancies between `historical_cases` and history-manifest IDs are rejected rather than guessed. Only metadata are returned; no hidden source passages, audit notes or new references enter the user prompt or formal assistant target.

**Expected DEV_ONLY REV1 result:** seven distinct primary publications but **six strict model-visible independent clusters**, because the FUSE and Cassini publication groups become connected. The six-cluster count is a strict source-exposure upper bound, not six scientifically independent diagnosed events, expert-approved cases or robust evaluation folds.

## Boundaries and scientific significance

- This **strict unseen-publication** criterion must not be confused with real-world deployment: a properly qualified, as-of-safe Cassini historical reference may remain useful at inference. The audit does not invalidate historical CONTEXT generally.
- The frozen FUSE input also contains source-only answer hypotheses, and three history hits lack independently verified `verified_at` evidence. These are *separate* scientific and as-of blockers addressed by prior DEV_ONLY isolation/review work; passing this new audit does not certify them.
- No official train/validation/test assignment, independent expert receipt, source-rights certification, Gold promotion or model training is performed.
- For comparing DGSI against generic Self-Instruct, report model-visible document clusters as the strict sampling unit where claiming unseen-publication generalization. Avoid significance claims from only six coupled document clusters.
- This discovery concerns **evaluation isolation**, not changing the frozen REV1 case statements or removing legitimate ML diagnosis results.

## Verification and development lesson

Run `PYTHONPATH=src python -m unittest tests.test_l1_model_visible_source_holdout -v`. The tests include immutable REV1 metadata, a counterfactual that removes the FUSE-to-Cassini exposure in a **copy** and restores seven components, mismatched historical manifests, unresolved source IDs, cross-split plans and synthetic history reuse.

**Lesson:** the split graph must include **what the model sees**, not only the facts that originally generated a target. A historical reference can be scientifically non-confirmatory yet still carry a document-leakage risk in an unseen-source benchmark. Future source-document holdout audits should maintain primary-source and model-visible-source counts separately.

**Next product step:** obtain actual two-person adjudications of the six input-bounded FUSE/TROPICS candidate labels (P5-C14 v0.2), validate rights and historical temporal provenance, then conduct an explicitly authorized held-out evaluation. Until then, REAL Gold=0; synthetic review pending; split=0; model comparison NOT_RUN; training_authorized=false.
