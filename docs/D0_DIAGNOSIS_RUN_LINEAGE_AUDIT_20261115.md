# D0: declared upstream ML diagnosis-run lineage audit — 2026-11-15

## Product and security boundary

DGSI curates SFT for **second-stage interpretation** of upstream ML fault candidates, diagnostic logs, spacecraft/mission/configuration context, and reviewed historical experience. Raw telemetry is processed upstream and is not the default LLM input.

Earlier declared-file SHA-256 reuse auditing (PR #32) can miss the same upstream ML run after reserialization, redaction, or changes to log/result file bytes. This complementary audit checks pseudonymized **run identifiers** supplied by an authorized custodian, **without** reading Case targets, source logs, expert records, or raw telemetry.

## Input contract

Provide exactly one minimal lineage JSON alongside each handoff manifest, with only the fields extracted from an already validated Case:

~~~json
{"case_id":"PSEUDONYM","source_group":"EVENT-FAMILY-PSEUDONYM","diagnosis_run_refs":["RUN-PSEUDONYM"],"generation_method":null}
~~~

The case_id and source_group must match their manifest counterparts; unknown additional fields, including expected_output, review, expert_target, and telemetry are rejected. The custodian prepares this separately inside the authorized environment; no real examples are committed. These fields **remain unverified declarations** until checked against their authorized original Case and actual ML run record.

Run IDs must be stable pseudonyms and should identify individual upstream ML executions, not model types or a generic pipeline. A repeated ID may also reflect a legitimate intentional replay, which requires manual interpretation. Cross-split reuse is conservatively blocked pending review.

## Local use

~~~bash
PYTHONPATH=src python scripts/audit_handoff_run_lineage.py \
  --pair /authorized/a/manifest.json /authorized/a/lineage.json \
  --pair /authorized/b/manifest.json /authorized/b/lineage.json
~~~

For **already-existing manually assigned** splits, in the same positional order:

~~~bash
PYTHONPATH=src python scripts/audit_handoff_run_lineage.py \
  --pair /authorized/a/manifest.json /authorized/a/lineage.json \
  --pair /authorized/b/manifest.json /authorized/b/lineage.json \
  --existing-split train --existing-split test
~~~

The program reads only explicitly named manifest and minimal-lineage JSON files. It never scans directories, follows references to source data, reads a complete Case/target, uploads files, accesses APIs, automatically assigns train/validation/test, trains models, or creates Gold. Outputs include only counts, fixed error codes and immutable eligibility denials, not case identifiers, run identifiers, paths or hashes. Any incomplete split cohort is rejected rather than silently omitting a split check.

## Gate behavior

- One declared run ID across differing event families: **manual event-family duplicate review**.
- One declared run ID across pre-existing train/validation/test splits: **BLOCKED_RUN_LINEAGE**.
- Same event-family ID across distinct pre-existing splits: **rejected** even if run references differ.
- Synthetic and real-claimed records sharing a declared run ID: **blocked** for potential source laundering.
- A real-claimed record containing a synthetic:// run ID or explicit synthetic generation method: **blocked**.
- Missing references, incomplete source permissions or provenance: **manual review**.
- Fully synthetic clean input: **SYNTHETIC_TEST_ONLY**. A clean real claim: **PASS_UNTRUSTED_RUN_CLAIMS_ONLY**. Neither is training-/Gold-eligible.

This is one **additional** conservative gate alongside Manifest, Case binding, local file digest and diagnosis/log evidence validation. It does not certify the run identity, chronology, source rights, score calibration, authenticity, expert conclusion, or split independence under changed aliases. In particular it cannot detect similar but genuinely distinct ML runs evaluating the same event without additional manually verified event-family evidence. Do not rely on this result as a substitute for expert review.

## Test and data limitation

All unit/CLI fixtures are explicitly **SYNTHETIC**, including simulated records that claim a real source class for adversarial testing. No R21 raw telemetry, operational logs, restricted cases, credentials or model targets were added. Independent Gold review remains at zero verified examples in publicly reviewable source material.

Proceed to 5–10 properly authorized and de-identified real episodes only after provenance, permission, algorithm/version and score semantics, diagnosis logs, mission/configuration, temporal validity, historical availability and independent expert decisions are verified. Curate ~20 high-quality examples before proposing a 300–500 sample controlled SFT pilot.
