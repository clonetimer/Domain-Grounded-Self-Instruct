# ADCS + EPS Holdout Evaluation Protocol

**Status:** holdout suite and runner support implemented; formal live evaluation has not yet been executed. Both Skills remain DRAFT.

## Objective

Test whether the procedural ADCS/EPS Skills transfer to public failure cases that were not used to draft the project-specific Skills or term catalogs.

This is distinct from the 13-case development pressure suite:
- Development suite: 6 ADCS + 7 EPS cases; used to shape the initial Skill and validator.
- Holdout suite: 4 ADCS + 4 EPS cases; frozen against the Skill/term baseline in `docs/HOLDOUT_FREEZE_MANIFEST.md`.

The holdout is unseen to this project's Skill-writing process, not guaranteed unseen to foundation-model pretraining.

## Experimental controls

1. Same generator model, output schema, case task and registered source evidence for baseline and treatment.
2. Baseline receives no Skill treatment instructions.
3. Treatment receives only the Skill's extracted `Blind-evaluation treatment instructions` section. Full Skill reference material is not injected as extra case knowledge.
4. Every generated claim must cite at least one source passage from the exact case bundle.
5. Deterministic preflight checks case-scoped passage IDs, allowed claim scope and term alias classification before judging.
6. A separate declared model family judges anonymous candidate A/B. Condition labels are mapped back only after scoring.
7. Generation order alternates by frozen case position; A/B judge order is separately randomized by deterministic case hash.
8. Expected behaviors are passed to the judge only, never to the generator.
9. Record Skill, treatment section, term catalogs, source registry, source passages and suite hashes with the run.
10. Any holdout-driven Skill/rubric/term change retires this suite from future holdout claims.

## Case matrix

| Case | Domain | Main transfer challenge |
|---|---|---|
| H01 SOHO | ADCS | Distinguish gyro hardware fault from ground command/configuration error and misdiagnosis |
| H02 Kepler | ADCS | Report wheel failures without inventing undisclosed internal mechanisms |
| H03 Swift | ADCS | Preserve preliminary belief of mechanical failure without inventing a failed part |
| H04 Integral | ADCS | Separate radiation-belt-associated initial wheel stop from tentative star-tracker explanation for recurrence |
| H05 Seasat | EPS | Progressive slip-ring short; likely brush arcing versus unresolved initiating path |
| H06 IS-804 | EPS | Preserve ESD/battery-circuit/high-voltage propagation chain and its most-likely status |
| H07 IS-802 | EPS | Localize likely harness short rather than solar cell or battery failure |
| H08 COSMIC | EPS | Identify ADCS recovery loop as initiating fault with downstream charging and thermal effects in EPS |

All eight cases are public-literature-derived synthetic prompts, not raw telemetry, native Basilisk traces or ground-truth training labels.

## Scoring

Use the six 0–2 dimensions from `docs/SKILL_PRESSURE_TEST_PROTOCOL.md`: terminology, evidence traceability, causal calibration, self-attestation control, truth/counterfactual control, and abstention/uncertainty.

Report ADCS and EPS separately; each case's baseline and treatment score; paired score deltas; deterministic preflight findings and critical failures; judge preference and rationale; and human adjudication of every critical causal/localization disagreement.

Do not report the mean score as diagnostic accuracy. Eight cases are a transfer probe, not a statistically powered benchmark.

## Commands

```bash
# Zero-network validation
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json

# 4-case smoke: 2 ADCS + 2 EPS, 12 API calls
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 4

# Full holdout: 8 cases, 24 API calls
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 8
```

The runner requires local API credentials and distinct declared generator/judge model families. Output is local-only under `reports/skill_blind_eval/`. Responses API `store=false` does not eliminate abuse-monitoring retention; use public evidence and synthetic prompts only.

## Promotion gate

Do not promote either Skill until the holdout run is completed and reproducible; no critical failure is hidden by aggregate score; independent ADCS/EPS reviewers adjudicate mechanism and localization; first-pass human acceptance and revision time are measured on a separate curation pilot; and the holdout suite is retired if used for remediation.
