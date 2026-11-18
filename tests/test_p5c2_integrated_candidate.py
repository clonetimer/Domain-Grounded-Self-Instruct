"""SYNTHETIC_TEST_ONLY: integrated C2 candidate review and blocked projection."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import validate_l1_task_packet_collection
from dgsi.l1_model_projection_audit import audit_l1_synthetic_collection_projection

ROOT=Path(__file__).resolve().parents[1]
CANDIDATE=json.loads((ROOT/"examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json").read_text(encoding="utf-8"))
CARDS=json.loads((ROOT/"examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))["cards"]
CORRECTED=json.loads((ROOT/"examples/l1_literature_synthetic_task_packets_c2_content_corrected_2026-11-18.json").read_text(encoding="utf-8"))
CORRECTED_CARDS=json.loads((ROOT/"examples/l0_public_literature_fact_cards_c2_content_corrected_2026-11-18.json").read_text(encoding="utf-8"))["cards"]
COHORTS=((CANDIDATE,CARDS),(CORRECTED,CORRECTED_CARDS))
class P5C2IntegratedCandidateTests(unittest.TestCase):
 def test_candidate_collection_validates_without_promotion(self):
  for candidate,cards in COHORTS:
   with self.subTest(collection=candidate["collection_id"]):
    r=validate_l1_task_packet_collection(candidate,source_fact_cards=cards)
    self.assertEqual(r["decision"],"VALID_L1_COLLECTION")
    self.assertEqual(r["packet_count"],15)
    self.assertEqual(r["event_family_count"],9)
    self.assertFalse(r["training_authorized"])
    self.assertEqual(r["gold_eligible_count"],0)
 def test_all_current_support_refs_exclude_l0_context_ids(self):
  for p in CANDIDATE["packets"]:
   context={x["evidence_id"] for x in p["case"]["input"]["knowledge_evidence"]}
   refs=p["formal_target"]["evidence_assessment"]["supporting_refs"][:]
   refs += [r for c in p["formal_target"]["cause_localization"]["candidates"] for r in c["supporting_refs"]]
   self.assertFalse(context.intersection(refs),p["task_id"])
 def test_source_context_remains_available_and_bounded(self):
  for p in CANDIDATE["packets"]:
   self.assertTrue(p["case"]["input"]["knowledge_evidence"])
   self.assertTrue(all(x.get("claim_boundary") for x in p["case"]["input"]["knowledge_evidence"]))
 def test_specialized_rejected_sel_history_is_unknown(self):
  for task in ("L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003","L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013"):
   p=next(x for x in CANDIDATE["packets"] if x["task_id"]==task)
   h=next(x for x in p["history_context"]["items"] if x["case_ref"]=="SYNTHETIC-HISTORY-SEL-REJECTED-001")
   self.assertEqual(h["outcome_status"],"REJECTED")
   self.assertEqual(h["hardware_compatibility"],"UNKNOWN")
 def test_canonical_target_binding_all_packets(self):
  for p in CANDIDATE["packets"]: self.assertEqual(p["formal_target"],p["case"]["expected_output"])
 def test_projection_is_blocked_and_emits_zero_rows(self):
  for candidate,cards in COHORTS:
   with self.subTest(collection=candidate["collection_id"]):
    r=audit_l1_synthetic_collection_projection(candidate,source_fact_cards=cards)
    self.assertEqual(r["decision"],"BLOCKED_PENDING_EXTERNAL_ADMISSION")
    self.assertEqual(r["packet_count"],15)
    self.assertEqual(r["event_family_count"],9)
    self.assertEqual(r["sft_records_emitted"],0)
    self.assertFalse(r["internal_review_exported"])
    self.assertFalse(r["training_authorized"])
if __name__=="__main__": unittest.main()
