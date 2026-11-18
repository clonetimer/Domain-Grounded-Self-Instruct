# P4 L1 historical/current source isolation (SYNTHETIC-only)

## Defect and protection

Prior L1 synthetic field-lineage validation accepted `source_fact_refs` from the **union** of current-event sources and retrieved-history sources for every generated input root. Consequently, a historical Cassini source could be labeled as the provenance of a current FUSE upstream-ML finding, log, spacecraft configuration or operating mode, even when the current-event source did not contain that fact.

The L1 runtime gate now applies two complementary boundaries:

1. `case.input.machine_diagnosis`, `diagnostic_logs`, `spacecraft_context` and `operational_context` can cite **only the current task's `source_fact_refs`**. They can still be explicitly generated scenario inputs, but retrieved-history records cannot serve as a second provenance channel for the current incident.
2. When `history_context.retrieval_status=HIT`, `case.input.historical_cases` provenance must cite **at least one declared `history_context.items[].source_refs`**. The historical field may also cite a current source for comparison, provided a genuine history-source binding is present. A `SYNTHETIC-*` history ref remains a synthetic fixture, not evidence of a real historical case.

Other controls remain unchanged: analysis-cutoff timing, hardware compatibility, unconfirmed/rejected memory statuses, event-family isolation, source-review requirements, and explicit separation of REAL_GOLD_TRACK from LITERATURE_DERIVED_SYNTHETIC_TRACK.

## Fixture correction and tests

Two TROPICS SYNTHETIC-only rejected-history input declarations previously cited the *current* TROPICS incident card. They now cite their already-declared `SYNTHETIC-HISTORY-REVIEW-REF-001`, without changing the formal diagnostic target, curator notes or invented source content.

`tests/test_l1_history_field_source_isolation.py` supplies nine cases, including preservation of the existing 15-packet collection, FUSE↔Cassini cross-incident source laundering, TROPICS synthetic prior source attribution, and the allowed comparative historical provenance case. These are **test fixtures only**, not genuine on-orbit ML executions or ground/flight logs.

## Admission and reporting

Passing the guard proves only referential consistency of a declared synthetic generation recipe. It does not establish factual origin, independent domain review, licensure, reviewer identity, calibration, de-identification or training rights. All 15 packets remain `REVIEW_REQUIRED` and training-unauthorized. No Gold promotion, train/validation/test allocation or model training occurs in this change.
