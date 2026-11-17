# P5-C2 integrated production workflow (candidate-only)

Release: 0.2.0-rc.1 DRAFT. **The only product goal** is scientifically grounded spacecraft fault-diagnosis SFT data. The production Skill and the candidate corpus are co-equal deliverables toward this one goal; neither can authorize training or Gold promotion.

## Input and output boundary

An LLM receives upstream ML diagnostic results, timestamped diagnostic logs, spacecraft configuration, mission/operating context and qualifying historical case summaries in one user context. Original telemetry is analyzed by upstream ML and is **not** in the default LLM input. Preserve method/version/run identifiers, score semantics and calibration status, evidence IDs, analysis cutoff, historical case status and applicable hardware/mission restrictions.

- **REAL_GOLD_TRACK:** authentic/de-identified engineering cases remain candidates until source authenticity, IP/usage rights, permissions, independent expert review, upstream result/log/context integrity and release authorization all pass.
- **LITERATURE_DERIVED_SYNTHETIC_TRACK:** L0 literature-backed facts constrain L1 synthetic upstream inputs; mark scenario and generated fields SYNTHETIC, record recipe/version, assumptions and unmodeled details. Never impersonate an actual flight record, ML run, log or expert signature.
- Keep the two tracks, event families, independent holdouts and measured quality statistics separate. Synthetic task count does not increase REAL Gold count.

## Integrated C2-B / C2-C / C2-D / C2-E execution

1. **Freeze provenance:** record exact collection revision, packet SHA-256, source L0 fact-card hashes, source locator, source rights status, event-family and episode relationships. Existing 15-packet baseline and 9 source event families remain review-required; any v0.2 correction is another candidate, not automatically promoted.
2. **C2-B scientific review:** examine each packet against its exact cited source, separating observation, alternative hypotheses, source-attributed mechanism certainty, fault source, affected components, telemetry measurement chain and documented disposal. Quarantine unresolved rights; preserve source uncertainty and all unsimulated gaps. Record independent reviewer tokens and disagreement disposition outside model inputs.
3. **C2-C formal target:** constrain assistant to phenomenon analysis, interpretation of upstream ML, fault-source vs affected-component conclusions, current-event evidence assessment, uncertainty, documented disposal and recommended follow-up. Historical source/context may inform transfer limits but never directly prove the current event. A missing disposal record must map to NOT_RECORDED with empty measures; new diagnostic checks belong to follow_up_actions. Source-backed target claims only; internal curatorial prompts or alternative-hypothesis checklists remain Case-root `internal_review` with `not_for_sft=true`.
4. **C2-D model projection:** construct system/user/assistant views using explicit allowlists. The system/user message carries no hidden truth, reviewer material, future information, raw telemetry by default or post-cutoff history. The assistant target must equal the canonical formal_target. Check deterministic hashes and round-trip parse/validation against the same snapshot. **This preflight emits zero SFT training rows.**
5. **C2-E coverage:** report task-type and event-family coverage separately. Check conflict cases, no-hit/incompatible/rejected/unresolved/future historical cases, sensor vs actuator and cross-subsystem cases, missing-evidence abstention and disposal semantics. Add only justified, reviewed source families; do not count repeated variants as independent events.
6. **One release manifest:** include corpus identity, exact hash bindings, field-level dispositions, outstanding rights/expert requirements, train/validation/test holdout eligibility and blocking reasons. Independent expert adjudication, rights clearance, SFT authorization and training are separate controlled stages.

## Blocking rules

- Uncalibrated upstream scores are **not probabilities**; candidate ML findings are **not confirmed root causes**.
- A literature fact card is **not** direct support for an invented current synthetic-event measurement; context-only historical cases are **not** direct evidence either.
- `analysis_cutoff` is a hard as-of boundary; missing `available_at` or `verified_at` must block or downgrade memory hits, never infer a time.
- Same `event_family` and all episodes cannot cross train/holdout boundaries; unresolved or unsupported lineage prevents release.
- Do not include private reviewer identities, source documents or raw logs in the public toolkit ZIP. The archive contains only allowlisted reusable code/contracts/documentation, never the corpus or private evidence.
- Any packaging, regression or structural preflight PASS is an engineering verification only, not Gold, expert approval, clearance or permission to fine-tune.

## Read-only verification

Build with `python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip`. Verify `PACKAGE_SHA256_MANIFEST.json` byte sizes/hashes and that all authorization flags are false. Run the portable toolkit package test and repository suites on Ubuntu/Windows for the exact PR head. The existing `src/dgsi/l1_model_projection_audit.py` collection preflight returns hashes and blocked state only, not model-ready SFT JSONL.

See repository `docs/P5C2_INTEGRATED_COMPLETION_2026-11-17.md` for milestone acceptance criteria. This portable reference is the bounded execution recipe, not an independent external review.
