# P5-C0 reproducible readiness snapshot audit

The P5-C0 snapshot is a **counting contract**, not a reviewer signature or source
admission. Run from the repository root:

```sh
python scripts/audit_p5c_readiness.py
python -m unittest tests.test_p5c_readiness -v
```

The tool reads the three public, bundled fixtures in `examples/`: the P5-C
baseline, the L1 literature-derived synthetic collection and the L0 fact-card
registry. It prints **aggregate JSON only**. It never copies prompts, targets,
logs, source paragraphs or private reviewer information. An unchanged snapshot
yields `BLOCKED_PENDING_INDEPENDENT_REVIEW` and exit status 0 (audit
completed); malformed/stale or unsafe input yields a fixed code and exit 2.

The audit recomputes packet count, independent event-family count, six task-type
counts, history hit/no-hit counts, referenced event-card classes and all
source-family packet counts. It fails closed when a source is missing or a
packet's source family disagrees with its cited L0 card; it detects a stale
snapshot rather than silently publishing the old dataset size. It also blocks
default raw telemetry, cross-track packet claims, unisolated internal review,
unreviewed sources masquerading as approvals, official splits, Gold flags,
training or SFT export.

This is **not** a complete science or authenticity verifier: it cannot attest
source licensing, source-passage accuracy, whether two differently named event
families denote the same physical incident, real ML provenance or independent
expert identity. Real engineering intake candidates are **not** counted as
Gold and are outside the 15-packet synthetic inventory. The existing deeper
L0/L1 validators, global leakage checks, blinded review receipts, trusted
release gate and independent human judgments remain separately required.

After any legitimate change to task inventory, L0 facts or review status, a
new source-bound baseline and corresponding independent re-review are required.
Never modify counts merely to make this audit green. No export or training
authorization is created by an audit pass.
