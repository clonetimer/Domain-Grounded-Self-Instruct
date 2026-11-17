"""SYNTHETIC_TEST_ONLY regressions for the P5-C2 specialized-task review candidate."""
from __future__ import annotations
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import validate_l1_task_packet_collection

ROOT=Path(__file__).resolve().parents[1]
COLLECTION=json.loads((ROOT/"examples/l1_literature_synthetic_task_packets_v0.2_review_candidate.json").read_text(encoding="utf-8"))
SOURCE=json.loads((ROOT/"examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))["cards"]
SPECIALIZED={
 "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003",
 "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012",
 "L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013",
 "L1-CASSINI-RWA-NEXT-STEP-SYNTH-014",
 "L1-SPACEBORNE-TWTA-LNA-HANDOVER-SYNTH-015",
}
class SpecializedTaskReviewCandidateTests(unittest.TestCase):
 def test_candidate_collection_passes_existing_l1_contract_without_admission(self):
  result=validate_l1_task_packet_collection(COLLECTION,source_fact_cards=SOURCE)
  self.assertEqual(result["decision"],"VALID_L1_COLLECTION")
  self.assertEqual(result["packet_count"],15)
  self.assertEqual(result["event_family_count"],9)
  self.assertFalse(result["training_authorized"])
  self.assertEqual(result["gold_eligible_count"],0)
  self.assertEqual(result["split_assignment_count"],0)
 def test_specialized_targets_do_not_cite_historical_source_as_current_support(self):
  for packet in COLLECTION["packets"]:
   if packet["task_id"] not in SPECIALIZED: continue
   contextual_ids={x["evidence_id"] for x in packet["case"]["input"].get("knowledge_evidence",[])}
   target=packet["formal_target"]
   for ref in target["evidence_assessment"]["supporting_refs"]:
    self.assertNotIn(ref,contextual_ids,packet["task_id"])
   for candidate in target["cause_localization"]["candidates"]:
    for ref in candidate["supporting_refs"]:
     self.assertNotIn(ref,contextual_ids,packet["task_id"])
 def test_contextual_source_remains_available_for_source_grounding(self):
  for packet in COLLECTION["packets"]:
   if packet["task_id"] not in SPECIALIZED: continue
   self.assertTrue(packet["case"]["input"]["knowledge_evidence"],packet["task_id"])
   self.assertTrue(all(x["claim_boundary"] for x in packet["case"]["input"]["knowledge_evidence"]))
 def test_rejected_sel_history_is_not_declared_hardware_compatible(self):
  for task_id in ("L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003","L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013"):
   packet=next(x for x in COLLECTION["packets"] if x["task_id"]==task_id)
   item=next(x for x in packet["history_context"]["items"] if x["case_ref"]=="SYNTHETIC-HISTORY-SEL-REJECTED-001")
   self.assertEqual(item["outcome_status"],"REJECTED")
   self.assertEqual(item["hardware_compatibility"],"UNKNOWN")
   self.assertTrue(item["applicability_limitations"])
 def test_formal_target_and_case_expected_output_remain_bound(self):
  for packet in COLLECTION["packets"]:
   self.assertEqual(packet["formal_target"],packet["case"]["expected_output"])
 def test_all_packets_remain_review_required_and_training_disabled(self):
  self.assertTrue(all(x["review"]["status"]=="REVIEW_REQUIRED" for x in COLLECTION["packets"]))
  self.assertFalse(COLLECTION["gold_eligible"])
  self.assertFalse(COLLECTION["training_authorized"])
if __name__=="__main__": unittest.main()
