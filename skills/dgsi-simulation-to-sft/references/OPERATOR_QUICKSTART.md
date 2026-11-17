# DGSI Skill operator quick start

## Deliverables
The Skill/toolkit and dataset are co-equal deliverables. The Skill provides repeatable production instructions and validators; the dataset is a versioned output. Neither CI nor package creation grants data approval.

## Prerequisites
1. Confirm source processing and intended-use permissions with the source owner.
2. De-identify restricted identifiers and keep raw telemetry, command histories, private reports, reviewer identities and hidden truth in authorized storage.
3. Freeze batch ID, source hashes, event-family IDs and analysis cutoff.
4. Quarantine any source with unknown rights.

## Execute the workflow
Give the AI the complete `skills/dgsi-simulation-to-sft/` folder, not only SKILL.md. Follow:
INGEST → L0 source facts → L1 candidates → TARGET → AUDIT → independent REVIEW → PROJECT → COVERAGE → PACKAGE.

| Stage | Output |
|---|---|
| INGEST | Source inventory, rights status, hashes and exact locators |
| L0 | One bounded source fact card per event episode |
| L1 | Review-required diagnostic task packets |
| TARGET | Canonical structured engineering report |
| AUDIT | Schema, evidence, leakage, duplicate and lineage report |
| REVIEW | Append-only independent review records |
| PROJECT | Allowlisted three-message preview and round-trip report |
| COVERAGE | Task-type and independent event-family coverage |
| PACKAGE | Skill ZIP, dataset manifest and release-state summary |

Never invent missing ML outputs, run IDs, logs, measurements, mission modes, actions or outcomes. Missing values remain missing. Synthetic assumptions stay in the synthetic track.

## Build and verify the toolkit
From the repository root:
```bash
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip
python -m unittest tests.test_portable_toolkit_package_build -v
```
The ZIP contains an explicit SHA-256 manifest. Extract it into a clean directory and verify every listed byte count and hash. Run the offline validator subset documented by the README without repository PYTHONPATH or private source files.

## Release states
DRAFT, REVIEW_REQUIRED, ENGINEERING_REVIEWED_CANDIDATE, EXPERT_ADJUDICATED, RIGHTS_CLEARED, SFT_AUTHORIZED and TRAINED are distinct states. A Skill package may be distributed while the dataset remains blocked. A successful ZIP build never authorizes Gold, SFT export or training.

## Handoff checklist
- [ ] Versioned Skill folder and portable ZIP
- [ ] Matching manifest and SHA-256 verification
- [ ] L0 source inventory and rights blockers
- [ ] L1 collection and per-packet dispositions
- [ ] Canonical targets and model-facing projection
- [ ] Round-trip and leakage audit
- [ ] Coverage by task type and event family
- [ ] Rejected, revised, pending and quarantined counts
- [ ] Explicit SFT export/training authorization state
