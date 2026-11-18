# P5-C2 review-only source identity guard (2026-11-18)

## Scientific risk

The same L0 case can be referenced by several literature-derived synthetic L1 tasks. Matching `public_fact_sha256` alone is insufficient for source-rights deduplication if a downstream dossier is modified: the same fact identifier/digest could be attributed to a different source publication, event family, source class or source locator on another task. This would misstate the number of independently reviewed publications or episodes.

## Change

In `build_c2_source_rights_queue`, keep an immutable identity tuple for each reused L0 `case_id` across the entire collection: `(public_fact_sha256, source_id, source_title, source_url, event_family_id, source_class, source_locator)`. Reject a changed digest with `C2_RIGHTS_L0_FINGERPRINT_DRIFT`, and unchanged digest with changed identity with `C2_RIGHTS_L0_IDENTITY_DRIFT`. Validate the required event-family/source-class strings and optional locator type. The checks are in addition to the document-level source-ID collision gate.

Four `SYNTHETIC_TEST_ONLY` regression tests tamper with the second occurrence of a repeated L0 source, altering document identity, event family, locator or source class without changing its bound SHA.

## Boundaries

This is a structural protection for untrusted dossier inputs, **not** authentication of a publication, a legal rights grant, verification of a source fact or expert sign-off. No case content, L0/L1 fingerprints, Gold, official splits or SFT records are modified. `training_authorized=false` remains mandatory. CI should run on the exact PR head in Ubuntu and Windows; do not merge this draft PR automatically.
