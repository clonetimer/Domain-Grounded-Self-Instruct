# Simulation run receipt intake — bounded design

User-approved scope: continue Skill engineering without waiting for test reports or actual logs. Keep design-derived candidates distinct from simulator runs. The next deliverable is a portable, local-only receipt validator with explicit test fixtures, not a simulator or SFT exporter.

## Implementation choice
Add a separate `dgsi-simulation-run-receipt.v1` contract and offline CLI, building on PR #75 (`596963adf8929df30a5bc3420ddac0df02df8023`). Do not widen the existing L1 enum or weaken its release gate. A receipt contains run/build/configuration identity, artifact hashes, declared availability times and six independently reported evidence stages. It never contains diagnosis targets or injected fault values. Artifacts remain local; CLI prints fixed errors and aggregate counts only.

Alternatives considered: adding only enum values would disguise missing evidence checks; using the specific R84-R3A adapter would falsely imply arbitrary Simulink/Basilisk runs meet its frozen experiment contract. A separate intake layer avoids both.

## Evidence stages
`injection_configured`, `injection_executed`, `physical_effect_observed`, `diagnostic_effect_observed`, `upstream_ml_detected`, `upstream_ml_localized`. Values YES / NO / UNKNOWN. YES and NO require references with stage-appropriate roles; UNKNOWN is never silently inferred to be NO. Do not infer later stages from earlier ones, and allow ML false positives/negatives as legitimate recorded outcomes.

## Security and correctness
Strict nested schema; reject duplicate JSON keys and nonfinite values; timezone-aware timestamps; verify each declared local artifact's length/hash; portable relative paths only; reject traversal, symlinks, cross-run references and cross-visibility aliases; verify model-visible references and declared cutoff. Inspect JSON/JSONL visible records for a bounded set of label/target/injection keys. No claim of exhaustive semantic leak detection, source authentication, independent physics validity or calibrated diagnosis.

Nominal and fault-test runs are both allowed. Replay metadata binds the declared scenario/family; it does not certify replay equality. Synthetic test artifacts are explicitly marked SYNTHETIC_TEST_ONLY, cannot be renamed to an actual run without rejection, and are never training examples.

## Deliverables and non-goals
Python 3.11+, jsonschema >=4.22,<5; standalone runnable subset ZIP; fixture builder; adversarial tests and human-readable Chinese handoff. No original design report or derivatives added to the public changes. No external model calls, paid API use, real-run acceptance, official split, Gold, SFT or training authorization.
