"""SYNTHETIC_TEST_ONLY: L1 dual-track and context-retrieval packet contract."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from dgsi.l1_task_packet import L1TaskPacketError, validate_l1_task_packet, validate_l1_task_packet_collection


ROOT = Path(__file__).resolve().parents[1]
_BASE_CASE = json.loads((ROOT / "examples/diagnostic_context_case_illustrative.json").read_text(encoding="utf-8"))


def source_card(source_class="PUBLIC_FLIGHT_REPORT"):
    return {
        "schema_version": "dgsi-source-fact-card.v1",
        "domain_review_status": "AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION",
        "domain_review_evidence_sha256": None,
        "case_id": "L0-SEASAT-001",
        "source_class": source_class,
        "source_reference": {
            "source_id": "NASA-NTRS-SYNTHETIC-REF",
            "source_locator": "test fixture paragraph 1",
            "source_title": "Synthetic test-only source fact fixture",
            "publication_date": None,
            "source_url": "https://example.invalid/source",
            "page_or_section": "fixture",
        },
        "phenomenon_analysis": "The source fact fixture records a solar-array slip-ring electrical anomaly.",
        "cause_localization": {
            "source_statement": "The source reports an arc between adjacent brush assemblies as the most likely cause.",
            "certainty_in_source": "EXPLICIT_MOST_LIKELY",
            "fault_source": "slip-ring brush interface",
            "affected_components": ["solar-array power interface"],
            "mechanism_notes": ["Test fixture only; not a real source quotation."],
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
            "reviewer_questions": ["Is the source attribution being over-stated?"],
            "quality_flags": ["SYNTHETIC_TEST_ONLY"],
        },
        "sft_eligible": False,
        "event_status": "FLIGHT_EVENT",
        "knowledge_source_not_event": False,
        "event_family_id": "L0-SEASAT-FAMILY",
        "event_episode_id": "L0-SEASAT-EPISODE",
        "migration_assessment": {
            "tier": "CONDITIONAL_MECHANISM",
            "rationale": "Fixture checks a literature-derived mechanism link.",
            "constraints": ["No direct inference to another spacecraft without configuration comparison."],
        },
        "missing_materials": ["upstream_ml_result", "diagnostic_logs", "spacecraft_context"],
    }


def make_case(*, synthetic=True, history_status="UNRESOLVED", with_history=True):
    case = copy.deepcopy(_BASE_CASE)
    case["case_id"] = "SYNTH-L1-ADCS-001" if synthetic else "REAL-CANDIDATE-ADCS-001"
    case["provenance"]["source_group"] = "LITERATURE-DERIVED:L0-SEASAT-FAMILY" if synthetic else "USER-EVENT-FAMILY-001"
    case["provenance"]["diagnosis_run_refs"] = ["SYNTHETIC-MLRUN-001"] if synthetic else ["USER-MLRUN-REF-001"]
    case["provenance"]["generation_method"] = "LITERATURE_DERIVED_SYNTHETIC" if synthetic else "USER_SOURCE_CASE"
    case["review"]["status"] = "REVIEW_REQUIRED"
    case["input"]["analysis_cutoff"] = "2026-04-12T09:10:00Z"
    if with_history:
        case["input"]["historical_cases"][0]["outcome_status"] = history_status
    else:
        case["input"]["historical_cases"] = []
        case["expected_output"]["historical_experience_relevance"] = []
        case["provenance"]["historical_case_refs"] = []
    return case


def make_history_context(case, *, include=True, future=False):
    query = {
        "equipment_scope": "reaction_wheel_2",
        "subsystem": "ADCS",
        "mission_phase": case["input"]["operational_context"]["mission_phase"],
        "operating_mode": case["input"]["operational_context"]["operating_mode"],
        "fault_modes": ["torque authority loss"],
        "configuration_keys": ["wheel type"],
    }
    if not include:
        return {
            "schema_version": "dgsi-history-context.v1",
            "mode": "CONTEXT",
            "retrieval_status": "NO_HIT",
            "query": query,
            "items": [],
        }
    history = case["input"]["historical_cases"][0]
    outcome = history["outcome_status"]
    metadata = {
        "case_id": history["case_ref"],
        "source_group_id": "SYNTHETIC-PRIOR-EVENT-017",
        "equipment_scope": "reaction_wheel_2",
        "diagnostic_vote_allowed": False,
        "available_at": "2026-04-11T09:00:00Z" if not future else "2026-04-12T10:00:00Z",
        "status": "UNRESOLVED_HISTORICAL_CASE_NOT_CURRENT_TRUTH",
    }
    if outcome == "CONFIRMED":
        metadata.update({
            "verified_fault_id": "SYNTHETIC-PRIOR-FAULT",
            "proposed_fault_id": "SYNTHETIC-PRIOR-FAULT",
            "truth_source_ref": "synthetic://prior-verification",
            "reviewer": "SYNTHETIC-REVIEWER",
            "snapshot": 1,
            "relation_status": "CONSISTENT_HISTORICAL_CASE",
            "verified_at": "2026-04-11T08:00:00Z",
            "status": "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH",
        })
    return {
        "schema_version": "dgsi-history-context.v1",
        "mode": "CONTEXT",
        "retrieval_status": "HIT",
        "query": query,
        "items": [{
            "case_ref": history["case_ref"],
            "event_family_id": "SYNTHETIC-PRIOR-EVENT-017",
            "historical_equipment_scope": "reaction_wheel_2",
            "hardware_compatibility": "COMPATIBLE",
            "outcome_status": outcome,
            "summary": history["prior_conclusion"],
            "source_refs": ["SYNTHETIC-HISTORY-SOURCE-017"],
            "relevance_basis": history["similarity_basis"],
            "applicability_limitations": history["applicability_limitations"],
            "hit_metadata": metadata,
        }],
    }


def make_packet(*, track="LITERATURE_DERIVED_SYNTHETIC", history_status="UNRESOLVED", with_history=True):
    case = make_case(synthetic=(track == "LITERATURE_DERIVED_SYNTHETIC"), history_status=history_status, with_history=with_history)
    refs = ["L0-SEASAT-001"]
    synthetic_provenance = None
    if track == "LITERATURE_DERIVED_SYNTHETIC":
        synthetic_provenance = {
            "classification": "SYNTHETIC",
            "generation_recipe": "Build an illustrative upstream result/log/context scenario bounded by the SEASAT L0 fact card; do not reproduce real flight telemetry.",
            "recipe_version": "dgsi-literature-recipe-0.1.0",
            "source_fact_refs": refs,
            "generated_fields": [
                {"field_path": "case.input.machine_diagnosis", "origin": "SYNTHETIC_SCENARIO_VALUE", "source_fact_refs": refs, "assumption": "Illustrative candidate result; no actual ML run is claimed."},
                {"field_path": "case.input.diagnostic_logs", "origin": "SYNTHETIC_ASSUMPTION", "source_fact_refs": refs, "assumption": "Illustrative log sequence derived from reported event order; exact timestamps are scenario values."},
                {"field_path": "case.input.spacecraft_context", "origin": "SYNTHETIC_ASSUMPTION", "source_fact_refs": refs, "assumption": "Configuration details are scenario assumptions, not copied from the source report."},
                {"field_path": "case.input.operational_context", "origin": "SYNTHETIC_ASSUMPTION", "source_fact_refs": refs, "assumption": "Mission phase and operating mode are illustrative scenario values."},
            ],
            "scenario_assumptions": ["The task uses a hypothetical ML candidate and synthetic diagnostic event timeline."],
            "not_simulated": ["Raw telemetry waveforms", "actual flight computer logs", "actual historical ML model execution"],
            "expert_review_status": "REVIEW_REQUIRED",
            "gold_eligible": False,
            "real_flight_record": False,
        }
        if with_history:
            # The synthetic fixture includes an explicit generated history input;
            # its source is a declared synthetic history reference, not real
            # engineering experience or a historical confirmation.
            synthetic_provenance["generated_fields"].append({
                "field_path": "case.input.historical_cases",
                "origin": "SYNTHETIC_SCENARIO_VALUE",
                "source_fact_refs": ["SYNTHETIC-HISTORY-SOURCE-017"],
                "assumption": "Historical context is an illustrative synthetic fixture.",
            })
    return {
        "schema_version": "dgsi-l1-task-packet.v1",
        "task_id": "L1-SYNTH-001" if synthetic_provenance else "L1-REAL-CANDIDATE-001",
        "track": track,
        "source_fact_refs": refs,
        "case": case,
        "formal_target": copy.deepcopy(case["expected_output"]),
        "history_context": make_history_context(case, include=with_history),
        "synthetic_provenance": synthetic_provenance,
        "review": {"status": "REVIEW_REQUIRED", "reviewer_id": None, "reviewed_at": None, "notes": []},
    }


class L1TaskPacketTests(unittest.TestCase):
    def validate(self, packet=None, cards=None):
        return validate_l1_task_packet(
            make_packet() if packet is None else packet,
            source_fact_cards=[source_card()] if cards is None else cards,
        )

    def test_literature_derived_synthetic_packet_is_valid_but_not_gold(self):
        result = self.validate()
        self.assertEqual(result["decision"], "READY_FOR_L1_EXPERT_REVIEW")
        self.assertEqual(result["track"], "LITERATURE_DERIVED_SYNTHETIC")
        self.assertFalse(result["gold_eligible"])
        self.assertFalse(result["training_authorized"])

    def test_real_case_candidate_is_a_separate_track(self):
        packet = make_packet(track="REAL_CASE_CANDIDATE", with_history=False)
        card = source_card("USER_SUPPLIED_CASE")
        card["event_status"] = "USER_REPORTED_CASE"
        result = self.validate(packet, [card])
        self.assertEqual(result["track"], "REAL_CASE_CANDIDATE")
        self.assertEqual(result["history_item_count"], 0)
        self.assertFalse(result["gold_eligible"])

    def test_synthetic_track_requires_explicit_provenance(self):
        packet = make_packet()
        packet["synthetic_provenance"] = None
        with self.assertRaisesRegex(L1TaskPacketError, "SYNTHETIC_PROVENANCE_REQUIRED"):
            self.validate(packet)

    def test_synthetic_track_rejects_user_case_as_literature_source(self):
        packet = make_packet()
        card = source_card("USER_SUPPLIED_CASE")
        card["event_status"] = "USER_REPORTED_CASE"
        with self.assertRaisesRegex(L1TaskPacketError, "LITERATURE_SYNTHETIC_REQUIRES_PUBLIC_L0_SOURCES"):
            self.validate(packet, [card])

    def test_knowledge_only_source_cannot_define_synthetic_incident(self):
        packet = make_packet()
        card = source_card("PUBLIC_EXPERT_SYSTEM_STUDY")
        card["event_status"] = "KNOWLEDGE_SOURCE_NOT_EVENT"
        card["knowledge_source_not_event"] = True
        card["event_family_id"] = "KNOWLEDGE-FAMILY"
        card["event_episode_id"] = "KNOWLEDGE-EPISODE"
        with self.assertRaisesRegex(L1TaskPacketError, "KNOWLEDGE_ONLY_SOURCE_CANNOT_DEFINE_SYNTHETIC_INCIDENT"):
            self.validate(packet, [card])

    def test_synthetic_provenance_must_cover_all_model_input_groups(self):
        packet = make_packet()
        packet["synthetic_provenance"]["generated_fields"].pop(0)
        with self.assertRaisesRegex(L1TaskPacketError, "SYNTHETIC_INPUT_FIELD_PROVENANCE_INCOMPLETE"):
            self.validate(packet)

    def test_generated_field_cannot_cite_unknown_l0_source(self):
        packet = make_packet()
        packet["synthetic_provenance"]["generated_fields"][0]["source_fact_refs"] = ["UNKNOWN-L0"]
        with self.assertRaisesRegex(L1TaskPacketError, "SYNTHETIC_FIELD_SOURCE_REFERENCE_UNRESOLVED"):
            self.validate(packet)

    def test_l0_literature_reference_cannot_be_current_cause_support(self):
        packet = make_packet()
        # The L0 fact is present in the *context* but is not a measurement
        # of the separate synthetic ML/log incident.
        evidence_id = packet["case"]["input"]["knowledge_evidence"][0]["evidence_id"]
        packet["case"]["expected_output"]["cause_localization"]["candidates"][0]["supporting_refs"].append(evidence_id)
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(
            L1TaskPacketError, "^L0_LITERATURE_CANNOT_PROVE_SYNTHETIC_CURRENT_CAUSE$"
        ):
            self.validate(packet)

    def test_l0_literature_reference_cannot_be_current_evidence_assessment_support(self):
        packet = make_packet()
        evidence_id = packet["case"]["input"]["knowledge_evidence"][0]["evidence_id"]
        packet["case"]["expected_output"]["evidence_assessment"]["supporting_refs"].append(evidence_id)
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(
            L1TaskPacketError, "^L0_LITERATURE_CANNOT_PROVE_SYNTHETIC_CURRENT_CAUSE$"
        ):
            self.validate(packet)

    def test_formal_target_must_be_exact_case_target(self):
        packet = make_packet()
        packet["formal_target"]["phenomenon_analysis"] += " curator prompt must not appear"
        with self.assertRaisesRegex(L1TaskPacketError, "FORMAL_TARGET_NOT_BOUND_TO_CASE"):
            self.validate(packet)

    def test_no_hit_context_is_explicit_and_empty(self):
        packet = make_packet(with_history=False)
        self.assertEqual(self.validate(packet)["history_item_count"], 0)

    def test_no_hit_cannot_hide_history_in_case_input(self):
        packet = make_packet(with_history=False)
        packet["case"]["input"]["historical_cases"] = [copy.deepcopy(_BASE_CASE["input"]["historical_cases"][0])]
        with self.assertRaisesRegex(L1TaskPacketError, "NO_HIT_CONTEXT_MUST_HAVE_NO_HISTORY_ITEMS"):
            self.validate(packet)

    def test_unresolved_history_is_context_but_not_confirmed_memory(self):
        packet = make_packet(history_status="UNRESOLVED")
        result = self.validate(packet)
        self.assertEqual(result["history_item_count"], 1)
        self.assertFalse(result["gold_eligible"])

    def test_unresolved_history_cannot_be_upgraded_to_confirmed(self):
        packet = make_packet(history_status="UNRESOLVED")
        packet["history_context"]["items"][0]["hit_metadata"]["status"] = "CONFIRMED_HISTORICAL_CASE_NOT_CURRENT_TRUTH"
        with self.assertRaisesRegex(L1TaskPacketError, "NONCONFIRMED_HISTORY_CANNOT_BE_UPGRADED"):
            self.validate(packet)

    def test_future_history_availability_is_blocked(self):
        packet = make_packet(history_status="UNRESOLVED")
        packet["history_context"] = make_history_context(packet["case"], future=True)
        with self.assertRaisesRegex(L1TaskPacketError, "HISTORY_AVAILABLE_AFTER_ANALYSIS_CUTOFF"):
            self.validate(packet)

    def test_confirmed_history_requires_asof_metadata_gate(self):
        packet = make_packet(history_status="CONFIRMED")
        result = self.validate(packet)
        self.assertEqual(result["history_item_count"], 1)

    def test_history_query_must_match_current_mission_context(self):
        packet = make_packet()
        packet["history_context"]["query"]["mission_phase"] = "different mission phase"
        with self.assertRaisesRegex(L1TaskPacketError, "HISTORY_QUERY_MISSION_PHASE_MISMATCH"):
            self.validate(packet)

    def test_history_query_cannot_select_unknown_equipment(self):
        packet = make_packet()
        packet["history_context"]["query"]["equipment_scope"] = "reaction_wheel_99"
        with self.assertRaisesRegex(L1TaskPacketError, "HISTORY_QUERY_EQUIPMENT_NOT_IN_CASE"):
            self.validate(packet)

    def test_current_event_family_cannot_be_reused_as_history(self):
        packet = make_packet()
        packet["history_context"]["items"][0]["event_family_id"] = packet["case"]["provenance"]["source_group"]
        packet["history_context"]["items"][0]["hit_metadata"]["source_group_id"] = packet["case"]["provenance"]["source_group"]
        with self.assertRaisesRegex(L1TaskPacketError, "CURRENT_INCIDENT_CANNOT_BE_HISTORY"):
            self.validate(packet)

    def test_synthetic_split_group_is_bound_to_source_event_family(self):
        packet = make_packet()
        packet["case"]["provenance"]["source_group"] = "LITERATURE-DERIVED:UNRELATED-FAMILY"
        with self.assertRaisesRegex(L1TaskPacketError, "L1_SYNTHETIC_SOURCE_GROUP_NOT_BOUND_TO_L0_FAMILY"):
            self.validate(packet)

    def test_reviewed_l0_backed_synthetic_pilot_packets_validate(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        self.assertEqual(collection["track"], "LITERATURE_DERIVED_SYNTHETIC")
        self.assertEqual(collection["packet_count"], 15)
        cards = {card["case_id"]: card for card in literature["cards"]}
        decisions = []
        for packet in collection["packets"]:
            bound_refs = set(packet["source_fact_refs"])
            bound_refs.update(
                source_ref
                for item in packet["history_context"]["items"]
                for source_ref in item["source_refs"]
                if source_ref in cards
            )
            bound_cards = [cards[ref] for ref in bound_refs]
            result = validate_l1_task_packet(packet, source_fact_cards=bound_cards)
            decisions.append(result["decision"])
            self.assertFalse(result["gold_eligible"])
            self.assertFalse(result["training_authorized"])
            self.assertEqual(packet["formal_target"], packet["case"]["expected_output"])
            self.assertNotIn("internal_review", packet["formal_target"])
            self.assertNotIn("curator_prompts", packet["formal_target"])
        self.assertEqual(decisions, ["READY_FOR_L1_EXPERT_REVIEW"] * 15)

    def test_l1_pilot_has_both_no_hit_and_history_context_variants(self):
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        statuses = {packet["history_context"]["retrieval_status"] for packet in collection["packets"]}
        self.assertEqual(statuses, {"NO_HIT", "HIT"})
        history_packet = next(packet for packet in collection["packets"] if packet["history_context"]["retrieval_status"] == "HIT")
        self.assertEqual(history_packet["history_context"]["items"][0]["outcome_status"], "REJECTED")
        self.assertFalse(history_packet["history_context"]["items"][0]["hit_metadata"]["diagnostic_vote_allowed"])

    def test_rejected_history_remains_rejected_and_is_not_positive_precedent(self):
        packet = make_packet(history_status="REJECTED")
        result = self.validate(packet)
        self.assertEqual(result["history_item_count"], 1)
        self.assertEqual(packet["history_context"]["items"][0]["outcome_status"], "REJECTED")
        self.assertFalse(packet["history_context"]["items"][0]["hit_metadata"]["diagnostic_vote_allowed"])

    def test_history_hardware_scope_mismatch_is_blocked(self):
        packet = make_packet()
        packet["history_context"]["items"][0]["hit_metadata"]["equipment_scope"] = "reaction_wheel_3"
        with self.assertRaisesRegex(L1TaskPacketError, "HISTORY_METADATA_EQUIPMENT_SCOPE_MISMATCH"):
            self.validate(packet)

    def test_conflicting_confirmed_and_rejected_history_can_be_preserved_with_status(self):
        packet = make_packet(history_status="CONFIRMED")
        case = packet["case"]
        second_ref = "SYNTHETIC-HISTORY-REJECTED-002"
        second_summary = "A separate historical contact-resistance hypothesis was rejected after connector inspection."
        second_history = {
            "case_ref": second_ref,
            "similarity_basis": ["similar communication symptom"],
            "prior_conclusion": second_summary,
            "outcome_status": "REJECTED",
            "applicability_limitations": ["different connector design", "rejected cause is not positive precedent"],
        }
        case["input"]["historical_cases"].append(second_history)
        case["provenance"]["historical_case_refs"].append(second_ref)
        case["expected_output"]["historical_experience_relevance"].append({
            "case_ref": second_ref,
            "relevance": "该历史假设已被否决，仅作为排除相似错误归因的对照。",
            "transfer_limitations": second_history["applicability_limitations"],
        })
        packet["formal_target"] = copy.deepcopy(case["expected_output"])
        packet["history_context"]["items"].append({
            "case_ref": second_ref,
            "event_family_id": "SYNTHETIC-PRIOR-CONNECTOR-FAMILY",
            "historical_equipment_scope": "reaction_wheel_2",
            "hardware_compatibility": "COMPATIBLE",
            "outcome_status": "REJECTED",
            "summary": second_summary,
            "source_refs": ["SYNTHETIC-HISTORY-REVIEW-REF-002"],
            "relevance_basis": second_history["similarity_basis"],
            "applicability_limitations": second_history["applicability_limitations"],
            "hit_metadata": {
                "case_id": second_ref,
                "source_group_id": "SYNTHETIC-PRIOR-CONNECTOR-FAMILY",
                "equipment_scope": "reaction_wheel_2",
                "diagnostic_vote_allowed": False,
                "available_at": "2026-04-10T10:00:00Z",
                "status": "REJECTED_HISTORICAL_CASE_NOT_CURRENT_TRUTH",
            },
        })
        # A second historical hit must carry its own synthetic source lineage.
        # This is a fixture correction, not a relaxation of the runtime gate.
        history_lineage = next(
            item for item in packet["synthetic_provenance"]["generated_fields"]
            if item["field_path"] == "case.input.historical_cases"
        )
        history_lineage["source_fact_refs"].append("SYNTHETIC-HISTORY-REVIEW-REF-002")
        result = self.validate(packet)
        self.assertEqual(result["history_item_count"], 2)
        self.assertEqual(
            {item["outcome_status"] for item in packet["history_context"]["items"]},
            {"CONFIRMED", "REJECTED"},
        )

    def test_l1_collection_validates_pilot_and_reports_track_counts(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        result = validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])
        self.assertEqual(result["decision"], "VALID_L1_COLLECTION")
        self.assertEqual(result["packet_count"], 15)
        self.assertEqual(result["event_family_count"], 9)
        self.assertFalse(result["split_audit_performed"])
        self.assertFalse(result["training_authorized"])

    def test_l1_collection_rejects_packet_count_mismatch(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        collection["packet_count"] += 1
        with self.assertRaisesRegex(L1TaskPacketError, "L1_COLLECTION_PACKET_COUNT_MISMATCH"):
            validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])

    def test_l1_collection_requires_one_track(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        collection["track"] = "REAL_CASE_CANDIDATE"
        with self.assertRaisesRegex(L1TaskPacketError, "MIXED_TRACKS_IN_L1_COLLECTION"):
            validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])

    def test_l1_collection_split_assignments_must_cover_every_packet(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        collection["split_assignments"] = [{"task_id": collection["packets"][0]["task_id"], "split": "train"}]
        with self.assertRaisesRegex(L1TaskPacketError, "L1_SPLIT_ASSIGNMENTS_INCOMPLETE"):
            validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])

    def test_l1_collection_blocks_event_family_cross_split_leakage(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        # Synthetic review metadata allows this fixture to reach the split
        # leakage branch; it is not a real expert review.
        for card in literature["cards"]:
            card["domain_review_status"] = "DOMAIN_EXPERT_CONFIRMED"
            card["domain_review_evidence_sha256"] = "f" * 64
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        original = copy.deepcopy(collection["packets"][0])
        variant = copy.deepcopy(original)
        variant["task_id"] = "L1-SEASAT-SLIPRING-SYNTH-001-VARIANT"
        variant["case"]["case_id"] = "CASE-SEASAT-SYNTH-001-VARIANT"
        variant["case"]["provenance"]["diagnosis_run_refs"] = ["SYNTHETIC-MLRUN-SEASAT-VARIANT"]
        collection["packets"].append(variant)
        collection["packet_count"] = len(collection["packets"])
        # This fixture tests leakage after review; the statuses below are
        # synthetic test metadata, not real expert approvals.
        collection["data_status"] = "APPROVED_FOR_L1_EXPERIMENT"
        for packet in collection["packets"]:
            packet["review"]["status"] = "APPROVED_FOR_L1_EXPERIMENT"
        collection["split_assignments"] = [
            {"task_id": packet["task_id"], "split": (
                "train" if packet["task_id"] == original["task_id"] else
                "validation" if packet["task_id"] == variant["task_id"] else
                "test"
            )}
            for packet in collection["packets"]
        ]
        with self.assertRaisesRegex(L1TaskPacketError, "L1_EVENT_FAMILY_CROSSES_DATASET_SPLITS"):
            validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])

    def test_incompatible_history_is_qualified_and_cannot_support_current_cause(self):
        packet = make_packet(history_status="CONFIRMED")
        item = packet["history_context"]["items"][0]
        item["historical_equipment_scope"] = "reaction_wheel_legacy_type"
        item["hardware_compatibility"] = "INCOMPATIBLE"
        item["applicability_limitations"] = ["不同代际轮组结构不同，不可直接迁移故障原因与处置方法"]
        prior = packet["case"]["input"]["historical_cases"][0]
        prior["applicability_limitations"] = list(item["applicability_limitations"])
        packet["case"]["expected_output"]["historical_experience_relevance"][0]["transfer_limitations"] = list(item["applicability_limitations"])
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        self.assertEqual(self.validate(packet)["history_item_count"], 1)
        packet["case"]["expected_output"]["cause_localization"]["candidates"][0]["supporting_refs"].append(prior["case_ref"])
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(L1TaskPacketError, "INCOMPATIBLE_HISTORY_CANNOT_SUPPORT_CURRENT_CAUSE"):
            self.validate(packet)

    def test_history_reuse_packet_preserves_partial_cassini_context_as_unknown_hardware(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        cards = {card["case_id"]: card for card in literature["cards"]}
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        packet = next(p for p in collection["packets"] if p["task_id"] == "L1-FUSE-RWA-HISTORY-REUSE-SYNTH-012")
        result = validate_l1_task_packet(packet, source_fact_cards=[cards[ref] for ref in set(packet["source_fact_refs"] + packet["history_context"]["items"][0]["source_refs"])])
        self.assertEqual(result["decision"], "READY_FOR_L1_EXPERT_REVIEW")
        self.assertEqual(packet["case"]["task_type"], "historical_case_reuse")
        history = packet["history_context"]["items"][0]
        self.assertEqual(history["outcome_status"], "PARTIALLY_CONFIRMED")
        self.assertEqual(history["hardware_compatibility"], "UNKNOWN")
        self.assertTrue(history["applicability_limitations"])
        self.assertFalse(history["hit_metadata"]["diagnostic_vote_allowed"])
        self.assertNotIn(history["case_ref"], packet["formal_target"]["cause_localization"]["candidates"][0]["supporting_refs"])
        self.assertIn(history["case_ref"], packet["formal_target"]["historical_experience_relevance"][0]["case_ref"])

    def test_l1_pilot_covers_all_six_declared_task_types(self):
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        task_types = {packet["case"]["task_type"] for packet in collection["packets"]}
        self.assertEqual(task_types, {
            "diagnostic_synthesis",
            "historical_case_reuse",
            "conflict_reconciliation",
            "evidence_sufficiency",
            "next_step_recommendation",
            "handover_summary",
        })

    def test_ground_test_source_cannot_be_mislabeled_as_flight_context(self):
        packet = make_packet()
        card = source_card("PUBLIC_GROUND_TEST_REPORT")
        card["event_status"] = "GROUND_TEST_EVENT"
        card["event_family_id"] = "L0-SEASAT-FAMILY"
        card["event_episode_id"] = "L0-SEASAT-GROUND-TEST"
        packet["case"]["input"]["operational_context"]["mission_phase"] = "IN_ORBIT_OPERATION"
        packet["history_context"]["query"]["mission_phase"] = "IN_ORBIT_OPERATION"
        packet["synthetic_provenance"]["generated_fields"][3]["assumption"] = "Synthetic flight operations context"
        with self.assertRaisesRegex(L1TaskPacketError, "L1_GROUND_TEST_SOURCE_MISLABELED_AS_FLIGHT_CONTEXT"):
            self.validate(packet, [card])

    def test_flight_source_cannot_be_mislabeled_as_ground_test_context(self):
        packet = make_packet()
        packet["case"]["input"]["operational_context"]["mission_phase"] = "GROUND_THERMAL_VACUUM_TEST"
        packet["history_context"]["query"]["mission_phase"] = "GROUND_THERMAL_VACUUM_TEST"
        packet["synthetic_provenance"]["generated_fields"][3]["assumption"] = "Synthetic ground test context"
        with self.assertRaisesRegex(L1TaskPacketError, "L1_FLIGHT_SOURCE_MISLABELED_AS_GROUND_CONTEXT"):
            self.validate(packet)

    def test_l1_packet_rejects_domain_expert_rejected_source_fact(self):
        packet = make_packet()
        card = source_card()
        card["domain_review_status"] = "DOMAIN_EXPERT_REJECTED"
        card["domain_review_evidence_sha256"] = "d" * 64
        with self.assertRaisesRegex(L1TaskPacketError, "L1_SOURCE_FACT_CARD_DOMAIN_REVIEW_REJECTED"):
            self.validate(packet, [card])

    def test_l1_experiment_approval_requires_domain_confirmed_l0_source(self):
        packet = make_packet()
        packet["review"]["status"] = "APPROVED_FOR_L1_EXPERIMENT"
        packet["review"]["reviewer_id"] = "SYNTHETIC-REVIEWER"
        packet["review"]["reviewed_at"] = "2026-11-16T08:00:00Z"
        with self.assertRaisesRegex(L1TaskPacketError, "L1_SOURCE_FACTS_NOT_DOMAIN_REVIEWED"):
            self.validate(packet)

    def test_l1_experiment_approval_accepts_confirmed_l0_with_receipt_digest(self):
        packet = make_packet()
        packet["review"]["status"] = "APPROVED_FOR_L1_EXPERIMENT"
        packet["review"]["reviewer_id"] = "SYNTHETIC-REVIEWER"
        packet["review"]["reviewed_at"] = "2026-11-16T08:00:00Z"
        card = source_card()
        card["domain_review_status"] = "DOMAIN_EXPERT_CONFIRMED"
        card["domain_review_evidence_sha256"] = "e" * 64
        result = self.validate(packet, [card])
        self.assertEqual(result["decision"], "READY_FOR_L1_EXPERIMENT")
        self.assertEqual(result["source_fact_domain_review_status_counts"]["DOMAIN_EXPERT_CONFIRMED"], 1)

    def test_collection_audit_reports_pending_l0_domain_review_count(self):
        literature = json.loads((ROOT / "examples/l0_public_literature_fact_cards_2026-11-15.json").read_text(encoding="utf-8"))
        collection = json.loads((ROOT / "examples/l1_literature_synthetic_task_packets_v0.1.json").read_text(encoding="utf-8"))
        result = validate_l1_task_packet_collection(collection, source_fact_cards=literature["cards"])
        self.assertEqual(result["source_fact_domain_review_status_counts"]["AI_ASSISTED_REVIEW_PENDING_DOMAIN_EXPERT_CONFIRMATION"], 12)
        self.assertEqual(result["source_fact_domain_review_status_counts"]["DOMAIN_EXPERT_CONFIRMED"], 0)


    def test_confirmed_compatible_history_is_not_current_fault_support(self):
        packet = make_packet(history_status="CONFIRMED")
        history_ref = packet["history_context"]["items"][0]["case_ref"]
        packet["case"]["expected_output"]["cause_localization"]["candidates"][0]["supporting_refs"].append(history_ref)
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(L1TaskPacketError, "^HISTORY_DIRECT_EVIDENCE_ROLE_FORBIDDEN$"):
            self.validate(packet)

    def test_rejected_history_is_not_evidence_assessment_support(self):
        packet = make_packet(history_status="REJECTED")
        history_ref = packet["history_context"]["items"][0]["case_ref"]
        packet["case"]["expected_output"]["evidence_assessment"]["supporting_refs"].append(history_ref)
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(L1TaskPacketError, "^HISTORY_DIRECT_EVIDENCE_ROLE_FORBIDDEN$"):
            self.validate(packet)

    def test_partially_confirmed_history_is_not_current_contradicting_observation(self):
        packet = make_packet(history_status="PARTIALLY_CONFIRMED")
        history_ref = packet["history_context"]["items"][0]["case_ref"]
        packet["case"]["expected_output"]["evidence_assessment"]["contradicting_refs"].append(history_ref)
        packet["formal_target"] = copy.deepcopy(packet["case"]["expected_output"])
        with self.assertRaisesRegex(L1TaskPacketError, "^HISTORY_DIRECT_EVIDENCE_ROLE_FORBIDDEN$"):
            self.validate(packet)


if __name__ == "__main__":
    unittest.main()
