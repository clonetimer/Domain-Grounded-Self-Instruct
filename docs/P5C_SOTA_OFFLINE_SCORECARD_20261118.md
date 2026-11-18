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

Same permitted source groups, episode/event families, task coverage, attempted candidates and **allocated token budgets** are required for a direct M0–M4 comparison. Actual token *usage* can differ and is reported separately. Do not share publication-linked or history-linked incident groups across training and holdout, and do not regard existing 21 REV1 review candidates as five independent generated arms or an untouched final test set.

Each trial JSON row represents exactly one *attempted candidate*, with:

- trial_id, arm, source_group, event_family, track
- attempts=1, accepted_candidates=0 or 1 (provisional generator/filter acceptance, **not** expert or dataset admission)
- generation_tokens (actual nonnegative integer) and token_budget (allocated nonnegative integer)
- critical_failures (supported fixed codes; no accepted candidate with a critical failure)
- review_status=PENDING or ADJUDICATED
- reviewer_tokens, scores and review_receipt_sha256 only for an adjudicated row

The root JSON has schema_version=dgsi-sota-construction-scorecard.v1, purpose=CONSTRUCTION_ONLY, and trials=[...]. Unreviewed rows must have reviewer_tokens=[] and scores={}. An adjudicated row needs two distinct anonymized reviewer tokens, a lowercase 64-character SHA-256 receipt digest, and all ten existing L1 science rubric dimensions, each scored 0/1/2. This is a receipt *format check*, not authentication, source-rights verification, proof of independent expertise or Gold admission.

## Conservative result states

- NOT_RUN: no attempted candidates for that arm
- NOT_COMPARABLE_OR_NOT_RUN: missing core arm or mismatched source, attempt count or allocated budget
- MATCHED_UNREVIEWED: same source-group/episode/track and budget, but no complete independent scoring
- REVIEWED_COMPARABLE_INPUT: matching submitted records with complete claimed adjudications; still requires offline receipt/authenticity and scientific source verification before claiming measured effectiveness

Never fill an unrun arm with speculative scores. Always score REAL_GOLD and LITERATURE_DERIVED_SYNTHETIC independently, without pooling their per-track rubric means; separate REAL_GOLD from LITERATURE_DERIVED_SYNTHETIC, retain all causal certainty and disposal-source boundaries, and do not convert history-only evidence into current-fault confirmation. A user-supplied gold_admitted=true assertion is insufficient by itself for admission.

Downstream training: NOT_RUN until explicit permission, expert-reviewed source-cleared training data and independent frozen holdout are available. Green CI proves tool execution, not model superiority.

## Development lessons

The earlier comparison protocol identified SOTA baselines but provided no runnable aggregation interface; this change makes the next locally authorized empirical trial countable without adding a model/API dependency. Each attempted candidate is one row to prevent aggregate yields from concealing fabricated outputs. Compare *allocated* budgets rather than exactly identical actual output-token usage, while still recording consumed tokens. Critical-failure candidates must never be counted as accepted. Store expert identities and detailed restricted reviews outside the public repository; only safe aggregates may be shared.

Local tests: python -m unittest discover -s tests -p test_sota_construction_scorecard.py -v. CI gates remain exact-head Ubuntu and Windows.
