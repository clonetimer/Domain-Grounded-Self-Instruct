"""Build and execute the actual portable toolkit after adding B4.4."""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,tempfile,zipfile
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ArtifactLineagePackageTests(unittest.TestCase):
 def test_full_toolkit_detached_artifact_lineage_tests(self):
  with tempfile.TemporaryDirectory() as t:
   temp=Path(t);z=temp/"toolkit.zip";r=subprocess.run([sys.executable,str(ROOT/"scripts/package_dgsi_simulation_to_sft.py"),"--output",str(z)],cwd=ROOT,capture_output=True,text=True,timeout=60);self.assertEqual(r.returncode,0,r.stderr);dst=temp/"detached"
   with zipfile.ZipFile(z) as a:
    expected={"src/dgsi/diagram_artifact_lineage.py","scripts/audit_diagram_artifact_lineage.py","tests/test_diagram_artifact_lineage.py","skills/dgsi-simulation-to-sft/schemas/diagram_artifact_lineage.schema.json","skills/dgsi-simulation-to-sft/references/DIAGRAM_ARTIFACT_LINEAGE.md","docs/DEVELOPMENT_EXPERIENCE_TOPOLOGY_REVIEW.md"};self.assertTrue(expected.issubset(a.namelist()));m=json.loads(a.read("PACKAGE_SHA256_MANIFEST.json"));self.assertFalse(m["training_authorized"]);self.assertFalse(m["gold_authorized"])
    for x in m["files"]:self.assertEqual(hashlib.sha256(a.read(x["path"])).hexdigest(),x["sha256"])
    for n in a.namelist():self.assertTrue((dst/n).resolve().is_relative_to(dst.resolve()))
    a.extractall(dst)
   env=os.environ.copy();env.pop("PYTHONPATH",None);r=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests","-p","test_diagram_artifact_lineage.py","-v"],cwd=dst,env=env,capture_output=True,text=True,timeout=120);self.assertEqual(r.returncode,0,r.stderr);self.assertIn("test_source_change_invalidates_all_descendants",r.stderr);self.assertIn("OK",r.stderr)
if __name__=="__main__":unittest.main()
