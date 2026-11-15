# DGSI L1/L2 target-quality review rubric v0.1

## Purpose

This rubric reviews whether an L1 task packet and its formal assistant target are suitable for expert-approved SFT preparation. It is separate from JSON/schema/CI validation.

A high score does not itself grant Gold status. Gold admission requires independent domain-expert approval, source rights, case provenance, complete input assets, evidence traceability and split-leakage checks.

## Scoring

Each dimension is scored 0, 1 or 2:
- **2 — Pass:** technically correct, supported by the supplied input, appropriately qualified and clearly expressed.
- **1 — Partial:** directionally acceptable but incomplete, ambiguous or missing an important limitation.
- **0 — Fail:** materially incorrect, unsupported, misleading or unsafe.

Weighted score = sum(weight × score / 2). Maximum 100.

| Dimension | Weight | Score 2 standard |
|---|---:|---|
| Source and synthetic-boundary fidelity | 15 | Public L0 facts are represented at their actual certainty; all generated inputs are explicitly synthetic; no invented real ML run, flight log, telemetry or expert sign-off. |
| Phenomenon analysis | 10 | Describes only supplied observations in correct time/order; separates observation from causal explanation. |
| Upstream ML interpretation | 10 | Preserves candidate/status/score semantics; uncalibrated ranking scores are not called probabilities; ML candidate is not silently promoted to confirmed root cause. |
| Fault-source vs affected-component localization | 15 | Fault source is separately identified from affected components/interfaces; multi-subsystem impact is not mistaken for multiple independent roots. |
| Evidence traceability and consistency | 15 | Every material conclusion is supported by resolvable evidence references; supporting, contradicting and missing evidence are distinguished; evidence is not assigned to unsupported candidates. |
| Uncertainty and conclusion strength | 10 | CONFIRMED / MOST_LIKELY / CANDIDATE / UNRESOLVED wording matches the evidence; alternative explanations remain open where required. |
| Historical Context use | 10 | History is used only within time and hardware applicability; confirmed, unresolved, rejected and unknown states are preserved; incompatible history is explicitly non-transferable; history never votes to confirm current root cause. |
| Disposal fidelity | 10 | Executed, planned, recommended and not-recorded states are distinct; historical action is never invented; NOT_RECORDED has no measures. |
| Follow-up action quality | 5 | Proposed checks are actionable, tied to missing evidence and clearly separated from historical disposal measures. |

## Automatic rejection gates

Any one of the following rejects the packet regardless of numeric score:
1. A synthetic field is represented as a real spacecraft event, actual ML run, real log or expert-reviewed fact.
2. A source claim is strengthened beyond its source certainty or a ground test/knowledge source is presented as an in-orbit event.
3. Internal curator prompts, reviewer questions, alternative-hypothesis checklists or quality flags leak into the model prompt or assistant target.
4. A rejected, unresolved, unknown or incompatible historical case is treated as confirmed positive evidence.
5. A post-cutoff or same-event-family history item is used as prior knowledge.
6. An uncalibrated score is presented as a probability or confidence.
7. An executed disposal action is invented or lacks required source evidence.
8. Fault source and affected component are conflated in a way that changes the diagnosis.
9. Evidence references are dangling, misattributed or do not support the attached claim.
10. Train/validation/test leakage occurs across variants from the same event family.

## Suggested disposition

- **90–100 and no rejection gate:** recommend L1 expert approval; still not automatic Gold.
- **75–89 and no rejection gate:** revise targeted fields and re-review.
- **Below 75:** return for substantive redesign.
- **Any automatic rejection gate:** reject until the defect is corrected and re-reviewed.

For real-case Gold admission, score is necessary but not sufficient. Independent expert adjudication and real-case asset/provenance checks remain mandatory.

## Review procedure

1. Freeze the exact L1 packet version and source L0 references.
2. Give reviewers the task input and formal target; keep internal curator prompts hidden during blind quality scoring.
3. Reviewers score independently without seeing the model arm or the other reviewer's scores.
4. Record each 0/1/2 score and a short evidence-based rationale.
5. Resolve disagreements through documented adjudication; do not average away a safety-critical disagreement.
6. Re-run all schema, evidence-reference, history-time, hardware-applicability and split-leakage checks after edits.
7. Preserve original, revised and adjudicated versions with hashes and reviewer status.

## Review output record

Each review record should include:
- task_id, packet_hash, source_fact_refs and track;
- reviewer pseudonymous ID, role and review timestamp;
- nine dimension scores and rationales;
- automatic rejection gate findings;
- final disposition: ACCEPT_FOR_L1_EXPERIMENT / REVISE / REJECT;
- adjudication record if reviewers disagree.

Do not store reviewer private identity in model-facing packets. Do not set `gold_eligible=true` in an L1 packet; Gold admission is a separate controlled process.
