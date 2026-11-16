# D0 / P4 REAL candidate review queue: local preflight

This is a **read-only, aggregate-only preflight** for the separately maintained v0.5 REAL candidate evidence-request queue. The queue is **not** an L0 fact card, formal L1 task packet, expert review receipt, training dataset or verified provenance record.

Run it only on an explicitly authorized local JSON file:

```bash
PYTHONPATH=src python scripts/audit_real_review_queue.py /path/to/authorized/local_queue.json
PYTHONPATH=src python -m unittest discover -s tests -p 'test_real_review_queue_preflight.py'
```

On Windows PowerShell, set `PYTHONPATH` to `src` before invoking Python.

The tool never scans source folders, reads engineering files, uploads data, writes files or outputs paths, case IDs, source text, reviewer identities or private notes. It enforces all nine missing-material categories, cohort counts, source case SHA-256 format, and no-promotion constraints. It rejects forged completed reviews, verification assertions and Gold/training flags within the intake-only queue. Actual verification must be recorded in a **separate, independently checked source/evidence and review receipt**.

The output is aggregate-only and always returns `training_authorized=false`, `real_gold_count=0`, `split_assignment_allowed=false`. A historical `NO_HIT` must be established by a separately verifiable as-of retrieval receipt; missing historical materials never justify invented history. Regression tests use `SYNTHETIC_TEST_ONLY` fixtures.

This preflight does **not** certify actual source authenticity/IP permission, hash-to-file correspondence, deidentification, real ML runs, diagnosis logs, timestamps, evidence adequacy or expert conclusions. It precedes the existing authorized handoff and downstream L0/Case/SFT gates.
