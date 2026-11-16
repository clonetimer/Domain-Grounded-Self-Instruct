# P5-B4: evidence-linked diagram candidate extraction contract

Date: 2026-11-16
Status: IMPLEMENTATION SPECIFICATION
Scope: bridge the existing source-hashed image assets, OCR text candidates and diagram annotation graph without claiming autonomous engineering-diagram understanding.

## 1. Objective

Produce a reviewable *candidate graph* from an exact source image and its OCR record. The first increment is deliberately conservative: OCR text may propose labels; geometric proximity may propose candidate associations; neither can establish a physical connection, port direction, signal type or causal relationship.

The output remains `REVIEW_REQUIRED` and `training_authorized=false`. It is not an L1 diagnostic case, Gold record or SFT example.

## 2. Existing contracts to reuse

- Document ingestion manifest binds the source document and figure locator.
- Extracted asset manifest binds the image bytes with SHA-256, size and source locator.
- `dgsi.ocr-candidates.v1` binds OCR lines/words to image hash, dimensions and pixel bounding boxes. OCR line status is `MANUAL_REVIEW_REQUIRED`.
- `dgsi.diagram-annotation.v1` represents nodes, ports, edges, claims and review state.
- Existing semantic validator rejects duplicate IDs, dangling node/port references, port-direction conflicts and promotion of `INFERRED_UNVERIFIED` edges to human-confirmed.

Do not fork these contracts or introduce a second document/asset identity system.

## 3. Candidate-generation pipeline

1. **Resolve provenance.** Require document source ID/hash, figure locator, asset ID/hash and OCR asset hash to agree. Reject mismatches before generating candidates.
2. **Validate OCR record.** Validate schema, positive image dimensions, non-empty unique line IDs, in-bounds non-empty boxes, OCR word containment inside its parent line box and mandatory manual-review status. Preserve raw OCR text and confidence; never silently normalize away the original.
3. **Propose text regions.** Group OCR lines using deterministic spatial rules only (overlap, baseline proximity and bounded horizontal/vertical gaps). Record algorithm/version and thresholds. Each group cites exact OCR line IDs and pixel boxes.
4. **Propose node labels.** Emit candidate labels only from OCR text or explicit human annotations. No component names may be synthesized from domain vocabulary or nearby prose.
5. **Propose hierarchy.** Populate hierarchy only when supported by explicit diagram containment, source text or a human annotation. Otherwise use an empty/unknown hierarchy and retain the unresolved state.
6. **Propose ports and edges.** The initial automated increment must not create physical ports or edges from proximity alone. Such associations may be emitted only as separate unresolved visual hypotheses, never as graph edges. A graph edge requires a visible connector/arrow observation or explicit text/human annotation with an exact locator.
7. **Semantic validation.** Run JSON Schema and semantic validation. Any unresolved reference, duplicate identity, out-of-bounds evidence or unsupported promotion fails closed.
8. **Human review.** Reviewer opens the original image, checks each candidate, and records a direct source locator. Critical power, command, control and mechanical paths require independent second review before any later admission.

## 4. Canonical evidence locator

Use a stable, machine-readable locator string in existing `evidence_locator` fields:

`asset:<asset_id>@sha256:<asset_sha256>#ocr-line:<line_id>#bbox-px:<left>,<top>,<width>,<height>`

For direct visual evidence not represented by OCR:

`asset:<asset_id>@sha256:<asset_sha256>#region-px:<left>,<top>,<width>,<height>#review:<review_record_id>`

The locator must refer to the original, unmodified asset coordinate system. Any crop, rotation, deskew, resize or enhancement creates a derived asset with its own hash and an explicit transform back to the original coordinate frame. Do not reuse coordinates across transformed images without a recorded transform.

## 5. Required candidate metadata

Every candidate batch must record:
- source/document ID and SHA-256;
- asset ID and SHA-256;
- OCR record ID/hash and OCR engine/version/language/PSM;
- candidate-generation algorithm name/version and configuration hash;
- source figure locator and original pixel dimensions;
- candidate IDs, cited OCR line IDs and pixel regions;
- unresolved/low-confidence warnings;
- review status and `training_authorized=false`.

Do not copy raw document text, unrelated figures, hidden truth, QA-only labels or private telemetry into portable examples.

## 6. Fail-closed conditions

Reject the batch if:
- document ingestion is explicitly `BLOCKED`, even if a separately extracted image and OCR record happen to have matching hashes;
- source or asset hash does not match its referenced manifest;
- OCR record refers to another asset;
- OCR line IDs are duplicated or missing;
- a cited box is empty or outside image bounds;
- an AI-generated node/port/edge lacks a precise source locator;
- an edge is inferred solely from proximity, layout order or domain expectation;
- a claim is promoted to observed fact without direct source evidence;
- any record sets training authorization true.

Low OCR confidence is not automatically a hard failure; it must remain visible and unresolved for human review. A missing arrow or ambiguous connector must remain unknown, not be guessed.

## 7. Acceptance tests

- Valid OCR lines on the exact asset produce deterministic label candidates and stable IDs.
- Reordering OCR input does not change candidate identity or output ordering.
- Asset-hash mismatch and OCR-to-asset mismatch are rejected.
- Duplicate/blank line IDs, invalid boxes, out-of-bounds boxes, words outside their parent line boxes and transformed-coordinate misuse are rejected.
- Low-confidence text remains flagged; no automatic domain-term correction.
- Proximity-only association cannot create a graph edge.
- Arrow/connector edge candidates require explicit visual evidence and remain AI_PROPOSED.
- Direction, relation type and units remain UNKNOWN unless explicitly evidenced.
- Existing diagram semantic validator still rejects dangling references, direction conflicts and unsupported human confirmation.
- Full portable ZIP contains the new contract, CLI, tests and development-experience record; package manifest hashes every included file and excludes user-specific assets.
- Ubuntu and Windows exact-head CI both pass.

## 8. Evaluation boundary

Unit tests prove deterministic contracts and failure handling, not visual recognition quality. Before claiming diagram extraction accuracy, assemble a separately labeled benchmark of representative spacecraft block diagrams, wiring/control diagrams, physical layouts and timing/state diagrams. Measure node-label precision/recall, OCR character error rate, port/edge precision/recall, direction accuracy and relation-type accuracy. Report unreadable/ambiguous figures and abstentions separately. Require expert adjudication and inter-reviewer agreement; do not use the frozen L1 holdout or hidden simulator truth as OCR labels.

## 9. Implementation sequence

- B4.1: canonical evidence locator and provenance consistency validator — implemented as `src/dgsi/diagram_provenance.py` and `scripts/audit_diagram_asset_provenance.py`; exact source/asset/OCR hash binding, byte-size matching, unique asset IDs, non-empty unique OCR line IDs, image bounds and word-in-line geometry are checked.
- B4.2: deterministic text-region grouping and candidate-node proposal — next increment; not implemented by the B4.1 validator.
- B4.3: explicit human annotation import and unresolved connector hypotheses.
- B4.4: adversarial tests, package integration and cross-platform CI.
- B4.5: labeled benchmark design; no performance claim until expert labels exist.

P5-B4 is complete only when the portable toolkit, exact-head CI and evidence-boundary tests pass. It does not imply P5-C multi-AI seed production is ready for training.
