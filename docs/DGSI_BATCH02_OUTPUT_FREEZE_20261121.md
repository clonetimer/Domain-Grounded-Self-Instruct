# DGSI Batch02 — external output freeze (2026-11-21)

**Run:** `DGSI-EXP-2X2-BATCH02-20261121`  
**Status:** `RAW_OUTPUTS_FROZEN_AWAITING_BLIND_REVIEW`  
**Classification:** `EXPLORATORY_REPLICATION_NOT_CONFIRMATORY`

The project received the user's 20 externally generated files (5 eligible anonymous source/document clusters × 4 unchanged factorial arms) as an original ZIP. The coordinator did not regenerate, revise, suppress or score any output.

## Material integrity and structural checks

| Test | Result |
|---|---|
| ZIP CRC and safe file names | PASS |
| Complete 5-case × 4-arm input matrix | 20/20 |
| JSON parsing + frozen target schema | 20/20 PASS |
| Run, case and input SHA-256 binding | 20/20 PASS |
| Instruction candidate records and deterministic selection | 20/20 PASS |
| Structured E-evidence IDs within the provided anonymous case | 20/20 PASS |
| Attached prompt bytes equal to original pre-generation prompts | 20/20 PASS |
| Pre-generation archive checksums | 34/34 PASS |
| Blind candidate instruction/target projection equal to raw output fields | 20/20 PASS |

No expert score has been assigned; raw output structure does not prove diagnostic physical correctness, external source authenticity, isolation between generation conversations, single generation attempt, or actual serving model version.

## SHA-256

- Original submitted outputs ZIP: `9dfd7e104bcb7d6cf98c1c0a0aec5ea0a1576006688552eb84255aed5f668c88`
- Pre-generation freeze ZIP: `a59ae02634bf30fee10df2106414d96b8b0772b21c2a8590b5c9e1cbada8db9b`
- Prompt-only ZIP: `fef363ef8d78ce672f6e9b4394aa8063b3153b0cadf872744bbebba2da829206`
- Prior ten-dimension 0–2 rubric: `8efead9630e565b4778b2cb68916dcf471cea3714555c173cd1a9b9f733b1db1`
- Frozen target JSON Schema: `4710df4e9fcbf7d42fcbf3f12ea6f80ce44135c8acae009e3aee1436112243c2`
- Frozen 2×2 plan: `5d32aa71681d0640da2115bd5e54e28771651753fd84f8a3b8b04ce2d06696a6`
- Anonymous reviewer delivery ZIP: `8e72f7181805da0413ad8444f8f3325e42dd47e8ae384ac1e62e32215a9f86a8`
- Private coordinator archive ZIP: `f432b11ac17a0366982be6419f654d1ca98d404ee39f36e98cefa5f57819477e`

The anonymous reviewer delivery has 20 random blind IDs, 5 approved anonymous source-fact inputs, byte-identical original instruction and target values, an unfilled 20-row `dgsi-blinded-reviewer-input.v1` scorecard, and unchanged copies of the frozen rubric and target schema. It omits the method mapping, instruction candidate selection records, source identities, source attribution sidecars and reference answers.

The private coordinator archive contains the original user-uploaded ZIP (exact bytes), raw outputs, the blind ID mapping and forensic verification. **Neither the raw submissions nor coordinator map are committed to GitHub.** The private archive is to be transferred only through the project's controlled exchange.

## Next stage

The custodian distributes only the anonymous reviewer delivery to two independent assessors and freezes both independent scorecards. The custodian subsequently checks the reference judgments held outside the generator and reviewer outputs. The coordinator then performs paired 2×2 descriptive analysis, preserving all negative outcomes and disagreements.

The review label hides arm names, but visible instruction phrasing can hint at a strategy; perfect method-blinding cannot be certified. No experimental scorecard, source identity check, expert identity attestation, or Gold/confirmed-SFT release exists yet.

**Development lessons:** Verify against the original pre-generation hashes and intact prompt bytes; protect all 20 raw generations before making blinded projections; keep coordinator mapping out of the reviewer and public-repo surfaces; classify facts that cannot independently be proven as NOT_ATTESTED rather than inventing evidence.
