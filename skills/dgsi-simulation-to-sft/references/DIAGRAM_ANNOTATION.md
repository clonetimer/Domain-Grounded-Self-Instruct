# Diagram annotation: evidence-linked graph

For the next implementation increment, follow `docs/P5B4_DIAGRAM_CANDIDATE_EXTRACTION_CONTRACT.md`. It defines provenance matching, canonical pixel evidence locators, deterministic OCR text grouping and the strict rule that proximity alone cannot create a physical edge.

Use this contract after a figure/image has been indexed and made available to a reviewer. The graph is a structured annotation of visible source content, not an automatically inferred physical model.

## Required objects
- Node: spacecraft, subsystem, unit, component, function or external system.
- Port: named input/output/bidirectional/unknown endpoint, signal or physical medium and unit where visible.
- Edge: from-port/to-port, relation class, direction basis and exact figure locator.
- Claim: visible label, connector, caption, adjacent text or human annotation with an explicit certainty class.

## Evidence and review states
- `AI_PROPOSED`: candidate label/port/edge proposed by a model or annotator; not confirmed.
- `HUMAN_CONFIRMED`: a reviewer checked the actual source figure and recorded its locator.
- `UNRESOLVED`: image quality or semantics do not support a reliable interpretation.
- `INFERRED_UNVERIFIED` direction cannot be marked human-confirmed without new direct evidence.

## Physical meaning boundary
A drawn connector does not by itself prove whether it carries data, command, power, fluid or a mechanical load. A label, arrow, port convention or adjacent text must support the relation. Direction conflicts are rejected by the semantic validator. Units, coordinate frames, signal polarity and timing semantics require explicit source evidence.

## Provenance preflight

Before using OCR or creating annotations, run `python scripts/audit_diagram_asset_provenance.py --document-manifest <manifest.json> --ocr-record <ocr.json> --asset <original-image>` from the repository root. The command checks the manifest/OCR schemas, exact asset ID and SHA-256 linkage, extracted-byte size, unique OCR line IDs, and non-empty in-bounds line/word boxes. It emits aggregate-only output; a pass means provenance consistency, not correct OCR or diagram semantics.

## OCR-only text-region proposals

The current B4.2 implementation preserves every single-line candidate and may add a separate two-line grouping hypothesis when the lines are immediately adjacent in top-to-bottom order, horizontal overlap is at least 0.5 and the vertical gap is no more than twice the larger line height. Group text is joined with a newline in top-to-bottom order. This is a deterministic spatial hypothesis only: it does not decide that the lines name one component, and it never assigns engineering object types, ports, hierarchy or connectivity. Use `python scripts/propose_diagram_text_regions.py --document-manifest <manifest.json> --ocr-record <ocr.json> --asset <original-image> --output <authorized-local-workspace/regions.json>`. The output file contains untrusted OCR text, so only write it to an authorized local annotation workspace. Existing output files are never overwritten, and stdout contains aggregate metadata only.

## Suggested review sequence
1. Open the exact source page and figure; preserve original asset hash.
2. Mark visible node labels and hierarchy; do not invent unnamed components.
3. Mark port labels and direction only when visible or textually specified.
4. Trace each connector; record arrow basis and source locator.
5. Assign relation type only with evidence; otherwise `UNKNOWN`.
6. Run the semantic validator; resolve all dangling node/port references.
7. Have a second reviewer confirm critical physical/control/power paths.

## Not implemented by this contract
- OCR, object detection, line/arrow tracing or visual grounding.
- Automatic inference of engineering semantics.
- Validation against simulator executable connections.
- Gold promotion or SFT export.

The schema and validator ensure referential integrity and prevent some unsupported promotions. They do not prove the diagram annotation is scientifically correct.