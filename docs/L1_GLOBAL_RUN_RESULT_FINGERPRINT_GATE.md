# P4: immutable upstream-result identity across L1 collections

This additional read-only cross-collection gate prevents an upstream diagnosis
run reference from being reused with a different `case.input.machine_diagnosis`
payload, **even if both tasks belong to the same canonical event family**.

## Why this is necessary

The prior global lineage preflight prevented reusing a run ID across different
source families, but permitted different ML outputs under one run ID when the
family matched. A controlled L1 task variant may change its formal target or
historical Context while reusing an identical upstream result; it may not silently
change the upstream result, algorithm version, finding, score semantics or score
while retaining the same run ID.

The validator calculates a stable SHA-256 of canonical JSON for
`case.input.machine_diagnosis` and compares the digest whenever a
`case.provenance.diagnosis_run_refs[]` identifier is encountered again.
Different run IDs may legitimately have different outputs within one family.

**Fixed blocking code:** `GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT`.

This is a structural identity check, not proof that the ML output, producer,
log or run identifier is authentic. Diagnostic logs and history Context are
not assumed to be intrinsic to a single ML run and are not covered by this
digest. Other source, temporal, split and review gates remain in force.

Replay SYNTHETIC-only cases:

```bash
python -m unittest tests.test_l1_global_run_result_fingerprint -v
python -m unittest tests.test_l1_global_case_run_family tests.test_l1_global_lineage -v
```

Passing is `STRUCTURAL_PREFLIGHT_ONLY` and does **not** authorize Gold,
dataset splitting or fine-tuning. No real data or restricted logs are stored.
