"""SYNTHETIC_TEST_ONLY: reproduce the frozen L1 v0.1 evidence-role audit.

This is an engineering precheck, not source/rights/expert certification.
The PR #122 v0.2 comparison is snapshot-bound but not present on this branch.
"""
from __future__ import annotations
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "examples/p5c2_15task_l0_evidence_role_precheck_2026-11-17.json"
PACKETS = ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json"
CARDS = ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json"


def direct_l0_roles(packet):
    target = packet["formal_target"]
    refs = [
        ref
        for c in target["cause_localization"]["candidates"]
        for ref in c["supporting_refs"]
        if ref.startswith("L0-E-")
    ]
    assessment = target["evidence_assessment"]
    support = [ref for ref in assessment["supporting_refs"] if ref.startswith("L0-E-")]
    conflict = [ref for ref in assessment["contradicting_refs"] if ref.startswith("L0-E-")]
    return {
        "cause_support": refs,
        "evidence_support": support,
        "evidence_contradiction": conflict,
    }


class P5C2EvidenceRoleSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.packets = json.loads(PACKETS.read_text(encoding="utf-8"))["packets"]
        self.cards = json.loads(CARDS.read_text(encoding="utf-8"))["cards"]

    def test_baseline_15_packets_31_direct_roles_and_nine_families(self):
        rows = self.audit["rows"]
        self.assertEqual(len(self.packets), 15)
        self.assertEqual(len(rows), len(self.packets))
        self.assertEqual(sum(x["baseline_role_occurrences"] for x in rows), 31)
        self.assertEqual(self.audit["summary"]["v01_misrole_occurrences"], 31)
        self.assertEqual(self.audit["summary"]["v02_misrole_occurrences"], 21)
        self.assertEqual(len({x["event_family_id"] for x in rows}), 9)
        by_id = {p["task_id"]: p for p in self.packets}
        by_source = {c["case_id"]: c["event_family_id"] for c in self.cards}
        self.assertEqual(set(by_id), {r["task_id"] for r in rows})
        for row in rows:
            packet = by_id[row["task_id"]]
            self.assertEqual(direct_l0_roles(packet), row["baseline_v01_direct_l0_refs"])
            self.assertEqual(
                row["baseline_role_occurrences"],
                sum(map(len, direct_l0_roles(packet).values())),
            )
            self.assertEqual(
                {by_source[x] for x in row["source_fact_refs"]},
                {row["event_family_id"]},
            )
            self.assertEqual(row["source_scientific_review"], "NOT_PERFORMED")
            self.assertEqual(row["expert_adjudication"], "NOT_PERFORMED")
            self.assertEqual(row["rights_clearance"], "NOT_CONFIRMED")

    def test_five_specialized_role_clean_candidates_do_not_count_as_approved(self):
        clean = [r for r in self.audit["rows"] if r["sibling_role_occurrences"] == 0]
        self.assertEqual(len(clean), 5)
        self.assertTrue(all(r["engineering_status"] == "PENDING_EXPERT_REVIEW" for r in clean))
        incomplete = [r for r in self.audit["rows"] if r["sibling_role_occurrences"] > 0]
        self.assertEqual(len(incomplete), 10)
        self.assertTrue(all(r["engineering_status"] == "REVISE_CANDIDATE" for r in incomplete))
        self.assertEqual(sum(r["sibling_role_occurrences"] for r in incomplete), 21)
        self.assertEqual(self.audit["audit_status"], "AUTOMATED_ENGINEERING_PRECHECK_ONLY")
        self.assertFalse(self.audit["summary"]["training_authorized"])
        self.assertEqual(self.audit["summary"]["real_gold"], 0)
        self.assertEqual(self.audit["summary"]["official_splits"], 0)
        self.assertEqual(self.audit["summary"]["sft_authorized_records"], 0)


if __name__ == "__main__":
    unittest.main()
