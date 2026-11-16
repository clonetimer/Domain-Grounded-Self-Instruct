#!/usr/bin/env python3
"""Local DGSI document extraction CLI; output remains on the local machine."""
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dgsi.document_ingestion import DocumentIngestionError,ingest_document

def main():
 p=argparse.ArgumentParser(description=__doc__); p.add_argument("--source",required=True,type=Path); p.add_argument("--source-id",required=True); p.add_argument("--output",required=True,type=Path); a=p.parse_args()
 try:
  result=ingest_document(a.source,a.source_id); a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
 except DocumentIngestionError as e: print(json.dumps({"decision":"BLOCKED","error_code":str(e),"training_authorized":False})); return 2
 except OSError: print(json.dumps({"decision":"BLOCKED","error_code":"DOCUMENT_IO_ERROR","training_authorized":False})); return 2
 print(json.dumps({"decision":"REVIEW_REQUIRED","media_type":result["media_type"],"page_count":len(result["pages"]),"asset_count":len(result["assets"]),"sha256":result["sha256"],"output":str(a.output),"training_authorized":False})); return 0
if __name__=="__main__": raise SystemExit(main())