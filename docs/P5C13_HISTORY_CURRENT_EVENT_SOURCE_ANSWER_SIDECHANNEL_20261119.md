# P5-C13 — Remove a current-event L0 answer embedded in HISTORY Context (2026-11-19)

## Scientific finding

Read-only review of the pinned v0.5 paired DEV_ONLY archive found a side-channel not addressed by earlier L0/source-fact quarantine: in FUSE task **012**, the Cassini historical case's **applicability_limitations** quoted a hypothesis about the **current FUSE event**, namely that a 2000-08-04 source suggested Kapton liner blistering. This is a **source-level possible explanation**, not an independently observed fact or confirmed fault source. It is absent from NO_HIT but appears in HISTORY, so the contrast includes current-event answer information, not just historical experience. Even with common L0 excerpts removed, that arm could be rewarded for a hidden-source explanation.

This does **not** prove model shortcut use: model execution remains NOT_RUN. Nor does it license removing the legitimate ML local-contact candidate, the synthetic wheel-drag and restart logs, Cassini's own prior observation, or its PARTIALLY_CONFIRMED historical status.

## Minimal DEV_ONLY repair

The deterministic local v0.6 copy is generated from pinned v0.5 SHA-256:
e3bc39e54ef6e15ab0e47ded3a5452545401fcb8ad36df5a467dc1e44b96524b.

Only task 012's **HISTORY** prior applicability-limitation sentence is replaced. The new text still says Cassini reported low-speed lubrication as a possible *historical* mechanism, but does **not** reveal the withheld current FUSE hypothesis. It preserves hardware UNKNOWN, transfer limitations, chronology, unconfirmed ML candidate and both task instructions. No change is made to any NO_HIT input, tasks 003/013, or frozen REV1.

- Local reproducible v0.6 ZIP SHA-256: edf987faae6a0b0dbdb148d134a72ffda06d2106868de9c92dbbe3971a00c781.
- The reviewer-facing diff, source phrase and replacement remain in a coordinator-only ledger with not_for_sft=true, never the model input or assistant target.
- New src/dgsi/history_source_answer_guard.py rejects reviewer-identified source substrings if reintroduced into the retrieved historical case. It is *additional*: existing history_pair_science_audit.py retains responsibility for A/B structural equivalence, as-of, event-family and release restrictions.
- Nine synthetic-only unit tests cover clean input, reinserted hint, mismatched replacement, wrong prior, digest tampering, disabled review guard, unauthorized training, fictitious redaction marker and arm swap.

## Scientific blockers

This is **targeted exact-marker isolation**, not proof of complete semantic non-leakage. The proposed edit requires two independent scientific reviewers before any label is accepted. Independently trustworthy verified_at is still missing for historical cases; controlled pairs remain DEV_ONLY and production as-of retrieval remains blocked. Source rights, independent 21-task review, and input-bounded per-arm reference targets also remain open. Positive historical transfer is NOT_EVALUABLE (3 pairs, 2 event families), model scoring is NOT_RUN, REAL Gold=0, formal splits=0, training_authorized=false.

### Development lesson

Historical-case transfer restrictions can themselves leak the current event's scientific explanation. Input reviews must inspect content inside historical cases, not only top-level evidence cards, logs and case IDs. Prefer narrow source-bound redaction over deleting legitimate ML candidates or upgrading hypotheses into confirmed facts.
