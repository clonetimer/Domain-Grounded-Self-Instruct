# P5-C2 conflict and justified-abstention candidate design

## Intent

Continue the user's authorized data-production mainline after PR148: improve the spacecraft diagnostic SFT candidate corpus using upstream ML summaries, diagnostic logs, configuration, mission context and bounded historical knowledge. Raw telemetry remains upstream. Record reusable development lessons and deliver one integrated batch.

## Approach and decisions

Reuse the corrected L0 snapshot and the existing RC4 runtime to append six deliberately different evidence structures to the corrected 15-task cohort. Adding unrelated publications would increase research and admission scope; merely renaming existing packets would not fill the demonstrated gaps. This batch instead uses two conflict-reconciliation variants and four evidence-sufficiency variants with a specific unsupported claim that must be withheld.

This is an implementation choice under the user's standing request to continue without repeated design approvals. It is not a claim that a human expert approved the new scientific content.

| New suffix | Source family | Distinct evidence structure | Required response boundary |
|---|---|---|---|
| 016 | Lunar Orbiter III TWTA | Same-window monitor indication versus independently checked received carrier summary | Reconcile scopes; do not equate one monitor indication with confirmed carrier loss or a uniquely failed diode. |
| 017 | TROPICS ground qualification | Same synthetic unit passes and fails under different environmental conditions | Preserve both observations; reject all-condition normality inferred from a local PASS; do not call the two condition-dependent observations logically impossible. |
| 018 | Lunar Orbiter III TWTA | Elapsed time and thermal cycling co-vary across synthetic startup summaries | Preserve the trend while withholding a unique causal attribution. |
| 019 | S-band TWTA ground test | Whole-unit power loss without module isolation, gas or EMMI results | Acknowledge the supported abnormality; withhold LNA hydrogen-mechanism confirmation. |
| 020 | FUSE reaction wheel | Executed restart and short downward drag trend without a healthy baseline or adequate follow-up | Record the attempt and observed trend; withhold both proven recovery and an unsupported persistent-fault declaration. |
| 021 | Cassini reaction wheel | Upstream DATA_QUALITY_ERROR with a wheel/window binding mismatch | Diagnose the input-quality limitation; infer neither current wheel health nor current hardware failure. |

## Constraints

- Keep the old corrected 15 packet objects canonical-identical and the corrected L0 file byte-identical. New packet, case and diagnosis-run identifiers are unique.
- Preserve the nine source event families; six variants are not six independent incidents. Keep the current twelve bound cards and seven primary source ID groups.
- Mark all new ML outputs, scores, logs, timestamps, configurations and current cross-check results as synthetic. Actual source passages constrain plausibility; they are not current-event observations.
- Reuse exact reviewed instruction templates. The existing projection includes task_type, so existing conflict/evidence-sufficiency types can carry the new task purposes without a new runtime version.
- Every formal target equals case.expected_output, uses model-visible inputs, and excludes historical/context identifiers from direct current-fault support.
- A dedicated correct-abstention task is evidence_sufficiency with an explicit unsupported claim, supported residual conclusion, and concrete evidence required to reconsider it. It is a coverage dimension, not a new schema task_type.
- All scientific review, rights, Gold, official split and training admission remain pending/false. No SFT rows or training runs are produced.
- Preserve prior delivered forms as historical artifacts. A new 21-task cohort requires newly bound A/B forms for all rows.

## Deliverable and acceptance

Deliver the complete 21-task candidate, an addition/source ledger, actual coverage, preflight, fresh A/B kit, a readable Word casebook for the six additions, and development lessons. Reuse the unchanged RC4 ZIP in the integrated delivery. Verify current source/packet binding, old-form rejection, final Word rendering, isolated runtime execution, and exact-head PR CI before merging into main.
