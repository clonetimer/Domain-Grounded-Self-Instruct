# P5-C2: six coverage tasks added to the corrected candidate

## Outcome and scope

The candidate expands from 15 to **21 literature-derived synthetic tasks**. It adds two conflict-reconciliation tasks and four dedicated justified-abstention tasks. All corrected baseline packet objects remain canonical-identical, the matching L0 file remains byte-identical, and the source event-family set remains nine. The new tasks reuse the existing instruction templates, schemas, validation functions and **0.2.0-rc.4** runtime.

This is a content extension. All 21 tasks remain `REVIEW_REQUIRED`; independent expert adjudications, source-rights clearances, official split assignments and authorized SFT records are zero. Structural validation and an AI content review do not change those states.

The new collection is `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-2026-11-18`. Its exact projection fingerprint is recorded in the [addition ledger](../examples/p5c2_coverage_additions_review_2026-11-18.json), [coverage report](../examples/p5c2_coverage_candidate_coverage_2026-11-18.json) and [preflight report](../examples/p5c2_coverage_candidate_preflight_2026-11-18.json). Historical cohorts remain available under their original filenames.

## What each new task teaches

| Task | Evidence available in the synthetic scenario | Required reasoning boundary |
| --- | --- | --- |
| 016 — Lunar Orbiter power comparison | An onboard monitor indication falls by about 3 dB. An independent, calibrated and normalized receiving summary for the same path, carrier, baseline and time window varies by no more than 0.2 dB. Comparison checks are supplied. | Reconcile the ML claim of a comparable actual carrier loss with the independent current evidence. Both observations can be valid. Prioritize the monitor response/calibration explanation without certifying a particular diode, total RF output or all TWTA functions. |
| 017 — TROPICS qualification comparison | The same synthetic slip-ring unit/channel fails an 18% RH air test and passes an 82% RH air test. Limits and declared operating profiles match; facility, acquisition-chain, order and handling differences are incompletely controlled. | Reject the ML generalization that the local PASS closes all qualification concerns. Preserve both conditional reports. Humidity is not established as the unique cause; these air tests are not TVAC or an in-orbit clearance. |
| 018 — Lunar Orbiter startup trend | Three comparable completed startup summaries show normalized peak helix current 1.40, 1.25 and 1.10, against an upper reference of 1.00. Elapsed time increases 6/12/18 hours while accumulated thermal cycles increase 0/1/2. | Preserve the observed decreasing positive exceedance. Withhold a unique mechanical-stress versus pressure-decay explanation because the candidate explanatory variables co-vary. Ask for discriminating summaries from existing records rather than new operating commands. |
| 019 — Spaceborne TWTA before isolation | Repeated, checked whole-unit measurements show about 4 dB output loss. The supplied material contains no current mode-comparison, EPC/TWT/LCAMP isolation, module-level, gas, EMMI or replacement-validation result. | Accept the whole-unit loss within the scenario. Withhold Z2/Z6 LNA hydrogen-poisoning attribution and exclusion of other internal paths. Missing supplied material does not establish that tests were never performed. Request staged isolation evidence. |
| 020 — FUSE recovery assessment | A restart is recorded as executed. During the next five minutes, a comparable drag index decreases from 100 to 70 with nonzero speed. The value 100 is a normalization start, not a healthy baseline; no recovery criterion or later valid window is supplied. | Record the action and 30% relative decrease. Neither confirmed recovery nor continuing abnormality follows without an applicable baseline and follow-up. Do not infer a removed Kapton contact or a proven repair. |
| 021 — Cassini input-quality failure | The current header names RWA-2 and an 08:00–08:20 window, while the only symptom manifest belongs to RWA-3 and 07:00–07:20. The upstream package explicitly reports `DATA_QUALITY_ERROR`; no verified mapping or independent current summary is available. | Establish the binding failure and withhold current hardware status. Rejecting the retained invalid physical candidate does not prove health. Request a corrected and verified upstream summary before evaluating current symptoms or mechanisms. |

The conflict label refers to a disputed diagnostic proposition. It does not require falsely declaring two condition-scoped observations mutually impossible. The four abstention tasks use the existing `evidence_sufficiency` type: three request additional analysis, while the input-binding failure returns `INSUFFICIENT_CONTEXT`.

All current values, dates, equipment identities, logs, comparison checks and ML scores are synthetic. Scores are ranking values, not calibrated probabilities. The six tasks contain no raw telemetry and manufacture no independent historical retrieval hit. Historical evidence remains explicit context; it is excluded from current supporting/contradicting evidence references and candidate-support references.

## Source boundaries

The [source ledger](../examples/p5c2_coverage_additions_review_2026-11-18.json) gives exact card bindings and passage locators. The source material constrains mechanisms and interpretation; it does not report the newly constructed current scenarios.

- The [Lunar Orbiter III report](https://ntrs.nasa.gov/api/citations/19670027946/downloads/19670027946.pdf), physical PDF pages 119–120 and 173, distinguishes a temperature-related power indication from received-carrier behavior and retains two explanations for the first-turn-on helix-current anomaly. The new measurements, 3 dB/0.2 dB comparison, and three-point covariation experiment are synthetic.
- The [TROPICS lessons paper](https://ntrs.nasa.gov/api/citations/20240011771/downloads/IEEEAero_TROPICS_2025_for_approval.pdf), Section 6, physical page 5, reports different contact-resistance outcomes across low- and high-humidity test environments. The new same-unit report set and ML closure claim are synthetic; the paper does not establish the new scenario's unique cause.
- The [published TWTA study](https://kjdzjs.spacejournal.cn/article/doi/10.3969/j.issn.1674-7135.2026.02.007), 2026, 23(2):46–53, contains a longer isolation and validation chain than an initial whole-unit loss. Detailed locators are inherited from the prior completed full-text correction review and unchanged L0. A renewed full-PDF request during this continuation reached a CAPTCHA; this batch does not claim another complete reading or new physical test evidence.
- The [FUSE operations paper](https://archive.stsci.edu/fuse/papers/spie4854/spie_4854-72.pdf), Section 3, physical page 5, distinguishes different wheel episodes and recovery times. Those historical times cannot certify the synthetic five-minute recovery window.
- [NASA LLIS 1416](https://llis.nasa.gov/lesson/1416) provides conditional historical low-speed and lubrication context. The new wheel/window mismatch is an invented input-quality scenario, not an assertion that Cassini experienced that data error.

## Coverage and preserved history

| Measure | Corrected baseline | Expanded candidate |
| --- | ---: | ---: |
| Total tasks | 15 | 21 |
| Diagnostic synthesis | 11 | 11 |
| Conflict reconciliation | 0 | 2 |
| Evidence sufficiency | 1 | 5 |
| Dedicated correct-abstention dimension | 0 | 4 |
| Historical-case reuse | 1 | 1 |
| Next-step recommendation | 1 | 1 |
| Handover summary | 1 | 1 |
| Source event families | 9 | 9 |
| Bound L0 cards | 12 | 12 |
| Primary source ID groups | 7 | 7 |

The full unchanged L0 file contains 13 cards, of which 12 are bound by this candidate. The unused ISEE card does not become an extra covered event. Six variants are not six new independent real incidents. Any later split must preserve the existing family grouping; this batch assigns no split.

## Review artifacts and operating commands

The complete delivery includes the 21-task collection, unchanged L0, source/coverage/preflight ledgers, two fresh blank review packs, a six-case Word casebook, development lessons and the unchanged RC4 toolkit. The Word casebook is a reading and editing aid for tasks 016–021, with the task request, exact input values, full proposed formal target and review-only questions in separate sections. It is not a completed assessment and does not replace either reviewer's 21-task scorecard.

Generate the cohort-bound kit from a repository checkout or an extracted RC4 toolkit, with the input files supplied separately:

```bash
python scripts/create_l1_c2_complete_review_kit.py \
  --collection /path/to/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json \
  --source-facts /path/to/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json \
  --output-file /path/to/DGSI_C2_21_tasks_COVERAGE_REVIEW_ONLY_20261118.zip
```

PowerShell uses the same existing command and parameters:

```powershell
python scripts/create_l1_c2_complete_review_kit.py `
  --collection 'C:\DGSI\inputs\l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json' `
  --source-facts 'C:\DGSI\inputs\l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json' `
  --output-file 'C:\DGSI\review\DGSI_C2_21_tasks_COVERAGE_REVIEW_ONLY_20261118.zip'
```

Use a destination that does not already exist. The output contains separate reviewer A/B archives and the coordinator's blank source-rights worksheet. Each reviewer archive includes its blank JSON/Word form and the complete scientific dossier. A completed form is accepted only against its exact current cohort and L0 snapshot. Prior 15-task forms are not reusable for the expanded collection. No review materials have been sent to third parties in this continuation.

The packaged quick start retains the prior cohort's worked example. This report supplies the new external input paths without rewriting the already issued RC4 package.

## Verification and remaining work

The [preflight report](../examples/p5c2_coverage_candidate_preflight_2026-11-18.json) records collection validation, blocked model projection, global lineage, actual blank-form intake and rejection of old forms. The final delivery receipt records the reviewed commit, CI runs, portable-package hashes and document verification. These are engineering and curation checks; domain judgment, reviewer authentication and source-use permission remain separate.

The next scientific step is to review the six distinct evidence structures together with the preserved fifteen tasks, resolve actual independent reviewer findings and obtain the required source-use decisions. Broader coverage still requires additional supported source families and reviewed cases; adding paraphrases within these nine families does not establish that breadth.

Development findings are recorded as [lessons 121–126](DEVELOPMENT_EXPERIENCE_C2_COVERAGE_TASKS_20261118.md).
