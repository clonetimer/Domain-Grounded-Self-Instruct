"""SYNTHETIC_TEST_ONLY: global Case / upstream-run identity collision checks.

The synthetic fixture identifiers below do not refer to real telemetry,
real algorithm runs, or authorized training materials.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_global_lineage import (
    L1GlobalLineageError,
    audit_l1_cross_collection_lineage,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json"
L0 = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"
FUSE = "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012"
CASSINI = "L1-CASSINI-RWA-DRAG-SYNTH-008"
TROPICS_A = "L1-TROPICS-PATHFINDER-CROSSSHORT-SYNTH-003"
TROPICS_B = "L1-TROPICS-PATHFINDER-EVIDENCE-SUFFICIENCY-SYNTH-013"


def batches(first=FUSE, second=CASSINI):
    source = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    cards = json.loads(L0.read_text(encoding="utf-8"))["cards"]
    result = []
    for position, identifier in enumerate([first, second]):
        collection = copy.deepcopy(source)
        collection["collection_id"] = f"SYNTHETIC-COLLISION-BATCH-{position}"
        collection["packets"] = [
            packet for packet in collection["packets"]
            if packet["task_id"] == identifier
        ]
        assert len(collection["packets"]) == 1
        collection["packet_count"] = 1
        collection["split_assignments"] = []
        result.append({"collection": collection, "source_fact_cards": copy.deepcopy(cards)})
    return result


def case(batch):
    return batch["collection"]["packets"][0]["case"]


class GlobalCaseRunFamilyTests(unittest.TestCase):
    def test_different_families_with_distinct_ids_are_structurally_valid(self):
        report = audit_l1_cross_collection_lineage(batches())
        self.assertEqual(report["task_count"], 2)
        self.assertEqual(report["decision"], "STRUCTURAL_PREFLIGHT_ONLY")
        self.assertFalse(report["training_authorized"])

    def test_cross_family_case_id_collision_fails_before_any_split(self):
        items = batches()
        case(items[1])["case_id"] = case(items[0])["case_id"]
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_CASE_ID_FAMILY_COLLISION"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_cross_family_upstream_run_collision_fails_before_any_split(self):
        items = batches()
        case(items[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            case(items[0])["provenance"]["diagnosis_run_refs"]
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_DIAGNOSIS_RUN_FAMILY_COLLISION"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_same_family_run_reuse_is_allowed_for_task_variants(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            case(items[0])["provenance"]["diagnosis_run_refs"]
        )
        result = audit_l1_cross_collection_lineage(items)
        self.assertEqual(result["track_family_counts"]["LITERATURE_DERIVED_SYNTHETIC"], 1)
        self.assertFalse(result["training_authorized"])

    def test_same_family_case_id_cannot_hide_distinct_upstream_runs(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["case_id"] = case(items[0])["case_id"]
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_CASE_ID_EVIDENCE_SNAPSHOT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_same_family_case_id_can_serve_multiple_targets_if_snapshot_identical(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["case_id"] = case(items[0])["case_id"]
        case(items[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            case(items[0])["provenance"]["diagnosis_run_refs"]
        )
        result = audit_l1_cross_collection_lineage(items)
        self.assertEqual(result["task_count"], 2)
        self.assertFalse(result["training_authorized"])

    def test_same_case_id_changed_log_payload_is_blocked(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["case_id"] = case(items[0])["case_id"]
        case(items[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            case(items[0])["provenance"]["diagnosis_run_refs"]
        )
        case(items[1])["input"]["diagnostic_logs"][0]["content"] = (
            "合成对抗测试：相同案例编号携带了不同的诊断日志。"
        )
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_CASE_ID_EVIDENCE_SNAPSHOT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(items)

    def test_same_case_id_changed_analysis_cutoff_is_blocked(self):
        items = batches(TROPICS_A, TROPICS_B)
        case(items[1])["case_id"] = case(items[0])["case_id"]
        case(items[1])["provenance"]["diagnosis_run_refs"] = copy.deepcopy(
            case(items[0])["provenance"]["diagnosis_run_refs"]
        )
        case(items[1])["input"]["analysis_cutoff"] = "2026-04-12T09:11:00Z"
        with self.assertRaisesRegex(
            L1GlobalLineageError, "GLOBAL_CASE_ID_EVIDENCE_SNAPSHOT_CONFLICT"
        ):
            audit_l1_cross_collection_lineage(items)


if __name__ == "__main__":
    unittest.main()
