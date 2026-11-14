# Domain-Grounded Self-Instruct

**Product objective:** build a high-quality spacecraft fault-diagnosis SFT dataset for an LLM that interprets upstream machine-learning diagnosis results together with diagnostic logs, operational context, historical experience and reviewed domain knowledge.

**Responsibility boundary:** upstream ML/statistical methods process raw telemetry and produce anomaly/fault candidates, localization and evidence summaries. The LLM does not re-diagnose raw telemetry in this SFT task. DGSI trains second-stage engineering synthesis, historical-case reuse, conflict reconciliation, evidence sufficiency, uncertainty handling and next-step recommendations.

The current LLM-facing contracts are:
- [Diagnostic context case schema](resources/diagnostic_case.schema.json)
- [Chat SFT export schema](resources/diagnostic_sft.schema.json)
- [Hypothetical case example](examples/diagnostic_context_case_illustrative.json) — schema illustration only, not a training example\n- [Hypothetical chat SFT serialization](examples/diagnostic_context_sft_illustrative.json) — review-required illustration, not approved training data
- [Corrected dataset purpose and roadmap](docs/DATASET_PURPOSE_CORRECTION.md)\n- [D0 preliminary asset inventory](docs/D0_PRELIMINARY_ASSET_INVENTORY.md)\n- [AstroGraph result mapping and diagnostic-log intake gate](docs/ASTROGRAPH_RESULT_MAPPING_AND_LOG_GATE.md)

Raw telemetry remains in the upstream ML pipeline. DGSI may retain restricted artifact references for lineage, but must not inline raw waveforms/high-rate telemetry into the LLM prompt. Uncalibrated ML scores are not probabilities; fault candidates are not confirmed root causes; historical unresolved cases remain unresolved.


## Current scope (Phase 1)

- Public indexes: `resources/sources.json` (33 sources), `resources/source_passages.json` (42 passage records), `resources/terms.json` (ADCS), `resources/eps_terms.json` (EPS), `resources/telemetry_channels.csv`, `resources/fault_effects.json`.
- Run admission contract: `resources/simulation_truth.json` (initially **zero verified runs**).
- Versioned candidate JSON contract: `resources/seed.schema.json`.
- Conservative Python preflight CLI: `src/dgsi/quality.py`, 69 adversarial tests.
- Human workflows and **draft** reusable Skills: `docs/`, `skills/adcs-gold-seed-curation/SKILL.md`, `skills/eps-gold-seed-curation/SKILL.md`.

## Run locally (Python 3.11+; no external runtime dependencies)

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

`REVIEW_REQUIRED` means suspicious technical compounds need manual terminology review. `CANDIDATE_CHECKS_PASSED` means **structural and rule-based preflight only**; factual correctness, complete terminology coverage and physical causal validity require independent domain review. Mechanism/causal claims use registered passage IDs, not free-text locators. A `CANDIDATE_CHECKS_PASSED` result is never a Gold Seed. Human review metadata is not proof of reviewer identity; Gold freeze remains a separate governed action.

## Security, provenance and IP

**This repository is public.** Never commit R21/other nonpublic telemetry, unpublished experiment archives, commercial FMEA tables, credentials, personal data, or copyrighted source PDFs. Public source URLs and a small set of reviewed *metadata* are not a blanket license to reproduce texts. Input prompts must be truth-free; fault injection metadata, labels, and future holdouts are isolated. Published demo data are explicitly hypothetical.

Use [`docs/DOMAIN_REVIEW_CHECKLIST.md`](docs/DOMAIN_REVIEW_CHECKLIST.md) to review the 16 draft ADCS terms and [`docs/EPS_DOMAIN_REVIEW_CHECKLIST.md`](docs/EPS_DOMAIN_REVIEW_CHECKLIST.md) to review the 25 EPS terms and 15 EPS source passages. The development pressure suite contains 13 public-literature cases (6 ADCS, 7 EPS). A separate frozen holdout suite contains 8 additional cases (4 ADCS, 4 EPS) from SOHO, Kepler, Swift, Integral, Seasat, Intelsat and COSMIC. See [`docs/HOLDOUT_FREEZE_MANIFEST.md`](docs/HOLDOUT_FREEZE_MANIFEST.md) and [`docs/HOLDOUT_EVALUATION_PROTOCOL.md`](docs/HOLDOUT_EVALUATION_PROTOCOL.md). The runner now reports ADCS/EPS results separately and includes per-case paired score deltas and critical-flag counts; these are not human acceptance rates. See [`docs/EXPLORATORY_MODEL_INTERNAL_PRETEST.md`](docs/EXPLORATORY_MODEL_INTERNAL_PRETEST.md) for the preliminary same-model A/B pretest (not an independent blind result), and [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) for the still-pending independent evaluation. Live runs require distinct generator and judge model-family identifiers and make 3 Responses API calls per case. The opt-in blind Skill runner is `scripts/run_skill_blind_eval.py`; its default mode makes **zero network calls**. For Windows, use [`scripts/Run-SkillBlindEval.ps1`](scripts/Run-SkillBlindEval.ps1) to enter the API key through a hidden prompt, review the call count and explicitly authorize the run; see [`docs/LOCAL_LIVE_EVAL_SETUP.md`](docs/LOCAL_LIVE_EVAL_SETUP.md). Run the holdout dry run with `python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json`; a 4-case smoke costs 12 API calls and the full 8-case holdout costs 24. See [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) before any paid run. Start with [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/QUALITY_PROTOCOL.md`](docs/QUALITY_PROTOCOL.md). The plan and design are under `docs/superpowers/`.
