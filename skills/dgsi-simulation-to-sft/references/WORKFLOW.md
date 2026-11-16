# Production workflow and directory contract

## Recommended working directory

Keep restricted user material outside the public DGSI repository. For each project batch:

```text
DGSI-BATCH-YYYYMMDD/
  00_source_inventory/
    asset_manifest.json
    source_evidence_ledger.csv
    source_hashes.sha256
  01_l0_source_facts/
    l0_fact_cards.json
  02_l1_candidates/
    l1_task_packets.json
  03_hidden_truth_QA/             # restricted; never supplied to generator
    simulation_truth_manifest.json
    run_receipts/
    adjudication_records/
  04_validation/
    schema_validation.json
    evidence_audit.json
    leakage_audit.json
    duplicate_audit.json
    batch_summary.json
  05_human_review/
    review_queue.csv
    corrected_targets/
  06_release_candidate/
    sft_preview.jsonl             # preview only until external admission
    provenance_sidecars/
    sha256_manifest.txt
```

Do not put private reports, logs, telemetry, truth labels, credentials or reviewer identities in the public repository.

## Batch sequence

1. Freeze a batch manifest and record source hashes.
2. Extract source facts before asking a model to generate tasks.
3. Have a separate reviewer/model check source extraction against exact locators.
4. Create L0 facts with one event episode per card; separate multiple episodes even when one report describes them together.
5. Build L1 prompts from information available at the analysis cutoff.
6. Store simulator injection truth and post-run QA evidence in the hidden sidecar.
7. Generate assistant targets from the visible evidence only. The hidden sidecar is used only by the auditor/reviewer to evaluate correctness.
8. Validate schema and cross-file references.
9. Run leakage, duplication and lineage checks.
10. Conduct independent human review. Preserve edits and decisions append-only.
11. Only after an authorized admission process may an approved SFT serializer emit training records.

## Batch accounting

Every report must count:
- source files by class;
- source events and event episodes;
- L0 fact cards;
- L1 tasks by task type;
- candidates by provenance class;
- incomplete/rejected/review-required/human-reviewed counts;
- duplicate/near-duplicate groups;
- evidence-reference failures;
- truth/time leakage failures;
- source families assigned to each split (if formally authorized).

Never combine real engineering, actual simulator-run, literature-derived, design-hypothetical and synthetic-test counts into one headline number.

## Stop conditions

Stop generation and return a blocker if:
- source permission is unknown or incompatible with the AI provider;
- event identity or analysis cutoff cannot be established;
- a diagnosis result is missing but the requested task assumes it exists;
- logs are temporally ambiguous or contain unresolvable contradictions;
- injection truth cannot be isolated from model-visible records;
- source files are incomplete or fingerprints changed during processing;
- the assistant target requires facts not in the visible input;
- the model cannot distinguish an observed effect from a design assumption.
