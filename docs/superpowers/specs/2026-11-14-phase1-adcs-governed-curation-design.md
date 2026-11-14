# Phase 1 — ADCS Evidence-Grounded Seed Curation Design

## Intent
Produce a reusable, auditable foundation for OpenAI-assisted Self-Instruct seeds in spacecraft fault diagnosis, starting with ADCS. AI drafts; humans approve. Never represent synthetic or catalog-only evidence as observed spacecraft evidence.

## Scope
Ship a source registry, terminology registry, fault/effect and telemetry metadata, an explicit simulation-truth admission registry, a versioned JSON seed contract, a deterministic preflight validator, a draft skill, adversarial fixtures/tests, and a development roadmap. P1 does not invoke paid models or freeze Gold Seeds.

## Hard requirements
- Public repository: no restricted, private, or raw telemetry files and no private credentials.
- Differentiate documents, engineering interface declarations, event catalog entries, and *verified* telemetry traces.
- No hallucinated fault effects, values, thresholds, causal links, or citations.
- A signal associated with a component does **not** establish a component-level root cause.
- Reject auto-promotion to Gold without a recorded human decision, while noting review metadata alone is not identity authentication.
- Separate training input from labels, fault injection truth, and hidden simulation events.
- Model ambiguity and insufficient evidence rather than forcing a diagnosis.
- Use standard-library Python 3.11+ for deterministic offline checks; no SDK or API key necessary for Stage 1.

## Alternatives considered
1. **Prompt-only Self-Instruct** — cheapest, but misses structural leakage and provenance mistakes.
2. **Governed registry + deterministic validation + human review (selected)** — testable, extensible, provenance-first.
3. **Full web annotation platform immediately** — premature before admissible evidence and quality metrics exist.

## Core contracts
SourceRegistry maps source_id to allowed evidence scopes and review scope. TelemetryCatalog maps channel ID to component and measurement semantics. FaultCatalog maps effect ID to fault/degradation and provides declared signatures only. SimulationTruthRegistry records verified or excluded per-run receipts; initially no runs are admitted. Seed schema distinguishes an illustrative candidate, observed evidence, claims, and human review status. A validation report provides machine-readable findings, severity, location, and an eligibility decision.

## Non-goals
- Model training, OpenAI API orchestration, or bulk self-instruction generation.
- Truth inference from a declared fault type or the presence of a model module.
- Publishing copyrighted source text or restricted R21 scenario content.
- Treating a machine check or self-reported approval metadata as verified human identity.

## Quality gates / experimental follow-through
Pilot target is 30–50 human-reviewed seeds after source review and admissible traces are available. Record first-pass human acceptance, final delivery yield, reviewer correction time, terminology errors, unsupported facts, unsupported causal links, and dataset leakage. Gold content must remain distinct from synthetic-train, validation, test, and rejected records. No efficacy claim until reviewer evaluation on unfamiliar cases.
