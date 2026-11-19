# DGSI Skill — user and developer handoff

**2026-11-19 delivery:** use [the v0.2.0 reproduction guide](../skills/dgsi-simulation-to-sft/references/CLOSEOUT_QUICKSTART.md) and the unified `run_dgsi_skill.py` entry. The new package includes actual GPT-generated development candidates and paired GPT reviews.

## Product identity

- Product: `dgsi-simulation-to-sft`
- Current repository version at handoff: `0.2.0-rc.4`
- Product status: portable candidate-generation/data-curation Skill; not a Gold/SFT authorization system.
- Main repository: https://github.com/clonetimer/Domain-Grounded-Self-Instruct
- Skill entry: `skills/dgsi-simulation-to-sft/SKILL.md`
- Operator guide: `skills/dgsi-simulation-to-sft/references/OPERATOR_QUICKSTART.md`

## What the Skill does

1. Ingest authorized spacecraft engineering sources and inventory provenance.
2. Extract L0 source facts and claim boundaries.
3. Build L1 diagnostic candidates from upstream ML findings, diagnostic logs, configuration, mission context and time-safe historical Context.
4. Separate current observations, source facts, scenario assumptions and hidden/post-event truth.
5. Produce formal diagnostic targets, evidence references, uncertainty and action-state semantics.
6. Run schema/source-closure checks and prepare independent review handoff.
7. Produce preview/serialization artifacts and coverage reports.

Raw telemetry remains in upstream ML/statistical pipelines. The LLM-facing input is the structured result and context, not high-rate raw telemetry.

## Clean environment installation

Requirements:
- Python 3.11 or later.
- `jsonschema>=4.22,<5` for validation.
- Authorized source files and a private working directory.

From a source checkout:

```bash
python -m pip install -r requirements-validation.txt
python -m unittest discover -s tests -v
```

PowerShell:

```powershell
python -m pip install -r requirements-validation.txt
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

For a portable Skill ZIP, extract it to a new directory and use the packaged operator instructions. The v0.2.0 package includes an allowlisted four-case public synthetic demo and its twenty construction candidates. Supply your own matching authorized files for further work. Verify `PACKAGE_SHA256_MANIFEST.json` and `SHA256SUMS.txt` before use.

## Core operator sequence

`INGEST → L0 → L1 → TARGET → AUDIT → REVIEW → PROJECT → COVERAGE → PACKAGE`

Typical preview command from the repository root:

```bash
python scripts/create_l1_model_preview.py \
  --collection /authorized/input/l1-candidate-collection.json \
  --source-facts /authorized/input/l0-source-facts.json \
  --output /authorized/output/l1-preview.json
```

The preview is an inspection artifact, not an authorized SFT record. Use a new output path; tools are designed to avoid overwriting prior evidence.

For complete review-kit generation, use the CLI and current cohort-bound instructions documented in `skills/dgsi-simulation-to-sft/references/OPERATOR_QUICKSTART.md`. Distribute reviewer A and B files separately through an authorized channel. Reviewer identity, source rights and adjudication must be verified outside the generator.

## Evaluation suite

The frozen suite inventory is `examples/dgsi_evaluation_suite_manifest_2026-11-18.json`. It distinguishes:
- 21 literature-derived synthetic L1 review tasks;
- 13 ADCS/EPS public-literature pressure cases;
- 8 ADCS/EPS process holdout cases;
- 5 user-provided private L0 case facts;
- one AAS RUN-03F synthetic integration fixture;
- two schema/serialization illustrations.

These categories are not additive independent incidents. The five L0 cases are not complete L1 records. AAS RUN-03F is not a real spacecraft event. No suite component is automatically Gold or trainable.

## Effectiveness and comparison

- Read `docs/DGSI_SKILL_EFFECTIVENESS_REPORT_2026-11-18.md` for observed results and unmeasured metrics.
- Read `docs/DGSI_SOTA_DATA_CONSTRUCTION_COMPARISON.md` for the matched-budget comparison protocol.
- The existing exploratory 7-case A/B pretest is same-model and concerns adjacent ADCS/EPS curation Skills; it is not independent proof of DGSI effectiveness.
- No live SOTA generation comparison or downstream SFT comparison has been executed at this handoff. Do not report them as completed.

## Hard boundaries

- Never fabricate upstream ML results, logs, scores, timestamps, spacecraft configuration or actions.
- Preserve score semantics; scores are not probabilities without calibration evidence.
- Keep fault candidates distinct from confirmed causes.
- Keep fault source distinct from affected components.
- Keep executed actions distinct from planned/recommended actions.
- Keep historical Context distinct from current direct evidence and enforce the analysis cutoff.
- Do not expose hidden truth, injection labels, curator-only notes or post-event answers in model-facing input.
- Do not call a test fixture REAL, Gold or SFT data.
- A CI pass proves software checks only, not domain correctness, expert approval, source permission or model effectiveness.

## Current known limitations

1. Independent domain-expert review of the 21-task REV1 cohort is not complete.
2. Source-use rights for evaluation-derived literature are not equivalent to training permission.
3. Five user-provided cases remain L0 facts; complete upstream ML/log/context packages are not present in the repository.
4. AAS RUN-03F is synthetic software acceptance data and cannot be used to fill a REAL case.
5. DGSI vs. SOTA construction comparison is designed but not run.
6. Downstream SFT effectiveness is NOT RUN because no separate approved training cohort and untouched event-family holdout are available.

## Handoff acceptance

A receiving operator should be able to:
- extract and verify the Skill package;
- read the Skill and operator quick start;
- run the offline schema/preflight and preview sequence against authorized sample inputs;
- inspect the Evaluation Suite manifest;
- distinguish demonstrated behavior from unrun comparisons and future dataset admission.

The product can be used as a candidate-generation and evaluation Skill within these limits. Formal SFT dataset admission remains a separate governed activity.
