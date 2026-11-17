"""SYNTHETIC_TEST_ONLY tests for dependency snapshot invalidation."""
from __future__ import annotations
import copy,hashlib,json,subprocess,sys,tempfile
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"src"))
def sha(b):return hashlib.sha256(b).hexdigest()
def dep(items):return sha(json.dumps(sorted(({"artifact_id":x["artifact_id"],"sha256":x["sha256"]} for x in items),key=lambda x:x["artifact_id"]),sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False).encode())
class ArtifactLineageTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name)
  self.data={"source":b"source","asset":b"asset","ocr":b"ocr","candidates":b"candidates","review":b"review","graph":b"graph","topology":b"topology"}
  self.roles=[("A0","DOCUMENT_SOURCE","source.bin",[]),("A1","EXTRACTED_ASSET","asset.bin",["A0"]),("A2","OCR_RECORD","ocr.bin",["A1"]),("A3","TEXT_CANDIDATES","candidates.bin",["A1","A2"]),("A4","TEXT_REVIEW","review.bin",["A3"]),("A5","NODE_GRAPH","graph.bin",["A4"]),("A6","TOPOLOGY_REVIEW","topology.bin",["A0","A1","A5"])]
  for k,v in self.data.items():(self.root/(k+".bin")).write_bytes(v)
  items=[]
  for aid,kind,path,parents in self.roles:
   k=Path(path).stem;items.append({"artifact_id":aid,"kind":kind,"path":path,"sha256":sha(self.data[k]),"depends_on":parents,"dependency_sha256":dep([{"artifact_id":p,"sha256":next(x["sha256"] for x in items if x["artifact_id"]==p)} for p in parents])})
  self.manifest={"schema_version":"dgsi.diagram-artifact-lineage.v1","snapshot_id":"SYNTHETIC","artifacts":items,"training_authorized":False,"gold_authorized":False,"not_for_sft":True}
 def audit(self,m=None):
  from dgsi.diagram_artifact_lineage import audit_artifact_lineage
  return audit_artifact_lineage(m or self.manifest,self.root)
 def reject(self,c):
  from dgsi.diagram_artifact_lineage import ArtifactLineageError
  with self.assertRaisesRegex(ArtifactLineageError,"^"+c+"$"):self.audit()
 def test_complete_chain_current(self):
  r=self.audit();self.assertEqual((r["artifact_count"],r["current_count"],r["stale_count"]),(7,7,0));self.assertEqual(r["decision"],"CURRENT_SNAPSHOT")
 def test_source_change_invalidates_all_descendants(self):
  (self.root/"source.bin").write_bytes(b"changed");self.assertEqual(self.audit()["stale_count"],7)
 def test_leaf_change_does_not_invalidate_ancestors(self):
  (self.root/"topology.bin").write_bytes(b"changed");s={x["artifact_id"]:x["status"] for x in self.audit()["artifacts"]};self.assertEqual(s["A6"],"CONTENT_CHANGED");self.assertTrue(all(s[f"A{i}"]=="CURRENT" for i in range(6)))
 def test_middle_change_invalidates_only_descendants(self):
  (self.root/"ocr.bin").write_bytes(b"changed");s={x["artifact_id"]:x["status"] for x in self.audit()["artifacts"]};self.assertEqual(s,{"A0":"CURRENT","A1":"CURRENT","A2":"CONTENT_CHANGED","A3":"DEPENDENCY_STALE","A4":"DEPENDENCY_STALE","A5":"DEPENDENCY_STALE","A6":"DEPENDENCY_STALE"})
 def test_order_independent(self):
  a=self.audit()["artifacts"];self.manifest["artifacts"].reverse();self.assertEqual(a,self.audit()["artifacts"])
 def test_duplicate_id(self):
  self.manifest["artifacts"].append(copy.deepcopy(self.manifest["artifacts"][0]));self.reject("ARTIFACT_LINEAGE_DUPLICATE_ID")
 def test_duplicate_artifact_path(self):
  self.manifest["artifacts"][1]["path"]="source.bin";self.reject("ARTIFACT_LINEAGE_DUPLICATE_PATH")
 def test_trailing_newline_path_rejected(self):
  self.manifest["artifacts"][0]["path"]="source.bin\\n";self.reject("ARTIFACT_LINEAGE_PATH_INVALID")
 def test_unknown_dependency(self):
  self.manifest["artifacts"][1]["depends_on"]=["MISSING"];self.reject("ARTIFACT_LINEAGE_DEPENDENCY_UNKNOWN")
 def test_duplicate_dependency(self):
  self.manifest["artifacts"][1]["depends_on"]=["A0","A0"];self.reject("ARTIFACT_LINEAGE_DUPLICATE_DEPENDENCY")
 def test_cycle(self):
  self.manifest["artifacts"][0]["depends_on"]=["A6"];self.reject("ARTIFACT_LINEAGE_CYCLE")
 def test_required_parent_kind(self):
  self.manifest["artifacts"][2]["depends_on"]=["A0"];self.manifest["artifacts"][2]["dependency_sha256"]=dep([{"artifact_id":"A0","sha256":self.manifest["artifacts"][0]["sha256"]}]);self.reject("ARTIFACT_LINEAGE_REQUIRED_PARENT_MISSING")
 def test_missing_file(self):
  (self.root/"ocr.bin").unlink();self.reject("ARTIFACT_LINEAGE_FILE_UNAVAILABLE")
 def test_symlink_blocked(self):
  target=self.root/"target";target.write_bytes(b"x");link=self.root/"source.bin";link.unlink()
  try:link.symlink_to(target)
  except (OSError,NotImplementedError):self.skipTest("symlink unavailable")
  self.reject("ARTIFACT_LINEAGE_SYMLINK_BLOCKED")
 def test_path_traversal_schema_blocked(self):
  self.manifest["artifacts"][0]["path"]="../x";self.reject("ARTIFACT_LINEAGE_MANIFEST_INVALID")
 def test_absolute_path_schema_blocked(self):
  self.manifest["artifacts"][0]["path"]="/tmp/x";self.reject("ARTIFACT_LINEAGE_MANIFEST_INVALID")
 def test_dependency_digest_tamper(self):
  self.manifest["artifacts"][1]["dependency_sha256"]="f"*64;r=self.audit();self.assertEqual(r["artifacts"][1]["status"],"DEPENDENCY_STALE");self.assertEqual(r["stale_count"],6)
 def test_empty_snapshot_not_training(self):
  r=self.audit(dict(self.manifest,artifacts=[]));self.assertEqual(r["artifact_count"],0);self.assertFalse(r["training_authorized"])
 def test_schema_valid(self):
  from jsonschema import Draft202012Validator
  s=json.loads((ROOT/"skills/dgsi-simulation-to-sft/schemas/diagram_artifact_lineage.schema.json").read_text());Draft202012Validator.check_schema(s)
class ArtifactLineageCliTests(unittest.TestCase):
 SCRIPT=ROOT/"scripts/audit_diagram_artifact_lineage.py"
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.root=Path(self.t.name);self.ws=self.root/"ws";self.ws.mkdir();(self.ws/"source.bin").write_bytes(b"source")
  item={"artifact_id":"A0","kind":"DOCUMENT_SOURCE","path":"source.bin","sha256":sha(b"source"),"depends_on":[],"dependency_sha256":dep([])}
  self.manifest={"schema_version":"dgsi.diagram-artifact-lineage.v1","snapshot_id":"SYNTHETIC","artifacts":[item],"training_authorized":False,"gold_authorized":False,"not_for_sft":True};self.path=self.root/"manifest.json";self.path.write_text(json.dumps(self.manifest))
 def runcli(self,*args):return subprocess.run([sys.executable,str(self.SCRIPT),"--manifest",str(self.path),"--root",str(self.ws),*args],capture_output=True,text=True)
 def test_cli_current(self):
  r=self.runcli();self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)["decision"],"CURRENT_SNAPSHOT")
 def test_cli_stale_exit_three(self):
  (self.ws/"source.bin").write_bytes(b"changed");r=self.runcli();self.assertEqual(r.returncode,3);self.assertEqual(json.loads(r.stdout)["decision"],"REVIEW_INVALIDATION_REQUIRED")
 def test_cli_new_report(self):
  out=self.root/"report.json";r=self.runcli("--output",str(out));self.assertEqual(r.returncode,0);self.assertTrue(out.is_file())
 def test_cli_no_overwrite(self):
  out=self.root/"keep.json";out.write_bytes(b"KEEP");r=self.runcli("--output",str(out));self.assertEqual(r.returncode,2);self.assertEqual(out.read_bytes(),b"KEEP")
 def test_cli_duplicate_keys(self):
  self.path.write_text('{"a":1,"a":2}');r=self.runcli();self.assertEqual(r.returncode,2);self.assertEqual(json.loads(r.stdout)["error_code"],"ARTIFACT_LINEAGE_INPUT_INVALID")
 def test_cli_invalid_utf8(self):
  self.path.write_bytes(bytes([255]));r=self.runcli();self.assertEqual(r.returncode,2)
 def test_cli_help(self):
  r=subprocess.run([sys.executable,str(self.SCRIPT),"--help"],capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertIn("--manifest",r.stdout)
if __name__=="__main__":unittest.main()
