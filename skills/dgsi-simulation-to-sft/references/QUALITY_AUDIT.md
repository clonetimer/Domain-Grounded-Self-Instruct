# Quality audit and acceptance rubric

## Automatic checks

1. JSON schema validity against the pinned schema version.
2. Every source/evidence reference resolves to a supplied artifact and exact locator.
3. Every ML/log/context reference belongs to the current case, not a historical case or hidden QA file.
4. All model-visible records are available by `analysis_cutoff`.
5. No injected fault ID/mode/time, QA truth, hidden target or split label appears in the prompt.
6. No post-event teardown, repair or retrospective adjudication appears in the prompt unless available by cutoff.
7. Fault-source component and affected components are separately represented.
8. Source certainty and ML score semantics are preserved.
9. Disposal status distinguishes executed, planned, recommended, conditional and not recorded.
10. Historical Context has event-family provenance, outcome status, as-of time and hardware applicability.
11. Case expected output exactly matches the L1 formal target where the L1 schema requires it.
12. All task variants from one event family remain grouped.
13. Duplicate and near-duplicate inputs/targets are identified.
14. Synthetic fields have field-level provenance and explicit assumptions.
15. Private information, credentials, restricted telemetry and unauthorized copyrighted content are absent.

## Human review rubric

Score each dimension 0–2:
- factual fidelity to source/run;
- phenomenon versus root-cause separation;
- fault-source localization;
- affected-component identification;
- evidence relevance and traceability;
- physical mechanism plausibility and model-scope consistency;
- uncertainty and abstention;
- ML score interpretation;
- temporal integrity and truth separation;
- historical experience applicability;
- disposal/action fidelity;
- usefulness/actionability of the report.

A critical failure overrides the numeric score:
- fabricated source, measurement, log or event;
- hidden fault truth leaked into model input;
- definitive unsupported root cause;
- affected component mislabeled as root-cause source;
- design assumption represented as observed run/flight fact;
- injected fault treated as validated physical effect without evidence;
- unresolved/likely mechanism promoted to confirmed;
- repair or action claimed as executed when only recommended/planned;
- unauthorized private data disclosure.

## Recommended decision labels

- `REJECTED`: fabricated, contradictory or materially unsupported.
- `INCOMPLETE_EVIDENCE`: potentially useful, but critical inputs are missing.
- `REVIEW_REQUIRED`: plausible candidate awaiting independent human review.
- `HUMAN_REVIEWED_CANDIDATE`: reviewed and corrected, but not yet authorized as Gold/SFT.
- `GOLD_ADMISSION_PENDING`: all technical checks complete; external rights/privacy/expert/training admission still pending.

Do not invent a numeric quality pass threshold before a reviewer calibration exercise. Report critical failures separately from averages.

## Candidate batch acceptance

Before declaring a batch ready for human review:
- 100% schema-valid or explicitly quarantined;
- zero unresolved evidence references;
- zero known truth/time leakage;
- zero fabricated factual claims;
- all synthetic assumptions labeled;
- all source groups and event families assigned;
- all duplicates grouped;
- all cases have explicit review state.

This means `REVIEW_QUEUE_READY`, not training-ready.
