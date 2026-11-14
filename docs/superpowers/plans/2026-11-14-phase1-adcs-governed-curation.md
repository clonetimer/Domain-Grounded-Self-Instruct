# Phase 1 ADCS Governed Curation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans task-by-task, with test-driven-development and verification-before-completion.

**Goal:** Create an auditable, public-data-safe source and seed curation baseline, and a tested deterministic quality gate for ADCS Self-Instruct candidates.

**Architecture:** Versioned JSON/CSV public metadata and a stdlib Python quality validator, initially permitting only illustrative evidence-limited candidate seeds; provenance and human review gate prevent machine-created Gold. A draft reusable skill specifies the workflow. No connection to private datasets or model APIs.

**Tech Stack:** Python 3.11+, JSON, CSV, stdlib unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-11-14-phase1-adcs-governed-curation-design.md`

## Global constraints
- Public repo: do not copy raw R21 telemetry or restricted documents.
- No fabricated sensor thresholds, unit conversions, exact fault outcomes or claims of verification.
- Explicit source/evidence/review states and no training label leakage.
- Human confirmation before Gold Seed; code may verify metadata presence, not reviewer identity.

## Review focus
- Unknown/forbidden technical term must be blocked or flagged for curation.
- A declared fault catalog entry must not turn hypothetical observations into a confirmed diagnosis.
- Causal assertions must have independent human-reviewed justification.
- Input should never include truth/label/onset fields in a would-be inference prompt.
- Missing/invalid source IDs, references, channel IDs or human approval should block promotion.

---

### Task 1: Public governance registries and seed contract
**Files:** `resources/*.json`, `resources/*.csv`, `examples/*.json`, `docs/README.md`, `README.md`.
**Interfaces:** Registry files have stable IDs; validator consumes `sources`, `terms`, `faults`, `simulation_truth`, and `telemetry`.
- [x] Identify source authority and permitted use; preserve a distinction between catalog vs. observed truth.
- [x] Prepare initial ADCS terminology, channel names, effect IDs and empty run-admission registry.
- [x] Publish one *illustrative CANDIDATE* example, never Gold.
- [x] Check JSON parsing, CSV reference integrity and example governance scope.

### Task 2: Preflight validation and tests
**Files:** `src/dgsi/{__init__,quality,cli}.py`, `tests/test_quality.py`, `.github/workflows/ci.yml`.
**Interfaces:** `load_registry(root) -> dict`; `validate_seed(seed,registry) -> list[Finding]`; `report(seed,registry) -> dict`.
- [x] Write adversarial tests first; observe missing implementation failure (RED).
- [x] Implement deterministic claim, reference, source, term, leakage, causal and Gold review checks.
- [x] Run all tests and CLI smoke tests; fix until GREEN.
- [x] Add CI running exactly those tests plus registry smoke validation.

### Task 3: Reusable draft Skill and phase handoff
**Files:** `skills/adcs-gold-seed-curation/SKILL.md`, `docs/ROADMAP.md`, `docs/QUALITY_PROTOCOL.md`.
**Interfaces:** Skill points to source registries and CLI, and explicitly distinguishes CANDIDATE vs GOLD.
- [x] Document evidence-bound drafting, automatic checks, human correction, gold freeze, and data split.
- [x] Document open challenges and acceptance metrics; no unverified accuracy or data-quality claims.
- [ ] Run pressure-scenario agent evaluation before marking Skill production-ready (requires independent model runs, not just validator fixtures).

## Verification commands
```
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
python -m compileall -q src tests
```
