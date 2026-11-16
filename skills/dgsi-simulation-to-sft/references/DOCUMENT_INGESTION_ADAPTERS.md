# Document ingestion adapter: DOCX/PDF

This adapter creates a local, source-hashed extraction manifest. It is an intake aid, not a semantic parser or a diagnosis generator.

## DOCX
- Extracts paragraph text and table cell text with document-order locators.
- Preserves OMML equation text conservatively and marks equation blocks for manual mathematical review.
- Indexes embedded image references; it does not OCR images or infer block-diagram topology.
- DOCX pagination is not rendered; locations use paragraph/table order and explicit page-break markers only.
- Tracked deletion and move-from content is excluded from extracted facts. Any tracked revision marks its affected paragraph for manual review and emits a warning. The extractor does not decide which revision is authoritative.
- ZIP member count, total uncompressed size and XML member size are bounded before reading document XML; oversized DOCX files are blocked rather than partially trusted.

## PDF
- Uses optional PyMuPDF (`fitz`) for page-indexed text blocks and image references.
- Install `PyMuPDF` separately when PDF extraction is required. The core validator dependency set does not silently install it.
- Does not reconstruct tables, equation semantics, multi-column reading order or diagram connectivity.
- Scanned PDFs without a text layer require OCR in a separately controlled workflow; the extractor does not invent OCR output.

## Use

```powershell
python scripts/ingest_dgsi_document.py --source .\\design.docx --source-id SRC-DESIGN-001 --output .\\out\\design_manifest.json
```

The manifest includes source SHA-256, size, extracted blocks, figure references and explicit warnings. It is written locally and is not automatically sent to any AI provider. Review every equation, table, figure and ambiguous reading order before generating facts or tasks.

## Boundaries
- Extraction success does not mean source facts are correct.
- A table row is text, not a validated parameter schema.
- An equation string is not a validated equation or unit-consistent model.
- An image reference is not an interpreted architecture diagram.
- Every block remains review-required; no Gold/SFT status is emitted.