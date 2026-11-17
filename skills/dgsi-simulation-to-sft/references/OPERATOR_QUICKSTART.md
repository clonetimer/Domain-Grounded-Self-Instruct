# DGSI Skill operator quick start

Use the complete `skills/dgsi-simulation-to-sft/` folder. Confirm source-use rights, de-identify restricted data, keep raw logs/telemetry/reviewer identities in authorized private storage, and freeze source hashes, event-family IDs and analysis cutoff.

Run the production sequence: INGEST → L0 → L1 → TARGET → AUDIT → independent REVIEW → PROJECT → COVERAGE → PACKAGE. Never invent missing ML results, logs, measurements, mission modes, commands or outcomes. Synthetic assumptions must remain explicitly synthetic.

## Create a blocked three-message preview

```bash
python scripts/create_l1_model_preview.py --collection examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json --source-facts examples/l0_public_literature_fact_cards_2026-11-15.json --output dist/l1-three-message-preview.json
python -m unittest tests.test_l1_model_projection_preview -v
```

The preview has no split, is not an SFT record, and emits zero authorized rows. The CLI refuses to overwrite an existing output.

## Package the Skill

```bash
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip
python -m unittest tests.test_portable_toolkit_package_build -v
```

Extract to a clean directory and verify the package manifest hashes. Skill release, expert adjudication, source rights, SFT authorization and actual training are separate states.
