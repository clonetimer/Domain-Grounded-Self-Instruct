# D0 local input-file SHA-256 check — 2026-11-15

## Scope

This incremental gate complements PR #30's manifest-to-Case field binding.
It is for **authorized custodians in their own local workspace**. It never
uploads or exports restricted input files. It does not extract original
telemetry or compute a new LLM diagnosis: DGSI SFT teaches second-stage
interpretation of upstream ML findings, logs, spacecraft and mission context,
historical experience, and relevant evidence.

A handoff manifest can optionally declare an \`input_file_sha256\` object:
keys are the fixed, allow-listed input file basenames and values are lowercase
SHA-256 hex digests. The check requires exactly one hash for each input
listed in \`available_files\`, excluding \`expert_target.json\`. The private
expert target is never opened or hashed by this tool.

After the custodian has prepared a de-identified folder, run:

\`\`\`bash
PYTHONPATH=src python scripts/verify_local_case_input_hashes.py \
  --manifest /authorized/episode/input/case_manifest.json \
  --input-directory /authorized/episode/input
\`\`\`

Only enumerated input basenames are accessed. Files must be regular, must not
be symlinks, and are streamed through bounded SHA-256 hashing (64 MiB per
input). This is an integrity check, not a data-content review. On Windows,
the link checks assume a custodian-controlled, quiescent folder and do not
defend against an attacker concurrently mutating the filesystem.

## Meaning of the output

- \`input_file_sha256_matched=true\` only states that the local input bytes
  matched hashes asserted in the submitted manifest.
- Every output remains \`gold_eligible=false\`, \`training_eligible=false\`,
  \`source_rights_verified=false\` and
  \`upstream_run_authenticated=false\`.
- \`source_artifact_hashes_verified=false\` stays false because the Case
  provenance field lists hashes but does not identify which precise input
  file or authenticated upstream run produced each digest.
- A synthetic manifest stays \`SYNTHETIC_TEST_ONLY\` even with matching bytes.
- A real-source claim with matching bytes is still an **unverified claim**:
  upstream run identity, source ownership/IP permission, chronology, redaction,
  evidence attribution, true event-family identity, cross-split leakage and
  independent expert findings must be checked separately.
- Missing/mismatched hashes, absent files, unsafe links and oversize inputs
  block the local integrity stage; only fixed error codes and aggregate counts
  are emitted.

The test suite uses synthetic, freshly generated local files only. No R21
telemetry, restricted reports, logs, credentials, or expert targets were
committed to the public repository. No Gold approval, auto-split, model API
call, model training or main-branch merge is performed.
