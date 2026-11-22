# P5-C5 — REV1 historical Context coverage and evaluation feasibility
2026-11-19 | **REVIEW_ONLY · not_for_sft=true · NOT expert validated**

## Sources / immutable boundaries
Read-only C2 REV1 21-task reviewer-A scientific handoff and four-case five-method development plan. Frozen collection projection SHA-256: `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`.
- C2 reviewer handoff ZIP SHA-256: `07e6ac7ad9c92d89aee6fb8123c61849684ba0ddd6571122de949cc81ed5eda1`
- Four-case development-plan ZIP SHA-256: `7c179663530ed2df38d8fb2ebe0a313cd8dc45178137d9fbd243ef1a4a60f118`
- The plan's four task/packet SHA-256 bindings and collection hash matched the read-only reviewer snapshot (4/4). Neither the frozen candidate packets nor expert forms were edited.

## Measured candidate coverage

| Metric | Checked result |
|---|---|
| Track | LITERATURE_DERIVED_SYNTHETIC only; 21 REVIEW_REQUIRED candidates, 9 event families, 7 source documents |
| Task types | diagnostic_synthesis 11; evidence_sufficiency 5; conflict_reconciliation 2; historical_case_reuse 1; next_step_recommendation 1; handover_summary 1 |
| Historical Context | 3/21 tasks, across only 2/9 event families |
| Historical status | PARTIALLY_CONFIRMED 1, REJECTED 2; two REJECTED hits are the **same synthetic history case** reused in two current packets |
| Historical hardware applicability | UNKNOWN 3; known COMPATIBLE 0 |
| Historical hits with confirmed **and** compatible positive transfer | **0** |
| History available_at | 3/3 populated and no later than respective synthetic analysis_cutoff; original source-time trust is separately unverified |
| Physical candidates | 22 candidate entries |
| Target evidence ID references | 71 summed packet-local unique refs, 0 unresolved aliases; ID resolution does NOT prove evidentiary support |
| Synthetic diagnostic logs later than analysis_cutoff | 0 detected in 21 packets |
| Candidate supporting_refs consisting only of an ML claim alias | 2 cases: SCI-002 `ML-E-002`, SCI-016 `ML-E-016-MONITOR` |
| RECORDED disposal | 5 packets: 004/006/009/012/020; SCI-009 episode-action semantics unresolved |
| SOTA plans | 4 input comparison units × 5 methods = 20 **NOT_RUN** slots; actual outputs 0; independent scores 0; independent holdout NOT assigned |

### Result for science claims

**Positive historical transfer benefit is NOT_EVALUABLE on REV1**. There is no CONFIRMED + COMPATIBLE historical example, no positive-transfer label that can support an effect-size estimate, and only two current event families with any hit. Rejected and partially confirmed history may support tests of cautious refusal/non-transfer after human review; they cannot confirm the current cause or stand in for positive transfer. The historical examples are clustered, not independent observations.

Likewise, the 21 packets are NOT 21 independent test events: related episodes and variants share event families, source facts and documents. The four-case plan is DEV_ONLY with no held-out evaluation and no model generation; do not claim SOTA performance.

### Expert questions and next actionable scientific work

1. Use the existing blinded A/B reviewer handoffs to adjudicate SCI-002/SCI-016 (monitor-vs-physical-RF evidence polarity) and SCI-009 (precursor heat treatment versus subsequent valve/injector disposal), and to verify SCI-017's humidity-scoped PASS/FAIL. Keep exact packet hashes; if approved changes exist, produce a distinct re-hashed REV2, never quietly edit REV1.
2. Pre-register a paired historical-context ablation: same upstream ML results, logs, current mission/configuration, and analysis_cutoff; only the as-of-eligible source-bound history summary changes between NO_HIT and HIT. Report negative-transfer refusal separate from positive-transfer utility. Positive transfer is currently NOT_EVALUABLE; do not report zero accuracy as if cases existed.
3. Keep any future train/validation/test separation by source event_family/episode and source lineage, never random record-level splits. Keep REAL Gold versus SYNTHETIC statistics and training/evaluation independently labeled.
4. Seek authenticated A/B review, reuse-rights evidence for seven source documents, and genuine upstream evidence/logs/configuration for five REAL candidate cases. The synthetic cohort must not be promoted to Gold or training authorized by this audit.

## Reproduction and limits

In the reviewer-A JSON handoff, iterate all 21 `items`, group by `event_family` and `task_type`; read `historical_context.items[].outcome_status`, `hardware_compatibility`, `hit_metadata.available_at`; compare to `synthetic_input.analysis_cutoff`. Count evidence refs per packet after union of candidate `supporting_refs` and `evidence_assessment` supporting/contradicting refs, checking membership against synthetic logs, upstream ML evidence aliases, and knowledge context. Check log timestamp <= cutoff. Identify candidates whose supporting refs are solely upstream ML evidence aliases, rather than independent logs. Cross-check four planned task IDs, packet SHA-256s and collection SHA with the same reviewer snapshot. This is **only structural triage**, not validated physical diagnosis, provenance/license clearance, independent experiment or expert review.

**Development experience:** Green CI and fully resolvable evidence IDs do not guarantee physically valid evidence polarity, temporal disposal roles or an identifiable historical-context treatment effect. Prioritize scientific adjudication and missing positive/negative experimental coverage over further generic gate proliferation.
