# P5-C1 real-case intake: five user-supplied cases

Status: REAL_CASE_CANDIDATE only. The original source document remains in the user's Library and is not copied into this repository. This register is a controlled transcription of the separately reviewed L0 facts, not a complete diagnostic task packet.

## Source inspected
- Original: `故障案例参考.docx`, user-supplied.
- Reviewed transcription: `DGSI_用户原始5例_正式结论与内部审核分离_v0.1.docx`.
- The transcription explicitly separates formal conclusion fields from internal review prompts.
- The user's earlier statement that the root-cause localizations are broadly accurate is retained as general curation feedback, not as five independent expert approvals.
- The source does not provide upstream ML results, diagnostic logs, spacecraft/mission context or independent expert adjudication. These fields remain missing.

## Five candidate cases

| Case ID | Domain | Source disposal notation | Principal unresolved issue |
|---|---|---|---|
| USER-ADCS-SADA-001 | ADCS | SOURCE_RECORDS_MEASURE | Measurement point definitions, chronology and execution/effectiveness of solar-array shutdown |
| USER-COMM-TWTA-002 | COMM | SOURCE_RECORDS_TEXT | Meaning of “可自行恢复”; no recovery action or verification described |
| USER-COMM-KU-TWTA-003 | COMM | SOURCE_RECORDS_CONDITIONAL_PROCEDURE | Three conditional branches must not be represented as executed actions |
| USER-PROP-THRUSTER-004 | PROPULSION | SOURCE_RECORDS_MEASURE | Temperature/thrust measurement basis, momentum-wheel and attitude timeline, evidence for structural damage |
| USER-ADCS-RW-BEARING-005 | ADCS | SOURCE_RECORDS_CONDITIONAL_MEASURE | Distinguish configuration switch from conditional 2000 rpm recommendation and actual execution |

The machine-readable register records case IDs, source state, missing evidence and review gates without copying the original document's detailed narrative into the repository.

## Production interpretation

These five records are materially different from the literature-derived synthetic pilot:
- They are real-case candidates based on user-supplied engineering material, not literature-derived synthetic scenarios.
- They are not yet complete LLM diagnosis inputs because upstream ML outputs, logs and mission context are missing.
- They are not REAL_GOLD and cannot be counted as SFT-eligible examples.
- The source's stated cause localization is preserved as supplied; it is not silently upgraded to a certainty level the source did not state.
- Disposal status is typed separately from actual execution. A conditional procedure or recommendation is not an observed action.

## Next evidence request

For each candidate, obtain only the missing evidence that exists and is authorized:
1. upstream ML result, algorithm/model version, run identifier, score semantics, candidate status and evidence IDs;
2. timestamped diagnostic logs and time-aligned event chronology;
3. spacecraft configuration, subsystem/component mapping, mission phase and operating mode;
4. measurement point definitions, units and provenance for temperature, current, power, thrust and wheel-speed observations;
5. actual disposal execution record and post-action verification, if available;
6. two independent expert assessments and secure adjudication of disagreements.

If an item does not exist, keep it explicitly unavailable. Do not manufacture a plausible ML result, log sequence, mission mode or action record to make the case appear SFT-complete.

## Privacy and admission boundary

The original Word file is not committed. Detailed case material should remain in the user's authorized private workspace until source rights, de-identification, repository access and intended training use are confirmed. The repository's access setting is not a substitute for a source-use decision.

The five cases remain REAL_CASE_CANDIDATE, with zero independent expert approvals, complete DGSI input packets, REAL_GOLD admissions, authorized SFT records or training permissions.
