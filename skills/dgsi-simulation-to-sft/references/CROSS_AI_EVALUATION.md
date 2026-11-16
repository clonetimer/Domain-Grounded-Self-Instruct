# Cross-AI Skill evaluation protocol

## Purpose

Measure whether different AI providers can independently extract the same engineering facts and produce defensible diagnostic candidates from the same source package. This is an evaluation protocol, not a model leaderboard.

## Blind setup

1. Freeze one source batch, source hash, page render set, schema revision and prompt revision.
2. Give each AI the same source files, Skill folder, schema and provider-neutral task prompt.
3. Do not provide any hidden simulator truth, answer key, prior AI output or reviewer annotations.
4. Require each AI to return source inventory, atomic facts, candidate packets, unresolved questions and a manifest.
5. Preserve raw outputs and exact model/provider/version, run date, settings and token limits.
6. A separate reviewer adjudicates each output against the source; generator self-review does not count as independent review.

## Scorecard

Score each dimension 0–2: 0 = materially wrong/absent; 1 = partial/needs correction; 2 = accurate and traceable.

- Source coverage: all in-scope sections considered; out-of-scope regions quarantined.
- Locator precision: every claim has a correct page/section/table/figure/log locator.
- Fact fidelity: extracted claim preserves source wording, units and qualifiers.
- Evidence class: design declaration, measured test result, run observation, inference and assumption correctly separated.
- Object hierarchy: spacecraft/subsystem/unit/component relationships preserved.
- Physical consistency: direction, units, frame, timebase and causal ordering are not altered.
- Fault semantics: symptom, fault source, affected component and system effect are distinct.
- Uncertainty: likely/candidate/confirmed/not-established distinctions preserved.
- Truth isolation: hidden labels and post-cutoff facts do not enter model-facing input.
- Task value: each task tests a distinct diagnostic decision, not a paraphrase.
- Target restraint: unsupported root causes are withheld and missing discriminating evidence is named.
- Schema/lineage: references resolve, hashes and source groups bind, schema validates.

Critical failures override the numeric score: fabricated measurement/log/event; unsupported definitive root cause; source locator mismatch; design statement presented as observed run result; hidden truth leakage; missing or invalid provenance; or unsafe instruction presented as executed.

## Reporting

Report per AI:
- total scores and score by dimension;
- critical failure count and examples;
- fact-level agreement/disagreement matrix;
- candidate-level agreement/disagreement matrix;
- corrections required per 10 facts and per 10 candidates;
- human review time;
- missing evidence and unresolved ambiguities.

Do not use raw agreement as truth. Two AIs can agree on the same incorrect interpretation. The source-grounded human adjudication is the reference.

## Initial pilot

Use the 0918 design report as a design-only pilot. It can evaluate source extraction, design knowledge representation, evidence sufficiency and task construction. It cannot evaluate real failure localization or runtime diagnosis because no test reports, run logs or upstream ML results were supplied.


## Machine-readable run record

Use `schemas/cross_ai_evaluation.schema.json` and `templates/CROSS_AI_EVALUATION_TEMPLATE.json` to freeze source/prompt/Skill revisions, record provider/model runs under blind aliases, and capture independent scores plus critical failures. Keep the provider-to-alias key separate from the adjudication sheet. No provider execution or empirical result is implied by creating this record.
