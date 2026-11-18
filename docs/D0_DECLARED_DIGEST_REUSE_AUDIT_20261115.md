# D0 handoff declared-source reuse audit — 2026-11-15

## Rationale and product boundary

DGSI trains second-stage **interpretation of upstream ML diagnosis results,
diagnostic logs, mission/configuration context, and historical experience**.
Raw telemetry remains upstream. In a controlled real-case handoff, a case owner
could unknowingly provide the same upstream diagnosis/log file under two
different incident-family pseudonyms. Later, assigning those apparent
"independent" cases to train and test would leak the source event.

PR #31's local byte verifier compares files with SHA-256 claims in a *single*
manifest. This stage checks **claims across manifests** without opening the
actual source files. It does not supersede authenticated source review.

## CLI (authorized local metadata only)

```bash
PYTHONPATH=src python scripts/audit_handoff_digest_reuse.py \
  /authorized/case_a/case_manifest.json \
  /authorized/case_b/case_manifest.json
```

To examine **already-existing** manual split labels (in manifest positional
order), add the same number of flags:

```bash
PYTHONPATH=src python scripts/audit_handoff_digest_reuse.py \
  --existing-split train --existing-split test \
  /authorized/case_a/case_manifest.json \
  /authorized/case_b/case_manifest.json
```

The script reads only explicitly named manifests. It never scans folders,
opens input files or private expert targets, creates dataset split labels, writes
a sample, invokes a model or contacts a network service. Results contain only
aggregated counts, fixed error codes and immutable eligibility denials, without
case IDs, event identifiers, source paths or hash values.

The stage compares the **declared** SHA-256 values for
`diagnosis_result.json`, `diagnostic_logs.jsonl` and
`diagnostic_logs.csv`. Generic spacecraft context and knowledge passages
are intentionally excluded as evidence of an event's identity.

## Policy

- A declared event-source digest reused across differing incident families
  triggers manual incident-family deduplication.
- Reuse across preassigned train/validation/test splits blocks the cohort,
  even if the event-family aliases differ. Repeated family IDs across splits
  also fail.
- Reuse between synthetic and real-claimed records blocks potential fixture
  laundering.
- Missing event-source digests or incomplete handoff metadata requires manual
  review. A digest string from a manifest is an *unverified assertion*.
- Fully synthetic cohorts remain SYNTHETIC_TEST_ONLY, even without detected
  overlaps. Passing a real-claimed cohort is only
  PASS_UNTRUSTED_DECLARATIONS_ONLY; never Gold/eligible for training.
- A mixed cohort with some assigned splits and some unassigned ones fails
  closed rather than silently skipping cross-split checks.
- Different bytes do not prove independent episodes: time shifting, redaction,
  recomputation, file serialization and aliases can hide shared incidents.
  Likewise a common log/header could yield a benign duplicate. Investigate
  these in authorized environments before manual split decisions.

## Evidence and limits

All added tests are SYNTHETIC: they include fabricated digests, incident IDs
and source classes, not actual engineering logs or R21 telemetry. The stage
makes no inference about fault correctness, expert truth, IP permission, model
score calibration or the authenticity of a claimed ML run. It makes no training
or Gold decision.

For real cases, a custodian must first independently establish source rights,
algorithm/run identity, score meanings, redaction and temporal provenance,
verify local bytes where permitted, and obtain independent expert review.
Start with 5–10 authorized reviewed episodes, then curate up to 20 examples;
300–500 controlled pilot examples require sufficient independent sources.
