# DGSI L0 review intake decisions — 2026-11-15

## Review result

The returned review package contains two revised Word files with visible editorial notes and 16 Word comments, plus a consolidated review memorandum. The review is AI-assisted and explicitly pending domain-expert confirmation.

- Five user-supplied case summaries remain L0 source fact cards. Their causes are source attributions pending case-level evidence, not independently verified root causes.
- Eleven public-literature cards remain L0. They are not homogeneous flight incidents: they include flight reports, ground qualification/life tests and an expert-system feasibility demonstration.
- The package does not contain the underlying original fault-case Word, spacecraft logs, ML diagnosis results, hardware inspection records or executed-action records. Therefore no case is eligible for Gold SFT from this review alone.

## Formal conclusion vs. internal review

Only source-grounded phenomena, source cause statements, evidence-supported affected objects and source-recorded disposal information belong in the formal report fields.

Curator migration notes, reviewer questions, alternative hypotheses and cautions remain under root-level internal_review with not_for_sft=true. They are never copied into the assistant target.

## User-case handling

The five source cases remain in the user-side review package and are not copied into the repository. Their record-level treatment is:

- Cause localization remains source attribution, with independent verification pending.
- The phrase “可自行恢复” is not a disposal action; its disposal status is SOURCE_TEXT_AMBIGUOUS with an explanatory source note and an empty action list.
- Conditional TWTA protection branches remain conditional procedures, not generic operational instructions.
- Thruster low-temperature / incomplete-combustion / structural-damage causal chain remains unverified.
- The 2000 rpm wheel limit remains a source-specific recommendation, not a transferable threshold.

## Public-literature handling

- SEASAT: conditional transfer at slip-ring arcing/short-circuit mechanism level; triggering cause remains non-unique.
- TROPICS TVAC: transfer diagnostic method and ground-test contact-reliability experience only.
- TROPICS flight CRC: split the two payload outcomes into separate event_episode_id values under one shared event_family_id. One payload was mitigated by reverse rotation; the other degraded and ceased payload operation.
- TROPICS Pathfinder: conditional common-cause analysis; 12 V bus / serial-line short remains the authors' more-likely explanation, not a universal confirmed cause.
- Lunar Orbiter helix-current report: the launch-stress and outgassing explanations remain alternatives. The start-time constraint was proposed for development, not recorded as implemented.
- Lunar Orbiter power-monitor report: temperature-dependent diode telemetry is a measurement-chain counterexample, not proof of real RF output power change.
- Cassini RWA: conditional transfer of low-speed lubrication / drag mechanism only; not equivalent to a blocked oil-feed line and not a transferable speed command.
- ISEE/IUE expert-system report: knowledge_source_not_event=true; exclude from real incident counts and event SFT.
- NASA TM-100232: injector plugging and catalyst contamination remain distinct ground-life-test findings, not user-case diagnoses.
- S-band TWTA ground test: the cited root cause is in linearizer-channel LNA chips, not the TWTA helix, EPC or cable/isolator connection.

## Structured-data changes

The L0 source fact-card contract now carries:
- event_status and knowledge_source_not_event;
- event_family_id and event_episode_id;
- migration_assessment with tier, rationale and constraints;
- explicit missing_materials;
- publication_year and ntrs_accession_year as separate metadata fields;
- disposal states for ambiguous source wording, conditional measures and proposed procedures.

The NASA TM-100232 record separates the report's 1987 year from the 1988 NTRS accession/cataloging year. Exact publication_date remains null when a precise date is not established. The ISEE report's publication year is left unset rather than inferred from its document identifier.

## Data synchronization rule

The reviewed Word is the current human-audited editorial source. JSON changes are versioned separately and must retain a review_basis reference. A Word-only change does not silently mutate JSON. The L0 JSON remains sft_eligible=false. A complete LLM SFT Case still requires upstream ML result, diagnostic logs, spacecraft/mission context, history provenance and an independently reviewed formal target.

## Verification boundary

Schema/validator CI verifies structure, provenance flags, event grouping and disposal semantics. It does not prove the underlying hardware root cause, source authenticity, rights clearance or expert Gold approval.
