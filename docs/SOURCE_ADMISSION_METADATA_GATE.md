# D0 / P3: authorized source-admission metadata gate

## Objective and trust boundary

DGSI's **only** SFT product is a second-stage LLM interpretation dataset. Input is the **already-computed** upstream ML diagnosis result, diagnostic logs, spacecraft/mission configuration, reviewed evidence and prior experience. Raw telemetry is processed upstream, not ingested into the LLM prompt.

The new module (src/dgsi/source_admission.py) provides a **metadata-only, read-only checklist**. The caller supplies a case and a locally held attestation. It never opens original materials, submits a model API request, uploads files, promotes Gold, or changes a train/validation/test assignment. Errors and return values contain **no case IDs, source paths or log text**.

All supplied metadata is **untrusted**. A true flag or SHA-256 string is not proof that permissions were obtained, evidence hashes match source bytes, or an event is real. A READY_FOR_MANUAL_SOURCE_AUDIT decision means exactly that: a human custodian must check the underlying audit evidence and source records. It does **not** mean the case is admitted, usable for training, independently reviewed or Gold. All returns have gold_eligible=false, eligible_for_training=false and authorization_verified_by_software=false.

## Required locally maintained attestation fields

For each candidate use the following shape; **do not commit completed attestations containing sensitive event IDs to this public repository**:

- schema_version: dgsi-source-admission.v1
- case_ref and incident_family: exactly bound to the source case ID and its incident-wide source_group, not just a prompt variant
- source_class: PUBLIC_SYNTHETIC_FIXTURE, INTERNAL_SYNTHETIC_SIMULATION, REAL_ENGINEERING_DIAGNOSIS, REAL_ON_ORBIT_RECORD
- producer: exact method and version appearing in the case's upstream ML result
- run_completed_at: timezone-aware timestamp; must not be later than the LLM's analysis_cutoff
- audit_evidence_sha256: digest of a locally held authorization and audit record; a digest cannot verify that record by itself
- permissions: explicit booleans for access_authorized, ip_rights_checked, deidentification_checked, internal_sft_use_authorized
- checks: explicit booleans for upstream_run_verified, log_provenance_verified, spacecraft_and_mission_context_verified, historical_outcomes_verified, evidence_citations_verified, source_hashes_verified, incident_family_deduplicated, cross_split_leakage_checked, score_semantics_verified

Missing/unverified checks fail closed with **non-sensitive reason codes**. Synthetic class and synthetic provenance markers block real-case intake even when assertions are all true. Unresolved historical cases are counted, **never silently converted into confirmed experience**. Only an authorized source owner can verify permissions; independent domain experts must judge target correctness.

## AstroGraph integration observations

Source-code families inspected:

- src/astrograph/diagnosis/unified_models.py: machine-result status, candidate screening_score, supporting/contradicting engines and diagnostic evidence. screening_score is not automatically a calibrated probability. Preserve exact semantics and producer version.
- src/astrograph/integrations/result_log_review.py: role-separated upstream diagnosis results, log reports and references. These provide **candidate and review evidence**, not confirmed fault truth.
- src/astrograph/integrations/manual_report_review.py: per-candidate report review events and independent evidence references. Report review is not automatically Gold root-cause verification.
- src/astrograph/integrations/material_case_memory.py: explicitly gated human review and reference confirmation; the caller must authenticate reviewers. Approved memory reuse is not SFT Gold adjudication.

These are *code interfaces*, not a verified inventory of real case packets. TC01–TC09, local illustrative cases and other synthetic workflows remain SYNTHETIC test fixtures. No restricted source data was copied.

## Manual workflow before the 20-case SFT prototype

1. Run the existing read-only restricted-case inventory utility **locally in the authorized workspace**. Keep files and potentially sensitive aggregate counts there.
2. Review 5–10 de-identified packets with a verified custodian: ML algorithm/version, score meaning, result/log timestamps, spacecraft/mission configuration, cited historical records, source artifact hashes, permitted use, incident-family identity and split contamination.
3. Use assess_source_admission only to triage the **metadata checklist**. A ready decision must be independently corroborated by a human audit of source files and permission receipts.
4. Have an **independent domain expert** adjudicate source-component versus affected-component claims, unknowns, contradicting evidence, abstention and the final target, storing the decision in the authorized review system.
5. Only then curate up to 20 actual reviewed cases and six SFT task types. Do not automatically export, train, publish, or call approved a case with incomplete expert review. Expansion to 300–500 requires sufficient source families and leakage-proof splits.

Tests in tests/test_source_admission.py are entirely **SYNTHETIC**, including a deliberately spoofed fake-real attestation demonstrating that metadata assertions cannot establish real-world authenticity. Tests are not training data.

## Reproduce

Install: python -m pip install -r requirements-validation.txt

Test: PYTHONPATH=src python -m unittest discover -s tests -v

Mandatory Ubuntu and Windows CI jobs must both succeed before acceptance. This remains a separate Draft PR on top of PR #15, without merging or modifying originals.
