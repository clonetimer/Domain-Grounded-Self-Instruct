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