# Local OCR candidate extraction

Optional local OCR uses Tesseract, Pillow and pytesseract. Install the Tesseract executable separately and install Python packages `Pillow` and `pytesseract`; OCR is not a mandatory dependency of the DGSI core.

```powershell
python scripts/ocr_dgsi_image.py --image .\\out\\design_assets\\IMG0001.png --asset-id IMG0001 --language eng --psm 6 --output .\\out\\ocr\\IMG0001.json
```

The output records the source image SHA-256, dimensions, OCR engine/version, language, line/word text, pixel bounding boxes and confidence. Every line remains `MANUAL_REVIEW_REQUIRED`.

OCR does not infer nodes, ports, arrows, edges, units or physical meanings. Low-confidence or blank text is not silently completed. Verify each candidate against the original figure. The OCR output is not an approved diagram graph and cannot enter SFT directly.

Use the OCR record only as an aid to create a separate `diagram_annotation` record; retain distinct source locators and review status.