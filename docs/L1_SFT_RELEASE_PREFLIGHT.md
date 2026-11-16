# P4: Fail-closed L1 to SFT release boundary

This PR adds a **read-only release preflight**, not an SFT exporter. No current L1
task is admitted for model training, and a public GitHub PR or test result is
not an authoritative source/license/privacy/independent-review approval.

## Existing checks reused

- `audit_l1_cross_collection_lineage` must validate the **full cohort**:
  immutable source facts and Case/run evidence, canonical event-family/split
  grouping, source track statistics and historical Context isolation.
- When supplied, every collection's reviewer receipt batch is validated by
  `audit_l1_review_receipt_batch`. An incomplete/unknown batch is rejected or
  counted as missing; receipt validation is *only* content binding.
- Hypothetical split plans are deliberately absent from this release API;
  they are permitted solely in adversarial evaluation.
- Official splits, L1 expert review, reviewer authentication and source
  authorization remain separate. Claiming `APPROVED_FOR_L1_EXPERIMENT` in an
  unsigned JSON object never grants training rights.

## Public interface

```python
from dgsi.l1_sft_release import (
    preflight_l1_sft_release, require_l1_sft_release
)

report = preflight_l1_sft_release([
    {"collection": collection, "source_fact_cards": l0_cards},
])
assert report["decision"] == "BLOCKED_PENDING_EXTERNAL_ADMISSION"

# A future SFT serializer MUST invoke this release guard first.
# It currently always fails closed until a trusted admission authority exists:
require_l1_sft_release([
    {"collection": collection, "source_fact_cards": l0_cards},
])
```

The report returns only aggregated counts and fixed blocking codes. It does
not contain user prompts, assistant targets, internal curator content, task
IDs, local paths, source text, reviewer identities or artifact hashes.

## Acceptance and remaining blocker

Run `PYTHONPATH=src python -m unittest tests/test_l1_sft_release.py -v`
and the full Windows/Ubuntu CI suite. Test fixtures are SYNTHETIC_TEST_ONLY.

**No actual SFT serialization occurs.** To unlock a future production
serializer, design and test an external, authenticated admission authority
that proves usable rights, de-identification, independent expert decisions,
frozen packet/source fingerprints, approved event-family splits, and an
explicit training/export authorization. Receipt binding and structural PASS
alone must never bypass these checks.

As of 2026-11-16: 15 synthetic L1 tasks, 9 target event families, zero real
Gold, zero formal splits, zero training approvals. This gate does not promote
synthetic cases into true flight/ML/expert observations.
