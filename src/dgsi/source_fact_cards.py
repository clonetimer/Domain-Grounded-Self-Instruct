"""L0 source fact cards: source-grounded facts, never SFT examples."""
from __future__ import annotations

from typing import Any

from .schema_validation import SchemaContractError, validate_payload_schema


class SourceFactCardValidationError(ValueError):
    """Raised when an L0 source fact card violates its provenance boundary."""


def validate_source_fact_card(card: dict[str, Any]) -> list[str]:
    """Validate source facts and return missing-material warnings.

    This validator does not generate an upstream ML result, create logs, infer
    confidence, approve causal truth or grant SFT eligibility.
    """
    if not isinstance(card, dict):
        raise SourceFactCardValidationError("SOURCE_FACT_CARD_NOT_OBJECT")
    try:
        validate_payload_schema("source_fact_card", card)
    except SchemaContractError as exc:
        raise SourceFactCardValidationError(str(exc)) from None

    if card["review_status"] != "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT":
        raise SourceFactCardValidationError("DOMAIN_EXPERT_REVIEW_STATUS_REQUIRED")
    if card["source_class"] == "PUBLIC_EXPERT_SYSTEM_STUDY" and card["record_kind"] != "KNOWLEDGE_SOURCE":
        raise SourceFactCardValidationError("EXPERT_SYSTEM_DEMO_MUST_BE_KNOWLEDGE_SOURCE")
    if card["record_kind"] == "KNOWLEDGE_SOURCE" and card["source_class"] != "PUBLIC_EXPERT_SYSTEM_STUDY":
        raise SourceFactCardValidationError("KNOWLEDGE_SOURCE_CLASS_MISMATCH")

    migration = card["migration_assessment"]
    if not migration["rationale"].strip():
        raise SourceFactCardValidationError("MIGRATION_RATIONALE_REQUIRED")
    if any(not item.strip() for item in migration["transfer_constraints"]):
        raise SourceFactCardValidationError("MIGRATION_TRANSFER_CONSTRAINT_EMPTY")

    execution = card["disposal_execution_status"]
    if execution == "NOT_RECORDED" and card["disposal_status"] != "NOT_RECORDED":
        raise SourceFactCardValidationError("DISPOSAL_EXECUTION_STATUS_MISMATCH")
    if execution == "NOT_APPLICABLE" and card["disposal_status"] != "NOT_APPLICABLE":
        raise SourceFactCardValidationError("DISPOSAL_EXECUTION_STATUS_MISMATCH")
    if execution == "CONDITIONAL_PROCEDURE" and card["disposal_status"] != "SOURCE_RECORDS_CONDITIONAL_PROCEDURE":
        raise SourceFactCardValidationError("DISPOSAL_EXECUTION_STATUS_MISMATCH")
    if execution == "AMBIGUOUS_SOURCE_TEXT" and card["disposal_status"] != "SOURCE_TEXT_AMBIGUOUS":
        raise SourceFactCardValidationError("DISPOSAL_EXECUTION_STATUS_MISMATCH")

    seen_episodes = set()
    for episode in card.get("episode_observations", []):
        if episode["episode_id"] in seen_episodes:
            raise SourceFactCardValidationError("DUPLICATE_EPISODE_ID")
        seen_episodes.add(episode["episode_id"])
        if episode["disposal_status"] in {"NOT_RECORDED", "NOT_APPLICABLE"} and episode["disposal_measures"]:
            raise SourceFactCardValidationError("EPISODE_UNRECORDED_DISPOSAL_MUST_BE_EMPTY")

    status = card["disposal_status"]
    measures = card["disposal_measures"]
    if status == "NOT_RECORDED" and measures:
        raise SourceFactCardValidationError("UNRECORDED_DISPOSAL_MUST_BE_EMPTY")
    if status in {"SOURCE_RECORDS_MEASURE", "SOURCE_RECORDS_CONDITIONAL_PROCEDURE"} and not measures:
        raise SourceFactCardValidationError("SOURCE_DISPOSAL_STATUS_REQUIRES_MEASURE_TEXT")
    if status == "NOT_APPLICABLE" and measures:
        raise SourceFactCardValidationError("NOT_APPLICABLE_DISPOSAL_MUST_BE_EMPTY")

    availability = card["available_materials"]
    warnings = []
    for field, code in (
        ("upstream_ml_result", "MISSING_UPSTREAM_ML_RESULT"),
        ("diagnostic_logs", "MISSING_DIAGNOSTIC_LOGS"),
        ("spacecraft_context", "MISSING_SPACECRAFT_CONTEXT"),
        ("operational_context", "MISSING_OPERATIONAL_CONTEXT"),
        ("historical_cases", "MISSING_HISTORICAL_CASES"),
        ("expert_adjudicated_target", "MISSING_EXPERT_ADJUDICATED_TARGET"),
    ):
        if availability[field] is not True:
            warnings.append(code)

    # L0 is always a source-curation layer. A complete availability matrix does
    # not promote it to an SFT Case; a separate Case construction and expert gate
    # remain required.
    if card.get("sft_eligible") is not False:
        raise SourceFactCardValidationError("L0_SOURCE_CARD_CANNOT_BE_SFT_ELIGIBLE")
    return warnings
