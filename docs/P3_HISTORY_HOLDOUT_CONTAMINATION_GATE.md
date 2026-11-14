# DGSI P3 — history-to-holdout contamination gate (2026-11-15)

Scope: **diagnostic-context SFT only**. LLM inputs consist of upstream ML
diagnosis results, diagnostic logs, mission/spacecraft context, and permitted
historical evidence. Raw telemetry stays with the upstream detector.

This stage extends PR #17's time-safe history screening with a *dataset-level*
audit. If a train case cites a validation/test case as "historical experience",
the holdout target has leaked into a training input even if ordinary case-group
and source-hash de-duplication would pass.

## Structural rules

- The same case ID or incident family cannot appear in multiple splits.
- A case cannot cite itself (including its incident-family identifier) as history.
- A historical reference equal to a known case ID / incident family in another
  split is **blocked**, including train-to-test and test-to-train exposure.
- An external historical reference reused by different splits requires
  **manual holdout review**, not automatic approval. It may be legitimate
  if it was a genuinely pre-existing shared memory with proof of availability
  before *every* relevant analysis cutoff.
- A same-split historical reference is not automatically valid; it still needs
  authenticated provenance, independent review and PR #17 as-of screening.
- Unknown ID aliases, semantically duplicated episodes and other records
  absent from the supplied manifest cannot be inferred by this local audit.

## Safe local usage

Create a manifest **in the authorized local environment only**, for example:

```json
{
  "entries": [
    {"split": "train", "case_path": "C:/restricted/dgsi/case_a.json"},
    {"split": "test", "case_path": "C:/restricted/dgsi/case_b.json"}
  ]
}
```

Run in an environment where `dgsi` is importable:

```powershell
$env:PYTHONPATH = "src"
python scripts/audit_history_split_exposure.py --manifest "C:/restricted/dgsi/split_manifest.json" --output "C:/restricted/dgsi/history_audit_aggregate.json"
```

The CLI reads source packets without modifying them. It prints and optionally
writes aggregate counts, stable reason codes and limitations, **never case
identifiers, source paths, log entries, scores, references or prompt content**.
Output is create-only; existing files must not be replaced. Exit code 0 =
structural pass; 2 = shared-history manual review required; 1 = invalid input
or blocked split contamination. Store the manifest and aggregate result locally
if their existence, paths or counts are restricted.

## Limitations / release decision

Passing this gate does not validate the truth or availability date of an
AstroGraph memory record, authenticate source authority, or certify expert
review. In particular, AstroGraph's current `retrieve_confirmed` result omits
`available_at`; PR #17's time screen must block those entries until an
authorized source attestation supplies verified `available_at` and
`verified_at`. The status of a prior *historical* case never confirms the
current fault source.

All associated examples and tests are explicitly **SYNTHETIC**. No real or
R21 restricted source is committed. No Gold elevation, training authorization,
main-branch merge or paid API call is performed.

Next decision: obtain 5–10 authorized, de-identified packets with upstream
result, logs, context, independent expert verdict and history timelines.
Only after independent case review should a first 20-case supervised pilot
be considered; any 300–500 scale-up is conditional on source quality.
