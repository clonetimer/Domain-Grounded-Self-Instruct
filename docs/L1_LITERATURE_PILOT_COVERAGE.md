# DGSI L1 literature-derived pilot v0.1 — coverage and review status

## Current inventory

The pilot now contains **15 L1 literature-derived synthetic packets across 9 L0 event families**. All are `REVIEW_REQUIRED`, `gold_eligible=false`, and `training_authorized=false`. The referenced L0 source-fact collection itself remains `AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`; its content has not been independently confirmed by a domain expert.

| Task | Source event class | Main diagnostic challenge |
|---|---|---|
| SEASAT slip-ring short | Flight | Solar-array power and rotary-interface common cause |
| Lunar Orbiter power monitor | Flight | Measurement-chain temperature sensitivity vs actual RF output change |
| TROPICS Pathfinder cross-short | Flight | Multi-interface common cause vs multiple independent failures; rejected SEL Context |
| TROPICS slip-ring TVAC | Ground test | Intermittent contact resistance and CRC under thermal-vacuum test |
| TROPICS payload A CRC | Flight | Candidate cause and source-recorded mitigation kept separate from current synthetic action |
| TROPICS payload B CRC | Flight | Progressive failure; payload A mitigation must not be transferred |
| Lunar Orbiter TWTA startup | Flight | Preserve both source explanations; no unique root cause |
| Cassini reaction-wheel drag | Flight | Low-speed lubricant redistribution distinguished from oil-line blockage |
| NASA 22 N injector plugging | Ground test | Valve-seat material shedding and injector obstruction |
| NASA catalyst contamination | Ground test | Iron/nickel contamination kept separate from injector plugging |
| Spaceborne S-band TWTA output loss | Ground test | Root cause localized to linearizer LNA chip, not TWTA internals |
| FUSE pitch-axis RWA history reuse | Flight | Cassini partially confirmed history with unknown hardware compatibility; no direct root-cause transfer |
| TROPICS Pathfinder evidence sufficiency | Flight | Decide whether current evidence supports cross-interface short or requires additional analysis |
| Cassini RWA next-step recommendation | Flight | Check model, lubrication design and operating limits before considering a speed strategy |
| Spaceborne S-band TWTA handover | Ground test | Preserve LNA location, ground-test source class, candidate status and evidence gaps |

Machine-readable manifest: `examples/l1_literature_pilot_coverage_v0.1.json`.

## Family grouping and leakage

Three source families have multiple L1 tasks, while the FUSE/Cassini history-reuse task also binds a separate historical source family as qualified Context:
- TROPICS flight slip-ring family: payload A and payload B are separate episodes but remain grouped for split assignment.
- Lunar Orbiter III TWTA report family: power-monitor indication and first-turn-on helix-current anomaly remain separate episodes but cannot cross splits.
- NASA 22 N hydrazine life-test family: injector plugging and catalyst contamination remain separate episodes but cannot cross splits.

The collection-level split auditor rejects any event family whose derived tasks are assigned to more than one of train/validation/test. No split assignments have been created for this pilot because independent L0 source confirmation and L1 expert review are pending.

## Data provenance and output boundaries

Every packet:
- references exactly one AI-assisted curated public L0 source fact card; the collection is pending independent domain-expert confirmation;
- uses an explicitly synthetic upstream ML result and synthetic run ID;
- uses synthetic log IDs, timestamps, spacecraft identifiers, equipment configuration and operational context;
- records field-level provenance, generation recipe/version, scenario assumptions and non-simulated source material;
- sets `raw_telemetry_included=false`;
- keeps formal assistant target separate from Case `internal_review`;
- uses `NOT_RECORDED` and an empty disposal list for the current synthetic episode, even when the historical source describes an action;
- remains non-Gold and not training-authorized.

For the Lunar Orbiter startup task, the target preserves both source explanations—launch mechanical-stress release and post-launch internal-pressure decay—as candidates. It does not choose one without discriminating evidence.

## Evaluation status

The 15 packets are task-coverage fixtures for expert review and validator regression. They are not 15 real incidents, not 15 expert-approved targets, and not an approved SFT corpus. The real-case/Gold track remains separate and requires real authorized upstream ML outputs, diagnostic logs, spacecraft/mission context and independent expert adjudication.

## Review next step

Use `docs/L1_TARGET_QUALITY_REVIEW_RUBRIC.md` and `resources/l1_quality_review.schema.json` to review each frozen packet. A high score permits consideration for an L1 controlled experiment only; it does not automatically grant Gold status or authorize fine-tuning.


## History-reuse example

The FUSE pitch-axis reaction-wheel drag task retrieves the Cassini RWA slow-speed drag case as a **PARTIALLY_CONFIRMED** historical contrast. Cassini's source describes likely lubricant redistribution after prolonged near-zero-speed operation; FUSE's source describes a likely Kapton-liner bubble/contact mechanism. The prior case is marked `hardware_compatibility=UNKNOWN`, with explicit transfer limitations. It may guide differential checks but cannot support the current FUSE root-cause candidate or transfer Cassini's speed-management action.

The Cassini lesson date is 2004-05-10. For the synthetic retrieval snapshot, `available_at=2004-05-10T23:59:59Z` is a conservative date-normalization convention (end of the stated lesson date), not a claim about the exact publication time.


## Task-type coverage

The 15-packet pilot now covers all six task types declared in the Case schema: `diagnostic_synthesis`, `historical_case_reuse`, `conflict_reconciliation`, `evidence_sufficiency`, `next_step_recommendation` and `handover_summary`. These task-type variants are grouped by their source `event_family_id`; adding a new task type does not create an independent incident or a new train/test group.


## L0 source-review status — important qualification

The referenced L0 collection records `review_status=AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION`. The L0 fact cards have undergone AI-assisted curation and structural validation, but this is not equivalent to independent domain-expert source verification. The L1 pilot must not describe these as expert-reviewed L0 facts.

Before treating any L1 target as suitable for an effectiveness experiment, reviewers must inspect the cited public source passage and confirm that the L0 fact-card statement, source certainty, event class, episode grouping and disposal status faithfully represent that source. A valid SHA-256 binding only proves which bytes were reviewed; it does not prove the source claim is true or expert-approved.
