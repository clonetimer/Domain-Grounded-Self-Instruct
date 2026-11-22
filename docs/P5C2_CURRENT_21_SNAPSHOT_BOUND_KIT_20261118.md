# P5-C2 — current 21-task snapshot-bound dual-review kit

## Purpose

The legacy blank Word/JSON handoff built for the **15-task** C2 pilot must not be presented as covering the corrected 21-task candidate. This separate checkout-only entrypoint binds the current 21 L1 packets to the corrected 13-card L0 inventory, then uses the already-reviewed C2 complete-kit builder. It does **not** modify the released RC4 toolkit or the scientific L0/L1 records.

### Generate offline for authorized expert distribution

From this branch's checkout, with a private destination **outside the repository**:

```bash
python scripts/create_l1_c2_current_21_review_kit.py --output-file "/path/outside/repo/DGSI_C2_21_REVIEW_ONLY.zip"
```

The outer ZIP includes reviewer A and B separate ZIPs with a **blank** ten-dimension Word/JSON scorecard plus the same complete SYNTHETIC scientific dossier, source rights blank JSON, coordinator manifest, hash list and warnings. Distribute reviewer packages independently, retain completed reviews and licensed records off GitHub. Experts must verify the source publications themselves; the generated dossier is not an approved scientific fact record.

## Fail-closed boundary

The wrapper authenticates both candidate input snapshots against expected committed Git blob identities (with LF canonicalization only for Windows checkout portability), requires precisely 21 synthetic packets in REVIEW_REQUIRED and 13 L0 cards still pending genuine domain-expert confirmation, then checks the assembled kit has 21 tasks, 9 event families, 7 distinct rights-source publications and 12 bound L0 event cards. A changed input must fail until explicitly reviewed and versioned, rather than silently producing a mismatched blank pack. Output is atomic, no-clobber and only allowed outside the repository.

All statuses remain **review only**: no reviewer authentication, expert verdict, rights clearance, real Gold, formal split, SFT export, paid model call or fine-tuning. The public repository does not store completed private reviewer identities or permissions.

This source-only wrapper and its tests are **not part of the frozen RC4 portable archive allowlist**, so the toolkit's issued archive SHA-256 remains unchanged.

## Engineering test

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_c2_current21_review_kit.py' -v
```

The new tests exercise real 21-packet / 13-L0 binding, Word/JSON blank review integrity, the two separated reviewer ZIPs, stale snapshot and fake approval rejection, no-overwrite semantics and repository-output blocking. The latest exact-head Ubuntu/Windows full test jobs must both pass before this work is accepted. No CI result constitutes source permission or independent expert approval.
