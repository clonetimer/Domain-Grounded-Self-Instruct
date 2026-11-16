# P4: immutable current-evidence snapshot for reused L1 Case IDs

## Risk and scope

Before this gate, the global collection audit rejected the same Case ID when bound
to different event families, but accepted two tasks with the same Case ID and
different current inputs or upstream diagnostic run references **within** one
family. A task variant could silently change a diagnostic log, ML result,
analysis cutoff or spacecraft configuration without changing Case identity.

`GLOBAL_CASE_ID_EVIDENCE_SNAPSHOT_CONFLICT` now rejects such cases before
any official or hypothetical train/validation/test split. The snapshot is
SHA-256 of the Case's current diagnostic input fields (excluding
`historical_cases`) plus a sorted set of `diagnosis_run_refs`, keyed by Case
ID. The audit compares digests only and never returns them or source content.

Task-specific `formal_target` and historical retrieval Context are omitted
from this **current-event** snapshot deliberately: an identical input event
may support several supervised tasks or as-of-eligible Context variants.
This does **not** claim that unreviewed Context is valid or permit historical
causes to establish a current root cause. Existing per-task, per-history-hit,
and as-of validators remain mandatory.

A changed upstream ML result with the same run reference is independently
blocked by `GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT`. This new gate also catches
a changed run reference, log, analysis cutoff or spacecraft configuration
under a reused Case ID when individual run IDs themselves differ.

## Synthetic-only regression

```bash
PYTHONPATH=src python -m unittest tests.test_l1_global_case_run_family -v
PYTHONPATH=src python -m unittest tests.test_l1_global_run_result_fingerprint -v
```

All adversarial modifications use invented L1 literature-derived synthetic
packets; no actual telemetry, operations logs or real ML runs are accessed.
The global audit remains `STRUCTURAL_PREFLIGHT_ONLY`,
`gold_eligible_count=0`, `training_authorized=false`. It is still a
read-only preflight rather than a mandatory SFT release/export operation:
there is no production L1-to-SFT exporter in the current branch, so this
commit does not misrepresent export enforcement as completed.

Independent literature review, authorized REAL Gold admission, dual-blind
L1 review and dataset approval remain separate prerequisites.
