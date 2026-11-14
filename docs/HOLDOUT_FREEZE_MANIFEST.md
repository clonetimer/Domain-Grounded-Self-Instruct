# Holdout Freeze Manifest — ADCS + EPS

**Purpose:** preserve a public-literature set for testing transfer of the ADCS/EPS curation Skills beyond the examples used to draft the project-specific Skills.

## Frozen baseline

The project-specific Skills and term registries are frozen at commit:

`f89bde513eac58a65ef37a3d72cafc9113231079`

| Artifact | Git blob SHA at freeze |
|---|---|
| ADCS Skill | `057d5f0104b96d9646d8d72d5658a928ea550d0e` |
| EPS Skill | `842295595c05a7685de5a998eb5d03b7d8c7b886` |
| ADCS terms | `923418728b575853ec19ca69a4ab3160112978ad` |
| EPS terms | `b5adda7fed8cf6d88889d354500f86e91158595f` |

The holdout suite and its source passages were added after this freeze. The listed Skills and term registries were not modified to incorporate these cases.

## Reproducibility artifact hashes

The following Git blob SHAs identify the holdout suite and the evidence/evaluator artifacts at the current implementation baseline:

| Artifact | Git blob SHA |
|---|---|
| Holdout cases | `59c28f899549242119d6a9c5a695dc749550fab4` |
| Public source registry | `9dd949b9050f0c444fbda970225e5758851c8b57` |
| Public passage registry | `bc1f9250591b147967b7cfd070634b56db05284b` |
| Blind evaluator | `1a36a528af80859135ed43a7d3b35cb209f8ffef` |

The runner also writes SHA-256 digests of the suite, source registry, passage registry, Skills, extracted treatment sections and term registries into each run's metadata. A new implementation commit changes the evaluator blob SHA but does not by itself change the frozen Skill/term baseline or holdout case content.

## Holdout suite

File: `resources/skill_holdout_cases.json`

- 8 cases: 4 ADCS + 4 EPS.
- Interleaved domain order for balanced 4-case smoke tests.
- 10 registered source-passage records across 7 new public source records.
- Expected behaviors are judge-only and are not included in generator prompts.
- The same task and registered evidence bundle are passed to baseline and treatment.
- Treatment receives only the extracted procedural Skill section.

### ADCS holdout sources

| Case | Source | Transfer target |
|---|---|---|
| H01 | SOHO Joint NASA/ESA Investigation Board | Ground-command/configuration error versus false gyro hardware diagnosis |
| H02 | NASA Kepler mission update | Two failed reaction wheels with no published internal mechanism |
| H03 | NASA/GSFC Swift GCN Circular 31547 | Preliminary mechanical failure belief versus confirmed mechanism |
| H04 | ESA Integral operations report | Separate initial wheel-stop and second star-tracker-occultation episodes |

### EPS holdout sources

| Case | Source | Transfer target |
|---|---|---|
| H05 | NASA Seasat Failure Review Board | Progressive solar-array slip-ring short; likely arc versus unresolved initiating path |
| H06 | Intelsat Form 20-F / IS-804 | ESD → battery-circuit high-current event → high-voltage power-system propagation |
| H07 | Intelsat Form 20-F / IS-802 | South solar-array harness short versus cell/battery mislocalization |
| H08 | COSMIC CubeSat on-orbit paper | ADCS recovery-loop failure propagating into EPS charging and thermal symptoms |

## Leakage controls

1. Do not add H01–H08 case-specific rules, mechanisms or wording to either Skill before the formal run.
2. Do not add case-specific terms to either term catalog after freeze. If a terminology correction is essential, retire the affected holdout case and create a replacement.
3. Do not tune Skills against the holdout expected-behavior labels. The case file is public in this repository, so this is a process holdout, not a cryptographically hidden test set.
4. Foundation-model pretraining exposure cannot be audited. “Unseen” means unseen by this project's Skill/term drafting process, not guaranteed unseen by the base model.
5. Once any holdout output is used to revise a Skill, term catalog, prompt or scoring rubric, this holdout suite becomes a development set and must no longer be reported as held out. Create and freeze a new suite before claiming generalization.
6. Every run records Skill hashes, treatment-section hashes, term-catalog hashes, case-suite hash, source-registry hash, passage-registry hash, model IDs and declared model families.

## Formal run

Dry run (zero network calls):

```bash
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json
```

Four-case smoke (two ADCS + two EPS; 12 Responses API calls):

```bash
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 4
```

Full holdout (8 cases; 24 Responses API calls):

```bash
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 8
```

Live execution requires local API credentials and separately declared generator/judge model families. Output remains under the ignored local `reports/skill_blind_eval/` directory. Do not commit candidate outputs or private telemetry.

## Interpretation limits

Eight cases are a small, deliberately heterogeneous transfer probe, not a statistically powered benchmark. Report per-case critical failures and per-domain results. A higher judge score alone is not a Gold-quality or human-acceptance improvement. Independent domain review and first-pass human acceptance/revision-time measurement remain required.
