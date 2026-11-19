# DGSI Skill operator quick start

For the completed v0.2.0 development workflow, start with [CLOSEOUT_QUICKSTART.md](CLOSEOUT_QUICKSTART.md). The commands below retain the external human-review route for later formal admission.

## What to prepare
Use the complete DGSI Skill folder or extracted toolkit. Before processing, confirm source-use rights, de-identify restricted data, keep raw logs/telemetry/reviewer identities in authorized private storage, and freeze source hashes, event-family IDs and analysis cutoff.

Use Python 3.11 or later and install the declared validation dependency:

```bash
python -m pip install -r requirements-validation.txt
```

The v0.2.0 ZIP includes an explicit public SYNTHETIC development demo under `evaluation/closeout_20261119/`. It excludes private user cases and unrestricted data directories. For your own data, supply authorized collection JSON and matching source-fact JSON.

The 2026-11-18 content-corrected cohort requires toolkit **0.2.0-rc.4** for its three task-specific instructions. Pair that cohort with its matching L0 and newly generated A/B forms. Original RC2 forms remain bound to the unchanged 2026-11-17 snapshot; do not transplant their metadata to a new cohort. The full content changes and source limitations are in `docs/P5C2_CONTENT_CORRECTION_2026-11-18.md`.

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
python scripts/create_l1_model_preview.py --collection examples/l1_literature_synthetic_task_packets_c2_content_corrected_2026-11-18.json --source-facts examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json --output dist/l1-three-message-preview.json
python -m unittest discover -s tests -p test_skill_delivery.py -v
```
The `examples/` paths above require a repository checkout; the standalone package includes its separate four-case demo fixtures.

## Generate separate expert review packs

From the extracted toolkit directory, supply the same frozen external L0/L1 inputs used for the preview. Create the output parent directory first and choose a new ZIP filename:

```bash
python scripts/create_l1_c2_complete_review_kit.py --collection /authorized/input/l1-candidate-collection.json --source-facts /authorized/input/l0-source-facts.json --output-file /authorized/output/C2-review-only.zip
```

The coordinator ZIP contains `reviewer_A.zip` and `reviewer_B.zip`. Each includes its own blank Word/JSON form and the same scientific dossier. Distribute the inner ZIPs separately through an authorized channel. The outer coordinator manifest binds the cohort and both archive hashes. Keep the original `C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json` unchanged and edit a separate copy for rights evidence intake.

## Receive independent expert forms

Keep each original JSON and have the corresponding reviewer fill a separate copy. Only `tasks[].scorecard` may change. Leave all other template metadata, including the original blank/status labels, unchanged. The intake report records the new completion state. Each reviewer uses one consistent private token throughout their form; A and B use distinct tokens. The ten scores are integers 1–5, with a decision `ACCEPT_L1`, `REVISE` or `REJECT` and the existing fixed finding codes. Unfilled values remain `null`; never generate missing scores. Word is a readable working copy: a completed Word form must be faithfully transcribed to its matching JSON and checked by the reviewer before intake.

Supply current L0/L1 files independently of the returned forms. From the extracted toolkit, choose a new private report filename in an existing directory:

```bash
python scripts/audit_l1_c2_current_expert_intake.py --reviewer-a /authorized/review/reviewer-A-return.json --reviewer-b /authorized/review/reviewer-B-return.json --current-collection /authorized/input/l1-candidate-collection.json --current-l0-facts /authorized/input/l0-source-facts.json --output-file /authorized/review/current-expert-intake.json
```

PowerShell:

```powershell
python scripts/audit_l1_c2_current_expert_intake.py --reviewer-a "D:\DGSI\review\reviewer-A-return.json" --reviewer-b "D:\DGSI\review\reviewer-B-return.json" --current-collection "D:\DGSI\input\l1-candidate-collection.json" --current-l0-facts "D:\DGSI\input\l0-source-facts.json" --output-file "D:\DGSI\review\current-expert-intake.json"
```

Stdout contains aggregate counts. The optional private file contains the source-bound task queue and fixed next actions, without reviewer tokens or scores. Existing files and symlinks are never overwritten. Omit `--output-file` for counts only.

| Intake state | Coordinator action |
|---|---|
| `PENDING_REVIEW_COMPLETION` | Obtain missing independent assessment fields. A blank or partly filled scorecard is not a completed review. |
| `PENDING_SECURE_ADJUDICATION` | Resolve REVISE, REJECT, substantive findings or disagreement in the authorized review process. Reviewer identity remains unverified. |
| `PENDING_REVIEWER_AUTHENTICATION` | Verify reviewer identities and independence; complete source rights and authoritative admission separately. |

A missing task row, duplicate task, changed binding or invalid field rejects the intake. Reordering task rows is allowed. Changing current L0/L1 review material requires new forms and re-review. RC2 forms for an unchanged candidate are compatible with this RC3 intake. See `docs/P5C2_CURRENT_EXPERT_INTAKE_20261118.md` for the precise boundary and partial-form behavior.

## Audit a rights worksheet against current sources

Use the four-file command for a real intake. Supply current L0/L1 inputs independently of the editable worksheet:

```bash
python scripts/audit_l1_c2_current_rights_intake.py --blank /authorized/review/C2_SOURCE_RIGHTS_CLEARANCE_QUEUE_BLANK.json --submission /authorized/review/rights-submission.json --current-collection /authorized/input/l1-candidate-collection.json --current-l0-facts /authorized/input/l0-source-facts.json
```

A successful result means the source snapshot and worksheet structure agree. Evidence submission still requires independent rights review. The tool cannot grant permission or authorize training. The older `audit_l1_c2_source_rights_intake.py` two-file command is a structural diagnostic and does not establish that the supplied blank is current. See `docs/P5C2_CURRENT_SOURCE_RIGHTS_PREFLIGHT_20261118.md` for the intake contract.

## Build the Skill from a source checkout

From the repository root:
```bash
python scripts/package_dgsi_simulation_to_sft.py --output dist/dgsi-simulation-to-sft-toolkit.zip
python -m unittest tests.test_portable_toolkit_package_build -v
```

Extract to a clean directory and verify every path, byte count and SHA-256 in `PACKAGE_SHA256_MANIFEST.json`. The ZIP contains reusable instructions, schemas, validators, scripts, tests and an allowlisted public SYNTHETIC development demo. It does not contain private user data or an admitted training dataset.

## Release states
Skill package release, curator review, independent expert adjudication, source rights, SFT authorization and actual training are separate states. A successful preview or ZIP build never grants Gold status, SFT export or training permission.

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
