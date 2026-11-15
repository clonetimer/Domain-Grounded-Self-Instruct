import copy
import unittest

from dgsi.source_fact_cards import (
    SourceFactCardValidationError,
    validate_source_fact_card,
)


BASE = {
    "schema_version": "dgsi-source-fact-card.v1",
    "case_id": "SYNTH-L0-001",
    "source_class": "SYNTHETIC_FIXTURE",
    "source_reference": {
        "source_id": "SYNTHETIC-SOURCE-001",
        "source_locator": "fixture://source/001",
        "source_title": "Synthetic L0 source card test fixture",
        "publication_date": None,
        "source_url": None,
        "page_or_section": "fixture",
    },
    "phenomenon_analysis": "Synthetic source fixture records a current drop and an equipment temperature rise.",
    "cause_localization": {
        "source_statement": "The source fixture states a possible contact failure.",
        "certainty_in_source": "EXPLICIT_MOST_LIKELY",
        "fault_source": "connector contact",
        "affected_components": ["payload power path"],
        "mechanism_notes": ["source-grounded synthetic test text"],
    },
    "disposal_status": "NOT_RECORDED",
    "disposal_measures": [],
    "available_materials": {
        "upstream_ml_result": False,
        "diagnostic_logs": False,
        "spacecraft_context": False,
        "operational_context": False,
        "historical_cases": False,
        "expert_adjudicated_target": False,
    },
    "internal_review": {
        "not_for_sft": True,
        "reviewer_questions": ["Does the source state an executed recovery action?"],
        "quality_flags": ["SYNTHETIC_ONLY"],
        "curator_prompts": ["Do not infer execution from a listed recommendation."],
    },
    "record_kind": "EVENT_FACT_CARD",
    "review_status": "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT",
    "disposal_execution_status": "NOT_RECORDED",
    "migration_assessment": {
        "migration_level": "NOT_ASSESSED",
        "target_case_refs": [],
        "rationale": "Synthetic fixture only; no transfer assessment.",
        "transfer_constraints": ["Do not treat the fixture as operational evidence."],
    },
    "sft_eligible": False,
}


class SourceFactCardTests(unittest.TestCase):
    def test_valid_l0_card_remains_not_sft_and_reports_missing_materials(self):
        warnings = validate_source_fact_card(copy.deepcopy(BASE))
        self.assertIn("MISSING_UPSTREAM_ML_RESULT", warnings)
        self.assertIn("MISSING_DIAGNOSTIC_LOGS", warnings)
        self.assertIn("MISSING_EXPERT_ADJUDICATED_TARGET", warnings)

    def test_unrecorded_disposal_cannot_have_measures(self):
        card = copy.deepcopy(BASE)
        card["disposal_measures"] = ["switch to backup unit"]
        with self.assertRaisesRegex(SourceFactCardValidationError, "UNRECORDED_DISPOSAL_MUST_BE_EMPTY"):
            validate_source_fact_card(card)

    def test_recorded_disposal_requires_source_text(self):
        card = copy.deepcopy(BASE)
        card["disposal_status"] = "SOURCE_RECORDS_MEASURE"
        with self.assertRaisesRegex(SourceFactCardValidationError, "SOURCE_DISPOSAL_STATUS_REQUIRES_MEASURE_TEXT"):
            validate_source_fact_card(card)

    def test_not_applicable_disposal_must_be_empty(self):
        card = copy.deepcopy(BASE)
        card["disposal_status"] = "NOT_APPLICABLE"
        card["disposal_measures"] = ["reconfigure"]
        with self.assertRaisesRegex(SourceFactCardValidationError, "NOT_APPLICABLE_DISPOSAL_MUST_BE_EMPTY"):
            validate_source_fact_card(card)

    def test_curator_review_is_required_to_be_non_sft(self):
        card = copy.deepcopy(BASE)
        card["internal_review"]["not_for_sft"] = False
        with self.assertRaises(SourceFactCardValidationError):
            validate_source_fact_card(card)

    def test_missing_ml_output_is_not_synthesized(self):
        card = copy.deepcopy(BASE)
        warnings = validate_source_fact_card(card)
        self.assertIn("MISSING_UPSTREAM_ML_RESULT", warnings)
        self.assertNotIn("machine_diagnosis", card)
        self.assertFalse(card["available_materials"]["upstream_ml_result"])

    def test_expert_system_demonstration_is_not_an_event(self):
        card = copy.deepcopy(BASE)
        card["source_class"] = "PUBLIC_EXPERT_SYSTEM_STUDY"
        with self.assertRaisesRegex(SourceFactCardValidationError, "EXPERT_SYSTEM_DEMO_MUST_BE_KNOWLEDGE_SOURCE"):
            validate_source_fact_card(card)

    def test_knowledge_source_kind_is_explicit(self):
        card = copy.deepcopy(BASE)
        card["source_class"] = "PUBLIC_EXPERT_SYSTEM_STUDY"
        card["record_kind"] = "KNOWLEDGE_SOURCE"
        warnings = validate_source_fact_card(card)
        self.assertIn("MISSING_UPSTREAM_ML_RESULT", warnings)

    def test_ai_review_cannot_be_mislabeled_as_domain_expert_approval(self):
        card = copy.deepcopy(BASE)
        card["review_status"] = "DOMAIN_EXPERT_APPROVED"
        with self.assertRaisesRegex(SourceFactCardValidationError, "DOMAIN_EXPERT_REVIEW_STATUS_REQUIRED"):
            validate_source_fact_card(card)

    def test_migration_assessment_requires_constraints(self):
        card = copy.deepcopy(BASE)
        card["migration_assessment"]["transfer_constraints"] = [""]
        with self.assertRaisesRegex(SourceFactCardValidationError, "MIGRATION_TRANSFER_CONSTRAINT_EMPTY"):
            validate_source_fact_card(card)

    def test_disposal_execution_status_must_match_source_disposal_status(self):
        card = copy.deepcopy(BASE)
        card["disposal_execution_status"] = "EXECUTION_CONFIRMED"
        with self.assertRaisesRegex(SourceFactCardValidationError, "DISPOSAL_EXECUTION_STATUS_MISMATCH"):
            validate_source_fact_card(card)

    def test_duplicate_tropics_unit_episode_is_rejected(self):
        card = copy.deepcopy(BASE)
        card["episode_observations"] = [
            {"episode_id":"TROPICS-PAYLOAD-A","unit_label":"payload A","outcome":"mitigated","disposal_status":"SOURCE_RECORDS_MEASURE","disposal_measures":["reverse rotation"]},
            {"episode_id":"TROPICS-PAYLOAD-A","unit_label":"payload B","outcome":"degraded","disposal_status":"NOT_RECORDED","disposal_measures":[]}
        ]
        with self.assertRaisesRegex(SourceFactCardValidationError, "DUPLICATE_EPISODE_ID"):
            validate_source_fact_card(card)


if __name__ == "__main__":
    unittest.main()
