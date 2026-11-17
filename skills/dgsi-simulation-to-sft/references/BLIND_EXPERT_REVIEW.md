# DGSI blind expert review protocol

## Purpose and boundary

Use this protocol to prepare a reproducible, metadata-only review request for a frozen L1 candidate collection. The review manifest is an identity and version-binding aid; it is not a scientific approval, reviewer-authentication service, source-rights clearance, Gold admission, split assignment, SFT export or training authorization.

The current P5-C2 pilot contains 15 literature-derived SYNTHETIC packets across 9 source event families. Do not describe these as 15 independent incidents.

## 1. Freeze the candidate

Before requesting review:

1. Freeze the exact L1 collection and matching L0 source-fact cards.
2. Record collection ID, event-family membership and the analysis/source snapshot.
3. Run collection-level schema, source-closure, current-vs-historical evidence-role, curator-isolation and canonical-target checks.
4. Do not edit either input after generating the manifest. Any edit or membership change requires a new manifest and new reviews.

The manifest binds each packet digest, its direct and historical source-fact public digests, and the whole-collection projection digest. Internal curator review content is excluded. The manifest does not include model targets, private reviewer notes, identity data or the dataset itself.

## 2. Generate the review manifest

From a trusted repository checkout:

```bash
python scripts/create_l1_blind_review_manifest.py \
  --collection <authorized-workspace>/l1-candidate-collection.json \
  --source-facts <authorized-workspace>/l0-source-facts.json \
  --output <authorized-workspace>/l1-blind-review-manifest.json
```

The output is metadata-only and has two unassigned reviewer slots. The CLI refuses to overwrite an existing output and publishes via a same-directory temporary file and atomic no-replace hard link. If the filesystem does not support hard links, publication fails closed. Do not replace this with an unsafe rename/copy fallback.

Keep the manifest paired with the exact frozen source snapshots in access-controlled storage. The portable Skill ZIP contains the CLI and reusable validator, not the example L0/L1 datasets.

## 3. Conduct two independent reviews

Assign two qualified reviewers through a separately controlled process. The reviewers must independently assess:

- source and claim fidelity, event/episode identity, flight versus ground-test classification;
- physical mechanism and measurement-chain semantics;
- fault-source component versus affected components;
- current-scenario evidence versus historical Context;
- upstream ML score meaning, ranking and limitations;
- uncertainty, competing hypotheses and correct abstention;
- historical transfer, hardware compatibility and rejected precedents;
- recommendation versus conditional procedure, execution and verified effect;
- source-use rights and any derivative/model-training restrictions.

Both reviewers must receive the same task, source and collection fingerprints. Keep reviewer identities, signed receipts, detailed comments and restricted source material outside the public repository.

## 4. Validate receipts without overclaiming

The structural receipt checker verifies task ID, packet digest, public source digest, whole-collection projection digest, two distinct nonempty tokens and an allowed recommendation. It does not authenticate the tokens or establish reviewer qualifications, independence, correctness, legal rights or adjudication.

Two `ACCEPT` recommendations are still only recommendations. Disagreements on source facts, fault localization, certainty, chronology or disposal semantics require controlled adjudication by an authorized process. Older receipts that omit the collection digest are stale and must be reissued against the current manifest.

## 5. Keep release states separate

Track these states independently:

- `ENGINEERING_REVIEWED_CANDIDATE`: structural and curator checks complete.
- `EXPERT_ADJUDICATED`: independent expert opinions and required adjudication completed and verified outside this structural checker.
- `RIGHTS_CLEARED`: intended source use and derivative/training permissions confirmed.
- `SFT_AUTHORIZED`: all applicable admission, privacy, rights, split and release gates passed.
- `TRAINED`: an authorized training run actually occurred.

The current manifest generator and receipt checker deliberately keep expert adjudication false, rights clearance at zero, official splits unassigned, SFT rows at zero, Gold eligibility false and training disabled.

## 6. Reproducibility and audit

Retain the exact input snapshots, manifest, manifest hash, reviewer receipts, adjudication record, rights decision, tool version and CI evidence in authorized storage. A changed packet, source card or collection membership invalidates prior receipts. Never infer evidence completeness from a checklist, CI pass, public URL or hash alone.
