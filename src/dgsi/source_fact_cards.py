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

    domain_review_status = card["domain_review_status"]
    review_digest = card["domain_review_evidence_sha256"]
    if domain_review_status in {"DOMAIN_EXPERT_CONFIRMED", "DOMAIN_EXPERT_REJECTED"}:
        if not review_digest:
            raise SourceFactCardValidationError("DOMAIN_EXPERT_DECISION_REQUIRES_REVIEW_EVIDENCE_DIGEST")
    elif review_digest is not None:
        raise SourceFactCardValidationError("PENDING_SOURCE_CARD_CANNOT_CARRY_DOMAIN_REVIEW_DIGEST")

    status = card["disposal_status"]
    measures = card["disposal_measures"]
    if status == "NOT_RECORDED" and measures:
        raise SourceFactCardValidationError("UNRECORDED_DISPOSAL_MUST_BE_EMPTY")
    if status in {
        "SOURCE_RECORDS_MEASURE",
        "SOURCE_RECORDS_CONDITIONAL_PROCEDURE",
        "SOURCE_RECORDS_CONDITIONAL_MEASURE",
        "SOURCE_RECORDS_PLANNED_PROCEDURE",
    } and not measures:
        raise SourceFactCardValidationError("SOURCE_DISPOSAL_STATUS_REQUIRES_MEASURE_TEXT")
    if status in {"NOT_APPLICABLE", "SOURCE_TEXT_AMBIGUOUS"} and measures:
        code = "NOT_APPLICABLE_DISPOSAL_MUST_BE_EMPTY" if status == "NOT_APPLICABLE" else "AMBIGUOUS_DISPOSAL_MUST_NOT_BE_ACTION"
        raise SourceFactCardValidationError(code)
    if status == "SOURCE_TEXT_AMBIGUOUS" and not card.get("disposal_source_note"):
        raise SourceFactCardValidationError("AMBIGUOUS_DISPOSAL_REQUIRES_SOURCE_NOTE")

    event_status = card["event_status"]
    is_knowledge = card["knowledge_source_not_event"]
    if is_knowledge != (event_status == "KNOWLEDGE_SOURCE_NOT_EVENT"):
        raise SourceFactCardValidationError("KNOWLEDGE_SOURCE_EVENT_CLASS_MISMATCH")
    if is_knowledge and card["source_class"] != "PUBLIC_EXPERT_SYSTEM_STUDY":
        raise SourceFactCardValidationError("KNOWLEDGE_SOURCE_CLASS_MISMATCH")
    if not card.get("event_family_id") or not card.get("event_episode_id"):
        raise SourceFactCardValidationError("EVENT_FAMILY_AND_EPISODE_REQUIRED")
    if card["event_episode_id"] == card["event_family_id"] and event_status == "KNOWLEDGE_SOURCE_NOT_EVENT":
        raise SourceFactCardValidationError("KNOWLEDGE_SOURCE_CANNOT_HAVE_EVENT_EPISODE")

    migration = card["migration_assessment"]
    if not migration["tier"].strip() or not migration["rationale"].strip():
        raise SourceFactCardValidationError("MIGRATION_ASSESSMENT_INCOMPLETE")
    if any(not item.strip() for item in migration["constraints"]):
        raise SourceFactCardValidationError("MIGRATION_CONSTRAINT_EMPTY")

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


def validate_source_fact_card_collection(cards: list[dict[str, Any]]) -> dict[str, Any]:
    """Audit collection identity and event-family grouping without merging episodes."""
    if not isinstance(cards, list):
        raise SourceFactCardValidationError("SOURCE_FACT_CARD_COLLECTION_NOT_LIST")
    seen_cases: set[str] = set()
    seen_episodes: set[str] = set()
    family_counts: dict[str, int] = {}
    knowledge_count = 0
    for index, card in enumerate(cards):
        try:
            validate_source_fact_card(card)
        except SourceFactCardValidationError as exc:
            raise SourceFactCardValidationError(f"COLLECTION_CARD_{index}_{exc}") from None
        case_id = card["case_id"]
        episode_id = card["event_episode_id"]
        family_id = card["event_family_id"]
        if case_id in seen_cases:
            raise SourceFactCardValidationError("DUPLICATE_SOURCE_FACT_CARD_ID")
        if episode_id in seen_episodes:
            raise SourceFactCardValidationError("DUPLICATE_EVENT_EPISODE_ID")
        seen_cases.add(case_id)
        seen_episodes.add(episode_id)
        family_counts[family_id] = family_counts.get(family_id, 0) + 1
        knowledge_count += int(card["knowledge_source_not_event"])
    return {
        "card_count": len(cards),
        "event_family_count": len(family_counts),
        "multi_episode_family_count": sum(1 for count in family_counts.values() if count > 1),
        "knowledge_source_not_event_count": knowledge_count,
        "sft_eligible_count": 0,
    }
