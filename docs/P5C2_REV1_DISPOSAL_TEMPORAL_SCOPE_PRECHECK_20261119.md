# P5-C2 | REV1 action / disposal chronology audit (2026-11-19)

**Classification: INTERNAL_REVIEW_ONLY — NOT_FOR_SFT=true — AI-assisted precheck, not a signed expert decision.** This memo and its companion JSON MUST NOT be ingested as an SFT input, target, source fact card, historical Context, or reviewer receipt. No revision to the frozen REV1 L0/L1 cohort is made here.

## Immutable evidence boundary

- Read baseline: PR #168 head `74fe21fe4bd5cadaa20b7415dbe5da5973133ee1` (Ubuntu and Windows checks successful). This branch is documentation only.
- REV1 dataset: `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json`, immutable collection `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`, projection SHA-256 `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`.
- The 21 SYNTHETIC packets have 5 `disposal_status=RECORDED` and 16 `NOT_RECORDED`. The five recorded claims refer to synthetic scenario logs; **none is proof of a real executed flight/ground action**. We verified the exact referenced log's natural-language description in all five.
- Existing human-review state remains `REVIEW_REQUIRED`; no source rights clearance, Gold enrollment, formal training split, or model run is authorized.

## Five recorded-action entries — trace of action, purpose and episode

| Task | Referenced current synthetic log | What the log actually describes | Semantic disposition for expert review |
| --- | --- | --- | --- |
| 004, TROPICS TVAC slip ring | `LOG-42` | Harness routing adjusted **after** intermittent CRC was observed; CRC persists | Relevant attempted correction, no demonstrated repair. Existing `RECORDED / EXECUTED` has an explicit log anchor |
| 006, TROPICS flight CRC-B | `LOG-62` | Multiple retries of an unstable link; stability not restored | Relevant response to the current episode, but not a repair. Existing `RECORDED / EXECUTED` has an explicit log anchor |
| **009, NASA 22 N hydrazine injector** | **`LOG-91`** | **Vacuum heat-lamp bake attempted for *earlier suspected catalyst-bed contamination*; afterward, `LOG-92` reports valve rupture and `LOG-93` reports injector-flow loss** | **New temporal/causal-role adjudication required:** this is an action preceding the valve/injector episode, aimed at a different suspected problem, and potentially causal to the current failure. Treating it as the current episode's completed *disposal measure* could train an incorrect action→failure relation |
| 012, FUSE–Cassini history reuse | `LOG-122` | A restart of the current synthetic reaction wheel followed by drag decline | Current synthetic intervention, not evidence that drag normalized or Cassini's wheel-speed approach applies |
| 020, FUSE recovery abstention | `LOG-020-01` | A current synthetic restart completed; subsequent observations do not establish recovery | Current synthetic intervention, no verified recovery; compatible with `UNRESOLVED` and abstention |

These are **exact field/content checks**, not an independent determination that each underlying scenario is physically plausible or that public source material can be copied for training.

## Newly identified scientific issue: SCI-009-PRECURSOR-AS-DISPOSAL

**Immutable task:** `L1-NASA-HYDRAZINE-INJECTOR-SYNTH-009`  
**Frozen packet SHA-256:** `11f8aefda38a3f34501c59d8419b8d5e02bf9a669690d17e45019abff73df77f`  
**Event family:** `LITERATURE-DERIVED:NASA-22N-HYDRAZINE-LIFE-TEST-1987`  
**L0 source:** `LIT-NASA-HYDRAZINE-INJECTOR-009` (NASA TM-100232); the paper's historical event is not a current executed experiment.

Observed snapshot fields:
- `case.input.diagnostic_logs[LOG-91]`: synthetic vacuum heat-lamp bake for **earlier suspected catalyst contamination**.
- `case.input.diagnostic_logs[LOG-92]`: afterward, valve pressure anomaly and rupture.
- `case.input.diagnostic_logs[LOG-93]`: subsequent injector-flow collapse.
- `formal_target.disposal_status=RECORDED`, `formal_target.disposal_measures[0].measure_type=EXECUTED`, `evidence_refs=[LOG-91]`.
- `formal_target.report_text` explicitly says the historical earlier catalyst washout was a distinct episode and the current injector cause remains unconfirmed.

**Why this is distinct from missing citation:** The cited action exists in the synthetic log. The scientific risk is **event-relative action classification**, not citation presence: `LOG-91` describes an operation intended for an earlier catalyst concern and temporally preceding the valve/injector failure, whereas the formal target's current diagnosis concerns the later injector obstruction. This could accidentally teach the model to characterize a failure precursor as corrective action for that later fault. It must also not be erased from the original scenario timeline; the operation itself is relevant potential causal evidence.

**Expert A/B adjudication choices (no choice selected):**
- **A — Current-event disposal misclassification:** in a proposed REV2 only, preserve `LOG-91` as an operation/precursor and causal hypothesis; set the later valve/injector episode `disposal_status=NOT_RECORDED`, `disposal_measures=[]`. Any new inspection suggestion remains only in `follow_up_actions`.
- **B — Episode scope encompasses the whole test sequence:** retain `RECORDED` *only if* reviewers explicitly agree that the case's disposition scope includes the prior contamination treatment; annotate purpose, temporal order, and **not an effective repair for later valve/injector obstruction**, with field semantics that prevent conflation.
- **C — Hold/rework:** require missing event-scoping or source evidence; no silent change to REV1 or elevation of source certainty.

Two independent reviewer tokens, each bound to the **exact task and packet digest**, should record a selected option, reason, references, and any dissent in an off-repository review artifact. A distinct safety adjudicator resolves differences. This document does not invent those signatures or outcomes.

## Cross-issue dependency / next scientific step

Task **016** already has `SCI-016-SUPPORTING-REF-ROLE` pending: `ML-E-016-MONITOR` is the origin of a monitor-only ML *inference*, not independent positive proof of a true RF carrier drop. Task **017** has `SCI-017-PASS-SCOPE` pending: a high-humidity PASS is not an all-qualification PASS. This new task **009** issue adds a third, distinct semantic axis—**temporal purpose and episode-relative action classification**. All three remain review-only and must be consolidated in the existing two-expert REV1 return, not miscounted as three completed expert approvals.

## Acceptance / mutation boundary

1. Obtain the real 21-task REV1 A/B expert decisions and source-use-rights documentation **outside the public repository**. Review must identify `task_id` and packet SHA; public PR comments may refer only to redacted decisions.
2. If experts request a correction, prepare a *separate immutable REV2* with corrected formal target **and** case `expected_output` consistency, recompute all packet/collection hashes, regenerate both expert packets, and invalidate stale REV1 approvals for changed packets. Do not modify existing source facts, historical cases, or run IDs.
3. Keep five experimental model arms `NOT_RUN`, real Gold 0, training authorization false and formal splits unassigned until independent scientific review and rights clearance. Automated schema and platform CI passing are **not** scientific admission.

**Development lesson:** Evaluating an action requires not only whether a log exists but also *when* it occurred, *which failure episode it addressed*, and whether it was observation, causal precursor, response, or genuine disposition. Log existence cannot substitute for temporal-episode semantics.
