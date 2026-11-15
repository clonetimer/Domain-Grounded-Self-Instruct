# P4: cross-collection Case and diagnosis-run identity collisions

The global read-only L1 preflight now checks that each `case.case_id`
and each declared `case.provenance.diagnosis_run_refs[]` identifies
the same canonical source event-family set everywhere it occurs, including
across different collections. Event-family aliases already supplied to the
existing preflight are resolved before this check.

The new fixed errors are:

- `GLOBAL_CASE_ID_FAMILY_COLLISION`: the same Case identifier is used for
  different current-source event families.
- `GLOBAL_DIAGNOSIS_RUN_FAMILY_COLLISION`: the same upstream-run reference
  appears against incompatible current-source event families.

Reusing a Case or run reference for controlled task variants **within the
same canonical event family** is permitted. This gate does not infer that
different identifiers are independent runs, nor authenticate synthetic
identifiers, actual mission logs, reviewer declarations or event-family
alias assertions. A successful preflight remains `STRUCTURAL_PREFLIGHT_ONLY`,
with no Gold or training authorization and no official split assignment.

Replay (SYNTHETIC_TEST_ONLY):

```bash
python -m unittest tests.test_l1_global_case_run_family -v
python -m unittest tests.test_l1_global_lineage tests.test_l1_global_lineage_cli -v
```

No actual engineering source record is accessed or uploaded.
