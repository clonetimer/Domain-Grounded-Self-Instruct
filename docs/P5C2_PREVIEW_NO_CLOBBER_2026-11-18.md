# P5-C2 — Atomic no-clobber protection for L1 model previews (2026-11-18)

## Why this change is necessary

The existing `create_l1_model_preview.py` CLI used `Path.exists()` followed by `write_text()`. This is a time-of-check/time-of-use race: another writer can create or replace the output path after the check. A dangling symlink also reports `exists() == False` and can redirect the output into a different file. The blind-review JSON CLI was hardened in PR #131/#134, but the model-preview CLI retained this separate vulnerability. The fix does not change any L0 fact card, L1 candidate, formal target, source reference, or gate.

The generated **15-task / 9-event-family** preview is a review-only, potentially model-facing rendering of candidate **LITERATURE_DERIVED_SYNTHETIC** packets. It is not approved SFT and may contain synthetic ML/log/context and canonical targets. Do not publish it as a real mission record, use it for training, or upload private documents into the repository.

## Deterministic behavior and no-clobber contract

1. Validate the whole synthetic collection and its L0 sources before writing.
2. Render JSON using `allow_nan=False` and write the complete content to `tempfile.mkstemp` in the output directory.
3. Publish via `os.link(temporary_path, requested_output_path)`: this atomic directory-entry creation fails if **any** output entry exists, including a regular file or dangling symlink. Only one simultaneous writer can succeed.
4. Remove the temporary name after the publish attempt; do not use `rename`, `replace`, `copy`, `open("x")`, or an `exists()` precheck as a fallback. When the filesystem does not support hard links, fail closed and request an operator-controlled compatible destination.
5. Preserve `preview_only=true`, `export_authorized=false`, `split=null`, `sft_records_emitted=0`, `training_authorized=false` in all successful previews. A programmatic preview is not proof of scientific correctness, source rights, reviewer independence, SFT release, or authorization to fine-tune.

## Regression evidence to obtain before integration

Run `python -m unittest tests.test_l1_model_preview_cli_no_clobber` with the repository `src/` on `PYTHONPATH`, and the full Ubuntu/Windows matrix at the **exact final PR head**. Tests are labeled `SYNTHETIC_TEST_ONLY` and cover the 15-task candidate preview, existing-file preservation, dangling symlink redirection (conditionally skipped where OS permissions forbid creating symlinks), concurrent writers, and unsupported hard links. Record any platform skips instead of claiming the skipped adversary ran.

## Boundaries and development lesson

This is a local write-safety guard, not an immutable audit log, source-rights system, or security boundary against an attacker with control of the output directory. An abrupt termination can leave an orphaned temporary name. Operator access controls and frozen L1/L0 snapshot hashes still apply. **Review all file-writing CLI entry points independently**: a fix in the blind-review generator does not automatically protect the three-message model preview, nor does a green PR prove every sibling branch includes the change. Reconcile the complete integration tree and rerun exact-head required CI.

No Gold promotion, formal train/validation/test assignment, SFT authorization, model API calls or fine-tuning is introduced.
