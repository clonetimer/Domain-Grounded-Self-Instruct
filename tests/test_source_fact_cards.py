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
    "event_status": "UNCLASSIFIED_SOURCE",
    "knowledge_source_not_event": False,
    "event_family_id": "SYNTH-FAMILY-001",
    "event_episode_id": "SYNTH-EPISODE-001",
    "source_reference": {
        "source_id": "SYNTHETIC-SOURCE-001",
        "source_locator": "fixture://source/001",
        "source_title": "Synthetic L0 source card test fixture",
        "publication_year": None,
        "ntrs_accession_year": None,
        "publication_metadata_note": None,
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
    "disposal_source_note": None,
    "disposal_measures": [],
    "migration_assessment": {
        "tier": "NOT_ASSESSED",
        "rationale": "Synthetic validator fixture only.",
        "constraints": ["No transfer claim is made."],
    },
    "missing_materials": ["upstream_ml_result", "diagnostic_logs"],
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

    def test_knowledge_source_kind_is_explicit(self):
        card = copy.deepcopy(BASE)
        card["source_class"] = "PUBLIC_EXPERT_SYSTEM_STUDY"
        card["event_status"] = "KNOWLEDGE_SOURCE_NOT_EVENT"
        card["knowledge_source_not_event"] = True
        card["event_family_id"] = "ISEE-IUE-KNOWLEDGE"
        card["event_episode_id"] = "ISEE-IUE-KNOWLEDGE-CARD"
        warnings = validate_source_fact_card(card)
        self.assertIn("MISSING_UPSTREAM_ML_RESULT", warnings)

    def test_expert_system_demonstration_is_not_an_event(self):
        card = copy.deepcopy(BASE)
        card["source_class"] = "PUBLIC_EXPERT_SYSTEM_STUDY"
        card["event_status"] = "KNOWLEDGE_SOURCE_NOT_EVENT"
        card["knowledge_source_not_event"] = True
        validate_source_fact_card(card)
        card["knowledge_source_not_event"] = False
        with self.assertRaisesRegex(SourceFactCardValidationError, "KNOWLEDGE_SOURCE_EVENT_CLASS_MISMATCH"):
            validate_source_fact_card(card)

    def test_ai_review_cannot_be_mislabeled_as_domain_expert_approval(self):
        card = copy.deepcopy(BASE)
        card["internal_review"]["domain_expert_approved"] = True
        with self.assertRaises(SourceFactCardValidationError):
            validate_source_fact_card(card)

    def test_migration_assessment_requires_explicit_constraints(self):
        card = copy.deepcopy(BASE)
        card["migration_assessment"]["constraints"] = []
        with self.assertRaisesRegex(SourceFactCardValidationError, "JSON_SCHEMA_MINITEMS"):
            validate_source_fact_card(card)

    def test_ambiguous_disposal_requires_source_note(self):
        card = copy.deepcopy(BASE)
        card["disposal_status"] = "SOURCE_TEXT_AMBIGUOUS"
        card["disposal_source_note"] = None
        with self.assertRaisesRegex(SourceFactCardValidationError, "AMBIGUOUS_DISPOSAL_REQUIRES_SOURCE_NOTE"):
            validate_source_fact_card(card)

    def test_duplicate_tropics_unit_episode_is_rejected(self):
        from dgsi.source_fact_cards import validate_source_fact_card_collection
        a = copy.deepcopy(BASE)
        b = copy.deepcopy(BASE)
        a["case_id"] = "TROPICS-A"
        a["event_status"] = "FLIGHT_EVENT"
        a["event_family_id"] = "TROPICS-SLIPRING-FLIGHT"
        a["event_episode_id"] = "TROPICS-PAYLOAD-A"
        b["case_id"] = "TROPICS-B"
        b["event_status"] = "FLIGHT_EVENT"
        b["event_family_id"] = "TROPICS-SLIPRING-FLIGHT"
        b["event_episode_id"] = "TROPICS-PAYLOAD-A"
        with self.assertRaisesRegex(SourceFactCardValidationError, "DUPLICATE_EVENT_EPISODE_ID"):
            validate_source_fact_card_collection([a, b])

    def test_distinct_tropics_episodes_share_family_without_merging(self):
        from dgsi.source_fact_cards import validate_source_fact_card_collection
        a = copy.deepcopy(BASE)
        b = copy.deepcopy(BASE)
        a["case_id"] = "TROPICS-A"
        a["event_status"] = "FLIGHT_EVENT"
        a["event_family_id"] = "TROPICS-SLIPRING-FLIGHT"
        a["event_episode_id"] = "TROPICS-PAYLOAD-A"
        b["case_id"] = "TROPICS-B"
        b["event_status"] = "FLIGHT_EVENT"
        b["event_family_id"] = "TROPICS-SLIPRING-FLIGHT"
        b["event_episode_id"] = "TROPICS-PAYLOAD-B"
        result = validate_source_fact_card_collection([a, b])
        self.assertEqual(result["multi_episode_family_count"], 1)
        self.assertEqual(result["card_count"], 2)


if __name__ == "__main__":
    unittest.main()
