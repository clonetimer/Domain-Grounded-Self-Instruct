# P5-C2 source-current rights intake preflight (2026-11-18)

The earlier source-rights intake audit (#143) correctly checks a private worksheet against its coordinator-supplied BLANK queue. **A structurally valid old blank can still be stale** when the underlying L1 task packet, L0 source fact, or episode mapping changes. This integration PR also carries the sibling #142 L0 source/episode identity guard, so both protections are exercised together.

Use the additional, strictly read-only preflight from the repository checkout that contains the **current** public L0 and L1 artifacts:

```bash
python scripts/audit_l1_c2_current_rights_intake.py \
  --blank <original-unedited-coordinator-rights-queue.json> \
  --submission <privately-edited-rights-queue.json> \
  --current-collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --current-l0-facts examples/l0_public_literature_fact_cards_2026-11-15.json
```

The script regenerates the 7-document blank queue from the 15-task L1 candidate and 12 referenced L0 fact cards. It compares the **entire source-bound regenerated queue**, not merely a copied collection hash, to the supplied original blank. A stale or modified blank is rejected; an editable submission is then checked by the independent rights-intake rules. Only fixed rejection codes and aggregate review-status counts are printed. No source text, private evidence bytes, or reviewer identity is exported.

## Scientific and legal boundaries

The current checkout must itself come from an authorized, version-controlled source. This preflight does **not** authenticate GitHub permissions, legal owners, evidence signatures, intellectual-property reuse, reviewer identities, expert science approval, or actual evidence contents. A source hash and a report saying `current_public_source_snapshot_matched=true` are **not permission clearance**. The data remain LITERATURE_DERIVED_SYNTHETIC, REVIEW_REQUIRED, and not eligible for Gold, official splits, SFT export, or training.

The old two-file CLI remains a structural diagnostic only; **use this four-file command for current-cohort processing**. Do not silently upgrade old review forms. Keep filled worksheets and legal artifacts in a controlled private location. No actual private evidence is required for CI fixtures.
