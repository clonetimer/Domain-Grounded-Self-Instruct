# DGSI Batch 01 v6 — one-time exploratory 2×2 preflight

**Run ID:** `DGSI-EXP-2X2-BATCH01-20261120`  
**Classification:** `EXPLORATORY_NOT_CONFIRMATORY`  
**Status:** `BLOCKED_BEFORE_GENERATION`  
**Authorization:** User authorized one one-time exploratory 2×2 comparison of CASE-002 and CASE-004 on 2026-11-20.  
**Structured record:** [`evaluation/exploratory_20261120/batch01_preflight.json`](../evaluation/exploratory_20261120/batch01_preflight.json)

## 1. Material receipt and integrity

Custodian batch: `DGSI-BATCH01-20261120-v6`  
Receipt: `DGSI-CUST-MATERIAL-RELEASE-20261120-008`

The uploaded developer ZIP was inspected. ZIP CRC passed; all 9 entries in `SHA256SUMS.txt` matched; both JSONL input strings exactly matched their corresponding UTF-8 TXT files; both input hashes matched the release manifest.

| Case | Candidate | Source cluster | Input SHA-256 | Custodian material decision |
|---|---|---|---|---|
| CASE-002 | CAND-002 | CL-002 | `31358c03020e734833519c3cbef677442c66bab3c0a018f2c7759d00140e95c3` | Released for internal evaluation |
| CASE-004 | CAND-004 | CL-004 | `3c1932c30d32d90f63c8b0f2cd30d96f9c012f2439d5ce1232be91fa6f1179f2` | Released for internal evaluation |

Batch ZIP SHA-256: `50d3730693bf95c5ce8e6620ab4cc40fb880040173f9936dd2923043ba725ea9`.

The receipt releases two anonymous inputs for closed internal evaluation only. It does not freeze the whole study or authorize the confirmatory preregistered run. The original 5–10 independent-cluster collection target remains unmet.

## 2. Exploratory scope authorized by the user

The only authorized exploratory matrix is:

| Arm | Evolution | Three-candidate selection | Formal target per case |
|---|---:|---:|---:|
| A | Off | Off | 1 |
| B | Off | On | 1 |
| C | On | Off | 1 |
| D | On | On | 1 |

Planned total: 8 formal targets (4 arms × 2 cases). Each arm must see identical case bytes and the same output schema and frozen scoring contract. Selection-enabled arms generate exactly three instruction candidates; selection is over instructions only, followed by one formal target. No retries, regeneration, post-hoc repairs, prompt tuning or threshold changes.

This two-case/two-cluster result is descriptive and exploratory only. It cannot establish statistical significance, population-level effects or DGSI superiority. The custodian records post-baseline developer exposure as NOT_ATTESTED, foundation-model pretraining exposure as UNKNOWN, and source re-identification risk as possible but not empirically tested.

## 3. Frozen artifacts and analysis contract

- Target schema: `evaluation/refinement_20261119/target_schema.json`
- Frozen target-schema SHA-256: `4710df4e9fcbf7d42fcbf3f12ea6f80ce44135c8acae009e3aee1436112243c2`
- Existing factorial scoring dimensions (0–2 each): source fidelity, phenomenon analysis, ML interpretation, fault source, affected components, evidence fidelity, uncertainty, disposal fidelity, historical context transfer, engineering actionability.
- Two method-blind reviewer tokens are required per case per arm by the existing scorecard contract.
- The existing descriptive analyzer reports per-case and per-cluster results, the evolution main effect, selection main effect and interaction; it does not infer significance from two clusters.

The original confirmatory preregistration at `evaluation/refinement_20261120/factorial_preregistration.json` is unchanged. It remains `PREREGISTERED_DESIGN_ONLY_NOT_RUN`; its untouched-source minimum and `DO_NOT_RUN` rule remain in force for the confirmatory study. This addendum does not change that study's status.

## 4. Pre-generation blockers

### 4.1 Existing task and system instructions are identified

The batch can reuse the existing project instruction pair without adding a new task instruction:

- System prompt: `examples/diagnostic_context_sft_illustrative.json`, SHA-256 `88077b2e1a29e8752035fe66200ef8add5e99c623d7d3e24c234c215efa1ab40`.
- Base task instruction: `examples/diagnostic_context_case_illustrative.json`, SHA-256 `91f288d07b8e713e622e79962b374dd0dea52ad0de4f572ef88ac84011db767d`.
- Shared evidence/scope policy: `src/dgsi/instruction_design.py`, with the same policy hash across all four arms.

The old M4 common prompt in `evaluation/refinement_20261119/prompts/M4.json` is **not reused**: it is a development-run meta-prompt that labels all inputs SYNTHETIC and restricts citations to LOG/ML IDs. Those details do not match Batch 01. This does not require changing the task instruction or rubric. For Batch 01, citations must use only the evidence identifiers actually visible in each input: CASE-002 `E01–E03`; CASE-004 `E01–E05`. No LOG IDs, ML findings, timestamps, measurements or other missing fields may be invented.

The absence of upstream ML outputs, structured logs, historical cases and raw telemetry is itself part of the input boundary. A valid target must state those absences rather than fabricate them. The ten existing score dimensions remain unchanged.

### 4.2 No isolated factorial model-execution route is configured here

The current execution environment has no `OPENAI_API_KEY`, `DGSI_GENERATOR_MODEL` or `DGSI_JUDGE_MODEL` configured. The repository's existing `scripts/run_skill_blind_eval.py` is a baseline-versus-Skill evaluator, not a four-arm factorial generator. The GitHub connector available in this session supports repository reads/writes but exposes no workflow-dispatch action for launching a live model run.

A single in-context assistant response containing eight outputs would not constitute eight isolated model calls: later arms could be influenced by earlier generated outputs. It must not be represented as an independent 2×2 run. No model output has been fabricated to fill this gap. An isolated generator execution route is still required before the authorized run can start.

### 4.3 Independent review remains separate from material release

The v6 receipt records zero human expert signatures and a same-model, shared-context, sequential two-role technical review. It does not satisfy a claim of independent human expert adjudication. The existing scorecard requires two method-blind reviewer tokens per case per arm. Any model-only scoring must be labeled advisory, not independent expert review.

## 5. Reference-answer handling

The custodian's reference answers are **not needed before generation** and must remain escrowed. They become relevant only after all eight outputs, effective instructions, method records and raw-output hashes are frozen. Only then may the custodian release the reference answers to the scoring/adjudication stage. They must never enter generator prompts, instruction-candidate scoring, selection or generation logs.

## 6. Isolated-session prompt pack prepared

A prompt pack was prepared from the existing system prompt, base task instruction, shared DGSI policy, the four frozen arm recipes, the released input bytes and the unchanged target schema:

- File: `DGSI_BATCH01_Exploratory_Prompt_Pack_v1.zip`
- SHA-256: `db509d57edee6d6aef255e1869c29930e703f57d2ceb626f83219f778a29b56f`
- Contains 8 one-run prompt files (A/B/C/D × CASE-002/CASE-004), the exact target schema, a run ledger template and execution instructions.
- ZIP CRC: PASS; internal SHA-256 entries: 11/11 PASS.

The pack is designed for **eight separate fresh ChatGPT conversations**, one prompt per conversation, to prevent one arm's output entering another arm's context. Do not upload the entire pack into one conversation. Save each raw response unchanged; invalid/blocked outputs remain visible and are not regenerated. The custodian's reference answers remain escrowed until all eight outputs and their hashes are frozen.

This pack is an execution aid, not evidence that any model call has occurred. The current session cannot launch those eight isolated conversations or call a configured external generator; the run remains blocked before generation.

## 7. Current run ledger

| Item | Count/status |
|---|---:|
| Authorized cases | 2 |
| Reviewed source clusters in this batch | 2 |
| Planned arms | 4 |
| Planned formal targets | 8 |
| Generation started | No |
| Generated targets | 0 |
| Frozen output hashes | 0 |
| Blind reviews | 0 |
| Scorecard | Not created |
| Confirmatory preregistration | Unchanged / NOT_RUN |
| Training / SFT authorization | None |

**Conclusion:** material integrity checks passed, the existing compatible task/system instruction pair is identified, and the user's exploratory scope is recorded. The run is not yet executable because this session has no isolated model-execution route; two method-blind reviewers are also not yet assigned. No generation, scoring, training, prompt change, rubric change or evaluation-set change has occurred.
