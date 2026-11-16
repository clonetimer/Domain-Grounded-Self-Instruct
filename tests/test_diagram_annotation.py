from __future__ import annotations
import copy,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"src"))
from dgsi.diagram_annotation import DiagramAnnotationError,validate_diagram_annotation
class DiagramAnnotationTests(unittest.TestCase):
 def setUp(self):
  self.record={"schema_version":"dgsi.diagram-annotation.v1","source_id":"SRC-1","source_sha256":"a"*64,"asset_id":"IMG-1","asset_sha256":"b"*64,"locator":"PDF page 3 figure 2","diagram_type":"BLOCK_DIAGRAM",
   "nodes":[{"node_id":"N1","label":"ADCS","object_type":"SUBSYSTEM","hierarchy_path":["Spacecraft","ADCS"],"evidence_locator":"visible label ADCS","review_status":"AI_PROPOSED"},{"node_id":"N2","label":"RW","object_type":"UNIT","hierarchy_path":["Spacecraft","ADCS","RW"],"evidence_locator":"visible label RW","review_status":"AI_PROPOSED"}],
   "ports":[{"port_id":"P1","node_id":"N1","label":"cmd out","direction":"OUTPUT","signal_or_medium":"command","unit":None,"evidence_locator":"connector start","review_status":"AI_PROPOSED"},{"port_id":"P2","node_id":"N2","label":"cmd in","direction":"INPUT","signal_or_medium":"command","unit":None,"evidence_locator":"connector end","review_status":"AI_PROPOSED"}],
   "edges":[{"edge_id":"E1","from_port":"P1","to_port":"P2","relation":"CONTROL","direction_basis":"ARROW_IN_DIAGRAM","evidence_locator":"arrow between P1 and P2","review_status":"AI_PROPOSED"}],
   "claims":[{"claim":"An arrow is drawn from command output to RW input","source_type":"VISIBLE_CONNECTOR","evidence_locator":"figure 2","certainty":"OBSERVED_IN_SOURCE"}],"review_status":"REVIEW_REQUIRED","training_authorized":False}
 def reject(self,code,r=None):
  with self.assertRaisesRegex(DiagramAnnotationError,"^"+code+"$"): validate_diagram_annotation(r or self.record)
 def test_valid_proposed_graph(self): self.assertEqual(validate_diagram_annotation(self.record)["edge_count"],1)
 def test_duplicate_node_port_edge_ids_rejected(self):
  for key,item,code in [("nodes",copy.deepcopy(self.record["nodes"][0]),"DIAGRAM_DUPLICATE_NODE_ID"),("ports",copy.deepcopy(self.record["ports"][0]),"DIAGRAM_DUPLICATE_PORT_ID"),("edges",copy.deepcopy(self.record["edges"][0]),"DIAGRAM_DUPLICATE_EDGE_ID")]:
   r=copy.deepcopy(self.record); r[key].append(item); self.reject(code,r)
 def test_unresolved_relationships_rejected(self):
  r=copy.deepcopy(self.record); r["ports"][0]["node_id"]="N404"; self.reject("DIAGRAM_PORT_NODE_UNRESOLVED",r)
  r=copy.deepcopy(self.record); r["edges"][0]["to_port"]="P404"; self.reject("DIAGRAM_EDGE_PORT_UNRESOLVED",r)
 def test_inference_not_promoted_without_human_evidence(self):
  r=copy.deepcopy(self.record); r["edges"][0]["direction_basis"]="INFERRED_UNVERIFIED"; r["edges"][0]["review_status"]="HUMAN_CONFIRMED"; self.reject("DIAGRAM_INFERENCE_CANNOT_BE_CONFIRMED",r)
 def test_port_direction_conflict_rejected(self):
  r=copy.deepcopy(self.record); r["ports"][1]["direction"]="OUTPUT"; self.reject("DIAGRAM_PORT_DIRECTION_CONFLICT",r)
 def test_training_never_authorized(self):
  r=copy.deepcopy(self.record); r["training_authorized"]=True; self.reject("DIAGRAM_SCHEMA_INVALID",r)
if __name__=="__main__": unittest.main()