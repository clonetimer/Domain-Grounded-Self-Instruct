# Domain-Grounded Self-Instruct

**Product objective:** build a high-quality spacecraft fault-diagnosis SFT dataset for an LLM that interprets upstream machine-learning diagnosis results together with diagnostic logs, operational context, historical experience and reviewed domain knowledge.

**Responsibility boundary:** upstream ML/statistical methods process raw telemetry and produce anomaly/fault candidates, localization and evidence summaries. The LLM does not re-diagnose raw telemetry in this SFT task. DGSI trains second-stage engineering synthesis, historical-case reuse, conflict reconciliation, evidence sufficiency, uncertainty handling and next-step recommendations.

The current LLM-facing contracts are:

- [Diagnostic context case schema](resources/diagnostic_case.schema.json)
- [Chat SFT export schema](resources/diagnostic_sft.schema.json)
- [Hypothetical case example](examples/diagnostic_context_case_illustrative.json) — schema illustration only, not a training example
- [Hypothetical chat SFT serialization](examples/diagnostic_context_sft_illustrative.json) — review-required illustration, not approved training data
- [Corrected dataset purpose and roadmap](docs/DATASET_PURPOSE_CORRECTION.md)
- [Formal report vs. curator review boundary](docs/FORMAL_REPORT_VS_CURATOR_REVIEW.md)
- [L0 source fact card schema](resources/source_fact_card.schema.json)
- [L1 dual-track and history Context design](docs/L1_DUAL_TRACK_AND_HISTORY_CONTEXT.md)
- [L1 task packet schema](resources/l1_task_packet.schema.json)
- [L1 collection/split manifest schema](resources/l1_task_packet_collection.schema.json)
- [First L1 literature-derived synthetic pilot](examples/l1_literature_synthetic_task_packets_v0.1.json)
- [Controlled SFT effectiveness protocol](docs/CONTROLLED_SFT_EFFECTIVENESS_PROTOCOL.md)
- [D0 preliminary asset inventory](docs/D0_PRELIMINARY_ASSET_INVENTORY.md)
- [Local read-only inventory script](scripts/inventory_diagnostic_case_assets.py)
- [AstroGraph result mapping and diagnostic-log intake gate](docs/ASTROGRAPH_RESULT_MAPPING_AND_LOG_GATE.md)

Raw telemetry remains in the upstream ML pipeline. DGSI may retain restricted artifact references for lineage, but must not inline raw waveforms/high-rate telemetry into the LLM prompt. Uncalibrated ML scores are not probabilities; fault candidates are not confirmed root causes; historical unresolved cases remain unresolved.


## P5-C2 current engineering candidate

The reusable toolkit remains **0.2.0-rc.4**. The current review candidate contains **21 literature-derived synthetic tasks, 9 source event families, 12 bound L0 fact cards and 7 primary source ID groups**. Six additions cover two conflict-reconciliation situations and four explicit justified-abstention situations using existing task types and instructions. The corrected original 15 packets and matching L0 bytes are unchanged. Cassini chronology has three separately listed corroborating sources. These counts describe coverage, not statistically independent incidents. Independent expert adjudications, rights-cleared publications, official dataset splits and authorized SFT rows remain **zero**; training is not authorized.

- Start with the [21-task content report and commands](docs/P5C2_COVERAGE_TASKS_2026-11-18.md). The packaged [operator quick start](skills/dgsi-simulation-to-sft/references/OPERATOR_QUICKSTART.md) retains the prior 15-task worked example; the same RC4 commands accept the new external cohort.
- The [returned preliminary-review response](docs/P5C2_AI_PRE_REVIEW_RESPONSE_2026-11-18.md) reconciles the original 15-task AI advice against the current full inputs and records the seven-source rights research. It preserves the current candidate and pending admission states; proposed AI scores are not expert submissions.
- The returned 21-task AI advisory and rights-evidence triage are dispositioned in [P5-C2 advisory disposition](docs/P5C2_AI_ADVISORY_DISPOSITION_2026-11-18.md). A new immutable REV1 candidate corrects only task 015's over-specific structured fault-mode label; it requires fresh cohort-bound A/B and rights forms. See [REV1 candidate](examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json), [REV1 coverage](examples/p5c2_coverage_candidate_coverage_2026-11-18_r1.json), and [REV1 rights research](examples/p5c2_current_source_rights_research_2026-11-18_r1.json). The prior 21-task cohort and advisory remain historical; no AI advisory is an expert receipt.
- Review the [21-task coverage candidate](examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json), [unchanged matching L0 source cards](examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json), [six-addition source ledger](examples/p5c2_coverage_additions_review_2026-11-18.json) and [current coverage report](examples/p5c2_coverage_candidate_coverage_2026-11-18.json).
- Coverage now includes 11 diagnostic-synthesis tasks, 2 conflict-reconciliation tasks, 5 evidence-sufficiency tasks and one each for history reuse, next-step recommendation and handover. Four of the evidence-sufficiency tasks explicitly withhold unsupported conclusions; abstention is a coverage dimension, not an added schema task type.
- The [content-corrected 15-task baseline](examples/l1_literature_synthetic_task_packets_c2_content_corrected_2026-11-18.json), [correction ledger](examples/p5c2_content_correction_review_2026-11-18.json), [prior content report](docs/P5C2_CONTENT_CORRECTION_2026-11-18.md) and [2026-11-17 snapshot](examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json) remain immutable historical cohorts.
- Generate separate A/B review kits with the [delivery contract](docs/P5C2_PACKAGE_DELIVERY_2026-11-18.md), then use the [current-source-bound expert intake](docs/P5C2_CURRENT_EXPERT_INTAKE_20261118.md) to receive completed or partial forms and produce the pending-action queue.
- Receive source-rights worksheets through the separate [current-source rights preflight](docs/P5C2_CURRENT_SOURCE_RIGHTS_PREFLIGHT_20261118.md).
- See [main reconciliation evidence](docs/P5C2_MAIN_RECONCILIATION_20261118.md) and the preserved [historical specialized-task review](docs/P5C2_SPECIALIZED_TASK_REVIEW_2026-11-17.md).

The expert intake accepts each historical form only against its matching cohort and source snapshot. The 21-task cohort requires fresh A/B forms covering all 21 tasks; neither set of prior 15-task forms can be reused for it. Intake does not authenticate reviewers, resolve scientific disagreements or authorize source use. REAL and literature-derived synthetic candidates remain separate parallel tracks.

## Foundational Phase 1 assets

- Public indexes: `resources/sources.json` (33 sources), `resources/source_passages.json` (42 passage records), `resources/terms.json` (ADCS), `resources/eps_terms.json` (EPS), `resources/telemetry_channels.csv`, `resources/fault_effects.json`.
- Run admission contract: `resources/simulation_truth.json` (initially **zero verified runs**).
- Versioned candidate JSON contract: `resources/seed.schema.json`.
- Conservative Python preflight CLI: `src/dgsi/quality.py`; the initial Phase 1 suite contained 69 adversarial tests.
- Human workflows and **draft** reusable Skills: `docs/`, `skills/adcs-gold-seed-curation/SKILL.md`, `skills/eps-gold-seed-curation/SKILL.md`.

## Run validation locally (Python 3.11+)

```bash
python -m pip install -r requirements-validation.txt
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

PowerShell:

```powershell
python -m pip install -r requirements-validation.txt
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

`REVIEW_REQUIRED` means suspicious technical compounds need manual terminology review. `CANDIDATE_CHECKS_PASSED` means **structural and rule-based preflight only**; factual correctness, complete terminology coverage and physical causal validity require independent domain review. Mechanism/causal claims use registered passage IDs, not free-text locators. A `CANDIDATE_CHECKS_PASSED` result is never a Gold Seed. Human review metadata is not proof of reviewer identity; Gold freeze remains a separate governed action.

## Security, provenance and IP

**This repository is public.** Never commit R21/other nonpublic telemetry, unpublished experiment archives, commercial FMEA tables, credentials, personal data, or copyrighted source PDFs. Public source URLs and a small set of reviewed *metadata* are not a blanket license to reproduce texts. Input prompts must be truth-free; fault injection metadata, labels, and future holdouts are isolated. Published demo data are explicitly hypothetical.

Use [`docs/DOMAIN_REVIEW_CHECKLIST.md`](docs/DOMAIN_REVIEW_CHECKLIST.md) to review the 16 draft ADCS terms and [`docs/EPS_DOMAIN_REVIEW_CHECKLIST.md`](docs/EPS_DOMAIN_REVIEW_CHECKLIST.md) to review the 25 EPS terms and 15 EPS source passages. The development pressure suite contains 13 public-literature cases (6 ADCS, 7 EPS). A separate frozen holdout suite contains 8 additional cases (4 ADCS, 4 EPS) from SOHO, Kepler, Swift, Integral, Seasat, Intelsat and COSMIC. See [`docs/HOLDOUT_FREEZE_MANIFEST.md`](docs/HOLDOUT_FREEZE_MANIFEST.md) and [`docs/HOLDOUT_EVALUATION_PROTOCOL.md`](docs/HOLDOUT_EVALUATION_PROTOCOL.md). The runner now reports ADCS/EPS results separately and includes per-case paired score deltas and critical-flag counts; these are not human acceptance rates. See [`docs/EXPLORATORY_MODEL_INTERNAL_PRETEST.md`](docs/EXPLORATORY_MODEL_INTERNAL_PRETEST.md) for the preliminary same-model A/B pretest (not an independent blind result), and [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) for the still-pending independent evaluation. Live runs require distinct generator and judge model-family identifiers and make 3 Responses API calls per case. The opt-in blind Skill runner is `scripts/run_skill_blind_eval.py`; its default mode makes **zero network calls**. For Windows, use [`scripts/Run-SkillBlindEval.ps1`](scripts/Run-SkillBlindEval.ps1) to enter the API key through a hidden prompt, review the call count and explicitly authorize the run; see [`docs/LOCAL_LIVE_EVAL_SETUP.md`](docs/LOCAL_LIVE_EVAL_SETUP.md). Run the holdout dry run with `python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json`; a 4-case smoke costs 12 API calls and the full 8-case holdout costs 24. See [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) before any paid run. Start with [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/QUALITY_PROTOCOL.md`](docs/QUALITY_PROTOCOL.md). The plan and design are under `docs/superpowers/`.


## L1 pilot and review

- [L1 literature pilot coverage](docs/L1_LITERATURE_PILOT_COVERAGE.md)
- [Machine-readable L1 pilot manifest](examples/l1_literature_pilot_coverage_v0.1.json)
- [L1 task coverage and independent blind review](docs/L1_TASK_COVERAGE_AND_BLIND_REVIEW.md)

- [L1 review receipt batch audit](docs/L1_REVIEW_RECEIPT_BATCH_AUDIT.md)

- [L0 source-fact domain review matrix](docs/L0_SOURCE_FACT_DOMAIN_REVIEW_MATRIX.md)

## Portable simulation-to-SFT production toolkit

A provider-neutral production Skill is available at
[`skills/dgsi-simulation-to-sft/`](skills/dgsi-simulation-to-sft/README.md).
It guides other AI systems through source ingestion, L0 fact extraction, L1
diagnostic candidate generation, simulator-truth separation, independent
audit and human-review handoff for authorized spacecraft design reports,
test reports and simulation run materials.

The toolkit is **DRAFT / candidate-generation only**. It does not authorize
Gold promotion, formal splits, SFT export or training. In particular, the
current L1 schema does not yet support the distinct
`SIMULATION_CASE_CANDIDATE` and `DESIGN_DERIVED_HYPOTHETICAL` tracks; do not
mislabel those records to force schema acceptance.

Build a portable ZIP from a repository checkout with:

```bash
python scripts/package_dgsi_simulation_to_sft.py
```

## Development experience

Reusable cross-platform engineering lessons are recorded in [`docs/DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md`](docs/DEVELOPMENT_EXPERIENCE_OPTIONAL_PYTHON_DEPENDENCIES.md), including the OCR optional-dependency mocking failure, its correction, and the rule for testing Python package import semantics.

The ongoing [development experience record](docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md) also covers source binding, review delivery, deterministic packaging, main reconciliation and the independent-review return path. Lessons 107 onward record the RC3 continuation.

[Lessons 121–126 on conflict and justified abstention](docs/DEVELOPMENT_EXPERIENCE_C2_COVERAGE_TASKS_20261118.md) record the six-task extension. This companion keeps the already issued RC4 package unchanged while documenting new content-design findings.

[Lessons 127–132 on processing a returned preliminary review](docs/DEVELOPMENT_EXPERIENCE_C2_REVIEW_RETURN_20261118.md) cover version reconciliation, evidence-sensitive disposition, rights dependencies and complete review handoffs.
