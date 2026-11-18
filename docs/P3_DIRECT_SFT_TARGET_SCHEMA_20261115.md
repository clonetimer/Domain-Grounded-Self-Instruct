# 2026-11-15 — Standalone SFT assistant-target contract (SYNTHETIC tests)

## Scope

The LLM synthesizes upstream ML results, diagnostic logs, spacecraft/mission context, and permitted historical cases; it does not reinterpret raw telemetry. The assistant target must be a structured diagnostic report; arbitrary text is not a valid target for the current v1 export.

## Gap and fix

Before this change, standalone `validate_sft_example` and `audit_sft_lineage` only checked that the assistant content was nonempty. They could accept malformed JSON, appended forged expert opinions, duplicated keys or out-of-schema reports without a Case→SFT binding call.

- Parse exactly one JSON object, rejecting duplicated object keys, nonfinite values, multiple objects and trailing prose.
- Execute the published Case `expected_output` Draft 2020-12 nested report schema: required sections, fault-source-vs-affected structure, evidence and uncertainty sections, permitted dispositions and action priorities.
- Fail with payload-free rejection codes. 12 tests use explicitly **SYNTHETIC** content.
- Adjust one prior lineage test to use a structurally valid synthetic contradictory target; do not weaken the semantic-conflict gate.

A schema-valid report **does not** establish source evidence correctness, independent expert review, Gold status, or permission to train. An authorized, content-bound source Case and reviewer remain necessary. No restricted logs, R21 telemetry, operational records, credentials, paid API, fine-tuning or main merge.
