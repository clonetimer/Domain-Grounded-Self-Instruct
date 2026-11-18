# P5-C2 main reconciliation — 2026-11-18

## Problem and source evidence

The complete implementation and RC2 delivery were on `feat/p5c2-integrated-completion-20261117`, while the default main branch contained only four files. Adoption into another feature base, and a successful feature push, did not put the toolkit on main. A separate main reconciliation was required.

| Source | Commit | Root tree | Files |
|---|---|---|---:|
| Verified RC2 integration | `b20b498b6aba84e25845505c201ef9305175eb16` | `dd61240a3bc5346682a2abd944e21379790696fa` | 354 |
| Existing main | `0e064ae5289a4cacc4b28dcb038c3843267bab2d` | `0e404d1f00f27d3eaed7cad7bd941c3ad2bc09b9` | 4 |
| Shared ancestor | `4f0d7f8db2691ec0fcf0fb1cd1860e59539a15bd` | — | — |

The histories diverged: the integration head was 927 commits ahead and 7 behind main at this audit. A complete recursive path/blob comparison and a local three-way Git merge probe were used to determine what to preserve. The probe used reconstructed trees and synthetic local parent commits solely to calculate the merge; those probe commits are not remote history.

## Resolution

- Preserve every integration file.
- Retain main-only `docs/P5C2_SPECIALIZED_TASK_REVIEW_2026-11-17.md`, preserving its original body and adding a historical note. Its old v0.2 candidate and test paths are no longer current; link the integrated 15-task candidate and disposition ledger instead.
- The evidence request matrix is byte-identical on both branches.
- Main README equals its shared-ancestor version, so the integration README is its natural successor; add current operator entrypoints and accurate dependency instructions.
- Resolve the sole add/add conflict in `scripts/create_l1_model_preview.py` using the integration implementation, blob `057c00597f8bcb09b28d4c4c82e1f258c4d0b919`. It preserves main's stage-specific fixed errors and adds atomic no-clobber publication, symlink refusal and race protection.

Before RC3 additions, this exact resolution has tree `ead095cfec356683086bbac47779cffd48109005`: 355 files, with 351 additions, 2 modifications and no deletions relative to main. These are the reconciliation-only counts, not the final RC3 file count.

## Integration contract

The feature commit records both real source parents: integration first, main second. This preserves both histories and makes the audited main head an ancestor. The destination is a main-targeted feature PR, validated on its own current head with full Ubuntu/Windows CI and the portable package workflow. Check live main/head refs before merging; a changed source requires re-evaluation rather than a forced ref update.

The package workflow now follows main push, main-targeted PRs, the legacy integration branch and the current RC3 branch. The full validation workflow already runs on push and pull_request. No branch protection or ruleset changes are part of this reconciliation.

The delivery receipt records the actual PR, final commit/tree, workflow runs and hashes after integration. This document records the source comparison and resolution; it does not substitute for those final runtime observations.

## Dataset boundary

The reconciliation and RC3 expert intake do not change the 15-task L1 candidate, its 12 referenced L0 cards, nine source event families or seven-publication rights queue. Previously issued RC2 review kits remain bound to the same candidate. No completed expert submissions, rights evidence or private reviewer identifiers are committed. Scientific approval, rights clearance and training remain separately pending.
