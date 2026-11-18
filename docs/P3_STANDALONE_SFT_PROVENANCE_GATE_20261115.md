# P3 standalone SFT provenance consistency gate — 2026-11-15

## Evidence-derived defect

Standalone `validate_sft_example` checked prompt/target schemas and citations,
but did not check whether exported `provenance.diagnostic_log_refs` and
`provenance.knowledge_passage_ids` matched the evidence identifiers inside
the JSON user packet. A structurally valid export could therefore claim
unprovided logs or omit the logs actually given to the LLM. Its spacecraft
context could also lack the very spacecraft referenced in the input. The
Case→SFT binding gate checked these relationships, but standalone exports
and batch lineage audits did not.

## Change

- Match log IDs against provenance log refs as a multiset (no invented, missing
  or duplicated refs; ordering is immaterial).
- Match input knowledge `passage_id` values against provenance passage refs.
- Require the input `spacecraft_id` in provenance context refs.
- Apply checks in direct SFT validation, and thus in batch lineage audit.
- Preserve established Case→SFT error codes when the same defect is found
  earlier by the direct SFT validator.
- Add SYNTHETIC-only adversarial tests for omissions, forgery, duplicates,
  source-input drift and batch-audit bypass.

## Important limits

This checks *internal consistency*, not independent authenticity. The upstream
diagnosis-run ref, source SHA-256 digests, source authorization, historical
event-family identity, time-of-availability and expert verdict cannot be proven
from an SFT JSON packet alone. The external Case→SFT binding, local source
admission and authorized independent expert review remain mandatory.

No inline raw telemetry, R21 material, restricted logs, credentials or actual
engineering cases are included. These tests never grant Gold status or approve
a training run. This draft PR is stacked on PR #26 and is not merged to main.
