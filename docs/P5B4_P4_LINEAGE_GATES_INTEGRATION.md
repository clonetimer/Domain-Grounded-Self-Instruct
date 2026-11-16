# P5-B4 integration: restore P4 Case/run lineage gates

Date: 2026-11-17  
Status: DRAFT / CI AND INTEGRATION REVIEW REQUIRED

## Scope and evidence

The P5 ingestion/OCR/diagram stack culminating in PR #92 branched through the
document-ingestion line. Its `src/dgsi/l1_global_lineage.py` lacked the P4
guards introduced independently by PR #64, PR #65 and PR #69. All three PRs can
pass CI separately while the P5 branch remains without these checks. Therefore
a green check on any one stacked PR is **not** a combined-security acceptance.

This integration PR carries the exact reviewed code from PR #69's lineage
module into the P5 branch and ports 15 SYNTHETIC_TEST_ONLY regression tests.
The P5 base and P4 gated versions differ only by these guards and the generic
`_digest(Any)` typing change. No source data, user documents or private logs
are copied.

## Required invariant

Before SFT or L1 release consideration, one run reference cannot change:
- its upstream ML result (`GLOBAL_DIAGNOSIS_RUN_RESULT_CONFLICT`, existing);
- its diagnostic-log snapshot (`GLOBAL_DIAGNOSIS_RUN_LOG_SNAPSHOT_CONFLICT`);
- its spacecraft/mission configuration snapshot
  (`GLOBAL_DIAGNOSIS_RUN_CONTEXT_SNAPSHOT_CONFLICT`);
- its real vs literature-derived synthetic track
  (`GLOBAL_DIAGNOSIS_RUN_CROSSES_TRACKS`).

One Case ID cannot cross the real/synthetic tracks
(`GLOBAL_CASE_ID_CROSSES_TRACKS`). The gates remain metadata-only; source
rights, authenticity, reviewer identity, and training authorization require
external approval. Historical Context remains excluded from run fingerprints,
and raw telemetry is not an LLM default input.

## Verification

```sh
PYTHONPATH=src python -m unittest tests.test_l1_global_run_log_snapshot \
  tests.test_l1_global_run_context_snapshot \
  tests.test_l1_global_track_identity -v
PYTHONPATH=src python -m unittest discover -s tests -v
```

Require both `validate (ubuntu-latest)` and `validate (windows-latest)`
SUCCESS for this PR's exact current head. Also review stacked sibling bases,
notably PR #89/#91 and previously recorded #10/#36/#79/#81/#83, separately.

This PR does not merge the original sibling PRs, change any official split,
promote a case to Gold, grant training rights, or run fine-tuning.
