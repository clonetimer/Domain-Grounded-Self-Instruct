# P5-C: Local canonical scenario-manifest audit (review-only)

**Scientific objective:** detect changed upstream ML findings, logs, spacecraft/mission context, as-of cutoff or historical retrieval snapshot silently reused under a five-arm comparison unit. This is an optional **offline independent consistency check** over submitted experiment inputs; it is not a source authentication service or data-admission workflow.

## Usage

Run in an authorized local environment, with protected files that are **not checked into this repository**:

```bash
python scripts/audit_sota_scenario_manifest.py \
  --trials /private/trials.json \
  --manifest /private/canonical_scenarios.json \
  --output /private/sota_scenario_audit.json
```

This command reads but does not overwrite trial or manifest inputs, rejects duplicate JSON keys and existing output, emits fixed error text without echoing source paths/content, and writes only non-identifying aggregate booleans/counts. It performs no model calls, network access, training or data promotion.

## Manifest contract

Root: `schema_version="dgsi-sota-local-scenario-manifest.v1"` and `scenarios=[...]`.

Each scenario entry must have `comparison_unit_id`, `source_group`, `event_family`, `track`, `requested_task_type` and `shared_input`. The shared input must contain:

- `upstream_ml_result` (object, including score semantics if provided upstream)
- `diagnostic_logs` (array of permissible summarized logs or an empty array if none)
- `spacecraft_mission_context` (object)
- `analysis_cutoff` (timezone-aware ISO-8601 string, no guessed times)
- `historical_context` (array; only independently as-of-admitted items should appear)
- `provenance` (object; literature-derived synthetic inputs require `synthetic=true` and nonempty `source_refs`; REAL_GOLD requires `synthetic=false`, but this local claim never authenticates Gold)

Recursively reject `raw_telemetry`, `internal_review`, `expert_identity`, `expert_signature`, `reviewer_identity`, `curator_prompt(s)`, `formal_target` and `assistant_target` at any depth in the shared scenario, including nested log entries and lists. Key matching also rejects case/hyphen/space variants. Overly deep or oversized structures fail closed. This is still a **key-name guard, not a PII scanner or scientific authenticity check**; source owners must apply existing Case/L1 validation, privacy, historical as-of, and usage gates before preparing the private manifest.

The SHA-256 is computed over canonical compact UTF-8 JSON with sorted keys and Unicode preserved, covering `source_group`, `event_family`, `track`, `requested_task_type` and `shared_input`. The opaque `comparison_unit_id` is deliberately not part of the hashed content. Method-specific instruction strings, outputs, expert ratings and post-cutoff information must not be inserted into the shared input. Bind each trial's `canonical_scenario_sha256` to this digest. Every unit must appear exactly once in the manifest; every attempted trial must match a manifest unit, its metadata and digest.

## What a PASS means

The local bytes and submitted SHA values match under the declared canonicalization. If all five arms are structurally paired, the scorecard can report `MATCHED_UNREVIEWED` or `REVIEWED_COMPARABLE_INPUT`, still with their existing review limitations.

A PASS **does not** establish literature fidelity, rights/IP permission, external ML/log authenticity, chronology of historical case availability, real expert identity/independence, independent holdout, fairness of actual model inference, or downstream SFT effectiveness. Those independent gates stay blocked. The audit reports `source_rights_verified=false`, `historical_as_of_verified=false`, `gold_authorized=false`, `training_authorized=false`, `downstream_sft_result=NOT_RUN` unconditionally.

## Development record

Earlier #163 paired `comparison_unit_id`, and #164 paired a self-declared hash, but neither recomputed a digest from a concrete input payload. This separate tool adds a local check of the shared diagnostic scenario bytes and metadata without exposing content publicly. Ten SYNTHETIC_TEST_ONLY adversarial unit tests cover changed ML results/history/cutoff, missing and repeated units, attribution drift, provenance and privacy rejection, noncanonical floats and no raw data disclosure.

**Dependency:** Draft #164; keep Draft and require exact-head Ubuntu/Windows CI. Do not merge without authorization. No original L0/L1 changes.

## 2026-11-19 nested-content regression

The original root-only forbidden-key check allowed raw telemetry, curator-only review content and leaked reference answers inside nested upstream ML records, diagnostic-log entries or mission-context arrays. Such inputs can contaminate five-arm fairness even when their hashes match perfectly. The new recursive guard rejects these fields without changing canonical hashing of valid scenarios. Added synthetic-only nested/privacy, answer-label, valid nested data and depth-limit regression tests. No source content is included in public CI.

## 2026-11-19 root-envelope regression

A hash covering only the six specified scenario fields could previously omit an
unvalidated *sibling* at the scenario root (for example, a reference answer or
method-specific instruction), and the top-level manifest wrapper was not
checked for review-only payloads. Five-arm consumers might inadvertently read
such unbound fields despite a matching digest. Scenario entries now require
exactly the six declared root fields, and the manifest wrapper requires
exactly `schema_version` and `scenarios`. The recursive prohibited-key scan
runs over the entire scenario entry and manifest wrapper, rather than only
`shared_input`. Explicit answer/review keys and mixed whitespace/hyphen
separators are rejected. Four SYNTHETIC_TEST_ONLY adversarial regression tests
cover these boundary cases; clean scenario digests stay unchanged. This remains
a schema/key-level control, not a substitute for independent source or privacy
review. Lesson: every field accessible to a generation arm must be either
included in the canonical pairing digest or rejected before the prompt stage.
