"""SYNTHETIC_TEST_ONLY: three-message preview never becomes SFT export."""
from __future__ import annotations
import copy,json
from pathlib import Path
import tempfile,unittest
from dgsi.l1_model_projection_preview import build_l1_preview,build_collection_preview
from dgsi.l1_model_projection_audit import L1ProjectionAuditError
ROOT=Path(__file__).resolve().parents[1]
COL=json.loads((ROOT/"examples/l1_literature_synthetic_task_packets_c2_review_candidate_2026-11-17.json").read_text(encoding="utf-8"))
CARDS=json.loads((ROOT/"examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))["cards"]
class L1ThreeMessagePreviewTests(unittest.TestCase):
 def test_all_15_preview_as_three_messages_without_split_or_export(self):
  result=build_collection_preview(COL,source_fact_cards=CARDS)
  self.assertEqual(result["packet_count"],15)
  self.assertEqual(result["event_family_count"],9)
  self.assertEqual(result["sft_records_emitted"],0)
  self.assertFalse(result["training_authorized"])
  self.assertFalse(result["official_splits_assigned"])
  for row in result["preview_records"]:
   self.assertTrue(row["preview_only"])
   self.assertFalse(row["export_authorized"])
   self.assertIsNone(row["split"])
   self.assertEqual([m["role"] for m in row["messages"]],["system","user","assistant"])
   user=json.loads(row["messages"][1]["content"])
   self.assertEqual(user["data_classification"],"LITERATURE_DERIVED_SYNTHETIC_NOT_REAL_RECORD")
   self.assertEqual(json.loads(row["messages"][2]["content"]),next(p["formal_target"] for p in COL["packets"] if p["task_id"]==row["example_id"]))
 def test_preview_deterministic(self):
  self.assertEqual(build_collection_preview(COL,source_fact_cards=CARDS),build_collection_preview(COL,source_fact_cards=CARDS))
 def test_curator_field_in_model_surface_blocks_preview(self):
  packet=copy.deepcopy(COL["packets"][0])
  packet["case"]["input"]["operational_context"]["reviewer_questions"]=["PRIVATE"]
  with self.assertRaisesRegex(L1ProjectionAuditError,"L1_PROJECTION_CURATOR_FIELD_IN_MODEL_SURFACE"):
   build_l1_preview(packet,source_fact_cards=CARDS)
 def test_preview_never_assigns_split(self):
  row=build_l1_preview(COL["packets"][0],source_fact_cards=CARDS)
  self.assertIsNone(row["split"])
  self.assertFalse(row["export_authorized"])
if __name__=="__main__":unittest.main()
