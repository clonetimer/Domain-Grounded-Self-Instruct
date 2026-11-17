"""SYNTHETIC_TEST_ONLY: fail-closed P5-C0 readiness snapshot drift regressions."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from dgsi.p5c_readiness import P5CReadinessError, audit_p5c_sft_readiness

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    names = (
        "p5c_sft_readiness_baseline_2026-11-17.json",
        "l1_literature_synthetic_task_packets_v0.1.json",
        "l0_public_literature_fact_cards_2026-11-15.json",
    )
    return [
        json.loads((ROOT / "examples" / n).read_text(encoding="utf-8"))
        for n in names
    ]


class P5CReadinessTests(unittest.TestCase):
    def test_real_pilot_snapshot_matches_without_granting_any_rights(self):
        report = audit_p5c_sft_readiness(*fixture())
        self.assertEqual(report["decision"], "BLOCKED_PENDING_INDEPENDENT_REVIEW")
        self.assertEqual(report["literature_synthetic_candidate_packets"], 15)
        self.assertEqual(report["literature_event_families"], 9)
        self.assertEqual(report["l0_source_cards_pending_domain_review"], 12)
        self.assertEqual(report["real_gold_admitted"], 0)
        self.assertFalse(report["training_authorized"])
        self.assertNotIn("L1-SEASAT", repr(report))

    def test_baseline_cannot_overstate_counts(self):
        snapshot, collection, l0 = fixture()
        snapshot["tracks"]["LITERATURE_DERIVED_SYNTHETIC"]["packet_count"] = 16
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SNAPSHOT_STALE"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_task_variant_drift_is_detected(self):
        snapshot, collection, l0 = fixture()
        collection["packets"][0]["case"]["task_type"] = "handover_summary"
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SNAPSHOT_STALE"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_source_event_class_drift_is_detected(self):
        snapshot, collection, l0 = fixture()
        l0["cards"][0]["event_status"] = "GROUND_TEST_EVENT"
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SNAPSHOT_STALE"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_duplicate_source_card_is_blocked(self):
        snapshot, collection, l0 = fixture()
        l0["cards"].append(copy.deepcopy(l0["cards"][0]))
        with self.assertRaisesRegex(P5CReadinessError, "P5C_DUPLICATE_SOURCE_CARD"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_unresolved_source_reference_cannot_be_counted(self):
        snapshot, collection, l0 = fixture()
        collection["packets"][0]["source_fact_refs"] = ["SYNTHETIC-MISSING-CARD"]
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SOURCE_REF_INVALID"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_family_alias_cannot_expand_independent_event_count(self):
        snapshot, collection, l0 = fixture()
        collection["packets"][0]["case"]["provenance"]["source_group"] = (
            "LITERATURE-DERIVED:SEASAT-SLIPRING-ALIAS"
        )
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SOURCE_FAMILY_MISMATCH"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_pending_source_metadata_is_not_expert_authentication(self):
        snapshot, collection, l0 = fixture()
        l0["cards"][0]["domain_review_status"] = "APPROVED"
        with self.assertRaisesRegex(P5CReadinessError, "P5C_SOURCE_REVIEW_NOT_AUTHENTICATED"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_no_splits_gold_or_training_transition(self):
        for edit, code in [
            (lambda s,c,l: c.update({"split_assignments": [{"task_id": "x", "split": "train"}]}), "P5C_UNAUTHORIZED_SPLIT"),
            (lambda s,c,l: c.update({"training_authorized": True}), "P5C_UNAUTHORIZED_TRANSITION"),
            (lambda s,c,l: s["tracks"]["real_case_track"].update({"real_gold_admitted_count": 1}), "P5C_UNAUTHORIZED_TRANSITION"),
        ]:
            snapshot, collection, l0 = fixture()
            edit(snapshot, collection, l0)
            with self.subTest(code=code), self.assertRaisesRegex(P5CReadinessError, code):
                audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_internal_review_and_real_track_leak_fail_closed(self):
        snapshot, collection, l0 = fixture()
        collection["packets"][0]["case"]["internal_review"]["not_for_sft"] = False
        with self.assertRaisesRegex(P5CReadinessError, "P5C_INTERNAL_REVIEW_LEAK_RISK"):
            audit_p5c_sft_readiness(snapshot, collection, l0)
        snapshot, collection, l0 = fixture()
        collection["packets"][0]["track"] = "REAL_GOLD_TRACK"
        with self.assertRaisesRegex(P5CReadinessError, "P5C_CROSS_TRACK_PACKET"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_history_status_must_match_hit_membership(self):
        snapshot, collection, l0 = fixture()
        p = next(p for p in collection["packets"] if p["history_context"]["retrieval_status"] == "HIT")
        p["history_context"]["retrieval_status"] = "NO_HIT"
        with self.assertRaisesRegex(P5CReadinessError, "P5C_HISTORY_STATUS_INVALID"):
            audit_p5c_sft_readiness(snapshot, collection, l0)

    def test_cli_is_aggregate_only_and_read_only(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "audit_p5c_readiness.py")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        self.assertFalse(out["training_authorized"])
        self.assertNotIn("LIT-SEASAT", proc.stdout)
        self.assertNotIn("diagnostic_logs", proc.stdout)


if __name__ == "__main__":
    unittest.main()
