# P5-C offline SOTA construction-quality scorecard

**Status: implemented locally and with synthetic unit tests; empirical method comparison NOT RUN.** No paid API, training, external source access, private logs or human adjudication is performed.

## Product question

Does DGSI construct higher-quality, evidence-faithful satellite fault-diagnosis SFT candidates than matched general instruction-synthesis methods? Its single product goal remains high-quality satellite-fault-diagnosis SFT for second-stage reasoning from upstream ML findings, logs, mission context and as-of historical experience. Raw telemetry remains upstream.

The executable scorecard permits an honest answer to the *candidate construction* portion once externally produced and independently adjudicated candidates are available. It cannot prove downstream SFT gains, grant Gold or authorize releases.

Run locally with:

    python scripts/score_sota_construction.py --input /private/trials.json --output /private/summary.json

Keep the input JSON in an access-controlled local directory. The summary contains only counts, token budgets/usage, preliminary filter-accepted yield, number of critical-failure trials and *separately reported REAL_GOLD versus literature-SYNTHETIC* adjudicated dimension means; it omits source snippets, target text, trial IDs, reviewers and private raw scores.

## Five-arm matched design

- M0: Self-Instruct
- M1: Evol-Instruct / WizardLM-style
- M2: Magpie-style adaptation
- M3: Auto-Instruct-style ranking, not automatically a complete SFT generator
- M4: DGSI with L0/L1 source-bound evidence and time-safe Context

The M5 no-Context DGSI ablation is *not* a sixth independent SOTA construction method; handle it as a paired ablation outside this five-arm core.

Same permitted source groups, episode/event families, **explicit matched comparison_unit_id and requested_task_type**, attempted candidates and **allocated token budgets per comparison unit/attempt** are required for a direct M0–M4 comparison. Matching only total token budget can hide an unfair per-attempt reallocation. An event family cannot be assigned to different source groups or tracks. Actual token *usage* can differ and is reported separately. Do not share publication-linked or history-linked incident groups across training and holdout, and do not regard existing 21 REV1 review candidates as five independent generated arms or an untouched final test set.

Each trial JSON row represents exactly one *attempted candidate*, with:

- trial_id, arm, source_group, event_family, track
- comparison_unit_id: stable non-identifying opaque ID for the *same input scenario/seed* across methods (not the generated candidate ID); requested_task_type: the same requested task objective across all matched arms
- canonical_scenario_sha256: lowercase SHA-256 of the **same preassigned canonical scenario payload** available to every arm (upstream ML finding and score semantics, allowed logs/evidence references, spacecraft/mission context, analysis cutoff and eligible historical-context envelope). Serialize a permission-cleared, versioned canonical JSON once, with stable field ordering/encoding, before constructing method-specific prompts; do not hash different method instructions or candidate targets. Store the actual canonical source/payload and rights-controlled manifest outside public GitHub. A self-reported hash is not authenticated proof of identical content.
- A different scenario from the same incident family must use a different comparison_unit_id. Use pre-established input assignments, not automatically invented matching from text similarity. This tool cannot independently attest that two different input texts are identical.
- attempts=1, accepted_candidates=0 or 1 (provisional generator/filter acceptance, **not** expert or dataset admission)
- generation_tokens (actual nonnegative integer) and token_budget (allocated nonnegative integer)
- critical_failures (supported fixed codes; no accepted candidate with a critical failure)
- review_status=PENDING or ADJUDICATED
- reviewer_tokens, scores and review_receipt_sha256 only for an adjudicated row

The scorecard remains backward-readable: rows without canonical_scenario_sha256 (even when comparison_unit_id is present) are accepted for descriptive aggregation but **always NOT_COMPARABLE_OR_NOT_RUN**. Old rows lacking both comparison-unit fields are also descriptive only. Rows with only one field are rejected. Reusing a unit ID across a different source group, event family, track, requested task objective **or canonical scenario digest** is rejected. Invalid uppercase/non-hex/short digest values are rejected. Group-level token sums can no longer hide unmatched input scenarios. The summary exposes only aggregate source_groups, comparison_units and comparison_units_complete; no raw unit IDs.

The root JSON has schema_version=dgsi-sota-construction-scorecard.v1, purpose=CONSTRUCTION_ONLY, and trials=[...]. Unreviewed rows must have reviewer_tokens=[] and scores={}, and must not contain a stale review_receipt_sha256. Aggregated ten-dimension means are available only within a single data track: when REAL_GOLD and literature-derived SYNTHETIC both occur, the per-arm pooled mean is null and the by_track means are the only reported review means. An adjudicated row needs two distinct anonymized reviewer tokens, a lowercase 64-character SHA-256 receipt digest, and all ten existing L1 science rubric dimensions, each scored 0/1/2. This is a receipt *format check*, not authentication, source-rights verification, proof of independent expertise or Gold admission.

## Conservative result states

- NOT_RUN: no attempted candidates for that arm
- NOT_COMPARABLE_OR_NOT_RUN: missing core arm, absent explicit comparison-unit pairing, or mismatched source, task objective, attempt count or allocated budget
- MATCHED_UNREVIEWED: same source-group/episode/track and budget, but no complete independent scoring
- REVIEWED_COMPARABLE_INPUT: matching submitted records with complete claimed adjudications; still requires offline receipt/authenticity and scientific source verification before claiming measured effectiveness

Never fill an unrun arm with speculative scores. Always score REAL_GOLD and LITERATURE_DERIVED_SYNTHETIC independently, without pooling their per-track rubric means; separate REAL_GOLD from LITERATURE_DERIVED_SYNTHETIC, retain all causal certainty and disposal-source boundaries, and do not convert history-only evidence into current-fault confirmation. A user-supplied gold_admitted=true assertion is insufficient by itself for admission.

Downstream training: NOT_RUN until explicit permission, expert-reviewed source-cleared training data and independent frozen holdout are available. Green CI proves tool execution, not model superiority.

## Development lessons

The earlier comparison protocol identified SOTA baselines but provided no runnable aggregation interface; this change makes the next locally authorized empirical trial countable without adding a model/API dependency. Each attempted candidate is one row to prevent aggregate yields from concealing fabricated outputs. Compare *allocated* budgets rather than exactly identical actual output-token usage, while still recording consumed tokens. Critical-failure candidates must never be counted as accepted. Store expert identities and detailed restricted reviews outside the public repository; only safe aggregates may be shared.

Local tests: python -m unittest discover -s tests -p test_sota_construction_scorecard.py -v. CI gates remain exact-head Ubuntu and Windows.

## 2026-11-19 experiment validity correction

Previously, two variants of the same event family could be swapped across arms while each arm retained identical family counts and token budgets. This would label the candidate construction comparison as matched without the same input case or diagnostic request. Matching now keys on comparison_unit_id plus requested_task_type and still checks source_group, event_family, track and per-attempt token allocation. Legacy files remain analyzable but cannot claim comparability until the actual generation prompts and units are independently mapped. This is a construction-evaluation correction, not evidence that any SOTA model run has been executed. Do not upgrade review tokens to verified expert identity or synthetic candidates to Gold.


## 2026-11-19 follow-up: scenario fingerprint is required for a match

One comparison_unit_id can accidentally be reused even when an upstream ML result, diagnostic log, mission context or historical retrieval snapshot has changed. This is a silent content-level swap not caught by matching labels and budgets. A canonical scenario SHA-256 must therefore agree across all trials attached to one input unit; missing hashes remain structurally readable but **cannot** yield MATCHED_UNREVIEWED or REVIEWED_COMPARABLE_INPUT. The scorecard outputs only a boolean `scenario_fingerprints_complete`, not raw hashes.

This is a fail-closed structural consistency check, **not an attestation of correctness**: a fabricated or copied digest, hash of the wrong serialization, changed method-specific context, invalid permissions or inaccessible payload can still evade the summary. Independent offline review must verify the canonical scenario manifest and hashed bytes before interpreting a SOTA result. Do not put private logs, reviewer identities, or underlying context in CI/public artifact records. No model run, reviewer approval or training is initiated by this change.
