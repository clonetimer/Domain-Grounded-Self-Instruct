# P5-C4 | REV1 TWTA monitor-vs-RF evidence-role audit (2026-11-19)

**INTERNAL_REVIEW_ONLY · not_for_sft=true · AI pre-review, not a human adjudication.** Frozen REV1 remains unchanged; this file cannot be exported as a training target, licensing decision or reviewer receipt.

## Evidence and version binding

- Collection: `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`; collection projection SHA-256 `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`; 21 SYNTHETIC tasks, nine source-event families, all review-required.
- Source file: `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json` at parent PR #170 head `41198ed61588a1e38d61823645f4eb111dbe3394`. Blank reviewer A/B packet hashes independently cross-checked against the already issued C2 REV1 21-task reviewer kit; no reviewer decision has been made.
- L0 boundary: `LIT-LUNAR-ORBITER-POWER-MONITOR-006`, NASA-CR-66461 / NTRS 19670027946, historical Lunar Orbiter III CE02 measurement-chain anomaly. The public-source fact card describes temperature-sensitive CE02 indication while deep-space-station received-signal strength stayed essentially constant **in the historical episode**; the source treats a diode rectification-temperature effect as possible, not teardown-confirmed. This historical independent cross-check **is absent from current synthetic task 002**.
- All current ML labels/scores, diagnostic logs, spacecraft IDs, timestamps and task scenarios are **SYNTHETIC**. The public report and L0 card constrain a historical mechanism; they are not current ML execution, current RF measurement or expert approval.

## New finding: SCI-002-MONITOR-ALIAS-AS-RF-SUPPORT (requires expert adjudication)

**Task:** `L1-LUNAR-ORBITER-POWER-MONITOR-SYNTH-002`, exact packet SHA-256 `19e6993bd7d0c5bde10d2875d2f931223adb6bba2424b9e85736e662e5073b04`.

1. Synthetic upstream `ML-FINDING-01` has `target=twta_power_monitor` but `result=TWTA_RF_OUTPUT_POWER_LOSS`; its sole `supporting_evidence_ids` entry is `ML-E-002`. The score 0.69 is explicitly synthetic **ranking**, not calibrated probability.
2. Synthetic `LOG-11` reports temperature-dependent **monitor indication** only; `LOG-12` explicitly says no independent current-window RF power measurement was supplied.
3. The formal target correctly says `UNRESOLVED`, separates `twta_power_monitor` from `TWTA_RF_output_path`, and warns that the historical ground-link observation cannot be imported into this synthetic event.
4. Nevertheless `formal_target.cause_localization.candidates[1]` uses `fault_mode=actual_RF_output_power_change_candidate` with `supporting_refs=[\"ML-E-002\"]`. If consumers interpret `supporting_refs` as **positive physical evidence**, this repeats the evidence-type error already flagged for task 016. That same ID **can** truthfully identify the upstream algorithm's hypothesis provenance; it **cannot** independently establish a physical RF decrease. The literal citation is present, but the *relation type* remains ambiguous.

This is **not** a claim that the RF hypothesis must disappear, that current physical output is stable, or that task 002 has been independently source-certified. It is a targeted, as-yet-unresolved semantic quality risk.

## Cross-case check: 002 / 016 / 019

| Task | Packet digest prefix | Upstream proposition | Available physical-path evidence | Current target handling | Decision |
| --- | --- | --- | --- | --- | --- |
| **002** TWTA power indication | `19e6993b...` | Synthetic ML predicts true RF loss despite targeting monitor | Only synthetic temperature-dependent monitor `LOG-11`; independent RF check absent (`LOG-12`) | `UNRESOLVED` text is correct; RF candidate nevertheless cites `ML-E-002` as `supporting_refs` | **New SCI-002** relation-role review |
| **016** TWTA contradictory evidence | `6e30feb4...` | Synthetic ML predicts true carrier decrease from monitor | Synthetic comparable independent ground-link summaries `LOG-162/163` contradict it | `UNRESOLVED` text correct; RF candidate cites `ML-E-016-MONITOR` as positive support | Existing SCI-016; reviewer option A/B/C already documented |
| **019** TWTA insufficient isolation | `4c98577d...` | Synthetic ML infers LNA hydrogen poisoning from whole-unit power decline | Synthetic repeat whole-unit measurements, no subassembly isolation | Correctly **does not populate confirmed/physical root-cause candidates** and preserves missing evidence | **Control case**, not flagged for same link error |

## Independent expert decision options for 002

- **A — Typed evidence-role correction (proposed only):** preserve the upstream ML result, its score semantics, and its origin `ML-E-002`; if `supporting_refs` means *positive physical support*, set only the RF-output candidate's `supporting_refs=[]` in an **independent REV2**; preserve the candidate as unverified, `LOG-11/12`, uncertainty, disposal `NOT_RECORDED` and follow-ups. Evaluate `evidence_assessment.supporting_refs` separately for the same relation-role ambiguity.
- **B — Explicit provenance/support distinction (proposed only):** if reviewer defines `supporting_refs` as claim source, specify typed `upstream_claim_refs` and `positive_physical_evidence_refs` contract before admitting the packet. Avoid inheriting an ambiguous alias in exports.
- **C — Maintain REVIEW_REQUIRED:** do not change the frozen target; request supporting evidence and/or field-semantic decision.

Reviewers A/B independently verify the L0 source boundary and task packet **without sharing decisions beforehand**. Record option, passage/field citations, and rationale against the **exact packet digest** in an off-repository artifact. A safety adjudicator resolves conflicts. No blank form, automated check or GitHub PR review equals a domain expert decision.

## Production impact and development lesson

The same structural weakness can appear with opposite current evidence conditions: **no independent RF measurement** (002) versus **independent contradictory RF measurement** (016). A clean end-to-end SFT example must teach the model to say "ML reports this hypothesis" without transforming that into "physical evidence confirms it". One well-scoped pair (plus the abstention control 019) is more informative than generating another batch of near-duplicate samples.

No source rights have been cleared; no Gold, splits, training, raw telemetry, public expert identities or real run records were created. Only on expert approval may a **new** version be constructed with regenerated packet/collection hashes and fresh reviewer forms.
