# P5-C2 whole-collection model-projection preflight

Status: **BLOCKED_PENDING_EXTERNAL_ADMISSION**. Only LITERATURE_DERIVED_SYNTHETIC candidate packets; never REAL Gold.

Per-packet model projection integrity checks do not establish collection membership or the absence of duplicate task IDs. This read-only preflight validates the existing L1 collection contract and each of its candidate user/assistant projections, then hashes a canonical manifest binding the collection ID, task IDs, case IDs, L0 source refs, event-family source groups, and both projection digests.

The report exposes only aggregate counts, a SHA-256 manifest fingerprint and constant blocked statuses. It cannot serialize user inputs, targets, history context, internal reviewer notes, source text or training rows. Packet ordering does not change the fingerprint; changed task membership, source bindings or model-facing content does.

The routine explicitly refuses any official split assignment and REAL-track inputs, even where another preflight might structurally accept them. Internal review remains Case-root `not_for_sft=true` and is not used in model projection. The existing 15 SYNTHETIC L1 packets remain REVIEW_REQUIRED and 9 event families are not 15 independent events.

This is **not** a rights/IP/privacy assessment, domain expert decision, source-fact validation, Gold promotion, or permission to train. Source-use rights, dual independent expert review, AstroGraph run integrity, actual REAL evidence, event-family split independence and controlled evaluation remain open gates.

## Regression evidence

Eight `SYNTHETIC_TEST_ONLY` tests cover current collection metadata, order-invariant canonical digest, model input change, curator note isolation, duplicate task identities, nested curator contamination, premature split/REAL track, and missing L0 source closure. Required Ubuntu and Windows CI must pass at the exact PR head before this is staged.
