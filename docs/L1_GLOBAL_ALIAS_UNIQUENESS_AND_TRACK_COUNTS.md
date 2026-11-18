# P4: unique alias declarations and stratified source-family counts

The cross-collection L1 structural preflight now fails closed if an event-family
alias is declared more than once, even when duplicate assertions use the same
canonical target. Contradictory canonical mappings retain their distinct
`GLOBAL_ALIAS_AMBIGUOUS_CANONICAL` code. An unreviewed or falsely reviewed
alias still cannot prove episode identity or expert authenticity.

The aggregate report includes `track_family_counts` alongside
`track_task_counts`. This counts distinct **canonical current source event
families per track**, not historical Context hits, not distinct diagnoses,
not unique spacecraft and **not real Gold**. Two SYNTHETIC tasks that share a
TROPICS event family count as two tasks but one source family.

The new counters are read-only. They do not merge parallel tracks, authorize
training, assign train/validation/test splits, or change the existing
`review_required` / domain-review gates. Independent expert adjudication of
actual event aliases and source evidence remains a separate prerequisite.

Replay: `python -m unittest tests.test_l1_global_lineage -v` and the
mandatory Ubuntu/Windows full CI on the exact PR head.
