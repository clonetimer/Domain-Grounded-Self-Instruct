from __future__ import annotations
import hashlib,json,sys,tempfile,types,unittest
from pathlib import Path
from unittest import mock
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from dgsi.ocr_candidates import OcrIngestionError,extract_ocr_candidates

class OcrCandidateTests(unittest.TestCase):
 def test_missing_file_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(OcrIngestionError,"OCR_IMAGE_UNAVAILABLE"): extract_ocr_candidates(Path(d)/"missing.png","IMG1")
 def test_ocr_records_words_boxes_hash_and_review_boundary(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"image.png"; p.write_bytes(b"test-image-bytes")
   image=mock.MagicMock(); image.size=(640,480)
   image.__enter__.return_value=image
   fake_pytesseract=types.ModuleType('pytesseract')
   fake_pytesseract.image_to_data=mock.Mock(return_value={
    "text":["ADCS","RW",""],"conf":["95","80","-1"],"block_num":[1,1,1],"par_num":[1,1,1],"line_num":[1,1,1],
    "left":[10,60,0],"top":[20,20,0],"width":[40,30,0],"height":[12,12,0]})
   fake_pytesseract.get_tesseract_version=mock.Mock(return_value="5.4.0")
   fake_pytesseract.Output=types.SimpleNamespace(DICT="DICT")
   pil_package=types.ModuleType("PIL")
   pil_image=types.ModuleType("PIL.Image")
   pil_image.open=mock.Mock(return_value=image)
   pil_package.Image=pil_image
   fake_pytesseract.__path__=[]
   with mock.patch.dict(sys.modules,{"pytesseract":fake_pytesseract,"PIL":pil_package,"PIL.Image":pil_image}):
    result=extract_ocr_candidates(p,"IMG1",language="eng",psm=6)
   self.assertEqual(result["asset_sha256"],hashlib.sha256(b"test-image-bytes").hexdigest())
   self.assertEqual(fake_pytesseract.image_to_data.call_args.kwargs["output_type"],"DICT")
   self.assertEqual(result["lines"][0]["text"],"ADCS RW")
   self.assertEqual(result["lines"][0]["bbox_px"],{"left":10,"top":20,"width":80,"height":12})
   self.assertEqual(result["lines"][0]["review_status"],"MANUAL_REVIEW_REQUIRED")
   self.assertFalse(result["training_authorized"])
   from jsonschema import Draft202012Validator
   schema=json.loads((ROOT/"skills/dgsi-simulation-to-sft/schemas/ocr_candidates.schema.json").read_text())
   Draft202012Validator.check_schema(schema)
   self.assertEqual([],list(Draft202012Validator(schema).iter_errors(result)))
 def test_invalid_psm_and_language_rejected_before_optional_import(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"image.png"; p.write_bytes(b"x")
   for kwargs,code in [({"psm":14},"OCR_PSM_INVALID"),({"psm":True},"OCR_PSM_INVALID"),({"language":"unsupported"},"OCR_LANGUAGE_UNSUPPORTED")]:
    with self.subTest(kwargs=kwargs):
     with self.assertRaisesRegex(OcrIngestionError,code): extract_ocr_candidates(p,"IMG1",**kwargs)
 def test_empty_and_oversized_images_rejected(self):
  from dgsi.ocr_candidates import MAX_OCR_IMAGE_BYTES
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"empty.png"; p.write_bytes(b"")
   with self.assertRaisesRegex(OcrIngestionError,"OCR_IMAGE_SIZE_INVALID"): extract_ocr_candidates(p,"IMG1")
   p.write_bytes(b"x"*(MAX_OCR_IMAGE_BYTES+1))
   with self.assertRaisesRegex(OcrIngestionError,"OCR_IMAGE_SIZE_INVALID"): extract_ocr_candidates(p,"IMG1")
 def test_import_missing_dependencies_is_explicit(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"image.png"; p.write_bytes(b"x")
   with mock.patch.dict(sys.modules,{"pytesseract":None,"PIL":None}):
    with self.assertRaisesRegex(OcrIngestionError,"OCR_DEPENDENCY_MISSING_PILLOW_OR_PYTESSERACT"): extract_ocr_candidates(p,"IMG1")
if __name__=="__main__": unittest.main()
