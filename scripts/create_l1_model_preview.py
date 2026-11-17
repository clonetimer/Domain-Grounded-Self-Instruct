#!/usr/bin/env python3
"""Create a synthetic three-message preview; never emits SFT-authorized rows."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from dgsi.l1_model_projection_preview import build_collection_preview
from dgsi.l1_model_projection_audit import L1ProjectionAuditError

def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--collection",required=True,type=Path)
 p.add_argument("--source-facts",required=True,type=Path)
 p.add_argument("--output",required=True,type=Path)
 a=p.parse_args(argv)
 try:
  collection=json.loads(a.collection.read_text(encoding="utf-8"))
  cards=json.loads(a.source_facts.read_text(encoding="utf-8"))["cards"]
  result=build_collection_preview(collection,source_fact_cards=cards)
  if a.output.exists():
   print(json.dumps({"decision":"REJECTED","error_code":"OUTPUT_ALREADY_EXISTS","sft_records_emitted":0}))
   return 2
  a.output.parent.mkdir(parents=True,exist_ok=True)
  a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 except L1ProjectionAuditError as exc:
  print(json.dumps({"decision":"REJECTED","error_code":str(exc),"sft_records_emitted":0}))
  return 2
 except (OSError,ValueError,KeyError,TypeError):
  print(json.dumps({"decision":"REJECTED","error_code":"INVALID_OR_UNREADABLE_INPUT","sft_records_emitted":0}))
  return 2
 print(json.dumps({"decision":result["decision"],"packet_count":result["packet_count"],"event_family_count":result["event_family_count"],"sft_records_emitted":0,"training_authorized":False}))
 return 0
if __name__=="__main__": raise SystemExit(main())
