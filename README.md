# Domain-Grounded Self-Instruct

Evidence-grounded, **human-approved** Self-Instruct seed curation for spacecraft fault diagnosis, starting with ADCS and EPS. The first deliverable is a deterministic, offline **candidate preflight gate** — not an LLM generating, fact-checking, diagnosis engine, or Gold certification service.

## Current scope (Phase 1)

- Public indexes: `resources/sources.json`, `resources/source_passages.json`, `resources/terms.json` (alias-aware v2), `resources/telemetry_channels.csv`, `resources/fault_effects.json`.
- Run admission contract: `resources/simulation_truth.json` (initially **zero verified runs**).
- Versioned candidate JSON contract: `resources/seed.schema.json`.
- Conservative Python preflight CLI: `src/dgsi/quality.py`, 44 adversarial tests.
- Human workflows and **draft** reusable Skills: `docs/`, `skills/adcs-gold-seed-curation/SKILL.md`, `skills/eps-gold-seed-curation/SKILL.md`.

## Run locally (Python 3.11+; no external runtime dependencies)

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

PowerShell:

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
python -m dgsi.cli validate examples/illustrative_gyro_abstain.json --root .
```

`REVIEW_REQUIRED` means suspicious technical compounds need manual terminology review. `CANDIDATE_CHECKS_PASSED` means **structural and rule-based preflight only**; factual correctness, complete terminology coverage and physical causal validity require independent domain review. Mechanism/causal claims use registered passage IDs, not free-text locators. A `CANDIDATE_CHECKS_PASSED` result is never a Gold Seed. Human review metadata is not proof of reviewer identity; Gold freeze remains a separate governed action.

## Security, provenance and IP

**This repository is public.** Never commit R21/other nonpublic telemetry, unpublished experiment archives, commercial FMEA tables, credentials, personal data, or copyrighted source PDFs. Public source URLs and a small set of reviewed *metadata* are not a blanket license to reproduce texts. Input prompts must be truth-free; fault injection metadata, labels, and future holdouts are isolated. Published demo data are explicitly hypothetical.

Use [`docs/DOMAIN_REVIEW_CHECKLIST.md`](docs/DOMAIN_REVIEW_CHECKLIST.md) to review the 16 draft ADCS terms and 11 source passages. See [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) for the still-pending independent Skill evaluation. Live runs require distinct generator and judge model-family identifiers and make 3 Responses API calls per case. The opt-in blind Skill runner is `scripts/run_skill_blind_eval.py`; its default mode makes **zero network calls**. See [`docs/SKILL_PRESSURE_TEST_PROTOCOL.md`](docs/SKILL_PRESSURE_TEST_PROTOCOL.md) before any paid run. Start with [`docs/ROADMAP.md`](docs/ROADMAP.md) and [`docs/QUALITY_PROTOCOL.md`](docs/QUALITY_PROTOCOL.md). The plan and design are under `docs/superpowers/`.
