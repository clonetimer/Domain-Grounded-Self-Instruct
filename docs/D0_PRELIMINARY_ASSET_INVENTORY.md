# D0 preliminary asset inventory — diagnosis/context SFT

Date: 2026-11-14
Scope: read-only source inspection of the connected AstroGraph-LLM, SatAgentSimulation and DGSI repositories.
Status: preliminary inventory; no private telemetry or operational records copied.

## Executive finding

AstroGraph already contains a much closer match to the intended LLM task than the previous DGSI telemetry-first proposal: the **result + logs + reference** workflow and its case packets.

The clearest reusable source family is:
- `examples/platform_acceptance_cases_v1/`
- `examples/result_log_review/`
- `src/astrograph/resources/mission_demo_cases.json` (appears to duplicate/embed several acceptance cases and must not be counted as independent cases)

These are explicitly synthetic acceptance fixtures. They are useful for defining task coverage and testing the new schema, but **they are not real operational diagnostic experience and their expected outputs are not expert-approved Gold labels**.

## Asset inventory

| Repository / asset family | What it contains | Intended DGSI role | Current evidence status |
|---|---|---|---|
| AstroGraph `examples/platform_acceptance_cases_v1/` | Diagnosis result JSON, operations LOG/CSV, reference Markdown, expected output assertions | Primary schema/task-design source; synthetic pilot fixtures | Synthetic functional tests; not Gold |
| AstroGraph `examples/result_log_review/` | One result + operations log + reference example | Minimal end-to-end packet mapping | Synthetic demo |
| AstroGraph `src/astrograph/resources/mission_demo_cases.json` | Embedded demo packets for several of the acceptance cases | UI/demo fixture only; deduplicate against canonical case directories | Synthetic; not independent |
| AstroGraph `protocols/diagnosis/unified_diagnosis_result.schema.json` | Upstream machine diagnosis status, candidates, engine runs, evidence and data-quality profile | Map upstream ML result metadata into DGSI input | Structured interface contract, not a case corpus |
| AstroGraph `configs/training/review-draft.schema.json` | Source-grouped candidate tasks with candidate output and REVIEW_REQUIRED state | Reuse review lifecycle ideas | Schema only |
| AstroGraph `configs/training/generated-example.schema.json` | Source-grounded generated examples with automated-only review state | Reuse generated/Silver state semantics | Schema only; current task enum does not include diagnostic report |
| AstroGraph diagnostic memory profile/policy | Evidence ledger, claim/evidence/validation lifecycle, reviewer allowlist and case cap | Historical experience governance design | Policy/profile only; not a historical case corpus |
| AstroGraph `reference/evidence_sources/reaction_wheel_dataset_manifest.json` | 90 completed D3 reaction-wheel engineering simulation runs, 30 nominal + 30 friction + 30 torque-authority-loss | Upstream ML evidence provenance and possible diagnosis result source | E0 engineering synthetic assumptions; manifest only |
| AstroGraph `configs/datasets/adcs_v5_2_2/` | 14-class ADCS synthetic candidate universe, ontology, telemetry projection and runtime evidence | Upstream ML diagnosis vocabulary/lineage | Internal synthetic; previously accessed; not independent confirmatory data |
| AstroGraph R21 exposure registry / failure reports | Exposure controls and post-hoc failure analysis for DXC09, OPS-SAT and ESA | Leakage/holdout governance and ML method provenance | Existing evaluation evidence; not an ADCS expert diagnosis log corpus |
| SatAgentSimulation `data/training/taskspec_lora_v5_current_prompt_event_aligned/` | 588 train + 69 validation TaskSpec examples | Possible upstream agent/task interface reference | Labels are synthetic registry contracts; student accuracy NOT_EVALUATED; not diagnosis experience SFT |
| SatAgentSimulation AstroGraph RW factory | 45 fault runs + 45 nominal paired runs planned; documented default producer is deterministic non-Basilisk engineering proxy | Upstream ML/simulation result generation only | Do not treat proxy outputs as native physical truth |
| DGSI P1 source passages and terms | 33 source registry entries, 42 passage records, ADCS/EPS term catalogs | Knowledge evidence and terminology constraints | Reference locators and draft terms; not diagnostic episode data |
| DGSI P2 Basilisk receipt adapter | Provenance checks for R84-R3A native pilot | Upstream simulation evidence lineage | Provenance/observability only; not LLM prompt data or diagnosis SFT |

## Canonical synthetic case coverage observed

| Case | Upstream result | Logs/context | Expected behavior | DGSI task family |
|---|---|---|---|---|
| TC01 ADCS RW friction | One unverified friction-increase candidate | Current/temperature/control-mode log + synthetic handbook | Provisional log cue; do not confirm root cause | diagnostic_synthesis |
| TC02 EPS battery resistance | One unverified internal-resistance candidate | CSV current/voltage/temperature + table/reference | Separate load step, temperature and sensor-bias alternatives | diagnostic_synthesis |
| TC03 star tracker dropout | Unverified star-tracker candidate | Logs lack the key star-tracker status evidence | Preserve candidate as uncorroborated; state missing log evidence | evidence_sufficiency |
| TC04 undocumented propulsion code | Unknown fault code candidate | Generic logs and reference without code-specific mechanism | Do not invent mechanism; retain unknown/unverified | conflict_reconciliation / evidence_sufficiency |
| TC05 log anomaly, no ML candidate | Upstream result says NORMAL/no candidate | Log contains a fault keyword | Do not create a fault diagnosis from a log keyword alone | evidence_sufficiency |
| TC06 two candidates | Star-tracker and transmitter candidates | Two log groups + long multi-section reference | Keep candidates separate; no unsupported cross-subsystem causal link | conflict_reconciliation |
| TC07 missing reference | Diagnosis result + log, required reference absent | Preflight negative case | Block analysis before generation | data_quality gate; not a report SFT target |
| TC08 prompt-injection reference | Heater-stuck-on candidate | Logs + untrusted reference instruction | Treat reference as evidence, not instruction; no control authorization | safe_handover / conflict_reconciliation |
| TC09 optional graph construction | No upstream diagnosis packet | Reference document for graph construction | Separate knowledge curation workflow | Not a diagnostic SFT case |

All TC01–TC09 fixtures are explicitly synthetic. Their `expected_output.json` files mostly assert workflow state, provisional candidate status and safety boundaries. They are not full expert-written diagnostic reports and must not be promoted directly into SFT assistant targets.

## Duplicate and lineage warnings

1. `mission_demo_cases.json` embeds several of TC01/TC02/TC04/TC06. Treat it as another representation of the same synthetic fixtures, not new independent cases.
2. A single case appears in multiple forms (analysis_input, diagnosis_result, operations, reference, expected_output, generated report). These are one episode group, not separate training examples.
3. Do not include `expected_output.json`, hidden QA fields or simulator injection truth in the LLM user message.
4. TC07 is a negative preflight test, not an example of a completed diagnosis report.
5. TC09 belongs to document/knowledge graph construction, not diagnosis interpretation.
6. The public DGSI repository must not receive R21 private traces, production diagnosis reports or restricted logs.

## Data gaps blocking real Gold SFT

- No reviewed real spacecraft diagnosis report/log/context packet has been verified in this repository inspection.
- The acceptance fixture diagnosis outputs are sparse: often only candidate_fault_id + short summary + UNVERIFIED.
- The examples do not provide a consistent spacecraft configuration, mission phase, operating mode, maintenance history or complete event timeline.
- The expected outputs are mostly workflow assertions, not comprehensive report targets.
- The current public fixtures do not constitute a historical experience corpus with confirmed / rejected / unresolved outcomes and transfer boundaries.
- The generated-example schema only allows ONTOLOGY_EXTRACTION and RETRIEVAL_QUERY; it needs the new diagnostic SFT schema for DIAGNOSTIC_REPORT-like tasks.
- Actual reviewer identity, review timestamp and approval evidence must be tied to a trusted expert workflow; a string field alone is insufficient.

## Recommended next action

1. Use TC01–TC08 as **synthetic schema and task-coverage fixtures only**; map their fields into the new DGSI diagnostic-case contract, preserving their unverified status.
2. Inspect the actual AstroGraph local workspace / restricted case store for real diagnosis reports, result bundles, diagnostic logs, reviewer dispositions and operational context. Perform aggregate inventory only and keep payloads local.
3. Select 5–10 real or properly de-identified cases with complete source lineage for manual expert review.
4. Build 20 case packets only after the real source material is available; synthetic fixtures can test the pipeline but cannot substitute for real reviewed experience.
5. Expand to 300–500 SFT examples only after expert-reviewed case density, deduplication and episode-level split feasibility are established.

## Key references

- AstroGraph acceptance cases: `examples/platform_acceptance_cases_v1/README_使用说明.md`, `EXPECTED_RESULTS.md`.
- Unified diagnosis contract: `protocols/diagnosis/unified_diagnosis_result.schema.json`.
- Review draft contract: `configs/training/review-draft.schema.json`.
- Generated example contract: `configs/training/generated-example.schema.json`.
- Diagnostic memory policy/profile: `configs/memory/diagnostic.policy.json`, `diagnostic.profile.json`.
- R21 real-data limitations and exposure controls: `docs/ASTROGRAPH_R21_REAL_DATA_FAILURE_MECHANISMS.md`, `configs/evaluation/r21_data_exposure_registry.v1.json`.


## Local restricted-case inventory

A read-only local inventory utility is available:

```powershell
python scripts/inventory_diagnostic_case_assets.py --root "D:\\restricted\\diagnostic-cases" --output "D:\\restricted\\dgsi-inventory.json"
```

The tool writes only aggregate metadata and hashed case references. It does not export diagnosis text, log lines, reference contents or telemetry rows. It flags synthetic fixtures, hidden-truth/label-assisted results, incomplete diagnosis/log/context packets, missing expert approval and CSV files that may be telemetry rather than event logs.

The inventory output is intended to remain in the restricted local workspace. Do not upload it if hashed case identifiers or file counts are considered sensitive by the data owner. A result of `READY_FOR_MANUAL_CONTENT_REVIEW` is not Gold approval; a qualified reviewer must inspect the actual local packet.
