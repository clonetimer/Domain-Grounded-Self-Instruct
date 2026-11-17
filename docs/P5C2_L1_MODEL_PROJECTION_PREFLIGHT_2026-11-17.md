# P5-C2 model-facing L1 projection boundary — preflight only

Status: **BLOCKED_PENDING_EXTERNAL_ADMISSION**. No dataset release, SFT example output, Gold promotion, split assignment, paid API call or fine-tuning.

## Verified scope

The current L1 pilot contains 15 LITERATURE_DERIVED_SYNTHETIC task packets across nine independent source event families. Each has curator-only \`case.internal_review\`, review status metadata and synthetic source/field provenance. These are **not** model-facing input fields.

\`src/dgsi/l1_model_projection_audit.py\` establishes a narrow dry-run:
1. Reject REAL candidates (a separate trusted REAL admission workflow is required), malformed inputs, prohibited curator/reviewer keys at any depth in the candidate input or target, unexpected input/target fields, raw telemetry as a default input, and unreviewed instruction templates.
2. Reuse the full L1 packet/L0 lineage validator. Only the existing three instruction templates are allowed. The input allowlist is the current nine-key contract (including optional telemetry_reference).
3. Reconstruct, **in memory only**, the candidate user view from case_id, task_type, an reviewed instruction template, input and an explicit \`SYNTHETIC_NOT_REAL_ML_OR_FLIGHT_LOG\` marker. Use \`packet.formal_target\` alone as the canonical target (and require equality to case.expected_output through the validator).
4. Return only SHA-256 fingerprints and fixed metadata. Never return a user message, target, complete sample, internal review, reviewer identity, synthetic recipe or evidence passage. The release gate remains permanently blocked here.

The projection digest is for local integrity checking, **not** a license, review signature, released training row, or permission to train. A hash is not proof of clinical/engineering correctness or dataset independence.

## Risk isolation and test coverage

Twelve SYNTHETIC_TEST_ONLY regressions cover all 15 existing packets; curator/reviewer note changes not modifying model-facing digests; input mutation changing only the user digest; duplicate-target drift; nested curator contamination; unapproved instruction injection; raw telemetry inclusion; new unreviewed input/target fields; REAL-track misuse; and unresolved L0 references.

## Remaining admission blockers

- Domain-expert validation of 12 referenced L0 facts and 15 L1 target/evidence assignments.
- Source-use/IP/privacy review and authenticated independent reviewers. Public accessibility alone is not training permission.
- Scientific plausibility of generated ML/log/task context, historical as-of correctness and event-family independence.
- No official train/validation/test split, no REAL Gold, no training authorization, and no SFT export.

Do not wire this audit to a serializer or reinterpret its blocked result as a positive release decision. Any actual output requires a **separately designed, independently reviewed and explicitly authorized** release path.
