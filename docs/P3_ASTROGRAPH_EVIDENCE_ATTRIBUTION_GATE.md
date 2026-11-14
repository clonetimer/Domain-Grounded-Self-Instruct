# P3 — AstroGraph candidate/evidence attribution gate (2026-11-15)

## Observed upstream contract and reproducible defect

Source: `clonetimer/AstroGraph-LLM/protocols/diagnosis/unified_diagnosis_result.schema.json` on the inspected `main` branch. The `UnifiedCandidate` record contains `effect_id`, `support_engines`, `contradicting_engines`, `screening_score` and `evidence_summary`, but **does not contain a candidate-specific `diagnostic_evidence[].evidence_id` mapping**. The global `diagnostic_evidence` list is not a claim that every entry supports every candidate.

The DGSI adapter previously assigned the complete global evidence-ID list as the `supporting_evidence_ids` of **each** candidate. For contradictory or multiple-candidate results, this creates an unsupported claim of corroboration. It would materially degrade `conflict_reconciliation`, `diagnostic_synthesis`, and `evidence_sufficiency` SFT targets.

## Implemented conservative contract

- Unified fault candidates retain status and unmodified numeric screening scores, explicitly marked **not calibrated probability**.
- Candidate `supporting_evidence_ids` stays empty until an upstream, independently verifiable candidate-to-evidence binding exists. Global diagnostic evidence is still exported as separately attributed derived-evidence findings.
- If an upstream candidate declares contradicting engines, its limitations explicitly require conflict reconciliation. An engine ID is not silently rewritten as an evidence ID.
- Missing or non-`false` `truth_used` / `labels_used` for unified results is **blocked**. Schema-level defaults are not evidence that an executed upstream diagnostic run excluded truth/labels. Legacy files may lack these flags, but they still need independent source provenance audit; their absence is never Gold approval.
- Reject malformed, duplicated or empty evidence IDs and candidate effect IDs, nonfinite/non-numeric/out-of-range screening scores, ill-typed engine references and unrecognized upstream schema versions.
- Payload-bearing error values are not echoed, reducing inadvertent disclosure from private records.

## Safe verification

`tests/test_astrograph_evidence_attribution.py` exercises **SYNTHETIC-only** contradictory two-candidate cases and adversarial provenance/evidence values. Existing TC01–TC09 remain explicitly synthetic and unchanged. Their legacy results must not be mislabeled as real diagnostic experience or expert-approved Gold.

This patch changes no source cases, historical data, split assignments, or raw-telemetry processing. No R21 data, operational logs, credentials or restricted reports are embedded in these tests. The result is **adapter safety**, not real dataset yield or expert diagnostic accuracy.

## Next source-facing dependency

For a real candidate, obtain authorized upstream `result + logs + references`, model/method version, spacecraft and mission configuration, as-of cutoff, history availability times, expert assessment and IP/de-identification permissions. If specific evidence supports a specific fault hypothesis, that binding must originate from the upstream run or an explicitly reviewed evidence record; do not infer it from membership in a global evidence list.

Retain Draft status and independent Ubuntu/Windows CI gate. No main merge, model API usage, fine-tuning or Gold promotion is included.
