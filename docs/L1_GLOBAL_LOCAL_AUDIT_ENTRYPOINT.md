# P4: local global lineage audit entrypoint

The global L1 audit in `dgsi.l1_global_lineage` is now callable on **local,
explicitly supplied** JSON collections. This is a read-only structural
preflight: it cannot approve data, experts, official splits, real Gold or
fine-tuning. Input files and filenames never appear in the result. No network
requests are made.

## Local manifest

Create a local manifest; paths may be absolute or relative to the manifest.
Do not commit private manifests, actual operations logs, telemetry, reviewer
identities, or source files.

```json
{
  "schema_version": "dgsi-l1-global-audit-manifest.v1",
  "batches": [
    {
      "collection_path": "local/l1_packets.json",
      "source_fact_cards_path": "local/l0_cards.json"
    }
  ]
}
```

The L0 file can be a JSON array or an object with a `cards` array. Every L1
collection is validated independently before cross-collection checks.
Batch-level tracks remain separate, and the report aggregates
`track_task_counts` without presenting synthetic tasks as real cases.

## Commands

```bash
python scripts/audit_l1_global_lineage.py --manifest /local/manifest.json
python scripts/audit_l1_global_lineage.py --manifest /local/manifest.json --aliases /local/reviewed_aliases.json
python scripts/audit_l1_global_lineage.py --manifest /local/manifest.json --hypothetical-splits /local/offline_adversarial_plan.json
python -m unittest tests.test_l1_global_lineage_cli -v
```

Hypothetical splits require an explicit option and **are test-only**. They are
not persisted to L1 packets. All identifiers, source cards, and optional alias
claims must pass existing validators. An alias with
`DOMAIN_EXPERT_CONFIRMED` is still **unverified metadata**, not an
authenticated specialist decision.

Successful runs return `STRUCTURAL_PREFLIGHT_ONLY`, the relevant aggregate
counts, `gold_eligible_count=0`, `training_authorized=false` and exit 0.
Blocked runs return fixed error codes and exit 2; no traceback or local source
content is printed. Duplicate JSON keys and non-finite JSON numbers fail
closed. Each local file is limited to 8 MiB; at most 64 batches are accepted.

The current pilot has 15 SYNTHETIC L1 packets, nine source event families,
REVIEW_REQUIRED status, no official split, zero verified real Gold and zero
training authorization. A successful audit changes none of these states.
Independent L0 provenance, IP, expert source adjudication and L1 double-blind
review remain mandatory.
