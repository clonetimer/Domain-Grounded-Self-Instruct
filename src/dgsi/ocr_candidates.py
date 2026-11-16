"""Optional local Tesseract OCR candidate extractor.

OCR text and boxes are proposals only; no diagram nodes, arrows, or physical
relationships are inferred or promoted to training data.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
from typing import Any

MAX_OCR_IMAGE_BYTES = 40 * 1024 * 1024
MAX_OCR_PIXELS = 100_000_000
ALLOWED_LANGUAGES = {"eng", "deu", "fra", "jpn", "chi_sim", "chi_tra"}

class OcrIngestionError(ValueError): pass

def extract_ocr_candidates(image_path: str|Path, asset_id: str, *, language: str="eng", psm: int=6) -> dict[str,Any]:
    path=Path(image_path)
    if path.is_symlink() or not path.is_file(): raise OcrIngestionError("OCR_IMAGE_UNAVAILABLE")
    if not isinstance(psm, int) or isinstance(psm, bool) or not 0 <= psm <= 13:
        raise OcrIngestionError("OCR_PSM_INVALID")
    if not isinstance(language, str) or language not in ALLOWED_LANGUAGES:
        raise OcrIngestionError("OCR_LANGUAGE_UNSUPPORTED")
    try:
        if path.stat().st_size <= 0 or path.stat().st_size > MAX_OCR_IMAGE_BYTES:
            raise OcrIngestionError("OCR_IMAGE_SIZE_INVALID")
    except OSError:
        raise OcrIngestionError("OCR_IMAGE_UNAVAILABLE") from None
    try:
        import pytesseract
        from PIL import Image
        from pytesseract import Output
    except ImportError:
        raise OcrIngestionError("OCR_DEPENDENCY_MISSING_PILLOW_OR_PYTESSERACT") from None
    try:
        data_bytes=path.read_bytes()
        digest=hashlib.sha256(data_bytes).hexdigest()
        with Image.open(path) as image:
            image.load()
            width,height=image.size
            if width<1 or height<1 or width*height>MAX_OCR_PIXELS:
                raise OcrIngestionError("OCR_IMAGE_DIMENSIONS_INVALID")
            raw=pytesseract.image_to_data(image,lang=language,config=f"--psm {psm}",output_type=Output.DICT)
            version=str(pytesseract.get_tesseract_version()).splitlines()[0]
    except OcrIngestionError:
        raise
    except Exception:
        raise OcrIngestionError("OCR_EXECUTION_FAILED") from None
    grouped={}
    count=len(raw.get("text",[]))
    for i in range(count):
        text=str(raw["text"][i]).strip()
        if not text: continue
        try: confidence=float(raw["conf"][i])
        except (ValueError,TypeError): confidence=-1
        if confidence<0: confidence_value=None
        else: confidence_value=max(0.0,min(100.0,confidence))
        key=(raw["block_num"][i],raw["par_num"][i],raw["line_num"][i])
        word={"text":text,"confidence":confidence_value,"bbox_px":{
            "left":int(raw["left"][i]),"top":int(raw["top"][i]),
            "width":int(raw["width"][i]),"height":int(raw["height"][i])}}
        grouped.setdefault(key,[]).append(word)
    lines=[]
    for n,(key,words) in enumerate(sorted(grouped.items()),1):
        left=min(w["bbox_px"]["left"] for w in words); top=min(w["bbox_px"]["top"] for w in words)
        right=max(w["bbox_px"]["left"]+w["bbox_px"]["width"] for w in words)
        bottom=max(w["bbox_px"]["top"]+w["bbox_px"]["height"] for w in words)
        valid=[w["confidence"] for w in words if w["confidence"] is not None]
        lines.append({"line_id":f"L{n:05d}","text":" ".join(w["text"] for w in words),
          "confidence":sum(valid)/len(valid) if valid else None,
          "bbox_px":{"left":left,"top":top,"width":right-left,"height":bottom-top},
          "words":words,"review_status":"MANUAL_REVIEW_REQUIRED"})
    return {"schema_version":"dgsi.ocr-candidates.v1","asset_id":asset_id,"asset_sha256":digest,
      "image_width":width,"image_height":height,"ocr_engine":{"name":"Tesseract","version":version,"page_segmentation_mode":psm},
      "language":language,"lines":lines,
      "warnings":["OCR is a text-recognition proposal; verify against the source image.",
                  "OCR boxes do not identify diagram nodes, ports, arrows, connectivity, units or physical meaning."],
      "review_status":"REVIEW_REQUIRED","training_authorized":False}
