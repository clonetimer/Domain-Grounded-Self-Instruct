"""Audit content and dependency snapshots for the local diagram evidence chain."""
from __future__ import annotations
import hashlib, json
from pathlib import Path, PurePosixPath
from typing import Any
from jsonschema import Draft202012Validator
SCHEMA=Path(__file__).resolve().parents[2]/"skills/dgsi-simulation-to-sft/schemas/diagram_artifact_lineage.schema.json"
MAX_ARTIFACTS=256; MAX_FILE_BYTES=128*1024*1024; MAX_TOTAL_BYTES=512*1024*1024
REQUIRED={"DOCUMENT_SOURCE":set(),"EXTRACTED_ASSET":{"DOCUMENT_SOURCE"},"OCR_RECORD":{"EXTRACTED_ASSET"},"TEXT_CANDIDATES":{"EXTRACTED_ASSET","OCR_RECORD"},"TEXT_REVIEW":{"TEXT_CANDIDATES"},"NODE_GRAPH":{"TEXT_REVIEW"},"TOPOLOGY_REVIEW":{"NODE_GRAPH","EXTRACTED_ASSET","DOCUMENT_SOURCE"}}
class ArtifactLineageError(ValueError):
    """Stable payload-free error."""
def canonical_digest(value:Any)->str:
    try: data=json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode()
    except (TypeError,ValueError,UnicodeError,RecursionError): raise ArtifactLineageError("ARTIFACT_LINEAGE_JSON_INVALID") from None
    return hashlib.sha256(data).hexdigest()
def dependency_digest(items):
    return canonical_digest(sorted(({"artifact_id":x["artifact_id"],"sha256":x["sha256"]} for x in items),key=lambda x:x["artifact_id"]))
def _safe_file(root:Path,relative:str)->Path:
    p=PurePosixPath(relative)
    if p.is_absolute() or not p.parts or any(x in {"",".",".."} for x in p.parts) or "\\" in relative or ":" in relative or "\n" in relative or "\r" in relative: raise ArtifactLineageError("ARTIFACT_LINEAGE_PATH_INVALID")
    candidate=root
    for part in p.parts:
        candidate=candidate/part
        if candidate.is_symlink(): raise ArtifactLineageError("ARTIFACT_LINEAGE_SYMLINK_BLOCKED")
    try:
        rr,res=root.resolve(strict=True),candidate.resolve(strict=True)
        if not res.is_relative_to(rr) or not res.is_file(): raise ArtifactLineageError("ARTIFACT_LINEAGE_FILE_UNAVAILABLE")
    except OSError: raise ArtifactLineageError("ARTIFACT_LINEAGE_FILE_UNAVAILABLE") from None
    return res
def _hash_file(path):
    h=hashlib.sha256(); size=0
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""):
                size+=len(chunk)
                if size>MAX_FILE_BYTES: raise ArtifactLineageError("ARTIFACT_LINEAGE_FILE_TOO_LARGE")
                h.update(chunk)
    except ArtifactLineageError: raise
    except OSError: raise ArtifactLineageError("ARTIFACT_LINEAGE_FILE_UNAVAILABLE") from None
    return h.hexdigest(),size
def _validate_graph(artifacts):
    if len(artifacts)>MAX_ARTIFACTS: raise ArtifactLineageError("ARTIFACT_LINEAGE_TOO_MANY_ARTIFACTS")
    by={x["artifact_id"]:x for x in artifacts}
    if len(by)!=len(artifacts): raise ArtifactLineageError("ARTIFACT_LINEAGE_DUPLICATE_ID")
    paths=[x["path"] for x in artifacts]
    if len(set(paths))!=len(paths): raise ArtifactLineageError("ARTIFACT_LINEAGE_DUPLICATE_PATH")
    for x in artifacts:
        parents=x["depends_on"]
        if len(set(parents))!=len(parents): raise ArtifactLineageError("ARTIFACT_LINEAGE_DUPLICATE_DEPENDENCY")
        if x["artifact_id"] in parents or any(p not in by for p in parents): raise ArtifactLineageError("ARTIFACT_LINEAGE_DEPENDENCY_UNKNOWN")
        if not REQUIRED[x["kind"]].issubset({by[p]["kind"] for p in parents}): raise ArtifactLineageError("ARTIFACT_LINEAGE_REQUIRED_PARENT_MISSING")
    order=[]; temp=set(); done=set()
    def visit(a):
        if a in temp: raise ArtifactLineageError("ARTIFACT_LINEAGE_CYCLE")
        if a in done:return
        temp.add(a)
        for p in by[a]["depends_on"]:visit(p)
        temp.remove(a);done.add(a);order.append(a)
    for a in sorted(by):visit(a)
    return by,order
def audit_artifact_lineage(manifest:dict[str,Any],root:str|Path)->dict[str,Any]:
    try:schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
    except (OSError,ValueError):raise ArtifactLineageError("ARTIFACT_LINEAGE_SCHEMA_UNAVAILABLE") from None
    if not Draft202012Validator(schema).is_valid(manifest):raise ArtifactLineageError("ARTIFACT_LINEAGE_MANIFEST_INVALID")
    by,order=_validate_graph(manifest["artifacts"]);base=Path(root)
    if base.is_symlink() or not base.is_dir():raise ArtifactLineageError("ARTIFACT_LINEAGE_ROOT_INVALID")
    actual={};results={};total=0
    for aid in order:
        item=by[aid];digest,size=_hash_file(_safe_file(base,item["path"]));total+=size
        if total>MAX_TOTAL_BYTES:raise ArtifactLineageError("ARTIFACT_LINEAGE_TOTAL_TOO_LARGE")
        actual[aid]=digest;dep=dependency_digest([{"artifact_id":p,"sha256":actual[p]} for p in item["depends_on"]])
        parents_ok=all(results[p]["status"]=="CURRENT" for p in item["depends_on"])
        status="CONTENT_CHANGED" if digest!=item["sha256"] else ("DEPENDENCY_STALE" if dep!=item["dependency_sha256"] or not parents_ok else "CURRENT")
        results[aid]={"artifact_id":aid,"kind":item["kind"],"status":status,"expected_sha256":item["sha256"],"actual_sha256":digest,"expected_dependency_sha256":item["dependency_sha256"],"actual_dependency_sha256":dep,"size_bytes":size}
    stale=sum(x["status"]!="CURRENT" for x in results.values())
    return {"schema_version":"dgsi.diagram-artifact-lineage-audit.v1","snapshot_id":manifest["snapshot_id"],"decision":"CURRENT_SNAPSHOT" if stale==0 else "REVIEW_INVALIDATION_REQUIRED","artifact_count":len(results),"current_count":len(results)-stale,"stale_count":stale,"training_authorized":False,"gold_authorized":False,"not_for_sft":True,"artifacts":[results[k] for k in sorted(results)],"claim_boundary":"Byte and declared dependency snapshot checks only; no source authenticity, reviewer authentication, visual inspection, semantic derivation, or engineering correctness is established."}
