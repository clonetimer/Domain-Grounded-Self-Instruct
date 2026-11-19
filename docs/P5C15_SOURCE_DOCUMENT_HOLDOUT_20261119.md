# P5-C15 — Source-document-level scientific holdout, not just event-family split

**Scope:** read-only, `REVIEW_ONLY`, not_for_sft=true. This note and the companion audit do **not** allocate an official train/validation/test split, authenticate source rights or expert identity, certify Gold, or authorize fine-tuning.

## Newly verified dataset-level finding

On immutable REV1 collection `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json` (Git blob `f141694748d5425b63b469b5b0b25064e1b402c8`), joined by `source_fact_refs` to `examples/l0_public_literature_fact_cards_2026-11-15.json` (Git blob `33b831408068e00e366eb6c6c3a0a1751195c685`), **21 task variants span 9 event-family IDs but only 7 distinct primary source documents**.

| Source document ID | REV1 task suffixes | Distinct source event families |
| --- | --- | ---: |
| `NASA-NTRS-20040171604` | 001 | 1 |
| `NASA-CR-66461` | 002, 007, 016, 018 | 1 |
| `MITLL-TROPICS-LESSONS-2025` | 003, 004, 005, 006, 013, 017 | **3** |
| `NASA-LLIS-1416` | 008, 014, 021 | 1 |
| `NASA-TM-100232` | 009, 010 | 1 |
| `JOURNAL-2026-TWTA-SBAND-POWER-DROP` | 011, 015, 019 | 1 |
| `FUSE-SPIE-2002-RWA` | 012, 020 | 1 |

The TROPICS Pathfinder, qualification and flight-CRC event families are different events but derive from **one lessons-learned publication**. Splitting those three families across training and holdout would leak the paper's mechanism, engineering narrative and interpretation, undermining a claim of evaluation on *unseen literature*. The existing event-family isolation is necessary but insufficient for this particular scientific generalization claim.

## Concrete engineering increment

`dgsi.l1_source_document_holdout.audit_l1_source_document_holdout` groups current L1 packet IDs through their validated **L0 source-card identifiers** and the source card's declared `source_reference.source_id` and `event_family_id`. The connected-component construction handles a future task with multiple L0 source references, merging document groups rather than falsely declaring them independent.

- An incomplete hypothetical task-to-split plan or missing L0 provenance is rejected; source document identifiers are never guessed from titles or equipment similarities.
- A hypothetical plan that puts tasks from the same source-document-connected component in different splits is rejected.
- Even a passing hypothetical plan returns `official_splits_assigned=false`, `training_authorized=false`.
- Seven tests include the real 21-task REV1 **structural fixture** and invented incompatible split plans; this is not a model-effectiveness test.

## Experimental implications

- Treat **7 document-linked clusters** as the *upper bound* on independent literature-source sampling units, not 21 task instances or 9 literature sources. These are **not** 7 independently expert-approved source reports.
- Keep event-family and episode isolation inside each document cluster. The broader holdout must also exclude unseen source passages from synthetic-generation prompts, examples, retrieval indexes and reviewer-facing hidden targets.
- The FUSE task uses Cassini as historical Context; review the existing cross-split target and `analysis_cutoff` gates separately. This metadata-only document audit does not certify historical `verified_at`, nor automatically ban legitimate time-safe history retrieval.
- For model comparison, report source-document clusters as units for uncertainty and sensitivity analyses; 7 clusters is too small for confident population-level performance or model-gain claims.
- Retain all tasks at `REVIEW_REQUIRED` with **REAL Gold 0, authorized split 0, trained examples 0** pending source-rights verification and two independent expert reviews.

Reproduce locally from the GitHub checkout:

```bash
PYTHONPATH=src python -m unittest tests.test_l1_source_document_holdout -v
```

**Development lesson:** independent event-family identities do not imply independent *source evidence*. For literature-derived synthetic data, leakage prevention must also respect common underlying publications; otherwise a model can recognize a paper's interpretation without performing a genuinely new engineering diagnosis.
