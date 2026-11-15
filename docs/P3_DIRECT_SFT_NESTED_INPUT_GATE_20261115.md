# 2026-11-15 — Direct SFT nested-input contract gate (SYNTHETIC tests)

Product scope: a second-stage LLM interprets upstream ML findings, diagnostic logs, spacecraft/mission context and historical experience. Raw telemetry remains upstream and cannot enter the SFT user message.

## Verified gap

The reviewed system/user templates and JSON packet parser of PR #22 check the envelope and outer four keys, but they did **not** execute the published Case **input** schema on standalone SFT records. Consequently, direct SFT validation or lineage audit could accept structurally plausible but invalid nested ML results, logs, or spacecraft context without a source Case binding.

## Scoped implementation

- Reuse `resources/diagnostic_case.schema.json#/properties/input` with JSON Schema Draft 2020-12 and a date-time format checker on standalone SFT input.
- Require explicit `raw_telemetry_included: false`; reject unsupported nested keys, invalid enums, missing source method/context and malformed date-times.
- Include twelve tests that are strictly **SYNTHETIC** and exercise both direct validation and batch audit paths.
- Never serialize input content or a case identifier in a validation error.

This is a **structural** gate. It does not verify log-to-cutoff ordering, score meaning, upstream causal correctness, real source/IP authorization, independent expert judgement, Case→SFT source binding, or Gold eligibility. Those are separate mandatory checks.

No restricted engineering records, R21 telemetry, private reports, model API usage, fine-tuning or main-branch merge.
