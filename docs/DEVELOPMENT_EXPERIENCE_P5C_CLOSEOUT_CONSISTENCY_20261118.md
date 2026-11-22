# P5-C product-closeout consistency lessons — 2026-11-18

## Actual defects found

1. **AAS evidence-version drift.** The same PR added a corrected AAS RUN-03F integration note (score vector distinct from decision-threshold vector), but the frozen Evaluation Suite manifest still pointed to the **superseded** original ZIP and SHA-256. A manifest cannot claim reproducible evidence while referring to an artifact explicitly superseded elsewhere in the same handoff.
2. **Method-table vs. report drift.** The effectiveness report stated that the SOTA comparison includes Auto-Instruct, yet the method table jumped from M2 to M4. Auto-Instruct's published contribution is **candidate instruction generation and ranking for black-box prompting**, not proof that its original method directly generates complete spacecraft-diagnosis SFT targets. A downstream Auto-Instruct-style SFT arm needs a documented adaptation or must be marked NOT APPLICABLE.
3. **Product-goal drift.** An independently releasable Skill/toolkit milestone was described as if it were the DGSI product's final outcome. The user's single product goal remains a rights-cleared, human-reviewed, evidence-grounded spacecraft diagnosis SFT dataset; a toolkit handoff is useful, but is not dataset admission or final product completion.

## Correction and preventive gate

- Bind the suite to the corrected AAS ZIP filename and SHA-256, preserve the previous artifact name as a superseded audit pointer, and never redefine scores as probabilities or thresholds without source semantics.
- Restore M3 Auto-Instruct-style ranking with the actual paper and identify adaptation limits; do not fabricate model-comparison or SFT results.
- Describe the Skill as a *tooling milestone* in the dataset program, with expert review, rights, independent holdout and training authorization still blocking dataset completion.
- Add a standard-library-only regression test for these document/manifest contracts. This test is an engineering consistency check, not a substitute for scientific assessment.

## Evidence and non-actions

Source inputs: PR #159 exact parent head `4f914907613e673b7bab15bf7e194ff70772db46`; existing corrected AAS note identifies SHA-256 `ef0ca966d5b9f762945bd20502f35971f1ae87ec48a69bc3ccd4e7bdb10c5c44`; Auto-Instruct: https://aclanthology.org/2023.findings-emnlp.659/.

No original cases, L0/L1 candidate packets, reviewer receipts or source rights are modified. No synthetic case is made Gold; no data split, training, paid API or main merge is authorized.
