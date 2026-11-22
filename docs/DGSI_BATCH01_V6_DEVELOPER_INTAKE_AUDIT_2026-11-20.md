# DGSI Batch 01 v6 — developer-side intake audit

**Date:** 2026-11-20  
**Package:** `DGSI_Batch01_Developer_20261120_v6.zip`  
**Custodian release:** `DGSI-CUST-MATERIAL-RELEASE-20261120-008`  
**Classification:** MATERIAL INTAKE / NO GENERATION / NO SCORING / NOT CONFIRMATORY RUN

## 1. Package integrity

Developer-side verification of the received ZIP:

- ZIP entries: 10.
- Entries listed in `SHA256SUMS.txt`: 9; all 9 hashes match the extracted bytes.
- `01_model_inputs.jsonl`: parses as exactly 2 records.
- For both records, the corresponding TXT file is byte-identical to the UTF-8 encoding of the JSONL `input` value.
- Both TXT SHA-256 values match the case-specific hashes in `02_release_manifest.json`.
- Manifest declares batch `DGSI-BATCH01-20261120-v6`, status `MATERIAL_RELEASED`, 2 cases and 2 source clusters within the custodian's reviewed scope.

ZIP SHA-256: `50d3730693bf95c5ce8e6620ab4cc40fb880040173f9936dd2923043ba725ea9`.

This verifies the delivered package and input consistency only. It does not verify original report bytes, original-source hashes, a trusted timestamp, source authenticity, completeness of historical exposure, or empirical source re-identification risk.

## 2. Released cases

| Candidate | Case ID | Cluster | Custodian material decision | History result | Rights basis stated in manifest |
|---|---|---|---|---|---|
| CAND-002 | CASE-002 | CL-002 | RELEASED_FOR_INTERNAL_EVALUATION | NO MATCH, pass within stated coverage | CC BY 4.0; attribution sidecar held by custodian/rights owner |
| CAND-004 | CASE-004 | CL-004 | RELEASED_FOR_INTERNAL_EVALUATION | NO MATCH, pass within stated coverage | Official file marked US public domain; author/institution attribution retained |

The two cases are the only model-visible payloads in this batch. Read `input` from each JSONL row or the corresponding TXT, not both. Do not load the manifest, receipt, rights notice, validation report, Word handoff, or attribution sidecar as generator prompts.

The released material is a post-investigation factual digest, not raw telemetry, a complete investigation record, or an upstream ML/log bundle. CASE-002 contains three evidence items; CASE-004 contains five. Evidence-item count is not independent sample count.

## 3. Custodian limits preserved

- The release is material-level admission for closed internal evaluation, not approval to start the entire confirmatory study.
- History result NO MATCH is limited to the custodian's received structured history and checks; it is not proof of never-exposed.
- Post-baseline developer exposure is NOT_ATTESTED.
- Foundation-model pretraining exposure is UNKNOWN.
- Source re-identification risk is POSSIBLE_NOT_EMPIRICALLY_TESTED.
- Technical review was the same AI in shared context performing sequential two-role review. Human expert signatures: 0. Isolated subagent runs: 0.
- Source identity, mapping, reference judgments and complete attribution sidecar are not in the developer package.
- The initial 5–10 independent-cluster collection target is not reached.
- CAND-001, CAND-003, CAND-005, CAND-006 and CAND-007 remain unreleased for their stated reasons; they are not silently added to this batch.

## 4. Preregistration compatibility

The existing 2×2 design remains unchanged:

- A: evolution off, selection off.
- B: evolution off, selection on.
- C: evolution on, selection off.
- D: evolution on, selection on.

The existing preregistration explicitly says no new generation, model calls, evaluation changes, training splits, Gold promotion or fine-tuning are authorized by that preregistration. The custodian's v6 receipt expressly says material-level release is not whole-study start authorization and does not itself establish sample-size sufficiency or statistical power.

Accordingly, this intake audit does **not** start generation or scoring. Before any execution, the project must reconcile the material release with the existing preregistration through an explicit, versioned authorization/amendment that preserves the frozen arms, rubric, thresholds and one-round stop rule. The project must also record whether two clusters are being used only for a separately labelled exploratory/pilot exercise or whether the preregistered confirmatory sample requirement has been met. Do not silently relabel a two-cluster batch as the planned 5–10-cluster collection or as statistically powered confirmation.

No prompt tuning, strategy selection, threshold adjustment, regeneration or case substitution is permitted on these two inputs under the stated holdout arrangement.

## 5. Current run ledger

| Item | Status |
|---|---|
| Package hash verification | PASS (9/9 listed entries) |
| JSONL parse / record count | PASS (2) |
| JSONL input equals TXT bytes | PASS (2/2) |
| Case input hashes match release manifest | PASS (2/2) |
| Material release | PASS for CASE-002 and CASE-004 only |
| Whole-study final dataset freeze | NOT DONE |
| Preregistration execution authorization | NOT GRANTED |
| Generation calls | 0 |
| Formal targets generated | 0 |
| Blind reviews | 0 |
| Scorecard rows | 0 |
| Model-performance gain evidence | 0 |
| Training / Gold promotion | NOT AUTHORIZED |

## 6. Developer-side disposition

Accept CASE-002 and CASE-004 into the restricted internal evaluation staging area, preserving their case IDs, cluster IDs, exact input bytes and hashes. Do not expose source identity, attribution sidecar, reference judgments or custodian-only files to generators/reviewers.

This document records package intake and boundary checks only. It does not amend the preregistration, certify independent human review, authorize model calls, or make a performance claim.
