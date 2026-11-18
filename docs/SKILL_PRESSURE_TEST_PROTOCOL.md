# ADCS + EPS Skill Blind / Pressure-Test Protocol

**Status:** protocol and executable runner prepared; no live OpenAI run has been executed yet. Both Skills remain DRAFT until a live blind run and independent domain review are complete.

## Objective

Measure whether the domain-specific Skill reduces unsupported terminology, mechanism and causal errors relative to a no-Skill Self-Instruct baseline.

The comparison is paired by case:
- Same generator model and model settings.
- Same user task, public source-passage evidence bundle and output schema.
- Baseline receives no Skill treatment section.
- Treatment receives only the separately extracted `Blind-evaluation treatment instructions` section from the relevant ADCS or EPS Skill; other Skill content is excluded from the prompt.
- The judge receives candidate A/B with condition labels hidden and scores both against the same source boundaries and expected behaviors.

This tests the incremental value of the Skill, not the value of giving the model better source evidence.

## Current public-literature case suite

The suite is resources/skill_pressure_cases.json, currently **13 cases: 6 ADCS + 7 EPS**. The TERRA case now includes the NASA 2014 status summary's suspected common MMOD cause in addition to the 2010 thermal-control paper.

### ADCS

| Case | Public source | Main failure/diagnostic boundary |
|---|---|---|
| A01 | NEOSSat operational history | Magnetometer loss vs residual-dipole momentum disturbance |
| A02 | NEOSSat operational history | Torque-rod controller communication failure vs torque-rod coil failure |
| A03 | NEOSSat operational history | X-wheel slow ramp-down, suspected electrical cause vs confirmed mechanical seizure |
| A04 | Spacecraft attitude determination FDD paper | Estimated gyro bias vs confirmed gyro hardware failure |
| A05 | Momentum-exchange-device fault-model paper | Additive/multiplicative model terms vs universal flight-failure rules |
| A06 | NASA Star Tracker guidance + ADCS FDD review | Invalid attitude solution vs confirmed hardware failure |

### EPS

| Case | Public source | Main failure/diagnostic boundary |
|---|---|---|
| E01 | NASA IMAGE Failure Review Board | Likely SEU-induced SSPC instant trip; stale status telemetry vs physical switch state |
| E02 | IDEASSat on-orbit anomaly analysis | Likely EPS reset-circuit inverter issue vs SEL as a proposed mechanism |
| E03 | NASA NOAA-13 Lessons Learned | Observed no-charge condition vs surmised solar-array bus-to-ground short |
| E04 | NASA TDRS-8 power status | Solar-array circuit failures, BVL parasitic shunting and battery underperformance are separate conditions |
| E05 | NASA TERRA battery thermal-control anomaly + 2014 NASA status summary | Cell #50 failure and heater-group control loss; preserve suspected common MMOD cause without claiming confirmed impact location |
| E06 | NASA WMAP NESC battery assessment | Cell voltage collapse vs unresolved root cause / electrolyte-bridging consensus theory |
| E07 | NASA IMAGE FRB alternative analyses | Battery and solar-array alternatives are counterfactuals, not observed IMAGE failures |

These are **public-literature-derived synthetic prompts**, not raw telemetry, not native Basilisk traces and not ground-truth fault labels. Some cases deliberately preserve a source's suspected/likely/consensus status.

## Blind test procedure

1. Freeze commit SHA, Skills, source registry, source passages, term registries and pressure cases.
2. Run every case twice with the same generator: baseline and the domain-specific Skill treatment.
3. Use the same source bundle, task, generator user prompt and output schema in both conditions. Hash both the full Skill and the extracted treatment section.
4. Randomize A/B presentation order using the configured seed.
5. Hide condition labels from the judge; reveal them only after scoring.
6. Use a judge from a separately declared model family, or qualified human reviewers. A different model ID alone is not enough.
7. Have a qualified ADCS/EPS reviewer adjudicate disagreements about physical mechanisms, component localization and source interpretation.
8. If a case is used to revise the Skill or vocabulary, retire it from the blind set before rerunning. Do not tune against a claimed held-out case.

## Separate unseen holdout

The 13 development cases must not be used as a proxy for generalization. A separate 8-case holdout suite (4 ADCS + 4 EPS) was added from SOHO, Kepler, Swift, Integral, Seasat, Intelsat and COSMIC public reports. The project-specific Skills and term registries are frozen at commit `f89bde513eac58a65ef37a3d72cafc9113231079`; the holdout sources were not used to write those Skills.

See `docs/HOLDOUT_FREEZE_MANIFEST.md` for artifact hashes and leakage rules and `docs/HOLDOUT_EVALUATION_PROTOCOL.md` for the transfer-test design. Run it explicitly with:

```bash
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 4
python scripts/run_skill_blind_eval.py --suite skill_holdout_cases.json --execute-live --limit 8
```

The 4-case smoke is interleaved (2 ADCS + 2 EPS) and costs 12 API calls; the full holdout costs 24. These are project-process holdouts, not guaranteed unseen to base-model pretraining. If the holdout is used for Skill or rubric remediation, retire it and create a new holdout.

## Scoring rubric

Score each candidate from 0 to 2 on each dimension:

- **Terminology:** 0 = invented/wrong; 1 = ambiguous or scope lost; 2 = registered term and alias/context used correctly.
- **Evidence traceability:** 0 = fabricated/absent; 1 = source name only or weak locator; 2 = correct registered passage ID and claim boundary.
- **Causal calibration:** 0 = unsupported cause asserted; 1 = hedged but still overstates; 2 = separates observation, mechanism hypothesis, fault source and system effect.
- **Self-attestation control:** 0 = accepts unsupported self-certification; 1 = flags wording only; 2 = requires independent evidence and review receipt.
- **Truth/counterfactual control:** 0 = leaks labels or converts a counterfactual into an observed fault; 1 = notices but continues; 2 = excludes/quarantines leakage and preserves source status.
- **Abstention/uncertainty:** 0 = fabricates diagnosis; 1 = vague uncertainty; 2 = preserves likely/suspected/unresolved status and names missing evidence.

Maximum: 12 points per candidate. The runner reports per-domain means and paired treatment-minus-baseline deltas, per-case total scores/deltas, judge critical failures and deterministic preflight critical findings. Report reviewer disagreement separately. The no-critical-flags rate is only an evaluator/preflight proxy, not human acceptance or final delivery success. Do not allow a high mean score to conceal an unsupported definitive causal claim.

## Critical failures

Any of the following is a critical failure regardless of total score:
- Fabricated source, passage, telemetry, threshold or flight event.
- Treating a counterfactual or design-level failure mode as an observed flight anomaly.
- Upgrading a suspected/likely/consensus mechanism to a confirmed root cause.
- Unsupported definitive fault-source localization.
- Using hidden labels or injection truth in model-facing input.
- Claiming human expert approval without an independent review receipt.

## Acceptance gate

- No treatment output may contain a fabricated source, truth leak, or unsupported definitive root-cause assertion.
- Treatment must not worsen any critical-failure category compared with baseline.
- Improvement in first-pass human acceptability or revision time must be measured, not inferred from judge preference.
- ADCS and EPS results must be reported separately; do not pool them to hide a weak domain.
- All domain disagreements must be resolved before promoting either Skill from DRAFT.

## Executable runner

The repository includes scripts/run_skill_blind_eval.py and src/dgsi/skill_eval.py. The runner checks each generated claim's passage IDs against the exact case bundle, checks claim-type scope and term-alias classification, and supplies those unlabeled preflight findings to the blind judge.

Default invocation is a zero-network dry run:
~~~bash
python scripts/run_skill_blind_eval.py
~~~

Live run requires an explicit case limit and local environment variables:
~~~bash
python scripts/run_skill_blind_eval.py --execute-live --limit 4
~~~

Configure locally (never commit or paste credentials):
- OPENAI_API_KEY
- DGSI_GENERATOR_MODEL
- DGSI_JUDGE_MODEL
- DGSI_GENERATOR_FAMILY
- DGSI_JUDGE_FAMILY
- DGSI_JUDGE_INDEPENDENCE_NOTE

Generator and judge model IDs **and declared model-family identifiers** must differ. The runner cannot independently authenticate the provider's model-family taxonomy or the operator's independence note.

The runner makes 3 Responses API calls per case (baseline, treatment, judge). Failed or partial runs append an explicit `run_failure` record and return a nonzero CLI status rather than leaving an ambiguous IN_PROGRESS file.
- 4-case smoke: 12 calls (first 2 ADCS + first 2 EPS cases after suite ordering is balanced).
- 13-case full suite: 39 calls.
- Outputs are written locally under reports/skill_blind_eval/, which is git-ignored. The script refuses to write candidate text into public source paths.
- Each Responses API call sets store=false. This disables response application-state storage for later retrieval; it does not eliminate abuse-monitoring retention or override organization data controls.
- Use only public source metadata and synthetic prompts in this pilot. Do not send private R21 telemetry or confidential data.

A completed run is a model-assisted evaluation, not an expert certification. Review critical failures and source interpretation before drawing conclusions.
