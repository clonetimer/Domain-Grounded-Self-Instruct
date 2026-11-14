# Case-to-SFT binding gate (synthetic development only)

## Why this is necessary

Valid Case JSON and valid SFT JSON can still disagree. An exported SFT user
message may silently alter an upstream ML screening score, omit a diagnostic
log, change spacecraft operating mode, or introduce an independently edited
assistant target. In that situation each schema can pass while the training
sample no longer reflects the reviewed source.

This small gate **does not generate SFT training data**. It checks an already
assembled pair using exact source correspondence. The input is the upstream
diagnosis/result **summary**, logs, spacecraft/mission context, history and
evidence; raw telemetry remains processed by upstream ML, not by the LLM.

## Read-only local check

```bash
python -m pip install -r requirements-validation.txt
PYTHONPATH=src python scripts/verify_diagnostic_case_sft_binding.py \
  --case examples/diagnostic_context_case_illustrative.json \
  --sft examples/diagnostic_context_sft_illustrative.json
```

Expected decision for the illustrative fixture is `PASS_BINDING_ONLY`,
with `gold_eligible=false`. Never treat that result as expert approval.

The strict preflight requires:
- Each Case and SFT object to pass its current semantic and JSON Schema gates.
- Identical case ID, task type, and physical incident family (`source_group`).
- One trailing JSON case packet in the SFT user message with **exactly** the
  keys `case_id`, `task_type`, `instruction`, `input`; the entire input must
  match the source Case, including ML scores and their uncalibrated semantics,
  logs, mission/configuration, history and cutoff.
- The entire assistant JSON target to equal the source Case
  `expected_output`. A corrected target requires a new reviewed Case
  version rather than quiet SFT-only editing.
- Exact multiset correspondence for upstream diagnosis run references,
  diagnostic log IDs, knowledge passages and source artifact hashes.
- A spacecraft context ID present in the SFT metadata.
- No ambiguous duplicate JSON object keys, NaN/Infinity, or unparsed suffix.
- An SFT claiming `APPROVED` cannot be bound to an unapproved source Case;
  known synthetic/illustrative cases cannot be approved.

Errors are stable, payload-free codes. The CLI never prints paths, case IDs,
input logs, answers, source hashes or operational data. Run restricted checks
*only* in an authorized local environment; do not submit their source or
individual results to the public repository.

## Limits and review gate

An exact match can still reproduce a poor or unauthorized source Case. This
gate **cannot** verify truth, privacy permission, algorithm score calibration,
expert independence, source-log authenticity, near-duplicate event families,
causal correctness or whether narrative text *outside* JSON contains semantic
answer contamination. Existing lineage auditing remains mandatory, and Gold
still requires real case-source checks and independent expert sign-off.

The shipped fixture and all unit tests are **SYNTHETIC/ILLUSTRATIVE** only.
Neither a passing test nor a passing binding check may be counted toward
5–10 real expert-reviewed cases, 20 quality SFT samples or the later
300–500 controlled pilot. No model training or main merge is authorized.
