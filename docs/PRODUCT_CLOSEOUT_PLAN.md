# DGSI SFT dataset program — tooling milestone closeout

**Decision:** close out the current Skill/toolkit **engineering milestone** when the five handoff artifacts are verifiable. This is not DGSI's product completion. The **single product goal** remains a high-quality spacecraft-fault-diagnosis SFT dataset for LLM second-stage assessment using upstream ML findings, diagnostic logs, mission/spacecraft context and time-safe historical experience; raw telemetry remains upstream. Review, rights, real-case evidence, independent holdout and training authorization are still hard gates for that dataset.

## Product boundary

- **Product goal:** independently reviewed, rights-cleared, evidence-grounded spacecraft fault-diagnosis SFT dataset. Real Gold and literature-derived SYNTHETIC remain separately classified and evaluated.
- **Tooling milestone:** DGSI Skill/toolkit — instructions, schemas, L0/L1 workflows, evidence and Context handling, validation, review handoff and export guidance.
- **Evaluation Suite:** the 21 literature-derived tasks, five user-provided L0 case facts, AAS RUN-03F and other fixtures. Their purpose is to test Skill behavior, coverage and failure modes. They are not automatically Gold or training data.
- **Formal SFT dataset:** the program's intended product, **not** an optional application outcome. It requires source permission, independent human adjudication, leak-free splits and explicit training/release decisions. Its absence does not block *toolkit-only* handoff, but **does block declaring the product goal achieved**.

## Five closeout deliverables

1. **Portable Skill package** — install/use instructions, version, dependency boundary, reproducible archive and SHA-256 manifest.
2. **Evaluation Suite** — [manifest](../examples/dgsi_evaluation_suite_manifest_2026-11-18.json) freezes 21 L1 synthetic tasks, 13 ADCS/EPS pressure cases, 8 process holdouts, 5 private user L0 facts, one AAS SYNTHETIC_TEST_ONLY integration fixture and two schema illustrations. The suite is not a training corpus.
3. **Skill effectiveness report** — [DGSI_SKILL_EFFECTIVENESS_REPORT_2026-11-18.md](DGSI_SKILL_EFFECTIVENESS_REPORT_2026-11-18.md) reports measured inventory, integration evidence, adjacent exploratory pretest and all metrics that remain unmeasured. Separate automated checks, AI advisory and human review.
4. **User/developer handoff** — [PRODUCT_USER_DEVELOPER_HANDOFF.md](PRODUCT_USER_DEVELOPER_HANDOFF.md), operator guide, known limitations, development lessons and exact clean-environment commands.
5. **SOTA data-construction comparison** — compare DGSI against Self-Instruct, Evol-Instruct/WizardLM, Auto-Instruct-style ranking and a clearly labelled Magpie-style adaptation under matched source/model/token budgets. First compare candidate-data quality; run downstream SFT only if a separate authorized training cohort and untouched event-family holdout exist. Follow docs/DGSI_SOTA_DATA_CONSTRUCTION_COMPARISON.md.

## Tooling-milestone acceptance (not dataset acceptance)

- All five deliverables have concrete files and reproducible evidence.
- Skill package installs and runs independently from a clean environment.
- Evaluation cases are correctly labelled; no test fixture is promoted to formal training data.
- Effectiveness report distinguishes observed results from planned or unavailable evaluations.
- Comparison protocol and results are reported honestly; an unrun downstream SFT arm is explicitly NOT RUN, not simulated.
- No further tooling expansion unless an actual closeout blocker is demonstrated.

## Dataset blockers versus tooling-only non-blockers

The following do not block **toolkit-only handoff**: completion of the 21-task human expert review, source clearance for any materials *not redistributed* in the toolkit, completion of the five REAL L1 cases, or a downstream fine-tuning run. These **remain open blockers for the corresponding formal dataset admission, permitted training use, and effectiveness claims**. A tool release must never be reported as a completed SFT dataset. Any redistributed source content still requires appropriate rights; keep restricted source text out of the public package.

## Current evidence snapshot

At plan creation, main contains a portable toolkit line (0.2.0-rc.4), a 21-task literature-derived synthetic review cohort, five user-provided L0 case facts and an AAS RUN-03F SYNTHETIC_TEST_ONLY integration demonstration. These demonstrate implementation and evaluation fixtures, not a completed SOTA comparison or approved SFT corpus. Recheck main and release artifacts before declaring final product release.


## 2026-11-19 bounded execution

The three engineering closeout stages have been executed as a v0.2.0 development delivery: one portable entry, representative offline CLI acceptance, and a fresh 4-case × 5-method construction comparison with 40 GPT advisory reviews. One separately versioned DGSI correction has two new GPT reviews; it never changes the original comparison scores. See [measured results](DGSI_CLOSEOUT_RESULTS_2026-11-19.md) and [the reuse guide](../skills/dgsi-simulation-to-sft/references/CLOSEOUT_QUICKSTART.md). Human review absence does not block this user-authorized GPT-assisted toolkit/demo handoff. Real-Gold and training admission remain separate, and no additional process expansion is part of this closed scope.
