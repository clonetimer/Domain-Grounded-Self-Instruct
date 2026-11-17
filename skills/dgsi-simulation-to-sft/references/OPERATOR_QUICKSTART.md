# DGSI Skill operator quick start

## What is delivered

The DGSI Simulation-to-SFT Skill is a provider-neutral production workflow. Use it with another AI agent or a human/AI team to create traceable L0 facts and L1 diagnostic candidates. It is not an automatic Gold approver or training authorization mechanism.

The dataset and Skill are co-equal deliverables:
- Skill/toolkit: reusable instructions, references, schemas, templates, validators and offline tests.
- Dataset: versioned L0/L1 candidate records and their review/projection/coverage evidence.

## Before starting a batch

1. Confirm that each source may be processed by the selected AI provider and for the intended purpose.
2. De-identify spacecraft identifiers, serial numbers, people, credentials and restricted mission details.
3. Keep raw telemetry, command histories, private reports, reviewer identities and hidden truth in authorized private storage.
4. Record source owner, rights status, confidentiality class, source fingerprint and exact page/section/log locator.
5. Freeze a batch ID, source snapshot, event-family IDs and analysis cutoff.

If permission is unknown, stop and quarantine the source. Public download access is not proof of third-party model-training rights.

## Run the Skill

Give the AI the complete `skills/dgsi-simulation-to-sft/` folder, not only `SKILL.md`. Ask it to follow the staged workflow:

| Stage | AI/operator action | Required output |
|---|---|---|
| INGEST | Inventory files, source rights, hashes, locators and missing materials | Source inventory and evidence ledger |
| L0 | Extract bounded event facts, one episode per card | Source fact cards |
| L1 | Build six diagnostic task types from cutoff-available evidence | Review-required task packets |
| TARGET | Write formal engineering conclusions and evidence references | Canonical structured target |
| AUDIT | Run schemas, evidence, leakage, duplicate and lineage checks | Audit report and blocker list |
| REVIEW | Prepare independent expert review; preserve disagreements | Append-only review receipts |
| PROJECT | Apply model-facing allowlist and exclude curator/hidden fields | Three-message preview and round-trip report |
| COVERAGE | Count task types and independent event families; classify gaps | Coverage and gap report |
| PACKAGE | Build portable toolkit and bind exact artifacts to hashes | Skill ZIP, dataset manifest and release summary |

Do not ask the generator to infer missing ML results, run IDs, diagnostic logs, measurement points, mission modes, actions or outcomes. Missing values remain missing. Synthetic assumptions must be explicitly labeled and remain in the synthetic track.

## Validate the toolkit

From the repository root:

```bash
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip
python -m unittest tests.test_portable_toolkit_package_build -v
```

The package builder uses an explicit allowlist and writes a SHA-256 manifest. The package regression verifies file hashes, required Skill files, the integrated production reference and the non-training-authorized flags.

For a clean-room package check, extract the ZIP to a new directory and inspect `PACKAGE_SHA256_MANIFEST.json`; verify each listed file's byte count and SHA-256. Run the offline validator subset documented in the Skill README. Do not rely on repository PYTHONPATH or private source files.

## Release states

- DRAFT: workflow or candidate under development.
- REVIEW_REQUIRED: candidate awaits human review.
- ENGINEERING_REVIEWED_CANDIDATE: curator review and structural checks complete.
- EXPERT_ADJUDICATED: independent expert reviews and disagreements resolved.
- RIGHTS_CLEARED: intended use authorized.
- SFT_AUTHORIZED: formal release gate passed.
- TRAINED: an actual authorized training run completed.

A packaged Skill may be distributed as a draft production tool while data remains blocked. Never infer data authorization from a successful ZIP build or CI run.

## Handoff checklist

A complete DGSI delivery includes both:
- [ ] Versioned Skill folder and portable ZIP.
- [ ] Matching manifest and SHA-256 verification.
- [ ] L0 source inventory and rights blockers.
- [ ] L1 candidate collection and per-packet review status.
- [ ] Canonical targets and model-facing projection.
- [ ] Round-trip and leakage audit.
- [ ] Coverage report at packet and event-family levels.
- [ ] Rejected, revised, pending and quarantined counts.
- [ ] Explicit SFT export/training authorization state.
