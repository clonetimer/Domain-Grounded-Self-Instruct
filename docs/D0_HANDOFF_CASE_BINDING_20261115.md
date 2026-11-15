# D0 — Hand-off manifest ↔ diagnostic Case binding (2026-11-15)

## Scope and product boundary

The only downstream product is an SFT corpus for **second-stage interpretation of upstream ML diagnosis results** together with diagnostic logs, spacecraft and mission context, and historical engineering experience. Raw telemetry is processed upstream, not serialized as a default LLM input.

PR #29 validates the **untrusted manifest alone**. This increment provides `assess_handoff_case_binding(manifest, case)` for **authorized, local** use with an already de-identified diagnostic Case. It does **not** open original files, generate targets, assign splits, or upload any case content.

## What is checked

- Both inputs pass the existing manifest and full diagnostic Case validators; errors are constant codes without case payloads.
- Pseudonymous case ID, event/incident family, analysis cutoff instant (including timezone offsets), and supplied spacecraft pseudonym match.
- Declared optional historical/knowledge files agree with evidence actually included in the Case.
- Diagnosis-run references and source-artifact hash *declarations* are present.
- A manifest claiming a real source cannot silently relabel a Case that still bears synthetic provenance markers.
- An asserted expert `APPROVED` or training-permission flag **does not** become independent proof, training permission or Gold approval.

The report contains only blocker/warning codes and booleans. A successful alignment means **metadata agreement**, not source authenticity. Source-file presence, byte-level hashes, de-identification completeness, algorithm version and score semantics, accuracy of logs, expert adjudication, and train/validation/test event isolation remain for the authorized custodian to verify.

## Safe local usage

```python
from dgsi.real_case_binding import assess_handoff_case_binding

# Both objects must already have been loaded/de-identified INSIDE an authorized environment.
report = assess_handoff_case_binding(local_manifest, local_diagnostic_case)
# Retain the report in the authorized workspace if counts/codes are sensitive.
```

| Decision | Meaning |
| --- | --- |
| `SYNTHETIC_TEST_ONLY` | Manifest explicitly describes a synthetic/simulation test input; never a Gold case. |
| `REJECT` | Invalid source class/permission status, or claimed real case carries synthetic provenance markers. |
| `BLOCKED_BINDING` | A real-source claim conflicts with Case identity, time, evidence declarations or provenance references. |
| `CONDITIONAL_ACCEPT` | Inputs align but manifest-level source declarations remain incomplete. |
| `READY_FOR_MANUAL_SOURCE_AUDIT` | Submitted fields align; **unverified claims only**, not a real/Gold certification. |

The function deliberately cannot prevent a malicious writer from **removing synthetic markers** and fabricating matching metadata. A new field or a hash-looking string is not proof of source integrity. Real-case admission requires independent custody/permission checks and expert corroboration outside this publicly testable layer.

## Evidence and tests

`tests/test_real_case_binding.py` uses the explicitly illustrative case and synthetic metamorphic mutations. It checks ID/family/cutoff drift, timezone equivalence, optional evidence declaration inconsistencies, fabricated permissions, missing run/hash declarations, raw telemetry injection, fake approval, output privacy, and synthetic-to-real laundering. These tests do not contain restricted records and **cannot** be counted as genuine diagnostic experience.

Keep PRs Draft. Do not merge `main`, promote data to Gold, fine-tune models, or copy R21/private diagnosis logs or expert records into this public repository. D0 #8 and P3 #4 remain open until independent real-case review.
