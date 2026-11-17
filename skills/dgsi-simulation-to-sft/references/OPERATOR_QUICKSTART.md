# DGSI Skill operator quick start

## What to prepare
Use the complete DGSI Skill folder or extracted toolkit. Before processing, confirm source-use rights, de-identify restricted data, keep raw logs/telemetry/reviewer identities in authorized private storage, and freeze source hashes, event-family IDs and analysis cutoff.

The portable Skill ZIP intentionally does **not** contain the repository's example L0/L1 dataset. This avoids bundling candidate data, source-derived material or private records into the reusable tool. Supply your own authorized collection JSON and matching source-fact JSON from your working directory.

## Run the production sequence
INGEST → L0 → L1 → TARGET → AUDIT → independent REVIEW → PROJECT → COVERAGE → PACKAGE.

Never invent missing ML results, run IDs, logs, measurements, mission modes, commands or outcomes. Missing fields remain missing. Synthetic assumptions stay explicitly synthetic and in their own track.

## Create a blocked three-message preview

Run from the repository root (or use absolute paths to your authorized data files):

```bash
python scripts/create_l1_model_preview.py --collection <authorized-workspace>/l1-candidate-collection.json --source-facts <authorized-workspace>/l0-source-facts.json --output <authorized-workspace>/l1-three-message-preview.json
```

PowerShell example:

```powershell
python scripts/create_l1_model_preview.py --collection "D:\DGSI\input\l1-candidate-collection.json" --source-facts "D:\DGSI\input\l0-source-facts.json" --output "D:\DGSI\output\l1-three-message-preview.json"
```

The preview contains three messages for engineering inspection only. It has no split, is not an SFT record, and emits zero authorized rows. The CLI refuses to overwrite an existing output. Use a separate, versioned output path for each run.

When working in a source checkout, the repository's current review candidate can be used for a smoke test:
```bash
python scripts/create_l1_model_preview.py --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json --output dist/l1-three-message-preview.json
python -m unittest tests.test_l1_model_projection_preview -v
```
The example files above are repository fixtures, not contents of the portable Skill ZIP.

## Package and verify the Skill

From the repository root:
```bash
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip
python -m unittest tests.test_portable_toolkit_package_build -v
```

Extract to a clean directory and verify every path, byte count and SHA-256 in `PACKAGE_SHA256_MANIFEST.json`. The ZIP contains reusable instructions, schemas, validators, scripts and tests, not the dataset.

## Release states
Skill package release, curator review, independent expert adjudication, source rights, SFT authorization and actual training are separate states. A successful preview or ZIP build never grants Gold status, SFT export or training permission.
