# DGSI development experience — returned C2 advisory (lessons 133–136)

## 133 — Distinguish advisory from human review
A package can contain two scorecard-shaped JSONs without containing two independent reviewers. Treat explicit provenance fields, authentication flags, reviewer count and official-handoff compatibility as authoritative. Never import a same-AI two-lens output into the human intake.

## 134 — Compare structured targets against the actual model-facing input
A narrative may correctly qualify a mechanism while a structured enum-like field overstates it. Validate `fault_mode`, source localization and status fields against upstream ML findings and current evidence, not only against report_text.

## 135 — Version every correction that changes a review-bound projection
Do not overwrite a reviewed cohort. Create a new collection ID and file, recompute the projection fingerprint, regenerate all cohort-bound A/B forms and rights queue, and reject old receipts against the new snapshot.

## 136 — Rights evidence triage is not a licence
Public access, a government metadata label, a mirror-copy notice, a publisher general policy or a different-DOI licence are evidence leads, not automatically permission for extraction, model training or redistribution. Keep rights decision, permitted scope and evidence reference null until independently supported.
