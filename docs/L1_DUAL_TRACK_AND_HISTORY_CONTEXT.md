# DGSI L1 dual-track task packets and historical Context retrieval

## User-approved direction

DGSI uses two separate data tracks:

1. `REAL_CASE_CANDIDATE`: actual or de-identified engineering cases. They remain candidates until provenance, rights, upstream ML outputs, logs, mission context and independent expert review are complete.
2. `LITERATURE_DERIVED_SYNTHETIC`: synthetic diagnostic tasks bounded by public literature L0 fact cards. These can extend task coverage and support controlled experiments, but are never represented as real flight records or Gold.

Historical experience is used as **Context**: retrieved, time-safe case summaries and their transfer limitations are included alongside the current ML result, diagnostic logs and mission context in the LLM-facing input.

## L0 → L1 packet

Schema: `resources/l1_task_packet.schema.json`.

An L1 packet contains:
- `track`: explicit real-candidate or literature-derived synthetic classification;
- `source_fact_refs`: exact L0 source-card IDs;
- `case`: the existing DGSI diagnostic Case, including input and formal report target;
- `formal_target`: an exact copy of `case.expected_output`, checked byte-structure-equivalent after JSON parsing;
- `history_context`: retrieval mode, query scope, hit/no-hit status and historical case summaries with provenance;
- `synthetic_provenance`: mandatory for the literature-derived track and forbidden for the real-candidate track;
- `review`: L1 curation state, not Gold approval.

The L1 packet is not automatically a standalone SFT example. The later SFT exporter must still apply prompt/target serialization, review, rights, evidence-reference, split and Gold-admission gates.

## Literature-derived synthetic provenance

For `LITERATURE_DERIVED_SYNTHETIC`:
- every referenced L0 card must be a public literature source describing an event or test; knowledge-only sources such as expert-system feasibility reports cannot alone define a synthetic incident;
- `generation_recipe` and `recipe_version` identify the scenario construction process;
- each generated field is listed in `generated_fields`, with field path, origin type, source L0 refs and explicit assumption;
- machine diagnosis, diagnostic logs, spacecraft configuration and operational context each require field-level provenance;
- diagnosis run references must be explicitly synthetic identifiers, not fabricated real run IDs;
- `scenario_assumptions` state what was introduced for the scenario;
- `not_simulated` lists important source material not reproduced, including raw telemetry or actual flight-computer logs;
- `gold_eligible=false` and `real_flight_record=false` are schema constants.

A literature statement may constrain a scenario, but any ML score, alarm timestamp, operator log, equipment configuration or mission operation absent from the source is a synthetic assumption, not a historical fact. A synthetic assistant target must be a formal conclusion, not the curator's prompt or reasoning checklist.

## Historical experience as Context

The current case's `input.historical_cases` contains the historical summaries the model sees. The L1 `history_context` sidecar binds those summaries to retrieval metadata:

- query equipment scope and subsystem must exist in the current spacecraft configuration;
- mission phase and operating mode must match the current case query;
- each retrieved reference must match exactly one case history entry, including outcome status, summary, relevance basis and applicability limitations;
- no-hit must mean both the retrieval list and current-case history list are empty;
- a historical event family cannot be reused as the current incident;
- all retrieved history must have timezone-aware `available_at` no later than the current `analysis_cutoff`;
- confirmed history must pass the existing independent verification and as-of metadata gate;
- unresolved, rejected, partially confirmed and unknown history may retain its original status, but cannot be upgraded to confirmed memory or vote on the current root cause;
- hardware mismatch, expired/late availability, future verification or missing time metadata blocks or requires review.

The Context retrieval is not a separate answer-generation stage. Its qualified result is part of the same diagnostic input as current machine findings and logs.

## Required L1 task variants

The task suite should cover:
1. no historical hit;
2. relevant, independently confirmed prior case;
3. unresolved prior case that must remain unresolved;
4. rejected prior case that must not be reused as positive precedent;
5. similar symptom but incompatible hardware/configuration;
6. conflicting prior cases;
7. case available only after the current analysis cutoff;
8. same incident family incorrectly returned as history;
9. current logs contradict historical precedent;
10. history supports a mechanism but does not confirm the current fault.

## Evaluation separation

Report results separately for:
- real-case candidates and, once approved, real Gold;
- literature-derived synthetic tasks;
- synthetic task families and event families (no variant leakage across splits).

A controlled experiment may compare base model, generic Self-Instruct, literature-derived synthetic SFT, real Gold SFT (when available), and DGSI with retrieved historical Context. All arms use the same independent holdout and report fault-source localization, affected-component identification, evidence consistency, uncertainty calibration, disposal fidelity and appropriate rejection/abstention.

Synthetic task count must never be reported as real-case count. Schema/CI PASS is not scientific effectiveness evidence.


## First L1 literature-derived pilot

`examples/l1_literature_synthetic_task_packets_v0.1.json` contains three review-required packets:
1. SEASAT slip-ring arc/short candidate;
2. Lunar Orbiter III TWTA power-monitor measurement-chain ambiguity;
3. TROPICS Pathfinder cross-interface common-cause short candidate, with a rejected SEL hypothesis included as qualified Context.

All three are explicitly synthetic. Their ML scores, run IDs, event logs, spacecraft identifiers, configuration and operating modes are scenario values. The source L0 fact cards constrain the historical mechanism statement and its certainty only. No real flight logs or ML execution are claimed. Formal assistant targets contain conclusion fields only; curator prompts remain under the Case's `internal_review`.

The first pilot intentionally covers:
- no historical retrieval hit;
- a retrieved rejected history item that must remain rejected and cannot vote on the current cause;
- distinct source event families and L0 evidence references.

This is a task-coverage fixture set, not an approved training corpus. Every packet remains `REVIEW_REQUIRED`, `gold_eligible=false`, and `training_authorized=false`.

## Collection and split audit

The L1 collection contract (`resources/l1_task_packet_collection.schema.json`) requires a single data track per collection. The collection validator checks packet count, task-ID uniqueness, source-card binding and optional split assignments. When split assignments are supplied, every packet must be assigned exactly once and all tasks derived from the same `source_group` / L0 event family must remain in one split. The current three-packet pilot has no train/validation/test assignments because it has not completed review.


## L1 source-event class alignment

For literature-derived synthetic tasks, the source L0 event status and the scenario's operational context must not silently contradict each other:
- `GROUND_TEST_EVENT` requires a ground-test/TVAC context marker in `mission_phase`;
- `FLIGHT_EVENT` cannot be relabeled as a ground-test/TVAC scenario;
- a task citing multiple L0 cards with conflicting event statuses is rejected until the source/event relationship is explicitly curated.

This is a source-class consistency check, not a proof that the synthetic scenario reproduces the historical event. A literature-derived synthetic input remains synthetic and must not be represented as the original flight/test record.

## Complete review receipt coverage

The batch receipt audit requires exactly one immutable packet/L0-bound blind-review receipt per task in a collection. It rejects missing, duplicate, unknown and cross-packet reused receipts. Its output is aggregate-only and distinguishes reviewer-authentication-pending from secure-adjudication-required counts. It never approves an L1 task, grants Gold or authorizes training.
