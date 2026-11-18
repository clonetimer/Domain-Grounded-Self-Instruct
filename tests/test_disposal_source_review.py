"""SYNTHETIC_TEST_ONLY — local source-excerpt/disposal audit adversarial cases."""
import copy
import hashlib
import json
import unittest
from pathlib import Path

from dgsi.disposal_source_review import (
    DisposalSourceReviewError,
    audit_disposal_source_review,
)

ROOT = Path(__file__).resolve().parents[1]


def synthetic_case():
    return json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))


def synthetic_executed():
    case = synthetic_case()
    action = "SYNTHETIC ONLY: scheduled slew command completed"
    case["expected_output"]["disposal_status"] = "RECORDED"
    case["expected_output"]["disposal_measures"] = [{
        "measure": action, "measure_type": "EXECUTED", "evidence_refs": ["LOG-02"],
    }]
    review = {
        "schema_version": "dgsi-disposal-source-review.v1",
        "case_ref": case["case_id"],
        "not_for_sft": True,
        "reviewer_id": "SYNTHETIC_EXPERT_ONLY",
        "reviewer_role": "INDEPENDENT_DOMAIN_EXPERT",
        "reviewed_at": "2026-05-01T00:00:00Z",
        "attestations": [{
            "measure_index": 0,
            "measure_sha256": hashlib.sha256(action.encode("utf-8")).hexdigest(),
            "evidence_ref": "LOG-02",
            "verbatim_excerpt": "The slew command was completed",
            "source_action_type": "EXECUTED",
            "verdict": "SUPPORTED",
        }],
    }
    return case, review


def synthetic_recommended():
    case = synthetic_case()
    action = "SYNTHETIC ONLY: source recommends review of wheel feedback"
    case["input"]["knowledge_evidence"][0]["excerpt"] = (
        "SYNTHETIC ONLY source recommends review of wheel feedback before corrective action."
    )
    case["expected_output"]["disposal_status"] = "RECOMMENDED_ONLY"
    case["expected_output"]["disposal_measures"] = [{
        "measure": action, "measure_type": "RECOMMENDED", "evidence_refs": ["DOC-E-01"],
    }]
    review = synthetic_executed()[1]
    review["attestations"] = [{
        "measure_index": 0,
        "measure_sha256": hashlib.sha256(action.encode("utf-8")).hexdigest(),
        "evidence_ref": "DOC-E-01",
        "verbatim_excerpt": "source recommends review of wheel feedback",
        "source_action_type": "RECOMMENDED",
        "source_published_at": "2026-01-01T00:00:00Z",
        "verdict": "SUPPORTED",
    }]
    return case, review


def synthetic_multi_source():
    """Two independent SYNTHETIC records citing the same stated action."""
    case, review = synthetic_executed()
    case["input"]["diagnostic_logs"][0]["content"] += (
        " SYNTHETIC ONLY: The slew command was completed and recorded."
    )
    case["expected_output"]["disposal_measures"][0]["evidence_refs"] = [
        "LOG-02", "LOG-01",
    ]
    second = copy.deepcopy(review["attestations"][0])
    second["evidence_ref"] = "LOG-01"
    second["verbatim_excerpt"] = "SYNTHETIC ONLY: The slew command was completed"
    review["attestations"].append(second)
    return case, review


class SyntheticDisposalSourceReviewTests(unittest.TestCase):
    def rejects(self, case, review, code):
        with self.assertRaisesRegex(DisposalSourceReviewError, code):
            audit_disposal_source_review(case, review)

    def test_synthetic_documented_action_requires_explicit_review(self):
        case, review = synthetic_executed()
        output = audit_disposal_source_review(case, review)
        self.assertEqual(output["measure_count"], 1)
        self.assertFalse(output["gold_approved"])
        self.assertFalse(output["expert_identity_verified"])

    def test_not_recorded_requires_no_attestation(self):
        case = synthetic_case()
        review = synthetic_executed()[1]
        review["attestations"] = []
        self.assertEqual(audit_disposal_source_review(case, review)["measure_count"], 0)

    def test_unreviewed_action_is_blocked(self):
        case, review = synthetic_executed()
        review["attestations"] = []
        self.rejects(case, review, "DISPOSAL_REVIEW_COVERAGE_MISMATCH")

    def test_reviewer_denies_semantic_support(self):
        case, review = synthetic_executed()
        review["attestations"][0]["verdict"] = "UNSUPPORTED"
        self.rejects(case, review, "DISPOSAL_SOURCE_NOT_EXPERT_SUPPORTED")

    def test_forged_text_not_present_in_record(self):
        case, review = synthetic_executed()
        review["attestations"][0]["verbatim_excerpt"] = "SYNTHETIC ONLY: thrusters were fired"
        self.rejects(case, review, "DISPOSAL_EXCERPT_NOT_IN_CITED_SOURCE")

    def test_measure_changed_after_attestation(self):
        case, review = synthetic_executed()
        case["expected_output"]["disposal_measures"][0]["measure"] += " changed"
        self.rejects(case, review, "DISPOSAL_MEASURE_CHANGED_AFTER_REVIEW")

    def test_review_citation_not_in_measure(self):
        case, review = synthetic_executed()
        review["attestations"][0]["evidence_ref"] = "LOG-01"
        self.rejects(case, review, "UNBOUND_DISPOSAL_SOURCE_REVIEW")

    def test_execution_with_unknown_log_time_blocked(self):
        case, review = synthetic_executed()
        case["input"]["diagnostic_logs"][1]["timestamp"] = None
        self.rejects(case, review, "DISPOSAL_SOURCE_TIME_MISSING")

    def test_duplicate_reviews_cannot_replace_coverage(self):
        case, review = synthetic_executed()
        case["expected_output"]["disposal_measures"].append(
            copy.deepcopy(case["expected_output"]["disposal_measures"][0])
        )
        review["attestations"].append(copy.deepcopy(review["attestations"][0]))
        self.rejects(case, review, "DUPLICATE_DISPOSAL_MEASURE_REVIEW")

    def test_review_packet_must_not_be_sft_content(self):
        case, review = synthetic_executed()
        review["not_for_sft"] = False
        self.rejects(case, review, "SOURCE_REVIEW_MUST_BE_INTERNAL")

    def test_review_role_must_be_explicit(self):
        case, review = synthetic_executed()
        review["reviewer_role"] = "CURATOR"
        self.rejects(case, review, "DISPOSAL_REVIEWER_ROLE_NOT_DECLARED")

    def test_review_packet_must_not_carry_uncontrolled_prompt(self):
        case, review = synthetic_executed()
        review["curator_prompt"] = "SYNTHETIC ONLY, not for assistant"
        self.rejects(case, review, "INVALID_REVIEW_PACKET_FIELDS")

    def test_recommended_with_source_passage_and_time(self):
        case, review = synthetic_recommended()
        output = audit_disposal_source_review(case, review)
        self.assertEqual(output["source_review_count"], 1)

    def test_recommended_without_source_excerpt_blocked(self):
        case, review = synthetic_recommended()
        case["input"]["knowledge_evidence"][0]["excerpt"] = None
        self.rejects(case, review, "DISPOSAL_EXCERPT_NOT_IN_CITED_SOURCE")

    def test_knowledge_source_without_publication_time_blocked(self):
        case, review = synthetic_recommended()
        del review["attestations"][0]["source_published_at"]
        self.rejects(case, review, "DISPOSAL_PUBLICATION_TIME_MISSING")

    def test_future_knowledge_cannot_support_past_decision(self):
        case, review = synthetic_recommended()
        review["attestations"][0]["source_published_at"] = "2027-01-01T00:00:00Z"
        self.rejects(case, review, "DISPOSAL_SOURCE_AFTER_DECISION_CUTOFF")

    def test_knowledge_cannot_prove_an_executed_action(self):
        case, review = synthetic_recommended()
        case["expected_output"]["disposal_status"] = "RECORDED"
        case["expected_output"]["disposal_measures"][0]["measure_type"] = "EXECUTED"
        self.rejects(case, review, "INVALID_SOURCE_CASE")

    def test_all_cited_sources_need_individual_review(self):
        case, review = synthetic_multi_source()
        result = audit_disposal_source_review(case, review)
        self.assertEqual(result["measure_count"], 1)
        self.assertEqual(result["source_review_count"], 2)
        self.assertEqual(result["reviewed_source_reference_count"], 2)
        self.assertFalse(result["gold_approved"])

    def test_second_source_unreviewed_cannot_be_blessed(self):
        case, review = synthetic_multi_source()
        review["attestations"].pop()
        self.rejects(case, review, "DISPOSAL_REVIEW_COVERAGE_MISMATCH")

    def test_duplicate_attestation_cannot_replace_second_source(self):
        case, review = synthetic_multi_source()
        review["attestations"][1] = copy.deepcopy(review["attestations"][0])
        self.rejects(case, review, "DUPLICATE_DISPOSAL_MEASURE_REVIEW")

    def test_duplicate_citation_in_measure_is_blocked(self):
        case, review = synthetic_executed()
        case["expected_output"]["disposal_measures"][0]["evidence_refs"].append("LOG-02")
        self.rejects(case, review, "DUPLICATE_DISPOSAL_EVIDENCE_REF")

    def test_secondary_source_excerpt_must_exist(self):
        case, review = synthetic_multi_source()
        review["attestations"][1]["verbatim_excerpt"] = (
            "SYNTHETIC ONLY: an entirely different disposal occurred"
        )
        self.rejects(case, review, "DISPOSAL_EXCERPT_NOT_IN_CITED_SOURCE")

    def test_secondary_attestation_action_type_cannot_change(self):
        case, review = synthetic_multi_source()
        review["attestations"][1]["source_action_type"] = "PLANNED"
        self.rejects(case, review, "DISPOSAL_ACTION_TYPE_MISMATCH")

    def test_secondary_source_after_cutoff_is_blocked(self):
        case, review = synthetic_multi_source()
        case["input"]["diagnostic_logs"][0]["timestamp"] = "2026-04-12T09:11:00Z"
        # Case validation itself fails closed on post-cutoff diagnostic logs.
        self.rejects(case, review, "INVALID_SOURCE_CASE")

    def test_multi_source_review_packet_remains_not_for_sft(self):
        case, review = synthetic_multi_source()
        review["not_for_sft"] = False
        self.rejects(case, review, "SOURCE_REVIEW_MUST_BE_INTERNAL")


if __name__ == "__main__":
    unittest.main()
