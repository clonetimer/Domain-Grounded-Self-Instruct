#!/usr/bin/env python3
"""Run local Tesseract OCR and write review-required text candidates."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dgsi.ocr_candidates import OcrIngestionError,extract_ocr_candidates

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--image",required=True,type=Path); p.add_argument("--asset-id",required=True)
 p.add_argument("--output",required=True,type=Path); p.add_argument("--language",default="eng"); p.add_argument("--psm",type=int,default=6)
 a=p.parse_args()
 try:
  result=extract_ocr_candidates(a.image,a.asset_id,language=a.language,psm=a.psm)
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 except OcrIngestionError as e:
  print(json.dumps({"decision":"BLOCKED","error_code":str(e),"training_authorized":False})); return 2
 except OSError:
  print(json.dumps({"decision":"BLOCKED","error_code":"OCR_OUTPUT_IO_ERROR","training_authorized":False})); return 2
 print(json.dumps({"decision":"REVIEW_REQUIRED","line_count":len(result["lines"]),"asset_sha256":result["asset_sha256"],"output":str(a.output),"training_authorized":False})); return 0
if __name__=="__main__": raise SystemExit(main())
