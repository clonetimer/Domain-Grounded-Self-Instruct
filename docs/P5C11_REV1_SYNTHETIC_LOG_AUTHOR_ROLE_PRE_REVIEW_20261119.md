# P5-C11 — REV1 synthetic log author-role ambiguity: bounded scientific pre-review (2026-11-19)

**Classification:** INTERNAL_REVIEW_ONLY / not_for_sft=true. **No formal expert adjudication, release approval, REAL Gold, training split or model execution.** This is a read-only audit of the immutable 21-task REV1; neither source facts nor any L1 packet are edited.

## Reproducible cohort binding

- Read source: `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json`, from #155 exact head `778481b1076386cea11bd8857b9e947cdb896987`; blob SHA `f141694748d5425b63b469b5b0b25064e1b402c8`.
- Collection: `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`; projection SHA-256 `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`.
- Inspected **every** `case.input.diagnostic_logs[].author_role` across the 21 packets: **58 log occurrences** and **51 unique pairs (`log_id`, `source_ref`)**.
- `log_type` occurrences: ALARM 13; EVENT 14; OPERATOR_NOTE 5; ENGINEERING_ANALYSIS 17; REVIEW 9. These are **counts of appearances, not independent physical observations**.
- Exactly **three occurrences** contain `author_role` without an explicit "synthetic" indicator. They reduce to **two distinct synthetic log IDs** and affect **three task packets**.

| Finding | Log / role | Bound REV1 packets and hashes | Concern |
| --- | --- | --- | --- |
| SCI-AUTHOR-ROLE-002 | `LOG-12` / `operator` | `L1-LUNAR-ORBITER-POWER-MONITOR-SYNTH-002` · `19e6993bd7d0c5bde10d2875d2f931223adb6bba2424b9e85736e662e5073b04` | Simulated operator note has an unqualified source-role label. |
| SCI-AUTHOR-ROLE-003-013 | `LOG-23` / `engineer` | `L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003` · `4b14c8dce62612d0c555ea9817bb57199701d60d7524526eadc091a6db5f12d8`; `L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013` · `a8f3872b94a6ff782680d1d142c32ce146d8f393af3610f52630ce13ce7bd0c4` | One reused synthetic engineer-hypothesis log may appear to have actual engineer authority; not two independent observations. |

**Important counter-evidence:** The cohort is explicitly `LITERATURE_DERIVED_SYNTHETIC`, the affected log bodies begin with “合成场景”, the `source_ref` values explicitly identify synthetic logs, and `synthetic_provenance.generated_fields` identifies all `case.input.diagnostic_logs` as generated. Therefore **do not claim these are forged real engineering logs or a proven policy violation**. This is a *role-metadata ambiguity* requiring a controlled reviewer decision.

## Scientific decision to obtain

1. Check whether the existing envelope/content/source provenance already removes reasonable reader/model ambiguity; a bare role label may be acceptable if the surrounding structured context is guaranteed.
2. If not, in a **new version only**, make the simulated nature explicit in `author_role` (or a separately validated simulated-role field) without altering source assertions, log meaning or equipment identity. Recompute packet and collection hashes; redo the official expert review.
3. Preserve the distinction between real upstream engineer analyses and curator-only `internal_review`. Nine `REVIEW` and 17 `ENGINEERING_ANALYSIS` log appearances are *not automatically curator instructions*: some represent legitimate simulated upstream quality/comparability findings. Blanket deleting them would damage evidence-sufficiency tasks.
4. In the restricted **DEV_ONLY negative-history A/B** experiment, LOG-23 is already quarantined from both arms by #176 v0.4 because it shortcuts the intended inference; that intervention is **not** a scientific finding that LOG-23 must be removed from full diagnostic SFT cases.
5. Human reviewers A/B must decide independently per `finding_id` and `packet_sha256`. No auto-approval, no Gold promotion and no silent edits to REV1.

A coordinator-only structured review JSON and separate blank A/B Word forms have been generated locally and delivered outside the public repository; they contain no actual human reviewer identities, opinions, signatures or restricted source material. Store such future restricted review responses outside GitHub.

## Development lesson

An input can be unambiguously **synthetic at collection level** yet have a **role label** that suggests real-world operator/engineer authority if extracted without its envelope. Audit field semantics as well as provenance while retaining appropriate upstream diagnostic inputs. The product objective remains secondary assessment of upstream ML outputs, logs, spacecraft context and appropriately scoped historical knowledge—not direct raw-telemetry inference.

**Remaining release gates:** independent science review (including SCI-002/009/016/017), source-specific reuse-rights decisions for seven documents, authentic real-case upstream evidence, trusted history `verified_at`, no official split, no actual SOTA model scoring and no training authorization.
