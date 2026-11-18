# P5-C3 — corrected 21-task literature/history-connected holdout audit

## Input and scientific boundary

This review-only check runs against the **current, content-corrected 21-task L1 collection**, not the obsolete 2026-11-17 candidate:

- `examples/l1_literature_synthetic_task_packets_c2_coverage_candidate_2026-11-18.json`
- `examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json`

The six newly introduced tasks 016–021 are not six independent incidents. They remain linked by the same L0 family or publication. Observed structural counts for the supplied candidate: **21 synthetic L1 tasks, 9 event families, 7 primary bound documents, 6 conservative connected groups**, group task sizes `[1,2,3,4,5,6]`, and group family sizes `[1,1,1,1,2,3]`. A prior review-only check for 15 tasks reported six groups with different sizes; that old result must never be used as a count for this cohort.

## Procedure

`dgsi.l1_holdout_independence.audit_l1_holdout_independence` validates the L0/L1 candidate and joins tasks sharing an event family, bound primary publication, or retrieved historical source that is also referenced by a target task. The group pressure report contains **counts only** and authorizes neither training nor any split. `check_hypothetical_holdout_partition` is a testing helper for detecting assignments that cross connected groups; passing it does not approve a formal split.

Run:

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_l1_holdout_independence.py' -v
```

The tests cover the 21-task current snapshot, TROPICS shared publication, FUSE↔Cassini historical reference, multiple Lunar episodes, *all six* new task variants 016–021, source-id collisions, incomplete and invalid hypothetical partitions, and explicitly blocked training/Gold/split flags.

## Scientific and legal limitations

This graph cannot infer undocumented aliases, unpublished/uncited derivatives, real-world hidden incident duplicates, or a foundation model's pretraining exposures. It is conservatively metadata-based and must not be read as statistical sample independence. Six structural groups do not mean six scientifically accepted groups or adequate holdout sample size. The new conflict-reconciliation and justified-abstention inputs are synthetic, with fields/measurements and ML scores declared as synthetic; nothing is promoted into REAL Gold. L0 and L1 remain pending domain-expert adjudication; source-rights verification, official split assignment, SFT export, and fine-tuning remain blocked.

The preceding P5-C3 proposal is [PR #149](https://github.com/clonetimer/Domain-Grounded-Self-Instruct/pull/149), based on an older feature branch. This independent follow-up deliberately uses the latest main's corrected cohort and does not rewrite historic L0/L1 files. Do not merge it without explicit user authorization.


## Cross-platform portable archive regression and fix (2026-11-18)

Exact head `01531db70dabbf9d04d609f86d52ce4956a93643` exposed a **real Windows CI failure**, although Ubuntu and the Ubuntu-only portable package workflow passed: `test_builder_emits_verified_source_only_archive` expected the frozen RC4 toolkit SHA-256 `6a96983b2aa07f3cb68358f34d19b54534530f693e769e682d65f6f6c647f2b9`, but the Windows checkout produced `2183f0792ecfa708ba185c056f37444ea1dbe72f4320de9c4eb65f4080724fb8` ([run 44273599422](https://github.com/clonetimer/Domain-Grounded-Self-Instruct/actions/runs/44273599422)). This is a **failed engineering gate**, not a passed PR; the earlier successful head is not valid acceptance evidence.

The packaging script previously pinned ZIP metadata but read every member directly from the checkout. On Windows, Git may materialize UTF-8 text with CRLF rather than the LF bytes used on Linux, changing both the ZIP and its per-file manifest. The corrective source-byte transformation normalizes CRLF to LF for decodable NUL-free UTF-8 text **before** building member hashes and ZIP entries. NUL-containing or non-UTF-8 binary members remain byte-identical. A new synthetic adversarial suite checks equivalent Windows/Linux text bytes, mixed UTF-8 text and untouched binary content. The previously issued Ubuntu RC4 archive hash remains the acceptance target; do not update that expected checksum to disguise the failure.

Full exact-head Ubuntu **and** Windows regression plus portable-package workflow must pass after the fix. Until both have completed, this branch remains unaccepted. This change never touches the candidate dataset, immutable L0 facts, review receipts, Gold, splits or training authorization.
