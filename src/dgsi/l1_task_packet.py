from __future__ import annotations

"""L1 task-packet validation for parallel real and literature-derived tracks.

L1 is a curated task layer, not Gold approval. It binds an L0 source card,
a diagnostic Case, its conclusion-only target, synthetic provenance where
applicable, and a time-safe historical context snapshot.
"""

from datetime import datetime
from typing import Any

from .diagnostic_context import validate_diagnostic_case
from .history_temporal_gate import screen_historical_memory_hit
from .schema_validation import SchemaContractError, validate_payload_schema
from .source_fact_cards import SourceFactCardValidationError, validate_source_fact_card


class L1TaskPacketError(ValueError):
    """Payload-free L1 packet validation error."""


def _date(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _fail(code: str) -> None:
    raise L1TaskPacketError(code)


def _validate_history_context(packet: dict[str, Any], case: dict[str, Any]) -> None:
    context = packet["history_context"]
    query = context["query"]
    cutoff = _date(case["input"]["analysis_cutoff"])
    if cutoff is None:
        _fail("INVALID_ANALYSIS_CUTOFF")

    spacecraft = case["input"]["spacecraft_context"]
    components = {
        component
        for subsystem in spacecraft["subsystem_context"]
        for component in subsystem["components"]
    }
    subsystems = {item["subsystem"] for item in spacecraft["subsystem_context"]}
    if query["equipment_scope"] not in components:
        _fail("HISTORY_QUERY_EQUIPMENT_NOT_IN_CASE")
    if query["subsystem"] not in subsystems:
        _fail("HISTORY_QUERY_SUBSYSTEM_NOT_IN_CASE")
    operational = case["input"]["operational_context"]
    if query["mission_phase"] != operational["mission_phase"]:
        _fail("HISTORY_QUERY_MISSION_PHASE_MISMATCH")
    if query["operating_mode"] != operational["operating_mode"]:
        _fail("HISTORY_QUERY_OPERATING_MODE_MISMATCH")

    case_history = case["input"].get("historical_cases", [])
    items = context["items"]
    if context["retrieval_status"] == "NO_HIT":
        if items or case_history:
            _fail("NO_HIT_CONTEXT_MUST_HAVE_NO_HISTORY_ITEMS")
        return
    if not items:
        _fail("HISTORY_HIT_CONTEXT_EMPTY")

    item_refs = [item["case_ref"] for item in items]
    case_refs = [item["case_ref"] for item in case_history]
    if len(set(item_refs)) != len(item_refs) or len(set(case_refs)) != len(case_refs):
        _fail("DUPLICATE_HISTORY_CONTEXT_REFERENCE")
    if set(item_refs) != set(case_refs):
        _fail("HISTORY_CONTEXT_CASE_REFERENCE_MISMATCH")

    by_ref = {item["case_ref"]: item for item in case_history}
    confirmed_hits: list[dict[str, Any]] = []
    for item in items:
        prior = by_ref[item["case_ref"]]
        if item["event_family_id"] == case["provenance"]["source_group"]:
            _fail("CURRENT_INCIDENT_CANNOT_BE_HISTORY")
        if item["outcome_status"] != prior["outcome_status"]:
            _fail("HISTORY_OUTCOME_STATUS_MISMATCH")
        if item["summary"] != prior["prior_conclusion"]:
            _fail("HISTORY_SUMMARY_CASE_BINDING_MISMATCH")
        if sorted(item["applicability_limitations"]) != sorted(prior.get("applicability_limitations", [])):
            _fail("HISTORY_LIMITATIONS_CASE_BINDING_MISMATCH")
        if sorted(item["relevance_basis"]) != sorted(prior["similarity_basis"]):
            _fail("HISTORY_RELEVANCE_CASE_BINDING_MISMATCH")

        hit = item["hit_metadata"]
        if hit.get("case_id") != item["case_ref"]:
            _fail("HISTORY_METADATA_REFERENCE_MISMATCH")
        if hit.get("source_group_id") != item["event_family_id"]:
            _fail("HISTORY_METADATA_EVENT_FAMILY_MISMATCH")
        if hit.get("equipment_scope") != query["equipment_scope"]:
            _fail("HISTORY_METADATA_EQUIPMENT_SCOPE_MISMATCH")
        if hit.get("diagnostic_vote_allowed") is not False:
            _fail("HISTORY_CANNOT_VOTE_CURRENT_ROOT_CAUSE")

        historical_scope = item["historical_equipment_scope"]
        compatibility = item["hardware_compatibility"]
        limitations = item["applicability_limitations"]
        if compatibility == "COMPATIBLE" and historical_scope != query["equipment_scope"]:
            _fail("HISTORY_COMPATIBILITY_SCOPE_CONTRADICTION")
        if compatibility == "INCOMPATIBLE":
            if historical_scope == query["equipment_scope"]:
                _fail("HISTORY_INCOMPATIBILITY_SCOPE_CONTRADICTION")
            if not limitations:
                _fail("INCOMPATIBLE_HISTORY_REQUIRES_TRANSFER_LIMITATION")
            relevance = next(
                (entry for entry in case["expected_output"].get("historical_experience_relevance", [])
                 if entry["case_ref"] == item["case_ref"]),
                None,
            )
            if relevance is None or not relevance["transfer_limitations"]:
                _fail("INCOMPATIBLE_HISTORY_MUST_BE_QUALIFIED_IN_TARGET")
            cited_as_support = set(
                case["expected_output"]["evidence_assessment"]["supporting_refs"]
                + case["expected_output"]["evidence_assessment"]["contradicting_refs"]
            )
            for candidate in case["expected_output"]["cause_localization"]["candidates"]:
                cited_as_support.update(candidate["supporting_refs"])
            if item["case_ref"] in cited_as_support:
                _fail("INCOMPATIBLE_HISTORY_CANNOT_SUPPORT_CURRENT_CAUSE")
        if compatibility == "UNKNOWN" and not limitations:
            _fail("UNKNOWN_HISTORY_REQUIRES_TRANSFER_LIMITATION")

        if item["outcome_status"] == "CONFIRMED":
            confirmed_hits.append(hit)
        else:
            # Unresolved/rejected/partial/unknown history can be shown with its
            # original status, but cannot be promoted to a confirmed memory hit.
            if hit.get("status") == "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH":
                _fail("NONCONFIRMED_HISTORY_CANNOT_BE_UPGRADED")
            available_at = _date(hit.get("available_at"))
            if available_at is None:
                _fail("NONCONFIRMED_HISTORY_AVAILABILITY_NOT_VERIFIED")
            if available_at > cutoff:
                _fail("HISTORY_AVAILABLE_AFTER_ANALYSIS_CUTOFF")
            verified_at = hit.get("verified_at")
            if verified_at is not None:
                verified = _date(verified_at)
                if verified is None or verified > cutoff:
                    _fail("HISTORY_VERIFICATION_TIME_INVALID_OR_FUTURE")

    for hit in confirmed_hits:
        screened = screen_historical_memory_hit(
            hit,
            analysis_cutoff=case["input"]["analysis_cutoff"],
            current_source_group_id=case["provenance"]["source_group"],
            equipment_scope=query["equipment_scope"],
        )
        if screened["decision"] != "PASS_TEMPORAL_METADATA_ONLY":
            _fail("CONFIRMED_HISTORY_ASOF_GATE_BLOCKED")


def validate_l1_task_packet(
    packet: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate one L1 packet and bind it to supplied L0 cards.

    The return value is a metadata-only readiness result. It never authorizes
    Gold, training, or public release.
    """
    if not isinstance(packet, dict):
        _fail("L1_PACKET_NOT_OBJECT")
    try:
        validate_payload_schema("l1_task_packet", packet)
    except SchemaContractError as exc:
        raise L1TaskPacketError(str(exc)) from None

    case = packet["case"]
    try:
        validate_diagnostic_case(case)
    except (ValueError, TypeError, KeyError, AttributeError):
        _fail("INVALID_DIAGNOSTIC_CASE")

    if packet["formal_target"] != case["expected_output"]:
        _fail("FORMAL_TARGET_NOT_BOUND_TO_CASE")
    if case["internal_review"].get("not_for_sft") is not True:
        _fail("INTERNAL_REVIEW_NOT_ISOLATED")

    if not isinstance(source_fact_cards, list):
        _fail("SOURCE_FACT_CARD_BATCH_NOT_LIST")
    cards_by_id: dict[str, dict[str, Any]] = {}
    for card in source_fact_cards:
        try:
            validate_source_fact_card(card)
        except (SourceFactCardValidationError, TypeError, KeyError):
            _fail("INVALID_L0_SOURCE_FACT_CARD")
        if card["case_id"] in cards_by_id:
            _fail("DUPLICATE_L0_SOURCE_FACT_CARD")
        cards_by_id[card["case_id"]] = card

    refs = packet["source_fact_refs"]
    if len(set(refs)) != len(refs):
        _fail("DUPLICATE_L0_SOURCE_REFERENCE")
    if set(refs) - set(cards_by_id):
        _fail("UNRESOLVED_L0_SOURCE_REFERENCE")
    cards = [cards_by_id[ref] for ref in refs]

    history_source_refs = {
        source_ref
        for item in packet["history_context"]["items"]
        for source_ref in item["source_refs"]
    }
    unresolved_history_refs = {
        source_ref for source_ref in history_source_refs
        if source_ref not in cards_by_id and not source_ref.startswith("SYNTHETIC-")
    }
    if unresolved_history_refs:
        _fail("UNRESOLVED_HISTORY_SOURCE_REFERENCE")
    resolved_history_refs = history_source_refs & set(cards_by_id)
    bound_source_cards = [
        cards_by_id[ref] for ref in sorted(set(refs) | resolved_history_refs)
    ]
    domain_review_states = {
        card["domain_review_status"] for card in bound_source_cards
    }
    if "DOMAIN_EXPERT_REJECTED" in domain_review_states:
        _fail("L1_SOURCE_FACT_CARD_DOMAIN_REVIEW_REJECTED")
    if packet["review"]["status"] == "APPROVED_FOR_L1_EXPERIMENT" and any(
        card["domain_review_status"] != "DOMAIN_EXPERT_CONFIRMED"
        or not card["domain_review_evidence_sha256"]
        for card in bound_source_cards
    ):
        _fail("L1_SOURCE_FACTS_NOT_DOMAIN_REVIEWED")
    if any(
        cards_by_id[source_ref]["source_class"] not in {
            "PUBLIC_FLIGHT_REPORT", "PUBLIC_GROUND_TEST_REPORT",
            "PUBLIC_ENGINEERING_TEST", "PUBLIC_EXPERT_SYSTEM_STUDY"
        }
        or cards_by_id[source_ref]["knowledge_source_not_event"]
        for source_ref in resolved_history_refs
    ):
        _fail("HISTORY_SOURCE_NOT_EVENT_OR_PUBLIC")
    allowed_refs = set(refs) | history_source_refs

    track = packet["track"]
    synthetic = packet["synthetic_provenance"]
    if track == "LITERATURE_DERIVED_SYNTHETIC":
        if synthetic is None:
            _fail("SYNTHETIC_PROVENANCE_REQUIRED")
        if synthetic["source_fact_refs"] != refs:
            _fail("SYNTHETIC_SOURCE_FACT_BINDING_MISMATCH")
        if any(card["source_class"] not in {
            "PUBLIC_FLIGHT_REPORT", "PUBLIC_GROUND_TEST_REPORT",
            "PUBLIC_ENGINEERING_TEST", "PUBLIC_EXPERT_SYSTEM_STUDY"
        } for card in cards):
            _fail("LITERATURE_SYNTHETIC_REQUIRES_PUBLIC_L0_SOURCES")
        if any(card["knowledge_source_not_event"] for card in cards):
            _fail("KNOWLEDGE_ONLY_SOURCE_CANNOT_DEFINE_SYNTHETIC_INCIDENT")
        families = {card["event_family_id"] for card in cards}
        if len(families) != 1:
            _fail("L1_SYNTHETIC_PACKET_MUST_BIND_ONE_EVENT_FAMILY")
        expected_group = "LITERATURE-DERIVED:" + next(iter(families))
        if case["provenance"]["source_group"] != expected_group:
            _fail("L1_SYNTHETIC_SOURCE_GROUP_NOT_BOUND_TO_L0_FAMILY")
        event_statuses = {card["event_status"] for card in cards}
        if len(event_statuses) != 1:
            _fail("L1_SYNTHETIC_SOURCE_EVENT_STATUS_AMBIGUOUS")
        source_event_status = next(iter(event_statuses))
        mission_phase = case["input"]["operational_context"]["mission_phase"].casefold()
        ground_context = any(
            token in mission_phase
            for token in ("ground", "tvac", "thermal vacuum", "thermal_vacuum")
        )
        if source_event_status == "GROUND_TEST_EVENT" and not ground_context:
            _fail("L1_GROUND_TEST_SOURCE_MISLABELED_AS_FLIGHT_CONTEXT")
        if source_event_status == "FLIGHT_EVENT" and ground_context:
            _fail("L1_FLIGHT_SOURCE_MISLABELED_AS_GROUND_CONTEXT")
        if case["provenance"].get("generation_method") != "LITERATURE_DERIVED_SYNTHETIC":
            _fail("CASE_GENERATION_METHOD_NOT_SYNTHETIC")
        if not case["provenance"]["diagnosis_run_refs"] or any(
            not ref.startswith("SYNTHETIC-") for ref in case["provenance"]["diagnosis_run_refs"]
        ):
            _fail("SYNTHETIC_DIAGNOSIS_RUN_REFS_REQUIRED")
        generated_paths = {item["field_path"] for item in synthetic["generated_fields"]}
        required_paths = {
            "case.input.machine_diagnosis",
            "case.input.diagnostic_logs",
            "case.input.spacecraft_context",
            "case.input.operational_context",
        }
        if not required_paths.issubset(generated_paths):
            _fail("SYNTHETIC_INPUT_FIELD_PROVENANCE_INCOMPLETE")
        for item in synthetic["generated_fields"]:
            if set(item["source_fact_refs"]) - allowed_refs:
                _fail("SYNTHETIC_FIELD_SOURCE_REFERENCE_UNRESOLVED")
        if case["review"]["status"] == "APPROVED":
            _fail("SYNTHETIC_L1_CANNOT_BE_GOLD_APPROVED")
    else:
        if synthetic is not None:
            _fail("REAL_TRACK_MUST_NOT_HAVE_SYNTHETIC_PROVENANCE")
        if any(card["source_class"] != "USER_SUPPLIED_CASE" for card in cards):
            _fail("REAL_TRACK_REQUIRES_USER_CASE_SOURCE")
        if case["provenance"].get("generation_method") == "LITERATURE_DERIVED_SYNTHETIC":
            _fail("REAL_TRACK_SYNTHETIC_GENERATION_MISMATCH")

    _validate_history_context(packet, case)

    return {
        "schema_version": "dgsi-l1-readiness.v1",
        "decision": "READY_FOR_L1_EXPERT_REVIEW" if packet["review"]["status"] in {
            "DRAFT", "REVIEW_REQUIRED"
        } else "READY_FOR_L1_EXPERIMENT",
        "track": track,
        "source_fact_count": len(bound_source_cards),
        "source_fact_domain_review_status_counts": {
            status: sum(card["domain_review_status"] == status for card in bound_source_cards)
            for status in (
                "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION",
                "DOMAIN_EXPERT_CONFIRMED",
                "DOMAIN_EXPERT_REJECTED",
            )
        },
        "history_item_count": len(packet["history_context"]["items"]),
        "gold_eligible": False,
        "training_authorized": False,
        "note": "L1 structural/provenance/context checks only; expert review and separate SFT admission remain mandatory.",
    }


def validate_l1_task_packet_collection(
    collection: dict[str, Any],
    *,
    source_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate one-track L1 collection and audit event-family split isolation.

    Collection-level PASS is structural/provenance readiness only. It never
    authorizes fine-tuning or Gold promotion.
    """
    if not isinstance(collection, dict):
        _fail("L1_COLLECTION_NOT_OBJECT")
    try:
        validate_payload_schema("l1_task_packet_collection", collection)
    except SchemaContractError:
        _fail("INVALID_L1_COLLECTION_SCHEMA")
    packets = collection["packets"]
    if collection["packet_count"] != len(packets):
        _fail("L1_COLLECTION_PACKET_COUNT_MISMATCH")

    task_ids: set[str] = set()
    source_groups: dict[str, str] = {}
    decisions: list[str] = []
    for packet in packets:
        result = validate_l1_task_packet(packet, source_fact_cards=source_fact_cards)
        if packet["track"] != collection["track"]:
            _fail("MIXED_TRACKS_IN_L1_COLLECTION")
        task_id = packet["task_id"]
        if task_id in task_ids:
            _fail("DUPLICATE_L1_TASK_ID")
        task_ids.add(task_id)
        source_group = packet["case"]["provenance"]["source_group"]
        source_groups[task_id] = source_group
        decisions.append(result["decision"])

    assignments = collection.get("split_assignments", [])
    if assignments:
        assigned: dict[str, str] = {}
        for item in assignments:
            task_id = item["task_id"]
            if task_id not in task_ids:
                _fail("SPLIT_ASSIGNMENT_UNKNOWN_TASK")
            if task_id in assigned:
                _fail("DUPLICATE_L1_SPLIT_ASSIGNMENT")
            assigned[task_id] = item["split"]
        if set(assigned) != task_ids:
            _fail("L1_SPLIT_ASSIGNMENTS_INCOMPLETE")
        group_splits: dict[str, set[str]] = {}
        for task_id, split in assigned.items():
            group_splits.setdefault(source_groups[task_id], set()).add(split)
        if any(len(splits) > 1 for splits in group_splits.values()):
            _fail("L1_EVENT_FAMILY_CROSSES_DATASET_SPLITS")
        # Source/event-family validation alone cannot authorize a training split.
        # Preserve earlier error priority for malformed or leaking assignments.
        if collection["data_status"] != "APPROVED_FOR_L1_EXPERIMENT" or any(
            p["review"]["status"] != "APPROVED_FOR_L1_EXPERIMENT" for p in packets
        ):
            _fail("L1_SPLIT_BEFORE_INDEPENDENT_REVIEW")

    return {
        "schema_version": "dgsi-l1-collection-audit.v1",
        "decision": "VALID_L1_COLLECTION",
        "collection_id": collection["collection_id"],
        "track": collection["track"],
        "packet_count": len(packets),
        "event_family_count": len(set(source_groups.values())),
        "split_assignment_count": len(assignments),
        "split_audit_performed": bool(assignments),
        "packet_decisions": decisions,
        "gold_eligible_count": 0,
        "training_authorized": False,
    }
