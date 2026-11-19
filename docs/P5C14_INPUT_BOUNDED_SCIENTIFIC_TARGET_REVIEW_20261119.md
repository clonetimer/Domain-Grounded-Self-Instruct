# P5-C14 — input-bounded scientific target candidates for the REV1 history A/B pilot

**Status:** DEV_ONLY, REVIEW_REQUIRED; coordinator-only annotation, **not_for_sft=true**. This note is a content-oriented scientific review candidate, *not* a new validator, new Gold case, expert finding, benchmark result, official target, training split, or authorization.

## Frozen input basis

- Pin: REV1 historical Context paired-input v0.6 local archive SHA-256 `edf987faae6a0b0dbdb148d134a72ffda06d2106868de9c92dbbe3971a00c781`, prepared under #179.
- Three A/B task pairs but only **two independent current diagnostic input cores** / two source event families. TROPICS tasks 003 and 013 reuse the same current evidence and cannot be scored as independent physical incidents.
- The pair arms differ only in retrieved `historical_cases`. No literature source-answer excerpts, coordinator labels or prewritten engineer analysis logs are supplied to the model. Do not compare responses against the full-source frozen REV1 answers.
- Every candidate below is an **editorial suggestion derived from visible synthetic inputs**, not a reviewer label. Two independent reviewers must verify the scientific wording, missing evidence, and scoreability before any use.

## Input-visible facts and guarded conclusions

| Pair | Input-visible evidence and ML output | Only supportable target claims / unsupported shortcuts |
| --- | --- | --- |
| **012: FUSE wheel** (`historical_case_reuse`) | Synthetic alarm `LOG-121`: above-baseline pitch reaction-wheel drag; synthetic event `LOG-122`: drag remains high briefly after restart then decreases. `ML-FINDING-012` proposes `rotor_housing_local_contact_candidate`, synthetic uncalibrated rank `0.76`, citation alias `ML-E-012`. | Can describe symptomatic wheel drag and an upstream candidate; **cannot** certify rotor/housing contact, any independently unverified physical material mechanism, lasting recovery, or a historical disposal intervention. In HISTORY arm, Cassini prior `HIST-CASSINI-RWA-DRAG-007` remains `PARTIALLY_CONFIRMED`, hardware `UNKNOWN`, `verified_at` absent; it does **not** establish the FUSE mechanism or authorize transferring a Cassini maneuver. |
| **003: TROPICS multi-interface** (`diagnostic_synthesis`) | Synthetic alarm `LOG-21`: payload serial CRC errors; event `LOG-22`: SADA drive / star tracker communication anomalies. `ML-FINDING-01` proposes `SLIP_RING_12V_SERIAL_CROSS_SHORT`, synthetic uncalibrated rank `0.77`, alias `ML-E-003`. | Can describe the **candidate** shared-interface failure and the **observed affected interfaces**. Cannot equate the ML candidate with independent physical confirmation, or label additional configured components as measured failures. HISTORY arm offers `REJECTED` prior `SYNTHETIC-HISTORY-SEL-REJECTED-001`, hardware `UNKNOWN`, no verified_at; should not add support. |
| **013: TROPICS evidence sufficiency** (`evidence_sufficiency`) | **Same LOG-21/22 and ML finding as 003**, different user instruction. | Can distinguish sufficient evidence for reported communication anomalies from insufficient evidence for a unique physical cross-short. History cannot remedy the shortfall. Need independent electrical/interface or isolation evidence. Do not count this as an extra independent source family. |

## Evaluation-ready behavior criteria (pending review, no scores)

1. **Phenomenon and affected components:** cite visible LOG IDs and distinguish observed anomalies from merely configured hardware; identify potential secondary effects conditionally.
2. **Upstream ML semantics:** cite `ML-FINDING-012` for FUSE or `ML-FINDING-01` for TROPICS, keep source as a *candidate* and `0.76/0.77` as synthetic ranking values, not calibrated probabilities; `ML-E-012/003` are only referenced aliases, not newly supplied independent measurement contents.
3. **Physical root cause:** explicitly abstain from confirming a unique mechanism without independent discriminating evidence. Do not reproduce withheld literature mechanisms from the source cards.
4. **Historical Context:** NO_HIT has no historical claim; HIT may name its provided status and hardware limits, but `verified_at` is absent, so it cannot be treated as a fully verified as-of retrieval or a vote confirming current root cause. A rejected prior remains rejected.
5. **Disposal fidelity:** none of these six model inputs establishes a historically documented *remedial decision* or approved operation. `disposal_status=NOT_RECORDED`, `disposal_measures=[]` is a **proposed editorial baseline requiring reviewer confirmation**; `LOG-122` mentions a restart occurrence, but does not on its own establish an authorized corrective measure. Suggestions to inspect or independently test belong to `follow_up_actions`.
6. **Source/classification:** explicitly keep synthetic diagnostic logs and upstream ML results separate from real flight telemetry or actual ML runs. Do not call the historical availability timestamp independently verified.
7. **Input-bounded scoring:** reviewer should mark each claim **SUPPORTED / UNSUPPORTED / NOT_EVALUABLE**, with a visible input path or log/finding ID. Scoring against full original REV1 reference, including withheld L0 mechanisms, is prohibited.

## Blind-review and reporting design

- Freeze each of the six candidate input hashes from the v0.6 coordinator manifest. Score arms individually without showing a paired-arm delta, original case identity, source fact card, hidden reference target or internal curator reminders.
- Two independent expert reviewers: separate forms, no invented identities, no automatic approval. Coordinator collects task ID, archive SHA, input-arm hash, reviewer token, 10-dimension quality scores, explicit claim-level support / not-evaluable labels and any disputed disposal interpretation.
- Aggregate **first by current diagnostic core/event family**, then report task-type sensitivity. `003` and `013` may be displayed separately but are dependent observations. Do not report three independent samples.
- The current pilot evaluates *negative historical transfer resistance* only; no confirmed hardware-compatible positive prior is provided. Positive-transfer effect, model gains, expert-approved task count and training readiness all remain `NOT_EVALUABLE` or `NOT_RUN`.
- A documented AI editorial candidate is **not** an A/B expert receipt, not data admission and not a scientific benchmark score. Source rights, expert scientific adjudications, valid as-of history, real upstream artifacts, and authorized holdouts remain independent gates.

## Correction / reviewer blinding note (2026-11-19)

- Cross-checked the six v0.6 model inputs against the P5-C14 candidate JSON and A/B Word forms. FUSE ML `finding_id` is **`ML-FINDING-012`**, not `ML-FINDING-01`; this discrepancy affected both editorial draft targets and both Word review forms but **did not change the frozen model inputs**.
- A source-hidden specific material hypothesis was inadvertently named as an example of a non-confirmable cause in both draft-target `evidence_evaluation` strings and Word tables. Even a negative mention can prime an expert reviewer. The corrected coordinator draft uses the generic formulation **“具体材料/接触机理未获独立验证”** and does not expose the withheld hypothesis in reviewer-facing text.
- The original P5-C14 v0.1 package is immutable evidence of the defect; v0.2 is a corrected **review candidate only**, with the same source-v0.6 input hashes and packet hashes. No expert approval, source-rights grant, Gold promotion or formal scoring is inferred. See the separate local v0.2 artifact for corrected Word/JSON candidate labels.

## Development lesson

Eliminating side channels is only half of a fair A/B experiment. The **expected answer itself must be bounded by the actual model-visible information**, and the experimental unit must be the independent diagnostic core / event family, not each task phrasing. This task deliberately produces source-constrained *review candidates* instead of another generic release gate.

Dependencies: #179 (latest-head Ubuntu and Windows PASS, run 44495220952); archive remains delivered locally and outside the public repo. This PR is Draft, based on exact #179 head and requires its own latest-head dual-platform CI. No merge or changes to frozen REV1.
