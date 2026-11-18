"""SYNTHETIC_TEST_ONLY. All scorecards and tokens below are fictional."""
import copy
import json
import unittest

from dgsi.l1_c2_expert_handoff import build_c2_expert_handoff
from test_l1_c2_scored_review import COLLECTION, CARDS, _submission


def forms():
    return [build_c2_expert_handoff(COLLECTION, source_fact_cards=CARDS, reviewer_slot=s)
            for s in ("A", "B")]


class ExpertIntakeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.templates = forms()

    def setUp(self):
        from dgsi.l1_c2_expert_intake import (
            C2ExpertIntakeError, audit_c2_expert_intake_against_current_sources,
        )
        self.audit = audit_c2_expert_intake_against_current_sources
        self.error = C2ExpertIntakeError
        self.a, self.b = copy.deepcopy(self.templates)

    def run_audit(self):
        return self.audit(self.a, self.b, COLLECTION, CARDS)

    def test_blank_reordered_and_single_unpaired_complete(self):
        self.b["tasks"].reverse()
        report = self.run_audit()
        self.assertEqual((report["incomplete_scorecard_count"], report["pending_completion_count"],
                          report["paired_review_count"]), (30, 15, 0))
        row = self.a["tasks"][0]
        row["scorecard"] = _submission(row)["blind_review"]["assessments"][0]
        result = self.run_audit()
        self.assertEqual(result["complete_scorecard_count"], 1)
        self.assertEqual(result["ten_dimension_rubric_validated_count"], 0)

    def test_current_match_attestation_and_actionable_reasons(self):
        for i, decision in enumerate(("REVISE", "REJECT", "ACCEPT_L1", "ACCEPT_L1")):
            row = self.a["tasks"][i]
            a, b = _submission(row)["blind_review"]["assessments"]
            b["decision"] = decision
            if i == 2:
                b["scores"]["fault_source"] = 3
            if i == 3:
                b["finding_codes"] = [next(c for c in self.a["allowed_finding_codes"] if c != "NO_ISSUE")]
            row["scorecard"] = a
            self.b["tasks"][i]["scorecard"] = b
        report = self.run_audit()
        self.assertIs(report.get("current_public_source_snapshot_matched"), True)
        for row, expected in zip(report["task_queue"], [
            {"REVIEWER_REQUESTED_REVISION", "RECOMMENDATION_DISAGREEMENT"},
            {"REVIEWER_REJECTED", "RECOMMENDATION_DISAGREEMENT"},
            {"SCORE_GAP"}, {"MATERIAL_FINDING_PRESENT"},
        ]):
            self.assertEqual(set(row["reason_codes"]), expected)

    def test_partial_does_not_claim_rubric_validation(self):
        card = self.a["tasks"][0]["scorecard"]
        card["finding_codes"] = ["NO_ISSUE"]
        card["scores"]["fault_source"] = 1
        self.assertEqual(self.run_audit()["ten_dimension_rubric_validated_count"], 0)

    def test_complete_pairs_delegate_and_hide_all_payload(self):
        for i, (decision, score, codes) in enumerate([
            ("ACCEPT_L1", 5, ["NO_ISSUE"]), ("REVISE", 5, ["NO_ISSUE"]),
            ("REJECT", 5, ["NO_ISSUE"]), ("ACCEPT_L1", 3, ["NO_ISSUE"]),
            ("ACCEPT_L1", 5, [next(c for c in self.a["allowed_finding_codes"] if c != "NO_ISSUE")]),
        ]):
            row = self.a["tasks"][i]
            left, right = _submission(row)["blind_review"]["assessments"]
            right.update(decision=decision, finding_codes=codes)
            right["scores"]["fault_source"] = score
            row["scorecard"] = left
            self.b["tasks"][i]["scorecard"] = right
        report = self.run_audit()
        self.assertEqual(report["adjudication_status_counts"], {
            "PENDING_REVIEWER_AUTHENTICATION": 1, "PENDING_SECURE_ADJUDICATION": 4,
            "PENDING_REVIEW_COMPLETION": 10})
        self.assertEqual(report["ten_dimension_rubric_validated_count"], 5)
        for key in ("identity_authenticated", "source_rights_verified", "official_splits_assigned",
                    "training_authorized", "gold_eligible"):
            self.assertIs(report[key], False)
        for private in ("SYNTHETIC_TEST_ONLY", "NO_ISSUE", "fault_source", '"scores"', codes[0]):
            self.assertNotIn(private, json.dumps(report))
        self.b["tasks"][0]["scorecard"]["scores"]["fault_source"] = 1
        with self.assertRaises(self.error):
            self.run_audit()

    def test_invalid_fields_coverage_and_metadata_fail_closed(self):
        for mutate in [
            lambda d: d.update(training_authorized=0),
            lambda d: d["tasks"][0].update(review_status="PRIVATE"),
            lambda d: d["tasks"].pop(),
            lambda d: d["tasks"].append(d["tasks"][0]),
            lambda d: d["tasks"][0].update(task_id="PRIVATE"),
            lambda d: d["tasks"][0]["scorecard"].update(extra="PRIVATE"),
            lambda d: d["tasks"][0]["scorecard"]["scores"].update(fault_source=True),
            lambda d: d["tasks"][0]["scorecard"]["scores"].pop("fault_source"),
            lambda d: d["tasks"][0]["scorecard"].update(reviewer_token=" "),
            lambda d: d["tasks"][0]["scorecard"].update(decision=[]),
            lambda d: d["tasks"][0]["scorecard"].update(finding_codes=["PRIVATE"]),
            lambda d: d["tasks"][0]["scorecard"].update(finding_codes=["NO_ISSUE"] * 2),
        ]:
            form = copy.deepcopy(self.a)
            mutate(form)
            with self.assertRaises(self.error) as caught:
                self.audit(form, self.b, COLLECTION, CARDS)
            self.assertNotIn("PRIVATE", str(caught.exception))

    def test_global_declared_reviewer_consistency_and_distinctness(self):
        self.a["tasks"][0]["scorecard"]["reviewer_token"] = " PRIVATE "
        for form, token in ((self.a, "OTHER"), (self.b, "PRIVATE")):
            form["tasks"][1]["scorecard"]["reviewer_token"] = token
            with self.assertRaises(self.error) as caught:
                self.run_audit()
            self.assertNotIn(token, str(caught.exception))
            form["tasks"][1]["scorecard"]["reviewer_token"] = None

    def test_stale_current_sources_and_collection(self):
        cards = copy.deepcopy(CARDS)
        for card in cards:
            card["phenomenon_analysis"] += "SYNTHETIC_TEST_ONLY"
        with self.assertRaises(self.error):
            self.audit(self.a, self.b, COLLECTION, cards)
        collection = copy.deepcopy(COLLECTION)
        collection["collection_id"] += "_NEW"
        with self.assertRaises(self.error):
            self.audit(self.a, self.b, collection, CARDS)
