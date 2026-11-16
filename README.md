# Domain-Grounded Self-Instruct

**Purpose:** Human-reviewed, evidence-grounded instruction seed curation for spacecraft fault diagnosis, starting with ADCS.

This repository is public. It must not contain private telemetry, unpublished R21 traces, proprietary source documents, credentials, or unlicensed copyrighted content. Only source indexes, reusable contracts, synthetic examples explicitly marked as illustrative, and independently tested tooling belong here.

**Project stage:** Phase 1 — evidence/source registry, terminology, fault ontology, simulation-truth admission contracts and seed annotation quality gates. Automated generation and any Gold Seed designation are out of scope until human review is recorded.

Development happens via feature branches and pull requests. See `docs/` in the working branch for the plan.
## Portable simulation-to-SFT production toolkit

A provider-neutral production Skill is available at
[`skills/dgsi-simulation-to-sft/`](skills/dgsi-simulation-to-sft/README.md).
It guides other AI systems through source ingestion, L0 fact extraction, L1
diagnostic candidate generation, simulator-truth separation, independent
audit and human-review handoff for authorized spacecraft design reports,
test reports and simulation run materials.

The toolkit is **DRAFT / candidate-generation only**. It does not authorize
Gold promotion, formal splits, SFT export or training. In particular, the
current L1 schema does not yet support the distinct
`SIMULATION_CASE_CANDIDATE` and `DESIGN_DERIVED_HYPOTHETICAL` tracks; do not
mislabel those records to force schema acceptance.

Build a portable ZIP from a repository checkout with:

```bash
python scripts/package_dgsi_simulation_to_sft.py
```
