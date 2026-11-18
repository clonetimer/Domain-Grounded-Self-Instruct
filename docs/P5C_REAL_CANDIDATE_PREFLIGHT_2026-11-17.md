# P5-C1 REAL candidate preflight (metadata-only)

Date: 2026-11-17  
Status: candidate intake integrity, **not** engineering-case authentication or training admission.

## Intent

The five user-supplied engineering cases are source-material candidates, **not** full DGSI SFT input packets. Upstream ML results, diagnostic logs, spacecraft/mission contexts, verified disposal execution and two independent expert reviews remain unavailable. No raw telemetry enters the default LLM input.

`python scripts/audit_p5c_real_intake.py` re-reads the checked-in *metadata-only* example, validates strict case IDs, domain and disposal notation, missing-evidence states and hard training gates, and prints an aggregate-only report. All failures return fixed codes without source excerpts or private paths. The command does not edit files.

The validator intentionally accepts only the **frozen initial incomplete snapshot**, with the original five case IDs and `MISSING` evidence fields. It must not be repurposed to accept later real evidence: use separate permissioned evidence receipts, secure reviewer identity controls, admissibility verification and explicitly authorized releases. A hypothetical ML run or an edited `APPROVED` flag does not constitute evidence. Conditional handling in the Ku-band TWTA and RW cases is never interpreted as an executed operation.

The reader rejects duplicate JSON object keys to avoid shadowed promotion flags. Unknown fields are blocked to prevent private target records or synthetic ML/log content being smuggled into this public candidate register.

## CI and interpretation

`PYTHONPATH=src python -m unittest tests.test_p5c_real_intake -v` (or normal full discovery) runs only `SYNTHETIC_TEST_ONLY` mutations of the sanitized register. Successful validation returns `BLOCKED_PENDING_REAL_EVIDENCE`; the correct current outputs are **five pending REAL candidates, zero authentic Gold, zero official split assignments, zero authorized SFT records and no training approval**. The 15 literature-derived SYNTHETIC L1 packets remain a separately reviewed data track.

This is not a test of private source truth, rights, de-identification, event-family independence, the real upstream ML interface or expert authenticity. Subsequent work must bind provenance evidence and preserve as-of limits, context-only historical cases, disposal-source fidelity and split isolation.
