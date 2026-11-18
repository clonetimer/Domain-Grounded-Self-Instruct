# P5-C2 returned AI advisory disposition — 2026-11-18

## Decision boundary

The returned ZIP is a checksum-valid **single-AI, two-lens advisory**, not two independent human expert reviews. Its A/B JSON files are not official scorecards and must never be submitted to the authenticated expert intake. The official blank A/B forms and source-rights queue remain untouched.

The advisory package binds the current 21-task cohort projection:
`7e8bc4cdccc61d5d656cd14afe67611fee9f8cc4ccf50ab9f3aa556317e4dad5`.
It covers 21/21 tasks and seven source-document groups / 22 task-source bindings. The source ZIP SHA-256 is recorded in the received AUDIT.json; all 49 original-entry checks passed.

## Scientific disposition

- Tasks 001–014 and 016–021: no deterministic internal target contradiction was identified by the two AI lenses. Keep their existing candidate content for this revision; their ACCEPT suggestions are not expert approvals.
- Task 015: both lenses identify the same structural precision defect. The model-facing ML result says `LINEARIZER_LNA_GAIN_DEGRADATION`, while `formal_target.cause_localization.candidates[0].fault_mode` says `linearizer_LNA_hydrogen_poisoning`. The same mismatch is duplicated in `case.expected_output`.
- The current scenario supplies no module-atmosphere hydrogen result or chip failure analysis. The narrative correctly treats hydrogen poisoning as a historical hypothesis, but the structured fault-mode field is more specific than the current evidence and could be misread by downstream consumers.

## Implemented content correction — REV1

A new immutable cohort file is created rather than overwriting the reviewed 21-task snapshot:

- New collection ID: `DGSI-L1-LITERATURE-SYNTHETIC-PILOT-C2-COVERAGE-CANDIDATE-REV1-2026-11-18`
- New file: `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json`
- New projection SHA-256: `3927c976af6eb46a8842b68926fd893b021df69b034ae8981dc5ed136278521a`
- L0 source facts are byte-identical to the prior cohort.
- Exactly one semantic field pair changes: task 015 `formal_target` and its mirrored `case.expected_output` both change from `linearizer_LNA_hydrogen_poisoning` to `linearizer_LNA_gain_degradation_candidate`.
- All 20 other tasks, task 015 input, logs, ML result, history, source bindings, narrative uncertainty, limitations, and follow-up actions are preserved.
- Task 015 remains `CANDIDATE_ONLY`, `HIGH` uncertainty, `REVIEW_REQUIRED`; this does not diagnose hydrogen poisoning or confirm a physical LNA fault.

This is a proposed curator correction based on an AI advisory and independent field-to-input consistency inspection. It is not a human adjudication. REV1 must receive a fresh, version-bound independent A/B scientific review; the prior 21-task forms and AI advisory are not reusable as official receipts.

## Seven-source rights disposition

The returned rights review is evidence triage, **not permission clearance**. All seven source entries retain:
- `rights_review_status=PENDING_INDEPENDENT_SOURCE_RIGHTS_REVIEW`
- `license_or_permission_evidence_ref=null`
- `permitted_reuse_scope=null`
- `rights_decision=null`
- `rights_cleared=false`

Important boundaries retained:
- FUSE/SPIE: the STScI one-personal-copy mirror notice is not training, modification, systematic reproduction or redistribution permission.
- Chinese TWTA DOI 2026.02.007: its article-specific licence remains unverified; a different DOI's CC BY-NC-ND notice is not transferable.
- TROPICS: NASA NTRS "use by or on behalf of the US Government" is not a general third-party licence; MIT/IEEE and contract rights remain unresolved.
- NASA-CR-66461 and NASA-TM-100232: favourable government metadata coexists with contractor/private co-author or third-party-content questions.
- NASA LLIS 1416: item-specific JPL/Caltech provenance and rights remain unresolved.
- SEASAT: public-use metadata is a lead; actual excerpt/PDF version and embedded third-party content still need scope review.

The supplemental general policy lead for a different DOI does not alter any per-source status. No legal determination or third-party permission request is claimed.

## Required next steps

Regenerate the cohort-bound review kit from the repository checkout. The output path must be new and its parent directory must already exist:

```bash
python scripts/create_l1_c2_complete_review_kit.py \
  --collection examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18_r1.json \
  --source-facts examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json \
  --output-file /controlled/review/DGSI_C2_REV1_21_tasks_REVIEW_ONLY.zip
```

This generates new independent A/B blank forms and a source-rights blank queue bound to the REV1 projection. The output is a controlled review candidate; do not publish it while rights remain pending. This invalidates all prior cohort-bound blank forms.
2. Obtain two independent qualified human reviews of all 21 REV1 tasks. Keep the two AI advisory JSONs outside the official intake.
3. Obtain source-owner/legal evidence and independent scope decisions for all seven source groups, separately covering extraction, translation/paraphrase, training, model delivery and dataset redistribution.
4. After genuine human submissions arrive, run the current-source-bound expert and rights intake preflights. Do not manually set review, rights, Gold, split or training flags.

Current counts remain: 21 synthetic review-required tasks; independent human adjudications 0; rights-cleared sources 0/7; Gold 0; official splits 0; SFT rows 0; training authorization false.
