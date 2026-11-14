# P1 Quality and Governance Protocol

## What passes and what does not

The preflight checks registry IDs, registered source-passage references, alias classes, selected suspicious technical compounds, self-certifying language, selected causal wording, evidence references, direct input label leakage, physical-claim scope, causal review metadata, admissible simulation runs, and human approval metadata. Mechanism/causal claims must cite registered `source_passage_ids` whose `allowed_claim_types` includes the claim type; a free-text locator cannot substitute. These checks do not establish that a prose statement is true. The compound-term scanner is intentionally narrow and cannot guarantee discovery of all unregistered technical expressions.

A result with `decision=REVIEW_REQUIRED` must be manually examined for suspicious compounds. A result with `decision=CANDIDATE_CHECKS_PASSED` is still an AI/synthetic **candidate**; scanner silence is not proof that every term is registered. `HUMAN_REVIEWED` may produce `GOLD_METADATA_ELIGIBLE_MANUAL_AUTHENTICATION_REQUIRED`, but the validator never authenticates reviewer identity and never moves a record into a Gold dataset. An independent curator must confirm the source and approval receipt outside the generated content.

## Evidence tiers

1. **Reference indexed**: NASA/Basilisk/papers or project code is in the source index; the exact passage and conditions have not automatically been vetted.
2. **Catalog/declaration**: channel names, model capabilities, fault-effect identifiers, engineering reference mappings. These cannot establish observed symptoms or case-level causality.
3. **Observed trace candidate**: local/raw telemetry with source identity, time grid, unit schema and effect receipt. Not admissible until independent verification.
4. **Admitted trace**: trace hash verified, injection/event window human-reviewed, physical effect observed, split authorized, truth kept out of inference input.
5. **Gold seed**: independently domain-reviewed output with provenance; review audit and freeze are separate from machine checks.

No run is admitted in v0.1. The public registry intentionally has `runs: []`. AAS and AstroGraph source schemas are references, not public copies of R21 data.

## Mandatory review workflow

1. Register the domain source and exact `source_passage_id` (section/page locator, allowed claim types, claim boundary), terminology IDs and provenance *before* asking an LLM to generate a new task.
2. Generate a small candidate with truth-free `input` and explicit observed vs. hypothetical evidence.
3. Atomize output into typed `claims`. Identify entity, component, channel, operating mode, units and certainty.
4. Run the offline validator. For every flagged term, citation or logical leap: correct, downgrade to uncertainty, or reject the sample. `DOCUMENT_EXCERPT` evidence must match a registered passage ID and its source ID. Do not invent locator strings. Never rewrite a wrong physical claim merely to satisfy regex rules.
5. A second reviewer verifies complex causal edges and any claimed fault-source localization with independent evidence. Reviewers must distinguish correlated affected components from proven originating components.
6. Confirm a candidate's artifact IDs, source passages, fault-window receipt, and data split. Record a human decision; freeze Gold in a separate controlled process.
7. Keep Gold Seed / Synthetic Train / Validation / Test / Rejected nonoverlapping by provenance group (run, scenario, source, model and near-duplicate instructions). Never tune prompts against a test holdout.

## Editorial risk checklist

- **Coinages:** preferred terminology is DRAFT; reject invented compound terms, verify bilingual aliases against references, and manually review unrecognized expressions even if CLI says PASS. Alias types are not interchangeable: exact, alternate translation, informal/contextual short form, broader description and structural subtype.
- **False causality:** association, affected component, fault event, fault source and mechanism are distinct. Every causal statement needs a precise source locator and at least two *genuinely* independent evidence groups plus explicit human review; metadata group names alone are not independence proof.
- **Self-attestation:** do not write “already proven”, “fully verified” or similar without independent provenance; the phrase scan is a coarse guard, not an NLP fact verifier.
- **Disguised labels:** remove simulation `label`, `fault_id`, `onset_s`, `group`, experiment identity, outcome timestamps or source hash from inference prompts even if a different field name is used. Review every prompt by hand for semantic leakage.
- **Uncertainty:** preserve `INSUFFICIENT_EVIDENCE`, `UNKNOWN_FAULT`, `AMBIGUOUS`, `CONFLICTING_EVIDENCE`, `DATA_ERROR`, rather than inventing a fault to make an answer complete.
- **Observed vs. hypothetical:** hypothetical observations make useful safe-abstention tutorials, but never certify a real anomaly or fault.

## Pilot measurement contract (no measurements claimed yet)

For an ADCS pilot of 30–50 seeds, record first-pass human approval rate, rejected rate, corrected-to-approved delivery yield, human revision time, terminology violations, unsupported factual statements, unsupported causal relations, and any holdout contamination. Use a reviewer-blind audit of unfamiliar tasks and compare to an ungrounded Self-Instruct baseline with the **same** review rubric; never use the same generator/judge as sole truth authority.
