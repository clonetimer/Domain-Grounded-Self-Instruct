# Offline SFT incident-family and leakage audit

This gate is for **second-stage diagnostic interpretation** examples. The user message contains only upstream machine diagnosis results, diagnostic logs, spacecraft/mission configuration and authorized historical/knowledge context. No raw telemetry or fault-injection truth belongs in the LLM prompt. The assistant reply is the proposed synthesis target, held outside that prompt. Expert adjudication is metadata, not prompt evidence.

## Run locally

```bash
PYTHONPATH=src python scripts/audit_diagnostic_sft_lineage.py --input examples/diagnostic_context_sft_illustrative.json
```

Input may be a single SFT JSON object, JSON array, or JSONL. The program is read-only, returns aggregate counts and error codes only, and never prints prompts, source IDs, hashes or file paths. Do **not** move private data into this public repository to run it.

## Split policy

- Assign `source_group` to the **physical incident/episode family**, before generating paraphrases or six SFT task-family variants. All variants and diagnostic revisions of that episode must stay in one split.
- A matching `case_ref`, upstream `diagnosis_result_refs`, or byte-level `source_artifact_hashes` cannot appear in a different split even if the case ID or group name was changed.
- Identical task+user-input text across splits is rejected; identical task+input and output inside one split is a duplicate; conflicting targets for the same task+input require adjudication.
- Exact `diagnostic_log_refs` such as `LOG-01` and shared `knowledge_passage_ids` are not treated as global event identifiers; operational log IDs can be scoped only to the local case. Generic spacecraft context is reusable. Explicit incident grouping is therefore still mandatory.
- If source hashes include common public manuals rather than episode-specific records, move that knowledge into `knowledge_passage_ids` before evaluating pilot splits. Do not make an exception that silently permits a diagnosis-report collision.

## Review and provenance boundary

- The gate always returns `gold_eligible=false`; `PASS_STRUCTURAL_ONLY` is **not** an authorization to train, share, publish or classify a case as real.
- Synthetic/illustrative records carrying a recognized marker must not be labeled `APPROVED`. A real approval stamp needs reviewer identity and timezone-aware timestamp, but cannot itself prove reviewer independence or source authority.
- Any SFT pilot also needs an authorized case register distinguishing **public synthetic fixture**, **internal simulation**, **real engineering diagnosis record**, and **real on-orbit record**; source owner and IP rights; immutable source provenance and upstream method/version; time-cutoff/label separation; expert incident-family confirmation and independent target review.
- The current schema does not have globally reliable episode IDs, case-fingerprint roles or an external verified expert roster. This audit catches exact identity reuse and obvious text duplication, not semantically similar incidents with independently renamed identifiers.

## Test and progression

`tests/test_sft_lineage_audit.py` probes same-event renaming, upstream diagnosis reference reuse, artifact-hash reuse, repeated prompts, conflicting answers and synthetic approval. These tests use synthetic-only constructed records. Obtain and independently review 5–10 sufficiently complete authorized real/de-identified cases before assembling 20 expert-approved samples. The 300–500 controlled SFT pilot must wait until episode and provenance quality are demonstrated.
