# P4 — Per-hit historical provenance coverage (SYNTHETIC-only)

## Defect

The L1 provenance validator previously accepted `case.input.historical_cases` whenever the generated-field declaration cited **any one** source among retrieved history hits. With two or more hits, a packet could present one cited historical source while silently omitting provenance for the other history item. A current-incident L0 source plus one prior source could also mask an uncited second prior.

This is a referential-integrity defect, **not** proof that any history content is true or false.

## Runtime rule

For `LITERATURE_DERIVED_SYNTHETIC` packets with `history_context.retrieval_status=HIT`:

- Keep the existing rule: the synthetic historical-input field must cite a source declared by a retrieved hit.
- Also require **each individual** `history_context.items[]` entry to have at least one `source_refs[]` identifier present in the historical input's generated-field `source_fact_refs[]`.
- Keep the existing permission to cite a current-event source as contextual comparison **in addition** to all historical sources; a current source never substitutes for an unreferenced history hit.
- Explicitly synthetic prior sources retain their SYNTHETIC label. This gate does not convert REJECTED, PARTIALLY_CONFIRMED or UNRESOLVED history into confirmed evidence.

The check is deterministic and metadata-only, reports only `SYNTHETIC_HISTORY_HIT_SOURCE_COVERAGE_INCOMPLETE`, and does not read or export restricted logs. It is compatible with the 15-packet pilot and validates new multi-hit fixtures.

## Regression and admission limits

`tests/test_l1_history_hit_provenance_coverage.py` uses a synthetic second rejected-history fixture; it covers missing source one/two, attempted current-source substitution, and valid complete coverage. It does not alter the source-fact cards, historical episodes, formal answers, or initial 15 task packets.

Passing this check **does not** prove semantic source support, independent reviewer identity, real ML provenance, IP permission, case authenticity, or Gold eligibility. No train/validation/test split is assigned, no training is authorized, and all pilot tasks remain `REVIEW_REQUIRED`.

The REAL_GOLD_TRACK remains independently gated by authorized primary ML results, logs, mission context, and expert review.
