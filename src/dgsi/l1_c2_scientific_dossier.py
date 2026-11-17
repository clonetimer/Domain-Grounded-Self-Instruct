"""C2 scientific review-only annex: full synthetic input/target and public L0 facts.

Not an SFT exporter. Internal curator/reviewer content must never be included.
"""
from __future__ import annotations
from copy import deepcopy
from typing import Any

from .l1_c2_expert_handoff import build_c2_expert_handoff

PUBLIC_L0_FIELDS = (
    "case_id", "source_class", "event_status", "knowledge_source_not_event",
    "event_family_id", "event_episode_id", "source_reference",
    "phenomenon_analysis", "cause_localization", "disposal_status",
    "disposal_source_note", "disposal_measures", "migration_assessment",
    "available_materials", "missing_materials",
)
FORBIDDEN_REVIEW_KEYS = frozenset((
    "internal_review", "curator_prompts", "reviewer_questions", "quality_flags",
    "reviewer_token", "expert_private_notes", "reviewer_id", "reviewed_at",
))


class C2ReviewDossierError(ValueError):
    """Fail closed when scientific review materials cannot be bound."""


def _check_no_private_keys(value: Any) -> None:
    if isinstance(value, dict):
        if FORBIDDEN_REVIEW_KEYS.intersection(value):
            raise C2ReviewDossierError("C2_DOSSIER_PRIVATE_FIELD_LEAK")
        for child in value.values():
            _check_no_private_keys(child)
    elif isinstance(value, list):
        for child in value:
            _check_no_private_keys(child)


def build_c2_scientific_dossier(
    collection: dict[str, Any], *, source_fact_cards: list[dict[str, Any]],
) -> dict[str, Any]:
    """Create an expert-readable evidence annex tied to existing A/B blank forms.

    Full synthetic input and proposed formal target are only for scientific
    inspection, without chat messages, real data claims or training approval.
    """
    handoff = build_c2_expert_handoff(
        collection, source_fact_cards=source_fact_cards, reviewer_slot="A"
    )
    packets = collection.get("packets", [])
    packet_map = {p["task_id"]: p for p in packets}
    if len(packet_map) != handoff["packet_count"]:
        raise C2ReviewDossierError("C2_DOSSIER_DUPLICATE_OR_MISSING_TASK")
    cards = {f["case_id"]: f for f in source_fact_cards}
    if len(cards) != len(source_fact_cards):
        raise C2ReviewDossierError("C2_DOSSIER_DUPLICATE_L0_FACT")

    items = []
    for entry in handoff["tasks"]:
        packet = packet_map.get(entry["task_id"])
        if packet is None:
            raise C2ReviewDossierError("C2_DOSSIER_TASK_ID_UNRESOLVED")
        case = packet["case"]
        if packet["formal_target"] != case.get("expected_output"):
            raise C2ReviewDossierError("C2_DOSSIER_TARGET_MIRROR_DRIFT")
        if packet.get("track") != "LITERATURE_DERIVED_SYNTHETIC":
            raise C2ReviewDossierError("C2_DOSSIER_NON_SYNTHETIC_TASK")
        provenance = packet["synthetic_provenance"]
        if provenance.get("classification") != "SYNTHETIC":
            raise C2ReviewDossierError("C2_DOSSIER_SYNTHETIC_MARKER_MISSING")
        if case["input"].get("raw_telemetry_included") is not False:
            raise C2ReviewDossierError("C2_DOSSIER_RAW_TELEMETRY_NOT_ALLOWED")
        bound_refs = [b["source_fact_ref"] for b in entry["source_fact_bindings"]]
        if len(bound_refs) != len(set(bound_refs)):
            raise C2ReviewDossierError("C2_DOSSIER_DUPLICATE_L0_BINDING")
        if not set(packet["source_fact_refs"]).issubset(bound_refs):
            raise C2ReviewDossierError("C2_DOSSIER_CURRENT_L0_BINDING_MISSING")
        public_l0 = []
        for ref in bound_refs:
            if ref not in cards:
                raise C2ReviewDossierError("C2_DOSSIER_L0_SOURCE_UNRESOLVED")
            public_l0.append({
                field: deepcopy(cards[ref][field])
                for field in PUBLIC_L0_FIELDS if field in cards[ref]
            })
        item = {
            "task_id": entry["task_id"],
            "case_id": entry["case_id"],
            "task_type": entry["task_type"],
            "event_family": entry["event_family"],
            "collection_projection_sha256": entry["collection_projection_sha256"],
            "packet_sha256": entry["packet_sha256"],
            "source_public_sha256": entry["source_public_sha256"],
            "source_fact_bindings": deepcopy(entry["source_fact_bindings"]),
            "l0_public_source_context": public_l0,
            "source_role_boundary": (
                "L0 facts describe the cited historical event and bound the "
                "synthetic scenario; they are NOT direct evidence confirming "
                "the present synthetic fault candidate."
            ),
            "task_instruction": case["instruction"],
            "synthetic_input": deepcopy(case["input"]),
            "formal_target_for_expert_review": deepcopy(packet["formal_target"]),
            "historical_context": deepcopy(packet["history_context"]),
            "synthetic_provenance": deepcopy(provenance),
            "review_status": "NOT_REVIEWED",
            "source_rights_verified": False,
        }
        _check_no_private_keys(item)
        items.append(item)
    dossier = {
        "schema_version": "dgsi-c2-scientific-review-dossier.v1",
        "purpose": "INDEPENDENT_EXPERT_REVIEW_ONLY_NOT_SFT",
        "notice": (
            "Contains full synthetic diagnostic inputs and proposed formal "
            "targets for review ONLY. Not approved SFT, flight records, real "
            "ML runs or expert verdicts. Source rights remain unverified."
        ),
        "track": "LITERATURE_DERIVED_SYNTHETIC",
        "collection_id": handoff["collection_id"],
        "collection_projection_sha256": handoff["collection_projection_sha256"],
        "packet_count": handoff["packet_count"],
        "event_family_count": handoff["event_family_count"],
        "items": items,
        "not_for_sft": True,
        "source_rights_verified": False,
        "expert_review_complete": False,
        "gold_eligible": False,
        "official_splits_assigned": False,
        "training_authorized": False,
        "sft_records_emitted": 0,
    }
    _check_no_private_keys(dossier)
    return dossier
