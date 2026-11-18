# P4: global target-family statistics use actual task sources

The global L1 preflight used to report `canonical_target_family_count` from
**all L0 fact cards supplied for validation** when no official or hypothetical
split existed. This overcounted source families not used by a current L1 target.
History/context-only and unused fact cards must not inflate the independent
target event-family count.

The metric now counts only canonical event-family IDs referenced by each
packet's `source_fact_refs`, both with and without hypothetical split checks.

The current public **SYNTHETIC-only** L1 pilot is the regression fixture:
13 supplied L0 cards, 10 total L0 families, 15 L1 packets and **9 current
target event families**. The denominator remains tied to packet sources, not
SFT sample rewrites or unrelated literature cards.

`source_card_count`, `track_task_counts`, `track_family_counts`, review
status and training gate are unchanged. This is purely a read-only statistics
correction; it does not allocate train/validation/test or admit Gold.

Replay:

```bash
python -m unittest tests.test_l1_global_target_family_counts -v
python -m unittest tests.test_l1_global_lineage tests.test_l1_global_case_run_family tests.test_l1_global_run_result_fingerprint -v
```
