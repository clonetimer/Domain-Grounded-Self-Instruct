# P5-C12 — Blinded DEV_ONLY case identifiers and input-bounded scoring (2026-11-19)

**Scope:** Only the three negative-history DEV_ONLY A/B pairs from P5-C10 v0.4. No mutation of the frozen 21-task REV1 corpus, real flight record, Gold, official split, fine-tuning or model-generated result.

## Read-only scientific finding

The pinned P5-C10 v0.4 model envelopes included the source/task-derived current `case_id` in **both A/B arms**. Example: `CASE-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003`. The term `CROSSSHORT` directly names the candidate failure mode. This is a **metadata answer cue** independently of the preserved upstream ML result. An ID is not a physical measurement or evidence source. A second task's identifier named `HISTORY-REUSE`, potentially disclosing the intended experiment task. These labels do **not** prove that any model used the shortcut; no model inference has been executed.

More consequential for scoring: the **full-context frozen REV1 targets are not blind reference outputs for the stripped paired arms**. The model-visible DEV_ONLY arms deliberately remove source L0 excerpts and engineer hypothesis log LOG-23. Their NO_HIT arms also withhold the historical case. The frozen formal targets sometimes discuss FUSE Kapton supplier hypotheses, related FUSE wheel episodes, Cassini/LLIS operating conditions, TROPICS slip-ring debris versus three independent SEL events, or the denied historical SEL case. Such claims are not necessarily observable from a particular arm. Text similarity against those full-context targets would reward invention of concealed facts and penalize appropriate uncertainty.

| Pair | Input-visible, eligible diagnostic behaviors | Not eligible for blind scoring without a new independent reference |
| --- | --- | --- |
| FUSE #012 | Synthetic reaction-wheel drag/restart chronology; upstream ML local-contact candidate remains unconfirmed; no unsupported claim of recovery; if HISTORY, preserve `PARTIALLY_CONFIRMED` and `UNKNOWN` hardware status | Historical Kapton/2001 wheel episode details; special LLIS zero-speed/exercise conditions if omitted by that arm; Cassini relevance in NO_HIT |
| TROPICS #003 | Current synthetic CRC and interface alarms; candidate versus confirmed short; source-/hardware-limited REJECTED history only if HISTORY; disposal/follow-up separation | Literary comparative claim about debris versus three independent destructive SEL events; quarantined LOG-23 engineer hypothesis; prior-case rejection in NO_HIT |
| TROPICS #013 | Phenomenon vs physical-root-cause evidence sufficiency; missing direct electrical/topology checks; inability of rejected history to confirm or eliminate current causes | Same hidden TROPICS literature comparison and LOG-23; any withheld prior-case statement in NO_HIT |

## Implementation and reproducible deliverable

- One new v0.5 purpose in the existing `src/dgsi/history_pair_science_audit.py`: only that purpose requires opaque stable `SYNTHETIC-EVAL-CASE-NNN` model-visible IDs, distinct from private coordinator original IDs; binds original ID with SHA-256, requires matching A/B IDs, and prevents duplicate opaque IDs.
- Five fully synthetic regression tests; prior v0.2-v0.4 manifests remain readable.
- Locally delivered archive `DGSI_REV1_历史Context模型输入案例ID盲化_DEV_ONLY_v0.5.zip`: six inputs, original current-case identity preserved only in coordinator manifest, per-arm hashes recomputed, fixed-source v0.4 archive SHA-256 `f6b5880068d9ca594fbb2467c832291781389362cb810d802604f7a44e46b462`; output ZIP SHA-256 `e3bc39e54ef6e15ab0e47ded3a5452545401fcb8ad36df5a467dc1e44b96524b`.
- Independent rebuilt ZIPs were byte-identical; ZIP integrity, 11 member digests, 3 pair ID bindings, absence of L0 and ENGINEERING_ANALYSIS in all six model inputs passed locally.
- The coordinator-only reference-visibility JSON **is not an adjudicated answer key**. Independent experts must validate which assertions are truly inferable from each arm prior to any model scoring. The measured effect is still `NOT_RUN`; positive historical transfer `NOT_EVALUABLE`.

## Scientific and access restrictions

The upstream ML candidate (`SLIP_RING_12V_SERIAL_CROSS_SHORT`, etc.) is **not removed**, because interpreting that candidate is the DGSI product task. Neutralizing the ID only prevents metadata from independently naming its intended answer. The case ID map is not an external review receipt and must never enter a model prompt. Missing historical `verified_at` still blocks trusted production retrieval. Three pairs represent two event families, not three independent scientific replications.

No official train/validation/test split, SFT export, authentic reviewer receipt, verified source rights, real Gold promotion, paid API or fine-tuning. Only after the new PR head obtains both Ubuntu/Windows mandatory PASS can this increment pass engineering gates.
