#!/usr/bin/env python3
"""Audit a local diagram artifact snapshot; --output writes a new report only."""
from __future__ import annotations
import argparse,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from dgsi.diagram_artifact_lineage import ArtifactLineageError,audit_artifact_lineage
def bad(*_):raise ArtifactLineageError("ARTIFACT_LINEAGE_INPUT_INVALID")
def pairs(items):
    out={}
    for k,v in items:
        if k in out:bad()
        out[k]=v
    return out
def read(path):
    try:
        if path.is_symlink() or not path.is_file():bad()
        data=path.read_bytes()
        if len(data)>4*1024*1024:bad()
        return json.loads(data.decode("utf-8"),object_pairs_hook=pairs,parse_constant=bad)
    except (OSError,ValueError,UnicodeError,RecursionError):raise ArtifactLineageError("ARTIFACT_LINEAGE_INPUT_INVALID") from None
def write_new(path,report):
    data=(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+"\n").encode()
    created=False
    try:
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600);created=True
        with os.fdopen(fd,"wb") as f:f.write(data)
    except FileExistsError:raise ArtifactLineageError("ARTIFACT_LINEAGE_OUTPUT_EXISTS") from None
    except OSError:
        if created:
            try:path.unlink()
            except OSError:pass
        raise ArtifactLineageError("ARTIFACT_LINEAGE_OUTPUT_IO_ERROR") from None
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--manifest",required=True,type=Path);p.add_argument("--root",required=True,type=Path);p.add_argument("--output",type=Path);a=p.parse_args()
    try:
        report=audit_artifact_lineage(read(a.manifest),a.root)
        if a.output is not None:write_new(a.output,report)
        keys=("decision","artifact_count","current_count","stale_count","training_authorized","gold_authorized","not_for_sft")
        summary={k:report[k] for k in keys};summary["output_written"]=a.output is not None
        print(json.dumps(summary,sort_keys=True));return 0 if report["stale_count"]==0 else 3
    except ArtifactLineageError as e:
        print(json.dumps({"decision":"BLOCKED","error_code":str(e),"training_authorized":False,"gold_authorized":False}));return 2
if __name__=="__main__":raise SystemExit(main())
