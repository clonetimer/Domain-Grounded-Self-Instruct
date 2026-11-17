# P5-C2: L1 fingerprint-bound double-blind review metadata (candidate only)

This is a **metadata-only technical review request** for the existing **15 literature-derived SYNTHETIC tasks / 9 source event families**. The authoritative candidate inputs remain `examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json` and `examples/l0_public_literature_fact_cards_2026-11-15.json`. No tasks, synthetic ML results, logs, source facts or expert judgments are created in this change.

## Contract

`build_l1_blind_review_manifest(collection, source_fact_cards=cards)` first runs the existing collection-level source, schema, context, track and leakage projection gates. Each sorted row has `task_id`, `case_id`, `event_family`, `task_type`, full `packet_sha256`, referenced L0 **public fact** digests, their aggregate `source_public_sha256`, and unassigned A/B review slots. The whole manifest carries the current projection hash and cannot authorize Gold, SFT, official train/validation/test split or training.

A source/content change requires a new manifest and new expert review tied to the new fingerprints. Historical source excerpts are not current-scenario direct evidence; these fingerprints establish review identity only, **not** truth or approval. `internal_review` content is excluded from L0 public hashes and no reviewer notes, identity, raw prompt or formal target are exported by the manifest.

The pair checker validates two receipts' task ID, full packet digest, public source digest, distinct nonempty reviewer tokens and allowed `ACCEPT/REVISE/REJECT` recommendations. It **does not verify expert identities, authorizations, rights, independence beyond token inequality, adjudication or correctness**. Even two `ACCEPT` values return `expert_adjudicated=false`, `gold_eligible=false`, `training_authorized=false`. Never store real reviewer identity or restricted opinions in the public repository.

## External expert/rights steps still required

1. Independently confirm L0 claim locators, event-vs-ground-test class, certainty, episode and source usage rights. The TROPICS MIT rights language and S-band TWTA journal use remain priority blockers.
2. Give two qualified independent reviewers the **same frozen task and source hashes** under separately controlled identities. Review scientific fidelity, current-vs-historical evidence roles, ML calibration semantics, cause vs affected components, disposal fidelity, uncertainty, historical transfer and actionability.
3. Compare signed/verified offline receipts and resolve disagreements via controlled adjudication. This module's token check is not a signature, identity service or Gold promotion.
4. Only after separate rights, source, independent expert, split leakage and release gates may another explicitly authorized system consider SFT output. This PR adds no serializer.

## Generate a local JSON expert-review identity pack

Run from the repository checkout (never from an untrusted packet source):

```bash
python scripts/create_l1_blind_review_manifest.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json \
  --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json \
  --output local_review/l1_blind_review_fingerprint_manifest.json
```

The CLI writes only review IDs, snapshot fingerprints, two **unassigned** reviewer slots and blocking states. It refuses to overwrite an existing destination, prints aggregate-only status and does not emit SFT rows. `local_review/` is an operator-managed directory; the output is not an expert receipt or an admission decision. The generated JSON must be kept paired with the exact L1/L0 source snapshots when distributed for controlled blind review.

## Regression scope

Run `python -m unittest tests.test_l1_blind_review_manifest` with repository `src/` on `PYTHONPATH`, or run the repository's established full CI matrix. The tests use `SYNTHETIC_TEST_ONLY` reviewer tokens and do not represent genuine expert reviews.
