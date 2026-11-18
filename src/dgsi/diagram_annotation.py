"""Semantic checks for human-auditable DGSI diagram graphs."""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
from jsonschema import Draft202012Validator
ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/"skills/dgsi-simulation-to-sft/schemas/diagram_annotation.schema.json"
class DiagramAnnotationError(ValueError): pass
def validate_diagram_annotation(record: dict[str,Any]) -> dict[str,Any]:
 try: schema=json.loads(SCHEMA.read_text(encoding="utf-8"))
 except (OSError,json.JSONDecodeError): raise DiagramAnnotationError("DIAGRAM_SCHEMA_UNAVAILABLE") from None
 if list(Draft202012Validator(schema).iter_errors(record)): raise DiagramAnnotationError("DIAGRAM_SCHEMA_INVALID")
 nodes={n["node_id"] for n in record["nodes"]}
 if len(nodes)!=len(record["nodes"]): raise DiagramAnnotationError("DIAGRAM_DUPLICATE_NODE_ID")
 ports={p["port_id"]:p for p in record["ports"]}
 if len(ports)!=len(record["ports"]): raise DiagramAnnotationError("DIAGRAM_DUPLICATE_PORT_ID")
 if any(p["node_id"] not in nodes for p in ports.values()): raise DiagramAnnotationError("DIAGRAM_PORT_NODE_UNRESOLVED")
 edge_ids=[e["edge_id"] for e in record["edges"]]
 if len(edge_ids)!=len(set(edge_ids)): raise DiagramAnnotationError("DIAGRAM_DUPLICATE_EDGE_ID")
 for edge in record["edges"]:
  if edge["from_port"] not in ports or edge["to_port"] not in ports: raise DiagramAnnotationError("DIAGRAM_EDGE_PORT_UNRESOLVED")
  if edge["from_port"]==edge["to_port"]: raise DiagramAnnotationError("DIAGRAM_SELF_LOOP_UNREVIEWED")
  if edge["direction_basis"]=="INFERRED_UNVERIFIED" and edge["review_status"]=="HUMAN_CONFIRMED": raise DiagramAnnotationError("DIAGRAM_INFERENCE_CANNOT_BE_CONFIRMED")
  if ports[edge["from_port"]]["direction"]=="INPUT" or ports[edge["to_port"]]["direction"]=="OUTPUT": raise DiagramAnnotationError("DIAGRAM_PORT_DIRECTION_CONFLICT")
 return {"decision":"REVIEW_REQUIRED","node_count":len(nodes),"port_count":len(ports),"edge_count":len(edge_ids),"human_confirmed_edge_count":sum(e["review_status"]=="HUMAN_CONFIRMED" for e in record["edges"]),"unresolved_edge_count":sum(e["review_status"]=="UNRESOLVED" for e in record["edges"]),"training_authorized":False,"gold_authorized":False}