# D0: Real-case handoff metadata validator (2026-11-15)

## Purpose and permitted scope

PR #28 defined a real-case handoff manifest but its original contract tests only inspected schema/document text. This stage **actually runs the published Draft 2020-12 JSON Schema**, validates a timezone-aware cutoff and redaction declarations, and audits multiple declared episode/event-family IDs.

This is a **local, read-only, metadata-only** pre-screen. It never reads the machine diagnosis, diagnostic logs, spacecraft configuration, expert target or telemetry. It never checks source authenticity or grants data access, training eligibility, Gold or automatic split assignment. Strings in the handoff manifest are untrusted self-assertions until reviewed by the authorized data custodian.

## Safe local usage

Use this command only inside an authorized environment, and pass explicit manifest paths (not source folders). Do not paste private manifest contents, files or output into a public issue.

```bash
PYTHONPATH=src python scripts/audit_real_case_handoffs.py \
    CASE-0001/input/case_manifest.json CASE-0002/input/case_manifest.json
```

PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python scripts/audit_real_case_handoffs.py CASE-0001/input/case_manifest.json CASE-0002/input/case_manifest.json
```

The command emits only aggregate counts, number of repeated incident families, decision counts and the constant flag `split_assignment_allowed: false`. Invalid manifest runs exit with code 2 and one payload-free error code; no source text, case IDs or local paths are emitted. The validator *does not write files*.

## Conservative decisions

- `SYNTHETIC_TEST_ONLY`: synthetic fixture or simulator record, regardless of claimed permissions or a confirmed outcome field; never real Gold.
- `REJECT`: missing source/permission class or manifest declaration of unredacted personal/sensitive identifiers.
- `CONDITIONAL_ACCEPT`: rights restricted to local review, incomplete logs/results/context/target declarations, incomplete timestamp/redaction metadata, or missing owner.
- `ACCEPT_FOR_EXPERT_REVIEW`: metadata claims are complete enough to request **independent manual examination**. It is *not* proof of authorization, source reality, diagnostic correctness, reviewer approval, or training eligibility.

A repeated `event_family_id` is counted as an event-family collision that must be grouped before any train/validation/test split. Multiple episodes in a family are not silently discarded, but none can be automatically split. Invalid or duplicated case IDs cause a fail-closed error.

## Mandatory next gates

For any candidate to move beyond metadata triage, an authorized custodian must verify original source/usage rights and redaction, check actual upstream ML version and score semantics, inspect log chronology against `analysis_cutoff`, verify configuration/mission context and evidence passages, and assess historical availability and episode-family grouping. Expert outcome stays under `target_private/` and must be independently adjudicated. Then the existing Case/SFT semantic and source admission gates apply.

No real-case material or R21 data was used in these tests. All added tests are **SYNTHETIC**. Do not commit restricted records to this public DGSI repository.
