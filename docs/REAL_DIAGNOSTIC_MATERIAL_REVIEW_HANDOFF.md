# Real diagnostic experience — user review handoff

## Purpose

This checklist is for selecting a small number of **real or properly de-identified engineering diagnosis episodes** for DGSI SFT review. DGSI's LLM task is second-stage interpretation: it consumes upstream ML diagnosis results, diagnostic logs, spacecraft/mission context, prior experience and reviewed knowledge. It does not consume raw telemetry as the default input.

Please start with **5–10 representative episodes**, not the entire R21 dataset or a bulk export. We will assess source quality and task suitability before requesting more.

## What to provide

For each episode, provide the following as separate files where available:

| File | Required content | Notes |
|---|---|---|
| `case_manifest.json` | pseudonymous episode ID, source class, source owner/permission status, event-family ID, spacecraft/configuration pseudonym, analysis cutoff | Do not include real spacecraft identifiers if restricted |
| `diagnosis_result.json` | actual upstream ML diagnosis output: method/model/version, run ID, analysis window, status, candidates, component localization, evidence IDs, score semantics/calibration, limitations | Preserve original candidate/uncertain status; do not rewrite as confirmed |
| `diagnostic_logs.jsonl` or `.csv` | alarms, event records, operator notes, engineering analysis, maintenance/telecommand records, timestamps and time zone, author role | Keep source type and temporal order; remove names/account IDs |
| `spacecraft_context.json` | spacecraft class/pseudonym, subsystem/component configuration, relevant redundancy and hardware/software versions | Remove serial numbers and sensitive configuration values if necessary |
| `operational_context.json` | mission phase, operating mode, recent operations, environmental/mission constraints, maintenance history available at cutoff | Separate contemporaneous context from retrospective information |
| `historical_cases.json` | references to earlier cases, prior conclusion, confirmed/rejected/unresolved state, similarity basis, transfer limitations | Optional; include only if actually used or available at cutoff |
| `knowledge_refs.json` | document/reference IDs and relevant passage IDs, claim boundaries | Do not send copyrighted full documents unless authorized |
| `expert_target.json` | final adjudicated diagnosis/report, fault-source conclusion, affected components, evidence, uncertainty, corrective action, outcome status | Keep separate from LLM input; this is the hidden target for review |

If a file does not exist, omit it and state that it is unavailable. **Do not create missing fields by guessing.**

## Strict input/target separation

Use this layout for each episode:

```text
CASE-0001/
  input/
    case_manifest.json
    diagnosis_result.json
    diagnostic_logs.jsonl
    spacecraft_context.json
    operational_context.json
    historical_cases.json       # optional
    knowledge_refs.json         # optional
  target_private/
    expert_target.json          # separate from LLM prompt
    adjudication_evidence/      # optional; only material available after the cutoff
```

Everything under `input/` must have been available at the declared `analysis_cutoff`. Anything learned later (inspection result, teardown, repair confirmation, retrospective expert conclusion) belongs in `target_private/` or a post-event outcome record. It must never leak into the LLM user message.

## Do not include

- Raw telemetry arrays, waveform files, high-rate CSV time series or full telemetry databases. Those remain with upstream ML methods.
- Passwords, API keys, access tokens, personal names, account IDs or other credentials.
- Unredacted spacecraft IDs, serial numbers, ground-station addresses or sensitive mission details.
- Simulator injection truth, hidden evaluation labels or test-set answers in `input/`.
- Post-event expert confirmation or repair outcome in `input/` if it was not available at the analysis cutoff.
- Entire 56 GB R21 data packages. A diagnosis-result packet and references are sufficient for this review.

If logs contain embedded telemetry values, redact or replace those portions with references to the upstream ML evidence artifact. Keep event descriptions and engineering interpretations that are legitimately part of the diagnostic log.

## De-identification rules

1. Replace spacecraft, equipment and incident IDs with stable pseudonyms. Use the same pseudonym consistently across all files in one episode.
2. Preserve relative time order and intervals. If absolute time must be shifted, apply one consistent offset to every timestamp in the episode and record that it was shifted.
3. Preserve units, score values and score semantics. Do not normalize or reinterpret them during de-identification.
4. Preserve whether a statement was an onboard alarm, operator note, ML result, engineering hypothesis, maintenance action or confirmed outcome.
5. Preserve the distinction between fault source, affected component and system-level symptom.
6. Remove personal names but retain role labels (e.g. operator, ADCS engineer, reviewer).
7. Record any fields that were redacted or transformed in `case_manifest.json`.

## Initial sample selection

Prefer a diverse set rather than ten copies of the same failure:
- 1–2 normal/no-fault episodes;
- 2–3 cases with a machine-generated fault candidate later confirmed;
- 1–2 candidate cases later rejected or left unresolved;
- 1–2 cases with conflicting ML findings and logs;
- 1 case with insufficient evidence / missing context;
- include multiple subsystems only if the underlying diagnosis records are genuinely available.

These are selection preferences, not quotas. Do not manufacture examples to fill a category.

## What I will check for each episode

| Review dimension | Pass condition |
|---|---|
| Source authenticity and rights | Source owner and permission/de-identification basis are clear |
| Upstream diagnosis integrity | Method/version/run and score semantics are preserved |
| Temporal integrity | Input contains only information available at analysis cutoff |
| Log quality | Source type, timestamp, chronology and event identity are clear |
| Context sufficiency | Configuration, subsystem, mission phase and operating mode support interpretation |
| Historical reuse | Prior outcomes and transfer limits are correctly represented |
| Evidence integrity | Every claim/reference resolves to supplied evidence; no fabricated support |
| Target quality | Expert target is traceable, independently reviewed and outcome status explicit |
| Leakage control | No raw telemetry, injection truth, post-event answer or cross-split duplicate leaks into input |
| SFT suitability | The episode teaches second-stage interpretation, not raw signal detection |

Each episode will receive one of:
- `ACCEPT_FOR_EXPERT_REVIEW` — complete enough for an independent domain reviewer to assess.
- `CONDITIONAL_ACCEPT` — useful, but specific fields or provenance need clarification.
- `REJECT` — source, temporal, context, target or rights defects make it unsafe/unusable.
- `SYNTHETIC_TEST_ONLY` — useful for software tests, not real-experience SFT.

None of these statuses automatically means Gold. Gold requires the authorized independent expert review and the dataset's separate admission gate.

## What you should upload

Please upload a ZIP containing **5–10 de-identified case folders** following the layout above. If only a few files are available, upload those files without forcing the directory structure. You may first upload one representative episode so we can verify the handoff format before preparing the remaining cases.

Keep any raw telemetry and full restricted source records in your controlled environment. This review package should contain only the diagnosis result, diagnostic logs, context and separately held expert target needed for review.
