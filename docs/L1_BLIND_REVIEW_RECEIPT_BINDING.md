# P4 L1 immutable blind-review receipt binding (v0.1)

**Status: development-only.** This adds an integrity sidecar to the existing **ten-dimension / two-independent-reviewer** workflow from PR #42. It is **not a second rubric**, does not authenticate reviewers, does not attest licensing or source truth, does not authorize training or Gold, and does not assign dataset splits.

## Threat model and integrity boundary

A detached scorecard without a cryptographic packet binding can be copied to another task or reused after the target or L0 facts change. A scorecard may also declare two ACCEPT_L1 votes while retaining a substantive fault/evidence/disposal defect code. These are rejected or routed to secure adjudication rather than promoted.

- The fingerprint_l1_review_material function first runs the actual L1 validator, then SHA-256 hashes stable UTF-8 canonical JSON (sorted keys, compact separators, no NaN) over **task ID, track, source refs, full reviewable Case minus curator-only internal_review and mutable Case review, formal target, history Context and synthetic provenance**.
- A second hash binds the **complete referenced L0 fact cards**, including L0 source location, certainty and documented disposal. An otherwise unrelated source card does not change the hash. Resolved history source cards are also included.
- Only SHA-256 digests, aggregate counts and fixed audit codes may be returned. No source content, private paths, expert narrative or reviewer identity is emitted.
- The validate_l1_review_receipt function compares both digests against the **current** authorized packet and L0 facts, requires blind_review.blinded_packet_ref of sha256:<packet_sha256>, calls the existing blind-review validator, and verifies pending adjudication/authentication status. A detached receipt cannot declare that adjudication has been completed.
- Non-NO_ISSUE finding codes require secure adjudication **even if both reviewer decisions read ACCEPT_L1**. Mixing NO_ISSUE with substantive finding codes, or recording NO_ISSUE with an unacceptable 1–2 score, fails closed. Leading/trailing whitespace cannot create a second pseudonymous reviewer token.

All tests use explicitly synthetic development fixtures. Do not serialize real reviewer identities, restricted source facts, diagnostic logs, raw telemetry, or private expert comments into this public repository. Submit real review receipts to an authorized, access-controlled review workspace only.

## Offline workflow

1. Freeze the authorized, de-identified L0 cards and L1 packet; validate track and synthetic_provenance.
2. Compute the packet and source-fact fingerprints in the authorized review workspace; retain these exact artifacts and the digest algorithm/version.
3. Show each reviewer the same authorized reviewable material **without curator prompts or another reviewer's response**, but still with explicit SYNTHETIC markings. Collect two independent blinded assessments against the exact SHA-256 reference.
4. Combine the assessments in a dgsi-l1-review-binding.v1 envelope with packet_sha256, source_fact_cards_sha256, blind_review, and adjudication_status set to PENDING_REVIEWER_AUTHENTICATION or PENDING_SECURE_ADJUDICATION.
5. Validate against freshly supplied source cards and packet. Any change invalidates the receipt; any substantive finding goes to secure adjudication.
6. Verify reviewer independence, source authorization, sample provenance, and the final decision **outside** public DGSI. Even an intact reviewed L1 task is not Gold or trainable by default.

The current 15 literature-derived SYNTHETIC packets / 9 event families remain REVIEW_REQUIRED, without approved splits, authenticated reviewers, or training authorization. This work adds a safety gate only. The unselected nine-dimension PR #41 proposal remains an alternative design, **not** an additional production admission gate.
