# P5-C9 — prevent literature source-fact answer shortcuts in history A/B experiments (2026-11-19)

Status: **DEV_ONLY / not_for_sft=true / NOT_RUN / NO TRAINING AUTHORIZATION**.

## Scientific defect (distinct from the earlier Cassini history leak)

The corrected P5-C7 v0.2 A/B archive still gave both models current-event `knowledge_evidence` excerpts copied from the L0 source fact card. In the two TROPICS tasks, this excerpt states the literature author's slip-ring short mechanism compared with independent SEL, close to the intended diagnostic conclusion. The FUSE passage similarly states historical wheel-fault explanations. Thus a language model may shortcut the *literature-specified hypothesis*, rather than demonstrate reasoning from the synthetic upstream ML candidate, logs, spacecraft and task context. Equal A/B input hashes do not prevent this form of science-label leakage.

This is a **development experiment control** issue, not a claim that all literature evidence is forbidden in real SFT. Existing REV1 L0/L1 facts and approval state are unchanged.

## Actual local deliverable, separately from repository contents

A reproducible local v0.3 DEV_ONLY paired input archive was constructed from the v0.2 exact archive. In **both arms** of each pair, source-derived `knowledge_evidence` passages are removed from model-visible input (`knowledge_evidence=[]`). The original source identifiers, passage IDs and excerpt SHA-256 remain exclusively in the coordinator-only manifest, with the original v0.2 archive SHA linking back to the precise source. Historical cases remain exclusively in the HISTORY arm; upstream synthetic ML outputs, diagnostic logs, mission/configuration, cutoffs, task instructions, and all other fields are unchanged within each A/B pair.

- Original v0.2 ZIP SHA-256: `89e55e253ad3dfb8b90cc3308a2824280da5360f09e79d18ea337fa1f18eea00`.
- New v0.3 ZIP SHA-256: `d30e8867da8e1a8bd15de5f98e19a32f3bd8e88aadbe42974e5a5e432c6c58c6`.
- Output: 6 model-visible JSON inputs; 3 pairs; **2 independent current evidence cores and event families**, not 3; 3 L0 passages quarantined; 0 source fact-card passages model-visible; 3 history hits with `verified_at` missing.
- ZIP integrity and all internal member digests verified; two independent deterministic builds were byte-identical.
- Local archive additionally embeds the construction script and its own scientific audit JSON; no model generation or independent scoring was performed.

The actual DEV inputs, archived passages, reviewer identities and any restricted records **are not committed to GitHub**. The ZIP is delivered separately to the user, not treated as officially approved data. Release statuses remain false.

## Code change and regression tests

`history_pair_science_audit.audit_pair_zip` still accepts the original v0.2 DEV-only archive and now recognizes the separate v0.3 source-blinded purpose. For v0.3 it fails closed if any literature fact card remains in the shared model-visible `knowledge_evidence`, if a coordinator-only provenance ledger is missing/inconsistent, or if the release boundaries are violated. Synthetic-only regression cases cover accepted v0.3 data, shared L0 answer shortcut even with matching newly computed hashes, tampered quarantine receipt, and coordinator metadata in a model envelope.

## Limitations and next scientific actions

- This removes one *explicit* source-fact-card answer channel only. Models may still recognize mission identifiers, infer from synthetic upstream ML candidate naming, or recall public facts from pretraining; **blind evaluator judgments** and genuine out-of-family holdouts remain necessary.
- Current historical hits are REJECTED or PARTIALLY_CONFIRMED; all hardware fit UNKNOWN. There are **zero confirmed-and-compatible positive transfers**. Positive history benefit stays `NOT_EVALUABLE`, model scores `NOT_RUN`.
- `available_at` in these synthetic development scenarios is declared, and no hit has trustworthy `verified_at`; none qualifies a real production as-of lookup.
- Do not modify frozen REV1 source facts or call this an independent expert review. SCI-002, SCI-009, SCI-016 and SCI-017 still require adjudication. Seven source-use rights groups and five REAL candidates remain incomplete.
- Train/validation/test split unassigned; REAL Gold=0; no microtraining, paid API, auto-merge or promotion.

**Lesson:** history-only ablation requires excluding *all* source-derived answer passages shared by both arms, not merely removing history refs. Structural parity, even if perfectly hashed, cannot on its own establish that an experiment measures the intended reasoning capability.
