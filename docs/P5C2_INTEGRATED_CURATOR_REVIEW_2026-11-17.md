# P5-C2 integrated curator review — current candidate dispositions

Source baseline: `examples/l1_literature_synthetic_task_packets_v0.1.json`  
Candidate: `examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json`  
Disposition ledger: `examples/p5c2_packet_review_dispositions_2026-11-17.json`

## Review scope and status

All 15 packets received a curator-level structural and source-role review. This is not independent domain-expert adjudication. Every packet remains review-required and not training-authorized.

The review confirms:
- 15 packets across 9 source event families;
- all six task types are represented, but five specialized types have one packet each;
- synthetic ML/log/spacecraft/operational inputs are explicitly provenance-marked;
- all formal targets remain bound to `case.expected_output`;
- internal review material remains in the full packet and must be omitted by the allowlisted projection;
- no official split or SFT row is authorized.

## Integrated evidence-role correction

The earlier specialized-task correction exposed a broader collection issue: all 15 tasks had their historical L0 context evidence IDs included among current-scenario supporting references. This incorrectly blurred historical source grounding with current synthetic scenario evidence.

The new C2 review candidate applies the same bounded correction to all 15 packets:
- L0 historical source evidence stays in `case.input.knowledge_evidence` with its claim boundary.
- L0 IDs are removed from current-event `formal_target.evidence_assessment.supporting_refs` and `cause_localization.candidates[].supporting_refs`.
- Synthetic ML findings and synthetic log IDs remain the current-scenario evidence references.
- `case.expected_output` is rebound to the single canonical `formal_target`.
- In the two Pathfinder tasks, rejected SEL history remains REJECTED and hardware compatibility is UNKNOWN, not COMPATIBLE.

No source facts, generated ML values, generated logs, timestamps, causal conclusions, certainty labels, disposal status, task count or event-family IDs were changed.

## Per-source rights and expert disposition

The machine-readable ledger contains one row per task. All rows remain pending expert review. All source rights remain pending review; this is not a legal clearance.

Priority quarantine:
- Three TROPICS source families use the same NASA TROPICS lessons-learned paper, which includes MIT copyright / government-rights language. Keep these tasks quarantined from SFT authorization until intended third-party training/derivative use is explicitly cleared.
- The spaceborne S-band TWTA source is a journal article. Public abstract access does not establish training rights; full-text claim locators and use rights remain pending.
- Other source families also remain RIGHTS_REVIEW_PENDING until source-specific intended-use review is recorded. Do not infer clearance from NASA/NTRS public access.

## C2-C target review

The current target structures pass the baseline schema/target binding checks. The bounded correction above addresses direct-vs-contextual evidence role. However, this curator review does not certify scientific truth, expert acceptability or model effectiveness.

Per-packet target disposition remains `CURATOR_REVIEWED_CANDIDATE_PENDING_INDEPENDENT_EXPERT`. Any source/target claim whose certainty is not stated must retain that state. Any target recommendation must not be upgraded to executed/effective disposal without supporting scenario evidence.

## C2-E coverage decision

The coverage report identifies:
- diagnostic synthesis: 10/15, spread across 9 families;
- each specialized task type: 1 packet only, therefore weakly covered;
- flight and ground-test source strata are both represented;
- measurement-chain and cross-subsystem cases exist but remain narrow;
- no dedicated correct-abstention task exists;
- multiple tasks share the same source family, so 15 packets are not 15 independent incidents.

Decision: **do not add more tasks in this pass.** First resolve source rights/expert review and complete target review. The missing correct-abstention capability is a valid future gap, but must be derived from a reviewed source event with genuine underdetermination. Do not fabricate an incident or inflate the count with paraphrases.

## C2-D blocked projection

The existing collection projection audit is metadata-only and intentionally emits zero SFT rows. The new candidate is required to pass the same whole-collection allowlist, curator-isolation, source closure, canonical-target and event-family checks. Passing it means serialization-ready engineering structure only, not SFT authorization.

## Current counts

- 15 review dispositions recorded.
- 0 independent expert adjudications.
- 0 source families rights-cleared.
- 0 official splits.
- 0 SFT rows emitted.
- 0 training runs.
