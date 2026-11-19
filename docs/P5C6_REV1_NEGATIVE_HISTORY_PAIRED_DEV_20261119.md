# P5-C6 — REV1 historical Context paired negative-transfer development set

Date: 2026-11-19  
**Scope: REVIEW_ONLY / DEV_ONLY / not_for_sft=true**  
No source-rights clearance, model call, expert approval, official holdout, Gold admission, SFT export or training authorization.

## Actual reproducible local artifact

A reproducible stdlib-only Python builder was executed against the **unchanged, locally held** REV1 reviewer-A handoff in the existing 21-task independent-review kit. No content from that handoff was uploaded to GitHub.

- Source reviewer-kit SHA-256: `07e6ac7ad9c92d89aee6fb8123c61849684ba0ddd6571122de949cc81ed5eda1`.
- Bound frozen collection projection SHA-256: `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`.
- Generated local archive: `DGSI_REV1_3组历史Context拒绝迁移配对输入_DEV_ONLY_v0.1.zip` (SHA-256 `6c4c41ecabfc0c9f1746000b1e2cc1f4fb38039183c9c3513e9ab1bdb08daeab`).
- Archive contains **six model-visible user-only payload files** (A/B for three task IDs), one **coordinator-only** arm/key/digest manifest, README, checksums and a copy of the exact local builder. All nine stored-file checksums and all three pair-equality invariants were verified locally. The archive is delivered separately to the requester, **not committed to the public repository**.
- The original 21 L1 packets, L0 cards, formal targets, reviewers' forms and hashes remain unchanged.

## Tested comparison boundary

For each of the three REV1 packets that originally has a history HIT, build the exact same task instruction and present the same synthetic upstream ML result, diagnostic logs, spacecraft/configuration, task operational context, knowledge evidence and analysis_cutoff. **The only experimental difference is `input.historical_cases`: original source-bound history versus `[]`.** Existing source-time annotations are only declared synthetic metadata, not independently authenticated original availability.

| Task ID suffix | Historical hit retained only in HIT arm | Hardware fit | Independent current-input core |
|---|---|---|---|
| `...HISTORY-REUSE-SYNTH-012` | Cassini `PARTIALLY_CONFIRMED` | UNKNOWN | SHA-256 prefix `8f46aac091a3` |
| `...CROSSSHORT-SYNTH-003` | prior synthetic SEL `REJECTED` | UNKNOWN | SHA-256 prefix `924031c75476` |
| `...EVIDENCE-SUFFICIENCY-SYNTH-013` | **same** rejected synthetic SEL prior | UNKNOWN | SHA-256 prefix `924031c75476` |

**Important independence correction:** the 003 and 013 packets have *identical current diagnostic input* (all fields other than historical_cases) but different task instructions/task types. Therefore three task-pair files represent only **two distinct current diagnostic-input conditions** across **two current event families**. Do not report three independent effects; use event-family-aware analysis.

## Science interpretation

These are **negative-transfer/refusal stress cases**, not a positive historical Context benefit experiment. There are no CONFIRMED + COMPATIBLE history hits in the 21-task cohort. A positive-transfer metric therefore remains `NOT_EVALUABLE`, not zero effect and not an improvement. No models have been called, no scores have been assigned, and no independent holdout is frozen.

Candidate scoring dimensions for a later *authorized* paired test are:
1. Retention of historical review status (`REJECTED` / `PARTIALLY_CONFIRMED`), not promotion to current truth.
2. Correct distinction between current ML/log evidence and historical analogy.
3. Explicit hardware-fit `UNKNOWN` limitation; no generic wheel operational instruction migrated.
4. Correct abstention on unresolved root cause and non-executed disposal.
5. Current-event evidence attribution unchanged between arms.

No scorer should see the coordinator mapping, frozen formal target, source rights or reviewer notes in a model prompt. The local archive can be examined by its owner **offline** for development/quality review; external provider use requires source-rights clearance and explicit approval. Any future formal evaluation must use separately admitted event-family-disjoint holdout examples and independent reviewer judgments.

## Development experience / next blocker

**Changed:** constructed and hash-bound three real paired **development input variants from existing synthetic candidate packets**; did not invent new real mission records or historical confirmations.  
**Why:** #172 showed a non-identifiable positive history effect; a useful next step is to make the measurable *negative-transfer* subproblem testable while stating the independence denominator honestly.  
**Pitfall:** counting `003` and `013` as independent cases double-counts exactly the same current diagnostic evidence; their only task-level difference is the instruction/type.  
**Next:** obtain verified source-use permission, independent A/B scientific labels for 21 REV1 packets (including SCI-002/009/016/017), and event-family-independent positive-history cases with authenticated availability/compatibility metadata. Until then, status is `DEV_ONLY` and `NOT_RUN`.

The original user review kit, local pairing builder and generated archive are intentionally kept outside GitHub; this document is metadata-only.
