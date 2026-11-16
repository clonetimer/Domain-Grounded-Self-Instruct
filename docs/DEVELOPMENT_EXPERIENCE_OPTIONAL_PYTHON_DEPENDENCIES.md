# DGSI development experience: optional Python dependencies and cross-platform CI

Date: 2026-11-16
Incident: OCR candidate extraction PR #88 / correction PR #89
Scope: reusable engineering lessons; no user-specific source material.

## Incident summary

The first OCR candidate implementation passed neither Ubuntu nor Windows CI. Both platforms ran 771 tests and failed the same test:
`test_ocr_records_words_boxes_hash_and_review_boundary`.

The production extractor used normal package imports:

```python
import pytesseract
from PIL import Image
from pytesseract import Output
```

The test double registered `pytesseract.Output` as a separate `sys.modules` entry and represented `pytesseract` / `PIL` with `SimpleNamespace`. This did not reproduce Python's package import semantics: `from pytesseract import Output` resolves an attribute from the imported package, not an independently registered dotted module. The import failed, and the production code correctly returned its optional-dependency error. The failure was in the test harness, not evidence that OCR runtime dependencies were missing on the CI workers.

## Corrective change

PR #89 uses `types.ModuleType` package/module doubles:
- `pytesseract` is a module with `image_to_data`, `get_tesseract_version`, and an `Output` attribute.
- `PIL` is a package module with an `Image` submodule/attribute.
- The test asserts the `Output.DICT` value is actually passed to `image_to_data`.
- The explicit missing-dependency test remains, so optional dependency failure is still fail-closed.

Exact-head PR CI then passed on both operating systems: Ubuntu 771/771 and Windows 771/771.

## Reusable engineering rules

1. **Mock import semantics, not just object shape.** If production uses `import package`, `from package import symbol`, or `from package.submodule import symbol`, tests must model the corresponding package/module hierarchy and attributes.
2. **Do not make optional runtime dependencies mandatory just to satisfy a unit test.** Test the adapter with realistic package doubles; separately test the explicit missing-dependency path.
3. **Separate three validation layers:** dependency import, adapter invocation/argument contract, and output semantics/schema. A test should identify which layer failed.
4. **Treat cross-platform parity as evidence, not assumption.** The same failing test on Ubuntu and Windows often indicates a shared test fixture or contract error; inspect both logs before changing platform-specific code.
5. **Keep failure codes stable and payload-free.** Dependency absence should have one explicit code; do not silently fall back to fabricated OCR text.
6. **Test the adapter boundary with observable calls.** Assert the expected image, language, page segmentation mode and output type were passed to the OCR library.
7. **Do not infer OCR or visual understanding quality from mocked tests.** Mock tests establish integration contract only. Real image accuracy requires a labeled figure benchmark with word/line metrics and engineering-term error analysis.

## DGSI-specific safeguards

- OCR output is a text/geometry candidate, never a verified node, port, arrow or physical relation.
- OCR lines remain `MANUAL_REVIEW_REQUIRED`.
- Asset SHA-256 binds OCR output to the exact image bytes.
- The generation AI does not receive hidden simulator truth or QA-only injection labels.
- No OCR output is Gold or SFT-ready without source review and independent engineering adjudication.

## Verification record

- Failing head: `a3c195ce3b2fca062e6bd54efd0e4d901fdbfc2f`
- Corrected head: `d99c3a09e176c04feb08b09a79e030c7c582d6b2`
- PR workflow: `43877926706`
- Ubuntu: 771/771 PASS
- Windows: 771/771 PASS
- Original push workflow on corrected head: `43877896425`, both platforms PASS

This record documents the cause and repair. It does not claim a real Tesseract OCR benchmark or validate diagram interpretation.
