# L1 synthetic generated-field lineage integrity

## Purpose

Literature-derived scenarios are not authentic spacecraft ML outputs or mission logs. The L1 `synthetic_provenance.generated_fields` list must describe **each major generated input**, not a generic assertion that the packet is synthetic.

## Additional runtime rules

- Each `field_path` is unique. A second entry cannot silently give a conflicting origin for the same synthetic input.
- Only these canonical LLM-input roots are accepted: `case.input.machine_diagnosis`, `case.input.diagnostic_logs`, `case.input.spacecraft_context`, `case.input.operational_context`, and, only if history is retrieved, `case.input.historical_cases`. New paths require a reviewed contract revision rather than permissive default acceptance.
- The four current upstream/context roots are mandatory, and each generated field must cite a declared L0 source fact or a history source reference already admitted by the L1 validator.
- `machine_diagnosis` and `diagnostic_logs` may be source-**constrained**, but cannot claim `DERIVED_FROM_SOURCE_FACT`. Simulated ML scores, log timestamps, run references and findings are synthetic scenario values, not original algorithm/operations records.
- `history_context.retrieval_status=HIT` requires explicit `case.input.historical_cases` generated-field lineage. A `NO_HIT` task must not claim generated history.
- A source-grounded spacecraft/context fact can retain `DERIVED_FROM_SOURCE_FACT`; this is not a blanket prohibition on accurately attributed public facts.

All paths represent complete roots, not an assertion that every nested scalar has its own source proof. Metadata validation does not establish factual correctness of the packet, reviewer identity, license, de-identification, Gold eligibility, or authorization to train.

## Regression and status

`tests/test_l1_synthetic_field_lineage.py` uses **SYNTHETIC_TEST_ONLY** mutations, including a sanity pass for the current 15 review-required literature-derived packets. No new synthetic tasks or real Gold records are created. All training splits remain unassigned.

This is a stacked Draft-only extension of PR #44. Its Ubuntu and Windows CI must both pass on the final head; do not merge without explicit authorization.
